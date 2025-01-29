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
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Log the raw response for debugging
        st.write(f"Raw Response: {response.text}")

        # Try to parse JSON
        try:
            response_json = response.json()
            return response_json.get('text', "No text key found in the response.")
        except ValueError:
            return "Error: Response is not valid JSON."
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

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
