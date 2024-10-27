# Scene-to-Style Web Application

This is a Streamlit app for furniture recommendations. Users can upload any type of video, and Gemini multimodal analysis evaluates it. If relevant, the app provides a range of furniture recommendations based on the style and architecture of the house. The Imagine model visualizes these recommendations, and Google Lens is used for users to search for items they like by image.


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


