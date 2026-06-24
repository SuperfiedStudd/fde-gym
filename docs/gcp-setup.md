# Optional GCP deployment path

Local Docker is the default. The GCP path is for deployment practice after the local missions work; nothing in the gym requires cloud access.

## Cost warning first

Cloud SQL is the largest likely always-on cost. Cloud Run, Artifact Registry storage, Pub/Sub, GCS, Secret Manager, logging ingestion/retention, egress, and build minutes can also incur charges. Free tiers and prices change—check the current GCP pricing pages and Billing reports before applying Terraform.

Use a dedicated project, attach a budget with alerts, keep Cloud Run minimum instances at zero, choose the smallest non-production Cloud SQL tier, and destroy the environment after practice. Budget alerts notify; they do not automatically cap spend.

## Prerequisites

- A dedicated GCP project with billing enabled.
- `gcloud` CLI authenticated with `gcloud auth application-default login`.
- Terraform 1.7+.
- Docker with Artifact Registry authentication.
- Permission to enable APIs, create service accounts, and manage the listed resources.

The Terraform configuration enables:

- Cloud Run Admin API
- Cloud SQL Admin API
- Artifact Registry API
- Pub/Sub API
- Secret Manager API
- Cloud Storage API
- Cloud Logging and Monitoring APIs
- IAM and Service Usage APIs

## Bootstrap images

Set variables in PowerShell:

```powershell
$env:GCP_PROJECT="your-fde-gym-project"
$env:GCP_REGION="us-west1"
gcloud auth configure-docker "$env:GCP_REGION-docker.pkg.dev"
```

Terraform creates the repository, so first apply with placeholder images or apply only the registry resource as described in `infra/gcp/README.md`. Then build and push versioned images manually. Never use mutable `latest` for a rollback exercise.

## Terraform

```powershell
Set-Location infra/gcp
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

Required variables include project id, region, unique GCS bucket name, image references, database password, and a cost-conscious Cloud SQL tier. Put secrets in `terraform.tfvars` only for local practice and never commit that file. For a longer-lived environment, inject secret values through CI or create secret versions outside Terraform state.

## Environment variables

API Cloud Run:

- `DATABASE_URL`: Unix-socket Cloud SQL asyncpg URL or a Secret Manager-backed equivalent.
- `MISSION_ROOT`: missions baked into the API image.
- `PROGRESS_FILE`: for cloud, replace local progress storage before relying on it across instances.
- `ENVIRONMENT=gcp`, `LOG_LEVEL=INFO`.
- `PUBSUB_TOPIC`, `OBJECT_BUCKET`, and `GCP_PROJECT` for future adapters.

Web Cloud Run:

- `API_INTERNAL_URL`: deployed API URL.
- `NEXT_PUBLIC_API_URL`: publicly reachable API URL or same-origin proxy.

The starter local worker speaks Redis. Pub/Sub is provisioned as the target transport, but deploying the worker requires completing a Pub/Sub push/pull adapter mission; do not point the Redis worker at Pub/Sub and assume compatibility.

## Service account basics

Each runtime receives a dedicated service account with narrow roles. API gets Cloud SQL client, secret accessor, Pub/Sub publisher, and object permissions scoped where Terraform supports it. Avoid user-managed service account keys; Cloud Run provides workload credentials automatically.

Do not grant project Editor. Audit `terraform plan` for IAM changes before applying.

## Logging and observability

Cloud Run captures structured JSON stdout/stderr in Cloud Logging. Preserve stable fields such as `request_id`, `service`, `route`, `status`, `duration_ms`, `job_id`, and `outcome`. Avoid high-cardinality metric labels and sensitive claim/user fields. Configure log-based metrics or Managed Prometheus only when a mission calls for them.

## CI/CD path

`.github/workflows/ci.yml` runs platform tests, TypeScript checks, and service tests without deploying. A deployment workflow should use GitHub Workload Identity Federation, build immutable image tags, run checks, deploy a new Cloud Run revision with no traffic, smoke test it, then shift traffic. Do not store JSON service-account keys in GitHub secrets.

## Teardown and surprise-billing defense

Before teardown, export anything you want to keep. Then:

```powershell
Set-Location infra/gcp
terraform plan -destroy
terraform destroy
gcloud artifacts docker images list "$env:GCP_REGION-docker.pkg.dev/$env:GCP_PROJECT/fde-gym"
```

Confirm in the Cloud Console that Cloud SQL, Cloud Run services, Artifact Registry images, GCS buckets, Pub/Sub subscriptions, and Secret Manager versions are gone. Terraform cannot delete resources you created manually outside its state. The most reliable final cleanup for a dedicated practice project is shutting down or deleting the project after checking for retained data.

