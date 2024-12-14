import streamlit as st
import sqlite3
import re
from openai import OpenAI
import os
import PyPDF2

st.title("Feature Extraction")
# Connect to the SQLite database
conn = sqlite3.connect('extracted_data.db')
c = conn.cursor()
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key="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"
)
# Create a table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS resumes (id INTEGER PRIMARY KEY, content TEXT)''')

# Function to extract profiles using OpenAI API
def extract_profiles(content_list):
    profiles = []
    print(content_list)
    for content in content_list:
        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.2-11B-Vision-Instruct",  # or the model you are using
                messages=[
                    {"role": "user", "content": f"Extract Name, contact details important details from  {content}"}
                ]
            )
            # Append the entire response to profiles for display
            profiles.append(response.choices[0].message.content)
        except Exception as e:
            profiles.append(f"Error occurred: {str(e)}")
    return profiles

# Function to read all PDF files in a specified folder
def read_pdfs_from_folder(folder_path):
    content_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            with open(os.path.join(folder_path, filename), 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
                content_list.append(text)
    return content_list

# Specify the folder containing the PDFs
pdf_folder_path = 'E:/AMiniproject/'
all_content = read_pdfs_from_folder(pdf_folder_path)

# Pass the content to the OpenAI client for profile extraction
profiles = extract_profiles(all_content)

# Display the extracted profiles on the Streamlit page
st.title("Extracted Profiles")
for profile in profiles:
    st.write(profile)

# Close the database connection
conn.close()

