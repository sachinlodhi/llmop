import streamlit as st
import requests
import json
import re

def clean_response(response_text):
    clean_text = re.sub(r'<.*?>', '', response_text)
    return clean_text.strip()

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
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            if response.status_code == 200:
                response_placeholder = st.empty()
                full_response = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            
                            # Get the new token from the response
                            token = json_response.get("response", "")
                            full_response += token
                            
                            # Clean and display the current accumulated response
                            clean_text = clean_response(full_response)
                            if clean_text.strip():  # Only display non-empty responses
                                response_placeholder.markdown(clean_text)
                            
                            # Update the message in the chat history
                            if st.session_state.messages:
                                st.session_state.messages[-1]["content"] = clean_text
                            
                            if json_response.get("done", False):
                                break
                                
                        except json.JSONDecodeError:
                            continue
                            
            else:
                st.error("Failed to get response from the model")
                
    except requests.exceptions.RequestException:
        st.error("Failed to connect to the Ollama server")

# Streamlit app layout
st.title("Ollama Chatbot Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Say something to the model:"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add assistant message placeholder
    st.session_state.messages.append({"role": "assistant", "content": ""})
    with st.chat_message("assistant"):
        get_ollama_response(prompt)