import streamlit as st
import requests

from app.config.settings import settings
from app.common.custom_exception import CustomException
from app.common.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent", layout = "centered")
st.title("Multi AI Agent using Groq and Tavily")

system_prompt = st.text_area("Define your AI Agent: ", height = 70)

selected_model = st.selectbox("Select your AI Model: ", settings.ALLOWED_MODEL_NAMES)

allow_web_search = st.checkbox("Allow web search")

user_query = st.text_area("Enter your query: ",height = 150)

API_URL = "http://127.0.0.1:9999/chat"

if st.button("Ask Agent") and user_query.strip():
    payload = {
        "model_name": selected_model,
        "system_prompt" : system_prompt,
        "messages" : [user_query],
        "allow_search" : allow_web_search
    }

    try:
        logger.info("Sending request to backend")

        response = requests.post(API_URL, json = payload)

        if response.status_code == 200:
            
            agent_response = response.json().get("response","")
            logger.info("Successfully Received response from backend")

            st.subheader("Agent Response")
            st.markdown(agent_response.replace("\n","<br>"),unsafe_allow_html=True)
        
        else:
            logger.error("Backend Error")
            st.error("Error with the backend")
    
    except Exception as e:
        logger.error("Error occured while sending message request to backend")
        st.error(str(CustomException("Failed to communicate with backend")))




