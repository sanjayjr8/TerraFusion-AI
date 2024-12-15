import streamlit as st
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  

# Gemini API Configuration
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Helper Functions
def read_image_data(file_path):
    image_path = Path(file_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Could not find image: {image_path}")
    return {"mime_type": "image/jpeg", "data": image_path.read_bytes()}

def clean_response_text(response_text):
    clean_text = re.sub(r'[*,]+', '', response_text)
    return clean_text

def generate_disease_analysis(image_path, language, district, state, area):
    input_prompt = f"""
    As a highly skilled plant pathologist, analyze this plant image for a farmer in {area}, {district}, {state}. Please provide:
    1. Disease identification (if any)
    2. Severity assessment
    3. Treatment recommendations
    4. Regional context: Is this disease common in {district}? What factors in this region might affect its spread?
    5. Preventive measures specific to this geographical area
    
    Consider local climate patterns and common agricultural practices in {state} when making recommendations.
    Please be concise and practical in your response.
    """

    language_prompt = f"Provide the following response in {language}: {input_prompt}"
    image_data = read_image_data(image_path)
    response = model.generate_content([language_prompt, image_data])
    return clean_response_text(response.text)

def get_regional_disease_insights(district, state, area):
    prompt = f"""
    As an agricultural expert, provide insights about plant diseases in {area}, {district}, {state}:
    1. What are the most common plant diseases in this region?
    2. Which seasons are these diseases most prevalent?
    3. What are the unique environmental factors in {district} that affect plant health?
    4. What preventive measures do you recommend for farmers in this specific area?
    
    Provide a concise, practical response focusing on local relevance.
    """

    response = model.generate_content([prompt])
    return clean_response_text(response.text)

def get_crop_suggestions(soil_type, ph_level, nutrients, texture, location):
    prompt = f"""
    As an expert agricultural advisor, based on the following details:
    - Soil Type: {soil_type}
    - pH Level: {ph_level}
    - Nutrient Content: {nutrients}
    - Soil Texture: {texture}
    - Location: {location}

    Suggest the best crops that can be planted in this region and soil type. 
    Provide reasons for your suggestions, including compatibility with soil, climate, and market demand. 
    Your response should be concise and farmer-friendly.
    """

    response = model.generate_content([prompt])
    return response.text.strip()

# Streamlit Navigation
st.title("\U0001F331 Agricultural Assistant")
st.markdown("Disease Detection & Crop Recommendation System")

# Sidebar Navigation
page = st.sidebar.radio("Navigate to", ["Disease Detection", "Crop Recommendation"])

if page == "Disease Detection":
    st.header("Disease Detection")
    uploaded_file = st.file_uploader("Upload Plant Image", type=["jpg", "jpeg", "png"], key="disease_upload")
    language = st.selectbox("Select Language", ["English", "Hindi", "Malayalam", "Tamil", "Telugu"], index=0)

    st.subheader("\U0001F4CD Location Details")
    area = st.text_input("Area/Village", placeholder="e.g., Kuttanad")
    district = st.text_input("District", placeholder="e.g., Alappuzha")
    state = st.text_input("State", placeholder="e.g., Kerala")

    if uploaded_file and st.button("Analyze Disease"):
        with st.spinner("Analyzing..."):
            try:
                image_path = f"temp_{uploaded_file.name}"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.read())

                disease_analysis = generate_disease_analysis(image_path, language, district, state, area)
                regional_insights = get_regional_disease_insights(district, state, area)

                st.image(image_path, caption="Uploaded Image", use_column_width=True)
                st.subheader("Analysis Results")
                st.text_area("Disease Analysis", disease_analysis, height=200)
                st.text_area("Regional Disease Insights", regional_insights, height=200)
            finally:
                os.remove(image_path)

elif page == "Crop Recommendation":
    st.header("Crop Recommendation")

    soil_type = st.text_input("Soil Type", placeholder="e.g., Clay, Sandy, Loamy")
    ph_level = st.text_input("pH Level", placeholder="e.g., 6.5")
    nutrients = st.text_input("Nutrient Content", placeholder="e.g., High N, Low P")
    texture = st.text_input("Soil Texture", placeholder="e.g., 60% sand, 30% silt")
    location = st.text_input("Location", placeholder="e.g., Kerala, India")

    if st.button("Get Recommendations"):
        with st.spinner("Fetching recommendations..."):
            recommendations = get_crop_suggestions(soil_type, ph_level, nutrients, texture, location)
            st.text_area("Crop Recommendations", recommendations, height=200)
