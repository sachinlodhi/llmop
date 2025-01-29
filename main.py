import streamlit as st
import requests
import json
import re

# Function to clean the response by removing unwanted tokens (e.g., <think>, </think>)
def clean_response(response_text):
    # Remove <think>...</think> and any other unwanted tokens
    clean_text = re.sub(r'<.*?>', '', response_text)  # Remove anything between <>
    return clean_text.strip()

# Function to make the request to the Ollama API
def get_ollama_response(prompt, history):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt
    }
    try:
        # Create a streaming request to get data in chunks
        with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
            if response.status_code == 200:
                # Create an empty container for real-time updates
                output_placeholder = st.empty()
                response_text = ""
                
                for chunk in response.iter_lines():
                    if chunk:  # Only process non-empty chunks
                        try:
                            # Decode the chunk into a JSON object
                            json_obj = json.loads(chunk)
                            if json_obj.get("done", False):  # Check if it's finished
                                break
                            response_text += json_obj.get("response", "")
                            
                            # Clean the response by removing unwanted tokens
                            clean_text = clean_response(response_text)
                            
                            # Update the text area in real-time with clean text
                            output_placeholder.text_area("Response from Ollama:", clean_text, height=200)
                        except json.JSONDecodeError:
                            st.write("Error decoding a part of the response.")
                
                # Add the cleaned response to history
                history.append(("Assistant", clean_text))
                
            else:
                st.write(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.write(f"Request failed: {e}")

# Streamlit app layout
st.title("Ollama Chatbot Interface")

# Initialize message history
if "history" not in st.session_state:
    st.session_state.history = []

# Display conversation history
for sender, message in st.session_state.history:
    if sender == "User":
        st.write(f"**You**: {message}")
    else:
        st.write(f"**Assistant**: {message}")

# Input box for the user
user_input = st.text_input("Say something to the model:")

# Submit button
if st.button('Submit'):
    if user_input:
        # Add user input to the history
        st.session_state.history.append(("User", user_input))
        
        # Get the response from the Ollama API (real-time)
        get_ollama_response(user_input, st.session_state.history)
        
        # Clear input field after submission
        st.experimental_rerun()
    else:
        st.warning("Please enter a prompt to submit.")
