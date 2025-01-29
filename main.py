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

# User input
user_input = st.text_input("Say something to the model:", "hi who are you?")

# Display the model's response
if user_input:
    response = get_ollama_response(user_input)
    st.write(f"Response from Ollama: {response}")
