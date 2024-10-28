# Scene-to-Style Web Application

This is a Streamlit app for personalized furniture and fashion recommendations. Users can upload a video, and the app uses Gemini's multimodal analysis to first identify whether the content is best suited for furniture or fashion recommendations. Based on this initial analysis, the app then provides tailored suggestions: for furniture, it evaluates the style and architecture of the space, offering relevant decor and furniture items; for fashion, it analyzes outfits, trends, and styles, recommending similar items to enhance the user’s wardrobe. The Imagine model visualizes these recommendations, and Google Lens enables users to search for items they like directly by image.

<div align="center">
  <img src="cover/scene-to-style-cover.gif" alt="Scene-to-Style Cover" width="500"/>
</div>

## Prerequisites

1. **GCP Account** - A GCP account with the image generation model activated. For more details on setup, refer to [this link]([https://cloud.google.com/](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)).
2. **Admin Role** - The user running the setup script must have Admin privileges, as it will:
   - Create a service account
   - Assign required roles
   - Set up Cloud Run
4. - **Organization Policy**: To make the application accessible outside of GCP, ensure the organization policy `iam.allowedPolicyMemberDomains` allows access to `allUsers` for the Cloud Run service. Alternatively, you can restrict access to a specific group or domain by setting `iam.allowedPolicyMemberDomains` to the desired domain (e.g., `example.com`) or group, rather than allowing all users. For more details, refer to the [Securing Access with Identity-Aware Proxy (IAP) guide](https://github.com/AmirMK/scence-to-style/edit/main/README.md#securing-access-with-identity-aware-proxy-iap).


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

- **Authentication**: By default, the application is configured to allow unauthenticated access. To restrict access, you can modify the Cloud Run settings in the script. Additionally, if you want to restrict access to specific users or domains, consider using [Identity-Aware Proxy (IAP)](https://github.com/AmirMK/scence-to-style/edit/main/README.md#step-2-enable-identity-aware-proxy-iap-for-cloud-run), which provides secure authentication and access control.

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

## Securing Access with Identity-Aware Proxy (IAP)

To restrict access to your Cloud Run app by user domain (e.g., `@google.com`), Google Cloud's Identity-Aware Proxy (IAP) allows only users with specific email domains to access the application. This method ensures that access is granted based on authenticated Google accounts, regardless of user location or device, creating a seamless yet secure user experience.

## Step-by-Step Instructions

### Step 1: Deploy the Cloud Run App Without Public Access
First, deploy your Cloud Run app but remove public access. This ensures that only authenticated users can access the app once IAP is enabled.

```bash
gcloud run deploy $CLOUD_RUN_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --platform managed \
    --region us-central1 \
    --service-account $SA_EMAIL \
    --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME,LOCATION=us-central1 \
    --concurrency 10 \
    --timeout 180
```
**Note**: Do not include the `--allow-unauthenticated` flag in this command. This prevents unauthenticated, public access to the app.

### Step 2: Enable Identity-Aware Proxy (IAP) for Cloud Run
1. Open the [Identity-Aware Proxy page in the Google Cloud Console](https://console.cloud.google.com/security/iap).
2. Find your deployed Cloud Run service in the IAP console.
3. Toggle **IAP** to **ON** for your service.

### Step 3: Configure Access Control with Domain Restriction
1. In the IAP page, click on **Access control** for your Cloud Run service.
2. To allow access by domain, add users with the role `IAP-secured Web App User`.
3. In the **New Principal** field, specify a domain like `@google.com` to allow all users from that domain, or specify individual emails as needed.
   - **Example**: To allow users from Google, you would enter `*@google.com` as a principal.
   - **Generalization**: This can be replaced with any domain you want to allow (e.g., `@example.com` for other organizations).
4. Click **Save** to apply the access controls.

### Step 4: Testing Access
1. Share the app’s URL with users from the authorized domain (e.g., `@google.com`).
2. When they access the URL, they’ll be prompted to sign in with their Google account.
3. Only users with an email that matches the specified domain will be allowed access.

### Optional: Update Project Policies
If you’ve previously configured `allowedPolicyMemberDomains` to allow all users, you can remove or restrict this setting, as it’s no longer necessary when IAP is in use.

## Benefits of Using IAP with Domain Restriction
- **Security**: Limits access to authenticated users from a specific domain, ensuring only authorized personnel can access the app.
- **Convenience**: Users don’t need to be on a specific network; access is granted based on their email domain.
- **Scalability**: Easily generalize to any organization by updating the domain in IAP.

This configuration provides a robust and flexible way to secure your Cloud Run app while keeping access management straightforward and scalable.
