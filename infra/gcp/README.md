# GCP infrastructure

Read `docs/gcp-setup.md` before applying. This stack creates billable resources.

Because Cloud Run image references must already exist, bootstrap in two phases:

```bash
terraform init
terraform apply -target=google_artifact_registry_repository.images
```

Build and push immutable API/web images, put their references in `terraform.tfvars`, inspect `terraform plan`, then apply the full stack. `apps/api/Dockerfile.gcp` includes mission manifests; the local API Dockerfile expects a bind mount instead.

The Pub/Sub topic, retrying subscription, and dead-letter topic are target infrastructure. The starter Python worker consumes Redis and is not deployed by this Terraform until a Pub/Sub adapter exists.

State contains sensitive database material in this practice configuration. Use a protected remote state backend and external secret version creation before treating this as shared infrastructure.

