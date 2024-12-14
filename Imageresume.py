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
        "https://growbilliontrees.com/cdn/shop/products/neem-plant-600.png?v=1676273294&width=533",
        "https://www.padmamnursery.com/cdn/shop/files/Ashoka-Tree_b10f777d-7a65-4f4d-888b-c81558034d41.jpg?v=1728317190",
        "https://i.redd.it/ff2go8uqo3191.jpg",
        "https://i.redd.it/cztnf0y4e7t81.jpg",
        "https://images.stockcake.com/public/4/2/b/42b30eef-7371-4b77-81ad-eacc29e8f5e8_large/deforestation-aerial-view-stockcake.jpg",
        "https://static3.bigstockphoto.com/9/3/3/large1500/339787648.jpg",
        "https://thumbs.dreamstime.com/b/aerial-view-deforested-area-amazon-rainforest-caused-illegal-mining-created-aerial-view-deforested-area-295465598.jpg",
    ],
)

# Chat input
prompt = st.chat_input("Press enter to extract data from image")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key="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"
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
                    "text": "Please extract all the text from this resume"
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