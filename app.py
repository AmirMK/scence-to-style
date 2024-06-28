import streamlit as st
import pandas as pd
from datetime import timedelta, datetime
import time
import filetype
import yaml
import urllib.parse

import google.auth
from google.auth import compute_engine
from google.auth.transport import requests

import recomm as rec
import gcs_handler as gcsh

def get_project_info():    
    global PROJECT_ID, LOCATION, service_account_email, bucket
    with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
    PROJECT_ID, LOCATION, service_account_email, bucket =  config['project_id'], config['location'], config['service_account_email'], config['bucket']
    
    return 0 
    
# Function to generate a signed URL
def generate_signed_url(bucket_name, blob_name, expiration_minutes=2):    
    auth_request = requests.Request()
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    signing_credentials = compute_engine.IDTokenCredentials(auth_request, "", service_account_email=service_account_email)
    expires_at_ms = datetime.now() + timedelta(minutes=expiration_minutes)
    signed_url = blob.generate_signed_url(expires_at_ms, credentials=signing_credentials, version="v4")
    encoded_url = urllib.parse.quote(signed_url, safe='')
    google_lens_url = f"https://lens.google.com/uploadbyurl?url={encoded_url}"
   

    return google_lens_url

def display_images(bucket, image_paths, furniture_name):
    try:
        cols = st.columns(2)
        for i, image_path in enumerate(image_paths):                        
            image = gcsh.get_image(f'{bucket}', image_path)            
            with cols[i % 2]:
                st.image(image, caption=f"{furniture_name} - {i}", width=300)
                google_lens_url = ''#generate_signed_url(f'{bucket}', image_path)
                st.markdown(f"[Google Search]({google_lens_url})")
    except Exception as e:
        st.write(f"Error loading images: {e}")

                        
# Function to display progress with task names
def update_progress(progress_stage, status_texts, task_names):
    for i, status_text in enumerate(status_texts):
        if i < progress_stage:
            status_text.markdown(f"**{task_names[i]}**: ✅")  # Completed task
        else:
            status_text.markdown(f"**{task_names[i]}**: 🔄")  # Pending task


# Display recommendations
def display_recommendations(bucket, data, recommendation_type, option, num_recommendations):
    
    st.subheader(f"{recommendation_type} Recommendations")    
    st.divider()  
    recs = data[data['recommendation_type'] == recommendation_type].head(num_recommendations)
    
    # Define a mapping from bucket to column names
    column_mapping = {        
        'decoration_recommendation': {
            'name': 'furniture_name',
            'description': 'furniture_description'
        }
    }
    
    # Get the appropriate column names based on the bucket
    name_column = column_mapping['decoration_recommendation']['name']
    description_column = column_mapping['decoration_recommendation']['description']
    
    for _, row in recs.iterrows():
        
        st.write(f"**Recommendation**:  {row[name_column]}")
        st.write(f"**Description**:  {row[description_column]}")
        st.write(f"**Why?**:  {row['reasoning']}")
        with st.expander('**Image**', expanded=True):                                    
            image_paths = [f"{option}/image-{row['ID']}-{i}.JPG" for i in range(2)]
            display_images(bucket, image_paths,row[name_column])
            
        st.write("---")

        
        
