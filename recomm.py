import sys
import os
import subprocess
import time
import json
import yaml
import datetime

import pandas as pd
import re

from google.cloud import storage
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    Content,
    FunctionDeclaration,
    GenerationResponse,
    Tool,
)

from vertexai.preview.vision_models import ImageGenerationModel
import gcs_handler as gcsh

def get_prompt(theme,validation=False):
    if validation:
        with open('prompt_config.yaml', 'r') as file:
            config = yaml.safe_load(file)


        return config['validation']['validation']
    
    else:
        with open('prompt_config.yaml', 'r') as file:
            config = yaml.safe_load(file)


        prompt = config['prompt']['decoration_recommendation']
        instructions = config['system_instruction']['decoration_recommendation']

        return prompt, instructions

def generate_recommenation(PROJECT_ID, LOCATION, video_file_url,prompt,instructions,file_type):
    
    generation_config = GenerationConfig(temperature=0)
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    MODEL_ID = "gemini-1.5-flash-001"  
       
    
    model = GenerativeModel(MODEL_ID,
                           system_instruction=instructions,)
    
    video_file = Part.from_uri(video_file_url, mime_type="video/{file_type}")
    contents = [video_file, prompt]

    response = model.generate_content(contents,generation_config=generation_config)

    return response
def video_validation(PROJECT_ID, LOCATION, video_file_url,prompt,file_type):
    
    prompt = get_prompt('',validation=True)

    response = generate_recommenation(PROJECT_ID, LOCATION, video_file_url,prompt,'',file_type)
    theme = response.text.strip().replace(".", "").lower()
    
    return theme


def clean_response(response_recom):
    intro_match = re.search(r"(.*)```json", response_recom.text, re.DOTALL)
    intro = intro_match.group(1).strip() if intro_match else ""

    json_match = re.search(r"`json(.*?)`", response_recom.text, re.DOTALL)
    json_str = json_match.group(1).strip() if json_match else ""

    clean_recom  =  json.loads(json_str)
    df_rocm = pd.DataFrame(clean_recom)
    df_rocm['ID'] = df_rocm.index + 1
    
    return intro, df_rocm


def image_gen(df_rocm):
    image_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    for index, row in df_rocm.iterrows():
        Id = row['ID']    
        images = image_model.generate_images(
            prompt=row['image_generation_prompt'],        
            number_of_images=2,
            language="en",    
            aspect_ratio="1:1",
        )
        for i in range(0,2):
            try:
                images[i].save(location=f'image-{Id}-{i}.JPG', include_generation_parameters=False)
            except:
                pass   

def image_save(df_rocm,bucket,name):    
    for index, row in df_rocm.iterrows():
            Id = row['ID']    
            for i in range(0,2):
                try:
                    gcsh.upload_blob_from_file_remote(bucket_name = bucket, 
                              source_file_path = f'image-{Id}-{i}.JPG', 
                              destination_blob_path=f'{name}/image-{Id}-{i}.JPG')
                except:
                    pass


def delete_images(df_rocm):
    for index, row in df_rocm.iterrows():
        Id = row['ID']    
        for i in range(0,2):
            image_path = f'image-{Id}-{i}.JPG'
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image {image_path}: {e}")

    return 0

