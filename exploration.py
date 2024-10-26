import streamlit as st
import gcs_handler as gcsh
import json
import ast
from datetime import timedelta, datetime

import google.auth
from google.auth import compute_engine, default
from google.auth.transport import requests
from google.cloud import storage
import urllib.parse


# Function to generate a signed URL
def generate_signed_url(bucket_name, blob_name, expiration_minutes=5):  
    
    # Use Google Auth Default credentials
    credentials, _ = default()
    auth_request = requests.Request()
    credentials.refresh(auth_request)            
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    signing_credentials = compute_engine.IDTokenCredentials(
                    auth_request,
                    "",
                    service_account_email=credentials.service_account_email
    )    
    
    expires_at_ms = datetime.now() + timedelta(minutes=expiration_minutes)
    
    signed_url = blob.generate_signed_url(expires_at_ms, credentials=signing_credentials, version="v4")
    encoded_url = urllib.parse.quote(signed_url, safe='')
       
    return encoded_url,signed_url


def read_data(bucket_name, subfolder):                
        recommendation = gcsh.load_csv(bucket_name, f'{subfolder}/rec.csv')
        intro = gcsh.load_json(bucket_name, f'{subfolder}/intro.json')
        videos = gcsh.list_files_in_subfolder(bucket_name, f'{subfolder}/videos')                
        return recommendation, intro, f'{videos[0]}'
    

def display_images(bucket,image_paths, recommendation_name):
        
        cols = st.columns(2)
        for i, image_path in enumerate(image_paths):                        
            image = gcsh.get_image(f'{bucket}', image_path)            
            with cols[i % 2]:
                st.image(image, caption=f"{recommendation_name} - {i}", width=300)
                encoded_url,_ = generate_signed_url(f'{bucket}', image_path)
                google_lens_url = f"https://lens.google.com/uploadbyurl?url={encoded_url}"
                st.markdown(f"[Google Search]({google_lens_url})")




def display_recommendations(bucket,recs,intro,video_url):
    st.subheader('Current Style')
    
    try:
        _,video_encoded_url = generate_signed_url(bucket, video_url, expiration_minutes=5)        
        st.video(video_encoded_url)
    except:
        st.warning("No video files found")

    
    for key, value in intro.items():
        formatted_key = key.replace('_', ' ')  # Replace underscores with spaces
        st.markdown(f"**{formatted_key}:** {value}")
    
    styles = recs['recommendation_type'].unique().tolist()
    for style in styles:
        st.subheader(style)
        rec = recs[recs['recommendation_type']==style]
        for _, row in rec.iterrows():

            st.write(f"**Recommendation**:  {row['recommendation_name']}")
            st.write(f"**Description**:  {row['recommendation_description']}")
            st.write(f"**Reason for this recommendation**:  {row['reasoning']}")
            with st.expander('**Image**', expanded=True):   
                image_url_list = ast.literal_eval(row['image_url'])

                display_images(bucket,image_url_list,row['recommendation_name'])

            st.divider()  

        
def explore(bucket_name):
    file_list = gcsh.list_subfolders(bucket_name)
    subfolder = st.selectbox('Select your item', file_list)
    if st.button('Show the recommendations', key='recomendation'):
        recommendation, intro, video_url = read_data(bucket_name, subfolder)    
        
        display_recommendations(bucket_name,recommendation,intro,video_url)
