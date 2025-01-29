import streamlit as st
import requests

# Set up the page
st.set_page_config(page_title="Ollama Chat", page_icon="🤖")
st.title("Ollama Chat")
st.markdown("""
    <style>
    .big-font {
        font-size: 20px !important;
        color: #4F8BF9;
    }
    </style>
    <p class="big-font">Chat with Ollama!</p>
    """, unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox("Choose a model", ["deepseek-r1:1.5b"])
    temperature = st.slider("Temperature", 0.1, 1.0, 0.7, help="Controls the randomness of the model's output.")

# Text input for the prompt
prompt = st.text_area("Enter your message:", height=100, placeholder="e.g., Tell me a joke or explain something.")

if st.button("Send"):
    if prompt:
        # Prepare the API request
        api_url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature
        }

        # Placeholder for the response
        response_placeholder = st.empty()

        # Stream the response from the API
        with requests.post(api_url, json=payload, stream=True) as response:
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        # Decode the JSON response
                        json_response = line.decode("utf-8")
                        token = eval(json_response)["response"]
                        full_response += token

                        # Update the response in real-time
                        response_placeholder.text(full_response)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    else:
        st.warning("Please enter a message.")