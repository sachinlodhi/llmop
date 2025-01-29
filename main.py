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

        # Split the response by newlines and parse each JSON object
        responses = response.text.strip().split("\n")
        response_text = ""
        
        for item in responses:
            try:
                json_obj = json.loads(item)
                response_text += json_obj.get('response', '')  # Get the response field from each chunk
            except json.JSONDecodeError:
                st.write("Error decoding a part of the response.")
        
        if not response_text:
            return "Error: No valid responses in the API output."
        return response_text.strip()
        
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
