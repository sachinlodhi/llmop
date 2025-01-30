import streamlit as st
import requests
import json
import re
from time import sleep

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
        "prompt": prompt,
        # Add performance optimization parameters
        "num_ctx": 512,          # Reduce context window
        "num_thread": 2,         # Limit threads for mobile
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 0.9,
    }

    try:
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            if response.status_code == 200:
                message_container = st.empty()
                full_response = ""
                buffer = ""
                token_count = 0
                update_frequency = 8  # Update UI every 8 tokens
                
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            token = json_response.get("response", "")
                            
                            if token:  # Only process non-empty tokens
                                full_response += token
                                buffer += token
                                token_count += 1
                                
                                # Update UI less frequently
                                if token_count >= update_frequency or json_response.get("done", False):
                                    clean_text = clean_response(full_response)
                                    if clean_text.strip():
                                        message_container.markdown(clean_text)
                                        sleep(0.01)  # Small delay to reduce UI strain
                                    buffer = ""
                                    token_count = 0
                            
                            if json_response.get("done", False):
                                # Final update to chat history
                                if st.session_state.messages:
                                    st.session_state.messages[-1]["content"] = clean_response(full_response)
                                break
                                
                        except json.JSONDecodeError:
                            continue
            else:
                st.error("Failed to get response from the model", icon="🚨")
                
    except requests.exceptions.RequestException:
        st.error("Failed to connect to the Ollama server", icon="🚨")

# Streamlit configuration to reduce resource usage
st.set_page_config(
    page_title="Chat Interface",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# App title
st.title("Ollama Chatbot Interface")

# Initialize chat history (with max message limit)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Limit chat history to last 10 messages to save memory
max_messages = 10
st.session_state.messages = st.session_state.messages[-max_messages:] if len(st.session_state.messages) > max_messages else st.session_state.messages

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