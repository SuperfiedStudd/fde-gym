variable "project_id" {
  description = "Dedicated GCP project id."
  type        = string
}

variable "region" {
  description = "Primary deployment region."
  type        = string
  default     = "us-west1"
}

variable "api_image" {
  description = "Immutable Artifact Registry image reference for the API."
  type        = string
}

variable "web_image" {
  description = "Immutable Artifact Registry image reference for the web app."
  type        = string
}

variable "db_password" {
  description = "Practice database password. Stored in Terraform state; use external secret versioning for long-lived environments."
  type        = string
  sensitive   = true
}

variable "sql_tier" {
  description = "Cloud SQL machine tier. Recheck current regional pricing before apply."
  type        = string
  default     = "db-f1-micro"
}

variable "object_bucket_name" {
  description = "Globally unique GCS bucket name."
  type        = string
}

variable "allow_public" {
  description = "Allow unauthenticated access to API and web for personal practice."
  type        = bool
  default     = false
}

variable "force_destroy_bucket" {
  description = "Allow Terraform destroy to remove non-empty practice bucket."
  type        = bool
  default     = false
}

