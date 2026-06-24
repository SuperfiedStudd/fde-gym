param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "us-west1",
    [Parameter(Mandatory = $true)][string]$Tag
)

$ErrorActionPreference = "Stop"
$Repository = "$Region-docker.pkg.dev/$ProjectId/fde-gym"

gcloud config set project $ProjectId
gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet

docker build --file apps/api/Dockerfile.gcp --tag "$Repository/api:$Tag" .
docker build --file apps/web/Dockerfile --tag "$Repository/web:$Tag" .
docker push "$Repository/api:$Tag"
docker push "$Repository/web:$Tag"

Write-Host "Images pushed. Set these immutable references in terraform.tfvars:"
Write-Host "api_image = `"$Repository/api:$Tag`""
Write-Host "web_image = `"$Repository/web:$Tag`""
Write-Host "Review terraform plan before applying."

