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
        # Create a streaming request to get data in chunks
        with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
            if response.status_code == 200:
                response_text = ""
                for chunk in response.iter_lines():
                    if chunk:  # Only process non-empty chunks
                        try:
                            # Decode the chunk into a JSON object
                            json_obj = json.loads(chunk)
                            if json_obj.get("done", False):  # Check if it's finished
                                break
                            response_text += json_obj.get("response", "")
                            
                            # Update the assistant's message in real-time
                            st.session_state.messages[-1]["content"] = clean_response(response_text)
                            st.rerun()  # Refresh the UI to show the updated message
                        except json.JSONDecodeError:
                            st.error("Error decoding a part of the response.")
            else:
                st.error(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

# Streamlit app layout
st.title("Ollama Chatbot Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for the user
if prompt := st.chat_input("Say something to the model:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add assistant message placeholder to chat history
    st.session_state.messages.append({"role": "assistant", "content": ""})
    
    # Display assistant message placeholder
    with st.chat_message("assistant"):
        assistant_placeholder = st.empty()
    
    # Get the response from the Ollama API (real-time)
    get_ollama_response(prompt)