import sys
import os
import subprocess
import time
import pandas as pd
import json
import yaml
import requests
import mimetypes

import streamlit as st

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    Content,
    GenerationResponse,    
)

import gcs_handler as gcsh

def get_config():            
    with open('prompt_config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    return config

def get_prompt(PROJECT_ID, LOCATION, video_file_url,opiotns,config,mime_type):
    
    theme_res = identify_recommenation(PROJECT_ID, LOCATION, video_file_url,opiotns,mime_type)
    
    if theme_res.text.strip(' "\'') in ['decoration_recommendation','fashion_recommendation']:
        theme = theme_res.text.strip(' "\'')
        prompt = config['prompt'][theme]
        instructions = config['system_instruction'][theme]
        response_schema = config['response_schema'][theme]

        return prompt, instructions,response_schema,theme_res
    else:
        return None,None,None,theme_res


def identify_recommenation(PROJECT_ID, LOCATION, video_file_url,opiotns,mime_type):
    
    instructions = """
    You indetify if this video is for fashion recommendation or decoration recommendation. 
    Video for decoration recommendation must show the full view of a house or a room or a place. 
    Video for fashion recommendation must show the style.
    If the video is vague then you response none. 
    if the video is not the video is a hosue, or a room, or a palce, or a person, or an outfit then you response none. 
    If the video is something else then you response none.
    You reponse with one single words.
    """
    
    generation_config = GenerationConfig(temperature=0)
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    MODEL_ID = "gemini-1.5-flash-001"  
    
    model = GenerativeModel(MODEL_ID,
                           system_instruction=instructions,)
    
    response_schema = {
     "type": "STRING",
     "enum": opiotns
    }
    
    # Set up the generation configuration to control Gemini's response
    generation_config = GenerationConfig(
        temperature=0,  # Set the temperature to 0 for consistent output
        response_mime_type="application/json",  # Expect the response to be in JSON format
        response_schema=response_schema  # Use the predefined response schema for structured output
    )
    
    video_file = Part.from_uri(video_file_url, mime_type=mime_type)#="video/mov")
    contents = [video_file, 'classify the video']

    response = model.generate_content(contents,generation_config=generation_config)

  
    return response


def generate_recommenation(PROJECT_ID, LOCATION, video_file_url,prompt,instructions,response_schema,mime_type):
    
    generation_config = GenerationConfig(temperature=0)
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    MODEL_ID = "gemini-1.5-flash-001"  
       
    model = GenerativeModel(MODEL_ID,
                           system_instruction=instructions,)
    
    
    # Set up the generation configuration to control Gemini's response
    generation_config = GenerationConfig(
        temperature=0,  # Set the temperature to 0 for consistent output
        response_mime_type="application/json",  # Expect the response to be in JSON format
        response_schema=response_schema  # Use the predefined response schema for structured output
    )
    video_file = Part.from_uri(video_file_url, mime_type=mime_type)#"video/mov")
    contents = [video_file, prompt]


    response = model.generate_content(contents,generation_config=generation_config)

    return response


def remove_recommendation_key(input_json, recommendation_field):
    # Copy the input JSON to avoid modifying the original
    new_json = input_json.copy()
    
    # Remove the 'Recommendation' key if it exists
    if recommendation_field in new_json:
        del new_json[recommendation_field]
    
    return new_json

def post_processing(response,recommendation_field):
    try:
        response_json = json.loads(response.text)
        recommendation_df = pd.DataFrame(response_json[recommendation_field])        
        intro_json = remove_recommendation_key(response_json, recommendation_field)
        return recommendation_df, intro_json
    except:
        return None, None
    
def image_generation(image_prompt,n=2):
    image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    
    images = image_model.generate_images(
        prompt=image_prompt,        
        number_of_images=n,
        language="en",    
        aspect_ratio="1:1",
    )
    
    return images 

def images_generation(recommendation_df,name,n=2):
    
    recommendation_df['image_name'] = ""
    for index, row in tqdm(recommendation_df.iterrows(), total=recommendation_df.shape[0], desc="Image generation..."):
        image_name = row[name].replace(" ", "_")
        image_prompt = row['image_generation_prompt']
        images = image_generation(image_prompt)   
        image_name_list=[]
        for i in range(0,n):
                image_name_ = f'image-{image_name}-{i}.JPG'
                image_name_list.append(image_name_)
                try:
                    images[i].save(location=image_name_, include_generation_parameters=False)
                except:
                    pass   

        recommendation_df.at[index, 'image_name'] = image_name_list
    
    return recommendation_df


def image_save(df_rocm, bucket, name):    
    for index, row in df_rocm.iterrows():
        for file_name in row['image_name']:  # Iterate over the list of file names
            try:
                gcsh.upload_blob_from_file_remote(bucket_name=bucket, 
                                                  source_file_path=f'{file_name}', 
                                                  destination_blob_path=f'{name}/image/{file_name}')
            except Exception as e:
                print(f"Error uploading file {file_name}: {e}")
                

def delete_images(df_rocm):
    for index, row in df_rocm.iterrows():
        for file_name in row['image_name']:  # Iterate over the list of file names
            image_path = f'{file_name}'
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    print(f"File {image_path} does not exist.")
            except Exception as e:
                print(f"Error deleting image {image_path}: {e}")


def images_generation(recommendation_df,name):
    
    recommendation_df['image_name'] = ""
    #for index, row in tqdm(recommendation_df.iterrows(), total=recommendation_df.shape[0], desc="Image generation..."):
    for index, row in recommendation_df.iterrows():
        image_name = row[name].replace(" ", "_")
        image_prompt = row['image_generation_prompt']
        images = image_generation(image_prompt)   
        image_name_list=[]
        for i in range(0,2):
                image_name_ = f'image-{image_name}-{i}.JPG'
                image_name_list.append(image_name_)
                try:
                    images[i].save(location=image_name_, include_generation_parameters=False)
                except:
                    pass   

        recommendation_df.at[index, 'image_name'] = image_name_list
    
    return recommendation_df


def update_progress(progress_stage, status_texts, task_names):
    for i, status_text in enumerate(status_texts):
        if i < progress_stage:
            status_text.markdown(f"**{task_names[i]}**: ✅")  # Completed task            
        elif i == progress_stage:
            status_text.markdown(f"**{task_names[i]}**: 🔄")  # Pending task
        else:
            status_text.markdown(f"**{task_names[i]}**: ⏳")  # Pending task

            
            
def generate_recommendation(project_id, location, video_file_url, bucket, subfolder,mime_type):        
    
    config = get_config()
    opiotns = config['theme']['enum']

    error_code = 100
    error_dic = {1:"video can not be used for fashion or decoration recommendation!",
                 2:"Text output is not readable. Please try again.",
                 3:"Image generation failed. Please try again.",
                 4:"Image saving failed. Please try again."
                }
                 
    recommendation_field = 'Recommendation'
    name = 'recommendation_name'
    
    task_names = ["Gemini is identifying the video theme", "Generate Recommendations","Fine Tune Recommendations","Generate Images","Save"]
    
    task1_status = st.empty()
    task2_status = st.empty()
    task3_status = st.empty() 
    task4_status = st.empty() 
    task5_status = st.empty() 
    
    status_texts = [task1_status, task2_status, task3_status,task4_status,task5_status]
    
    update_progress(0, status_texts,task_names)                 
    
    prompt, instructions,response_schema,theme = get_prompt(project_id, location, video_file_url,opiotns,config,mime_type)
    
    task_names[1] = f"Gemini is analysing the video for {theme.text}..."
    update_progress(1, status_texts,task_names)                 
    

    if prompt is not None:
        try:
            response = generate_recommenation(project_id, location, video_file_url,prompt,instructions,response_schema,mime_type)
            update_progress(2, status_texts,task_names)                 
        except Exception as e:
            st.error(f"An error occurred: {e}")
            error_code = 0
            response = None
    else:
            response = None
            error_code = 1
            
    

    if response is not None: #task 3
        try:
            recommendation_df,intro_json = post_processing(response,recommendation_field)
            update_progress(3, status_texts,task_names)                 
        except Exception as e:
            st.error(f"An error occurred: {e}")
            error_code = 0
            recommendation_df = None
    else: 
            recommendation_df = None
            error_code = min(error_code, 2)

            
    if recommendation_df is not None:#task 4
        try:
            recommendation_df_full = images_generation(recommendation_df,name)
            update_progress(4, status_texts,task_names)  
        except Exception as e:
            st.error(f"An error occurred: {e}")
            error_code = 0
            recommendation_df_full = None
    else:
            recommendation_df_full = None
            error_code = min(error_code, 3)

            
    if recommendation_df_full is not None: #task 5
        try:
            image_save(recommendation_df_full, bucket, subfolder)
            delete_images(recommendation_df_full)
            recommendation_df_full['image_url'] = recommendation_df_full['image_name'].apply(lambda x: [f'{subfolder}/image/{filename}' for filename in x])

            gcsh.save_df_to_gcs_as_csv(recommendation_df_full, bucket, f'{subfolder}/rec.csv')
            try:
                gcsh.upload_blob_from_string(bucket, json.dumps(intro_json), f'{subfolder}/intro.json')
                update_progress(5, status_texts,task_names)                 
            except Exception as e:
                st.error(f"An error occurred: {e}")
                error_code = 0
        except Exception as e:
            st.error(f"An error occurred: {e}")
            error_code = 0
                    
    else:        
        error_code = min(error_code, 4)


    if error_code not in [0,100]:
        st.error (error_dic[error_code])
        