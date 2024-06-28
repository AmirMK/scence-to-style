from google.cloud import storage
from google.auth import compute_engine
import pandas as pd
from PIL import Image
import io

def upload_blob_from_string(bucket_name, data, destination_blob_path):
    """Uploads a string to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_path)
    blob.upload_from_string(data)
    print(f"Text data uploaded to {destination_blob_path}.")


def upload_blob_from_file(bucket_name, file_obj, destination_blob_path):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_path)
    blob.upload_from_file(file_obj)
    print(f"File uploaded to {destination_blob_path}.")
    return f"gs://{bucket_name}/{destination_blob_path}"


def upload_blob_from_file_remote(bucket_name, source_file_path, destination_blob_path):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_path)
    with open(source_file_path, "rb") as file_obj:
        blob.upload_from_file(file_obj)
    print(f"File {source_file_path} uploaded to {destination_blob_path}.")
    return f"gs://{bucket_name}/{destination_blob_path}"


def save_df_to_gcs_as_csv(df, bucket_name, destination_blob_name):
    """Saves a DataFrame to Google Cloud Storage as a CSV."""
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)

    # Create a GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload the data
    blob.upload_from_string(csv_data, content_type='text/csv')
    print(f"DataFrame saved as CSV to gs://{bucket_name}/{destination_blob_name}")



# Load the CSV data from GCS
def load_data(theme, bucket):
    client = storage.Client()
    gcs_path = f'gs://{theme}/{bucket}/Rec_Table.csv'
    return pd.read_csv(gcs_path)

# Get image from GCS bucket
def get_image(bucket_name, image_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(image_name)
    image_bytes = blob.download_as_bytes()
    image = Image.open(io.BytesIO(image_bytes))
    return image

def read_file_from_bucket(bucket_name, file_name):
    # Initialize a client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Get the blob (file) from the bucket
    blob = bucket.blob(f'{file_name}/Intro.txt')

    # Download the contents of the file as a string
    content = blob.download_as_text()

    return content

def list_subfolders(bucket_name):
    
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)    
    blobs = bucket.list_blobs()    
    
    subfolders = set()

    for blob in blobs:        
        name = blob.name
        parts = name.split('/')
        if len(parts) > 1:
            subfolders.add(parts[0])
    subfolders_list = list(subfolders)
    subfolders_list.insert(0, 'None')
    return list(subfolders_list)