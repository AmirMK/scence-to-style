#!/bin/bash

# Function to display usage message
usage() {
    echo "Usage: $0 --project_id <project_id> --peo_access_key <peo_access_key>"
    exit 1
}

# Function to check the exit status of the last command
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed. Exiting."
        exit 1
    fi
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --project_id) PROJECT_ID="$2"; shift ;;
        --peo_access_key) PEO_ACCESS_KEY="$2"; shift ;;
        *) usage ;;
    esac
    shift
done

# Check if required arguments are provided
if [ -z "$PROJECT_ID" ] || [ -z "$PEO_ACCESS_KEY" ]; then
    echo "Error: PROJECT_ID and peo_access_key must be provided."
    usage
fi

# Automatically set the bucket name based on the project_id
BUCKET_NAME="${PROJECT_ID}_scene_style"

# Enable necessary GCP APIs
gcloud services enable storage.googleapis.com
check_status "Enabling Cloud Storage API"

# Create Google Cloud Storage bucket
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME/
check_status "Creating Google Cloud Storage bucket"


# Enable other necessary GCP APIs
gcloud services enable aiplatform.googleapis.com
check_status "Enabling Vertex AI API"

gcloud services enable artifactregistry.googleapis.com
check_status "Enabling Artifact Registry API"

gcloud services enable run.googleapis.com
check_status "enables the IAM Service Account Credentials API"

gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID
check_status "Enabling Cloud Run API"
# Create directory and move into it
mkdir -p scene_style
cd scene_style || exit
check_status "Directory creation"

# Download required files from the GCS folder
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/app.py
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/exploration.py
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/gcs_handler.py
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/generation.py
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/prompt_config.yaml
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/requirements.txt
curl -O https://raw.githubusercontent.com/AmirMK/scence-to-style/refs/heads/main/Dockerfile
curl -L -o logo.png https://raw.githubusercontent.com/AmirMK/scence-to-style/main/logo.png


check_status "Downloading Dockerfile"



# Build and push Docker image
IMAGE_NAME="${PROJECT_ID}-scene-style-img"
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME .
check_status "Docker build"

docker push gcr.io/$PROJECT_ID/$IMAGE_NAME
check_status "Docker push"

# Create service account and assign roles
SA_NAME="${PROJECT_ID}-scene-style-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
    --display-name="$SA_NAME" \
    --project=$PROJECT_ID
check_status "Service account creation"

# Assign IAM policy bindings
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"
check_status "Assigning aiplatform.user IAM policy"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectViewer"
check_status "Assigning storage.objectViewer IAM policy"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectCreator"
check_status "Assigning storage.objectCreator IAM policy"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
    --role="roles/iam.serviceAccountTokenCreator" \
    --member="serviceAccount:${SA_EMAIL}"
check_status "Assigning serviceAccountTokenCreator IAM policy"

gsutil iam ch serviceAccount:$SA_EMAIL:legacyBucketReader gs://$BUCKET_NAME
check_status "Assigning legecy read access"

# Set Cloud Run service name
CLOUD_RUN_NAME="${PROJECT_ID}-scene-style-run"

# Deploy Cloud Run service
gcloud run deploy $CLOUD_RUN_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account $SA_EMAIL \
    --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME,LOCATION=us-central1 \
    --concurrency 10 \
    --timeout 180
check_status "Cloud Run deployment"

gcloud run services add-iam-policy-binding $CLOUD_RUN_NAME \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
check_status "Cloud Run authentication"

# Finish setup
echo "Setup completed successfully!"
