
# Project Setup Instructions

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
