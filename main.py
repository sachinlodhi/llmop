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
        # Initialize empty response
        full_response = ""
        message_placeholder = st.empty()
        
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            
                            # Get the response token
                            token = json_response.get("response", "")
                            full_response += token
                            
                            # Update the placeholder with the accumulated response
                            clean_text = clean_response(full_response)
                            message_placeholder.markdown(clean_text)
                            
                            # If we're done, break the loop
                            if json_response.get("done", False):
                                break
                                
                        except json.JSONDecodeError as e:
                            st.error(f"Error decoding response: {e}")
                            continue
                
                # Update the final response in the chat history
                if st.session_state.messages:
                    st.session_state.messages[-1]["content"] = clean_response(full_response)
                
                return clean_response(full_response)
            else:
                st.error(f"Error: {response.status_code}")
                return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

# Initialize the Streamlit app
st.title("Ollama Chatbot Interface")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
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
        response = get_ollama_response(prompt)