import streamlit as st
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from streamlit_option_menu import option_menu
#from streamlit_lottie import st_lottie
import requests
import json

# Load environment variables and configure
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Keep all the original configurations
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
    transport="rest",  # Add this
    timeout=180  # Add this (in seconds)
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

# Original analysis functions
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

# Custom CSS with gradients and styling
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main gradient background */
    .stApp {
        background: linear-gradient(135deg, #E3F2FD 0%, #E8F5E9 100%);
    }
    
    /* Styled cards */
    .stCard {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .stCard:hover {
        transform: translateY(-5px);
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E3F2FD;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196F3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #2196F3, #4CAF50);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
    }
    
    /* Results container styling */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Animation classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        padding: 20px 0;
        max-width: 300px;  /* Increased container width */
        margin: 0 auto;    /* Center the container */
    }
    
    .logo-image {
        width: 100%;
        height: auto;
        object-fit: contain;  /* Maintain aspect ratio */
        transition: transform 0.3s ease;
    }
    
    .logo-image:hover {
        transform: scale(1.1);
    }
</style>
""", unsafe_allow_html=True)

#

# Load animation for the logo
lottie_plant = "https://gifyu.com/image/SPbZG"

# App Header with Logo
#neglect the below three commands(oldcode)
#st.markdown('<div class="logo-container">', unsafe_allow_html=True)
#st_lottie(lottie_plant, height=150, key="plant_animation")
#st.markdown("</div>", unsafe_allow_html=True)

#new changes
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("logo.gif")  # Make sure logo.gif is in the same directory as your script
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E88E5; font-size: 2.5em; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>🌱 AI-Driven Agricultural Assistant</h1>", unsafe_allow_html=True)

# Styled Navigation Menu
selected = option_menu(
    menu_title=None,
    options=["Disease Detection", "Crop Recommendation"],
    icons=["bug", "flower1"],
    menu_icon="list",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "#1E88E5", "font-size": "20px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "10px",
            "padding": "10px",
            "border-radius": "15px",
            "--hover-color": "#E3F2FD",
        },
        "nav-link-selected": {"background-color": "#2196F3", "color": "white"},
    }
)

# Disease Detection Page
if selected == "Disease Detection":
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1E88E5;'>Plant Disease Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Plant Image", type=["jpg", "jpeg", "png"], key="disease_upload")
    with col2:
        language = st.selectbox("Select Language", ["English", "Hindi", "Malayalam", "Tamil", "Telugu"], index=0)
    
    st.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>📍 Location Details</h3>", unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)
    with col3:
        area = st.text_input("Area/Village", placeholder="e.g., Kuttanad")
    with col4:
        district = st.text_input("District", placeholder="e.g., Alappuzha")
    with col5:
        state = st.text_input("State", placeholder="e.g., Kerala")
    
    if uploaded_file and st.button("Analyze Disease", key="analyze_btn"):
        with st.spinner("🔍 Analyzing your plant..."):
            try:
                image_path = f"temp_{uploaded_file.name}"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.read())

                disease_analysis = generate_disease_analysis(image_path, language, district, state, area)
                regional_insights = get_regional_disease_insights(district, state, area)

                st.markdown('<div class="results-container animate-fade-in">', unsafe_allow_html=True)
                st.image(image_path, caption="Uploaded Image", use_column_width=True)
                
                # Styled results
                st.markdown("""
                    <h3 style='color: #1E88E5; margin-top: 20px;'>🔍 Analysis Results</h3>
                    <div style='background: #F5F5F5; padding: 20px; border-radius: 10px; margin-top: 10px;'>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='white-space: pre-line;'>{disease_analysis}</p>", unsafe_allow_html=True)
                
                st.markdown("""
                    <h3 style='color: #1E88E5; margin-top: 20px;'>🌍 Regional Insights</h3>
                    <div style='background: #F5F5F5; padding: 20px; border-radius: 10px; margin-top: 10px;'>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='white-space: pre-line;'>{regional_insights}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            finally:
                os.remove(image_path)
    st.markdown('</div>', unsafe_allow_html=True)

# Crop Recommendation Page
else:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1E88E5;'>Smart Crop Recommendation</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.text_input("Soil Type", placeholder="e.g., Clay, Sandy, Loamy")
        ph_level = st.text_input("pH Level", placeholder="e.g., 6.5")
        nutrients = st.text_input("Nutrient Content", placeholder="e.g., High N, Low P")
    with col2:
        texture = st.text_input("Soil Texture", placeholder="e.g., 60% sand, 30% silt")
        location = st.text_input("Location", placeholder="e.g., Kerala, India")

    if st.button("Get Recommendations", key="crop_rec_btn"):
        with st.spinner("🌱 Generating recommendations..."):
            recommendations = get_crop_suggestions(soil_type, ph_level, nutrients, texture, location)
            
            st.markdown('<div class="results-container animate-fade-in">', unsafe_allow_html=True)
            st.markdown("""
                <h3 style='color: #1E88E5; margin-top: 20px;'>🌾 Crop Recommendations</h3>
                <div style='background: #F5F5F5; padding: 20px; border-radius: 10px; margin-top: 10px;'>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='white-space: pre-line;'>{recommendations}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
