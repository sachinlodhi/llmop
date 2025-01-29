import streamlit as st
import requests
import json
import re

def clean_response(response_text):
    # Remove tags like <think> from the response
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
        st.write("### Debug: Sending request to Ollama API...")
        st.write(f"**Payload:** `{data}`")
        
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            if response.status_code == 200:
                st.write("### Debug: API request successful. Streaming response...")
                
                # Create a placeholder for the streaming response
                response_placeholder = st.empty()
                full_response = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            st.write(f"**Received chunk:** `{json_response}`")
                            
                            # Get the new token from the response
                            token = json_response.get("response", "")
                            full_response += token
                            
                            # Clean and display the current accumulated response
                            clean_text = clean_response(full_response)
                            response_placeholder.markdown(clean_text)
                            
                            # Update the message in the chat history
                            if st.session_state.messages:
                                st.session_state.messages[-1]["content"] = clean_text
                            
                            # Check if the response is complete
                            if json_response.get("done", False):
                                st.write("### Debug: Streaming complete.")
                                break
                                
                        except json.JSONDecodeError as e:
                            st.error(f"### Debug: Error decoding chunk: {e}")
                            st.error(f"Raw chunk: `{line}`")
                            
            else:
                st.error(f"### Debug: Error: {response.status_code} - {response.text}")
                
    except requests.exceptions.RequestException as e:
        st.error(f"### Debug: Request failed: {e}")

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