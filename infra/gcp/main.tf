locals {
  services = toset([
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
  ])
}

resource "google_project_service" "required" {
  for_each = local.services
  project  = var.project_id
  service  = each.value

  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "images" {
  location      = var.region
  repository_id = "fde-gym"
  description   = "ClaimOps practice service images"
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}

resource "google_sql_database_instance" "postgres" {
  name             = "fde-gym-postgres"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.sql_tier
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 10
    disk_autoresize   = true

    backup_configuration {
      enabled = false
    }

    ip_configuration {
      ipv4_enabled = true
    }

    insights_config {
      query_insights_enabled = true
      record_client_address  = false
      record_application_tags = true
    }
  }

  deletion_protection = false
  depends_on          = [google_project_service.required]
}

resource "google_sql_database" "claimops" {
  name     = "claimops"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "claimops" {
  name     = "claimops"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "fde-gym-database-url"
  replication {
    auto {}
  }
  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret = google_secret_manager_secret.database_url.id
  secret_data = format(
    "postgresql+asyncpg://claimops:%s@/claimops?host=/cloudsql/%s",
    urlencode(var.db_password),
    google_sql_database_instance.postgres.connection_name,
  )
}

resource "google_pubsub_topic" "claim_events" {
  name       = "claimops-events"
  depends_on = [google_project_service.required]
}

resource "google_pubsub_subscription" "claim_events_worker" {
  name  = "claimops-worker"
  topic = google_pubsub_topic.claim_events.id

  ack_deadline_seconds       = 30
  message_retention_duration = "604800s"

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letters.id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }
}

resource "google_pubsub_topic" "dead_letters" {
  name = "claimops-events-dead-letter"
}

resource "google_storage_bucket" "objects" {
  name                        = var.object_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.force_destroy_bucket

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition { age = 30 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.required]
}

resource "google_service_account" "api" {
  account_id   = "claimops-api"
  display_name = "ClaimOps API runtime"
}

resource "google_service_account" "web" {
  account_id   = "claimops-web"
  display_name = "ClaimOps web runtime"
}

resource "google_project_iam_member" "api_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api.email}"
}

resource "google_storage_bucket_iam_member" "api_objects" {
  bucket = google_storage_bucket.objects.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${google_service_account.api.email}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "claimops-api"
  location = var.region

  template {
    service_account = google_service_account.api.email
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = var.api_image
      ports { container_port = 8000 }

      env {
        name  = "ENVIRONMENT"
        value = "gcp"
      }
      env {
        name  = "MISSION_ROOT"
        value = "/workspace/missions"
      }
      env {
        name  = "PUBSUB_TOPIC"
        value = google_pubsub_topic.claim_events.name
      }
      env {
        name  = "OBJECT_BUCKET"
        value = google_storage_bucket.objects.name
      }
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_project_iam_member.api_sql,
    google_project_iam_member.api_secret,
  ]
}

resource "google_cloud_run_v2_service" "web" {
  name     = "fde-gym-web"
  location = var.region

  template {
    service_account = google_service_account.web.email
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    containers {
      image = var.web_image
      ports { container_port = 3000 }
      env {
        name  = "API_INTERNAL_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
    }
  }

  depends_on = [google_project_service.required]
}

resource "google_cloud_run_v2_service_iam_member" "api_public" {
  count    = var.allow_public ? 1 : 0
  project  = var.project_id
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "web_public" {
  count    = var.allow_public ? 1 : 0
  project  = var.project_id
  location = google_cloud_run_v2_service.web.location
  name     = google_cloud_run_v2_service.web.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

