
# Project Setup Instructions

You need to have a GCP account in which the image generation model is activated (refer to this [link](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)).

1. **Create a Workbench Instance**  
   Set up a Workbench instance with Python 3 as the environment.

2. **Configure Firewall Rules**  
   Ensure the firewall rules allow access to external IPs.

3. **Note Project ID and Service Account**  
   Record your project ID and instance service account. Then, run the `setup_gcloud` script as follows:
   ```bash
   ./setup_gcloud.sh <project_id> <service_account_email>
   ```

4. **Clone the Repository**  
   Open the Workbench (Jupyter Notebook) and run the following command in the terminal:
   ```bash
   !git clone https://github.com/AmirMK/scence-to-style.git
   ```

5. **Install Required Packages**  
   Install the necessary packages by running the following command in the workbench terminal:
   ```bash
   pip install -r requirements.txt
   ```
