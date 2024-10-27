# Scene-to-Style Web Application

This is a Streamlit app for personalized furniture and fashion recommendations. Users can upload a video, and the app uses Gemini's multimodal analysis to first identify whether the content is best suited for furniture or fashion recommendations. Based on this initial analysis, the app then provides tailored suggestions: for furniture, it evaluates the style and architecture of the space, offering relevant decor and furniture items; for fashion, it analyzes outfits, trends, and styles, recommending similar items to enhance the user’s wardrobe. The Imagine model visualizes these recommendations, and Google Lens enables users to search for items they like directly by image.


<img src="images/cover.gif" alt="Alt text" width="700"/>

## Prerequisites

1. **GCP Account** - A GCP account with the image generation model activated. For more details on setup, refer to [this link]([https://cloud.google.com/](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)).
2. **Admin Role** - The user running the setup script must have Admin privileges, as it will:
   - Create a service account
   - Assign required roles
   - Set up Cloud Run
4. **Organization Policy** - To make the application accessible outside of GCP, ensure the organization policy `iam.allowedPolicyMemberDomains` allows `allUsers` access to the Cloud Run service.

## Quick Start

To set up and deploy the Scene-to-Style app, follow these steps:

### Step 1: Download the Setup Script

Open your GCP Cloud Shell and download the `set_up.sh` file:
   ```bash
   curl -L -o set_up.sh https://raw.githubusercontent.com/AmirMK/scence-to-style/main/set_up.sh
```

### Step 2: Run the Setup Script
In your Cloud Shell, make the script executable and run it as follows:

   ```bash
   chmod +x set_up.sh
  ./set_up.sh --project_id <YOUR_PROJECT_ID>
```
After the setup completes, you’ll receive the URL for accessing the web application. Additionally, all the application information, including project details, service account name, bucket name, and Cloud Run URL, will be saved in app_info.txt for reference.

## Important Notes

- **Authentication**: By default, the application is configured to allow unauthenticated access. To restrict access, modify the Cloud Run settings in the script.

- **Environment Variables**: The script sets essential environment variables for the application’s functionality:
  - **Service Account and Bucket Name**: In addition to `PROJECT_ID`, these are the main environment variables required to run the app. The script automatically assigns names to these variables, but users can change them by modifying lines 33 and 34 in the `set_up.sh` file.


## Deployment Process Overview

The `set_up.sh` script automates the setup process by performing the following actions:

### Project and Bucket Setup
- Sets up the bucket as `<project_id>_scene_style`.
- Enables required GCP APIs for Cloud Storage, Vertex AI, Artifact Registry, and Cloud Run.

### File Downloads
- Creates a `scene_style` directory and downloads the necessary files (application code, Dockerfile, configurations) from this repository.

### Builds and Pushes Docker Image
- Builds a Docker image from the provided `Dockerfile`.
- Pushes the Docker image to Google Container Registry with the name `gcr.io/<project_id>/<project_id>-scene-style-img`.

### Service Account Creation and Role Assignment
- Creates a dedicated service account `<project_id>-scene-style-sa`.
- Assigns roles:
  - Vertex AI User (`roles/aiplatform.user`)
  - Cloud Storage Viewer and Creator (`roles/storage.objectViewer`, `roles/storage.objectCreator`)
  - Service Account Token Creator (`roles/iam.serviceAccountTokenCreator`).

### Cloud Run Deployment
- Deploys the application on Cloud Run in `us-central1`, with environment variables set for `PROJECT_ID`, `BUCKET_NAME`, and `LOCATION`.
- Configures the Cloud Run service to allow unauthenticated access for public availability.

### Assigns Cloud Run Invoker Role
- Grants public access to the application by adding the `roles/run.invoker` role to `allUsers`.

### Completion
- Outputs a success message once the setup is complete.

