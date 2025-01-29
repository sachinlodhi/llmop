import streamlit as st
import requests
import json

# Function to make the request to the Ollama API
def get_ollama_response(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['text']
    else:
        return "Error: Unable to get a response from Ollama API."

# Streamlit app layout
st.title("Ollama Chatbot Interface")

# Input box for the user
user_input = st.text_input("Say something to the model:")

# Submit button
if st.button('Submit'):
    if user_input:
        # Get the response from the Ollama API
        response = get_ollama_response(user_input)
        # Display the response in the output box
        st.text_area("Response from Ollama:", response, height=200)
    else:
        st.warning("Please enter a prompt to submit.")
