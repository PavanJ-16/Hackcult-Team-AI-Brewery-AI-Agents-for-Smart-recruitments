from streamlit_image_select import image_select
import streamlit as st
import requests
from huggingface_hub import InferenceClient
from openai import OpenAI
import sqlite3
import json

st.title("Optical character recognition for photos of resumes")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Image selection
img = image_select(
    label="Select an image",
    images=[
        "https://i.imgur.com/LojtiMz.png",
        "https://i.imgur.com/BjjNQjr.png",
        "https://i.imgur.com/KQVfYtX.png",
        "https://i.imgur.com/hjVBFRD.png",
        "https://i.imgur.com/AfQlZBX.png",
    ],
)

# Chat input
prompt = st.chat_input("Press enter to extract data from image")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key=""
)

# Initialize SQLite database connection
conn = sqlite3.connect('extracted_data.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS resumes (id INTEGER PRIMARY KEY, content TEXT)''')

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process new messages
if prompt:
    # Show user message
    

    # Prepare the messages for the API
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please extract all the text from this resume. Keep the Person's name, and other contact details mentioned as well"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img
                    }
                }
            ]
        }
    ]

    # Show assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Create streaming response
        stream = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=messages,
            max_tokens=2000,
            stream=True
        )

        # Process the stream
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response)

        # Add the exchange to message history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Save the extracted output to the database
        json_output = json.dumps({"content": full_response})
        c.execute("INSERT INTO resumes (content) VALUES (?)", (json_output,))
        conn.commit()

# Close the database connection when done
conn.close()
