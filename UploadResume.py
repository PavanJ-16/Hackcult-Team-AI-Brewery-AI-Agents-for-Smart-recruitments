import streamlit as st
import sqlite3
import json

st.title("Upload Resume")

import os
import streamlit as st
import PyPDF2
import docx
from openai import OpenAI

# Initialize OpenAI client with environment variable for API key
XAI_API_KEY = ''
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Function to extract text from PDF files
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Initialize SQLite database connection
conn = sqlite3.connect('extracted_data.db')
c = conn.cursor()

# Create a table to store the extracted texts
c.execute('''
CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    content TEXT
)
''')
conn.commit()

# Streamlit app layout

st.write("Upload a PDF or DOCX file to extract text and send it to Model.")

# Upload file widget
uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

# Chat input box for user message
user_message = st.text_input("Enter your message to Model:")

if uploaded_file is not None:
    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document_text = extract_text_from_docx(uploaded_file)
    
    # Convert the extracted text to JSON format
    json_data = json.dumps({
        "file_name": uploaded_file.name,
        "content": document_text
    })

    # Store the JSON data in the database
    c.execute('INSERT INTO texts (file_name, content) VALUES (?, ?)', (uploaded_file.name, json_data))
    conn.commit()

    # Send extracted text and user message to Grok and get response
    completion = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_message},
            {"role": "user", "content": document_text}
        ],
    )
    
    # Display Grok's response
    st.write("Bot's Response:")
    st.write(completion.choices[0].message.content)

# Close the database connection when done
conn.close()

