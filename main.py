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
                        except json.JSONDecodeError:
                            st.write("Error decoding a part of the response.")

                # Clean the response by removing unwanted tokens
                clean_text = clean_response(response_text)

                # Add assistant's response to history
                st.session_state.history.append(("Assistant", clean_text))
                
                # Update the chat history in real-time
                update_chat_history()
                
            else:
                st.write(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.write(f"Request failed: {e}")

# Function to display chat history
def update_chat_history():
    for sender, message in st.session_state.history:
        if sender == "User":
            # Display the user's message on the left
            st.markdown(f'<div style="text-align: left; padding: 5px; background-color: #e1f5fe; border-radius: 10px; margin-bottom: 5px;">**You**: {message}</div>', unsafe_allow_html=True)
        else:
            # Display the assistant's message on the right
            st.markdown(f'<div style="text-align: right; padding: 5px; background-color: #f3f4f6; border-radius: 10px; margin-bottom: 5px;">**Assistant**: {message}</div>', unsafe_allow_html=True)

# Streamlit app layout
st.title("Ollama Chatbot Interface")

# Initialize message history
if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history
update_chat_history()

# Input box for the user
user_input = st.text_input("Say something to the model:")

# Submit button
if st.button('Submit'):
    if user_input:
        # Add user input to the history
        st.session_state.history.append(("User", user_input))
        
        # Get the response from the Ollama API (real-time)
        get_ollama_response(user_input)
        
        # Clear input field after submission
        st.experimental_rerun()
    else:
        st.warning("Please enter a prompt to submit.")