def main():
    
    st.image("./logo.png",width=1000)    
    st.title("")    
    
    get_project_info()
            
    with st.sidebar:
        task = st.radio("What do you want to do?",["Explore","Generate"])        
        #theme = f'decoration_recommendation'
        #st.session_state['theme'] = theme
        st.session_state['options'] = gcsh.list_subfolders(bucket)        
        st.session_state['option'] = 'None'
        

        if 'task' not in st.session_state or st.session_state['task'] != task:
                st.session_state['task'] = task
                st.session_state['option'] = 'None'
                st.session_state['video'] = ''
                        
                
        if task == "Explore":
                if 'options' not in st.session_state:
                    st.session_state['options'] = ['None']
                st.session_state['option'] = st.selectbox('Select your...', st.session_state['options'])            
                if st.button('Show me!') and st.session_state['options'] != 'None':            
                        st.session_state['data'] = gcsh.load_data(bucket, st.session_state['option'])
                        st.session_state['intro'] = gcsh.read_file_from_bucket(bucket, st.session_state['option'])                   
                        st.session_state['recommendation_types'] = st.session_state['data']['recommendation_type'].unique()
                        st.session_state['video'] = f"https://storage.cloud.google.com/{bucket}/{st.session_state['option']}/{st.session_state['option']}.{file_type}"
                        

        elif task == "Generate":
                        
            
            task_names = ["Initializing", "Recommendation","Rec Saving","Visulization","Viz Saving"]


            uploaded_video = st.file_uploader("", type=["mp4", "mov", "avi", "mkv"])
            
            filename = st.text_input('Enter the name for your recommendations', value="")
            st.session_state['option'] = filename
            if st.button('Show me!') and uploaded_video is not None:
                
                kind = filetype.guess(uploaded_video)
                file_type = kind.extension                
                
                task1_status = st.empty()
                task2_status = st.empty()
                task3_status = st.empty() 
                task4_status = st.empty() 
                task5_status = st.empty() 
                
                status_texts = [task1_status, task2_status, task3_status,task4_status,task5_status]

                with st.spinner('Generating Recommendation...'):
                    file = f"{st.session_state['option']}/{st.session_state['option']}.{file_type}"
                    video_file_url = gcsh.upload_blob_from_file(bucket, uploaded_video,file)                                     
                    update_progress(1, status_texts,task_names)                 
                    valid = rec.video_validation(PROJECT_ID, LOCATION, video_file_url,'',file_type)
                    
                    if valid == 'yes':
                                                                    
                        
                        update_progress(2, status_texts,task_names)                 
                        prompt, instructions = rec.get_prompt(bucket)                                                         
                        response_recom = rec.generate_recommenation(PROJECT_ID, LOCATION, video_file_url,prompt,instructions, file_type)    
                        intro, df_rocm = rec.clean_response(response_recom)
                        update_progress(3, status_texts,task_names) 
                        gcsh.upload_blob_from_string(bucket, intro, destination_blob_path=f"{st.session_state['option']}/Intro.txt")
                        gcsh.save_df_to_gcs_as_csv(df = df_rocm,  bucket_name = bucket,  destination_blob_name=f"{st.session_state['option']}/Rec_Table.csv")
                        
                        update_progress(4, status_texts,task_names) 
                        rec.image_gen(df_rocm)
                        
                        update_progress(5, status_texts,task_names) 
                        rec.image_save(df_rocm,bucket,st.session_state['option'])
                        rec.delete_images(df_rocm)
                
                        st.success('Done!') 

                        st.session_state['data'] = gcsh.load_data(bucket, st.session_state['option'])
                        st.session_state['intro'] = gcsh.read_file_from_bucket(bucket, st.session_state['option'])                   
                        st.session_state['recommendation_types'] = st.session_state['data']['recommendation_type'].unique()
                        st.session_state['video'] = f"https://storage.cloud.google.com/{bucket}/{st.session_state['option']}/{st.session_state['option']}.{file_type}"
                    else:
                        st.warning('The video does not have any valid/enough scences!')

            
    if 'data' in st.session_state and st.session_state['option']!='None':                                        
            st.sidebar.video(st.session_state['video'])         
            st.subheader(f"Current Style")
            st.write(st.session_state['intro'])


            st.sidebar.subheader(f"Select decoration type")
            selected_type = st.sidebar.radio("Select recommendation type", st.session_state['recommendation_types'])

           
            if selected_type:
                display_recommendations(bucket, st.session_state['data'], selected_type,st.session_state['option'], 5)
            else:
                st.write("Please select a recommendation type.")

if __name__ == "__main__":
    main()
