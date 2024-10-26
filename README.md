# Scence to Style:

This is a Streamlit app for furniture recommendations. Users can upload any type of video, and Gemini multimodal analysis evaluates it. If relevant, the app provides a range of furniture recommendations based on the style and architecture of the house. The Imagine model visualizes these recommendations, and Google Lens is used for users to search for items they like by image.


<img src="images/cover.gif" alt="Alt text" width="700"/>


# Project Setup Instructions

You need to have a GCP account in which the image generation model is activated (refer to this [link](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)).

1. **Dowload the setup file**
   Go to GCP cloud shell 
   Download the `set_up.sh` file:
   ```bash  
   curl -L -o set_up.sh https://raw.githubusercontent.com/AmirMK/scence-to-style/main/set_up.sh
   ```
   Then, run the `set_up.sh` script as follows from GCP cloud shell:
   ```bash
   chmod +x set_up.sh.sh
   ./set_up.sh.sh --project_id <project_id>
   ```
 
