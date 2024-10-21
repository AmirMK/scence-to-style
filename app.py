import streamlit as st
import mimetypes
import yaml
import gcs_handler as gcsh
import generation as gen
import exploration as ex

#@st.cache_data
def get_project_info():    
    global project_id, location, service_account_email, bucket
    with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
    project_id, location, service_account_email, bucket =  config['project_id'], config['location'], config['service_account_email'], config['bucket']
    
    return 0 

#@st.cache_data
def video_type_analysis(uploaded_video, filename):
        mime_type, _ = mimetypes.guess_type(uploaded_video.name)
        file_extension = mimetypes.guess_extension(mime_type)        
        updated_filename = filename.replace(' ','_')
        
        update_video_name = f'{updated_filename}{file_extension}'
        
        filename_location = f'{updated_filename}/videos/{update_video_name}'
        
        return mime_type, updated_filename, filename_location
    
def main():
    
    st.image("./logo/logo.png",width=1000)    
    st.title("")    
    
    get_project_info()
    
    
    tab_generation, tab_exploration = st.tabs(["Generation", "Exploration"])

    with tab_generation:
        allowed_file_types = ["mp4", "mkv", "avi", "mov"]
        uploaded_video = st.file_uploader("Upload your video file to get recommendation", type=allowed_file_types)
        
        if uploaded_video and ('uploaded_video' not in st.session_state or st.session_state['uploaded_video'] != uploaded_video.name):
                st.video(uploaded_video)        
                filename = st.text_input('Enter the name for your recommendations storage', value=uploaded_video.name)

        if st.button('Generate Recommendation!') and uploaded_video is not None:                    
            with st.spinner('Generating Recommendation...'):
                mime_type, updated_filename, filename_location = video_type_analysis(uploaded_video, filename)
                video_file_url = gcsh.upload_blob_from_file(bucket, uploaded_video,filename_location)
                gen.generate_recommendation(project_id, location, video_file_url, bucket, updated_filename, mime_type)
                
    with tab_exploration:            
            ex.explore(bucket, service_account_email)
    
                     
if __name__ == "__main__":
    main()

    
    

