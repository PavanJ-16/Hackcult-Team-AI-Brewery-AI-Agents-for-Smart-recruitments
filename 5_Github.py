import requests
import json
import time
import streamlit as st  # Import Streamlit
st.title("Github Scraping")
def fetch_github_data(username, token):
    url = f'https://api.github.com/users/{username}'  # Construct the GitHub API URL for the user
    headers = {'Authorization': f'token {token}'}  # Set the authorization header
    response = requests.get(url, headers=headers)  # Send a GET request to the GitHub API

    user_data = {}
    
    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        user_data['username'] = data['login']
        user_data['name'] = data.get('name', 'N/A')
        user_data['bio'] = data.get('bio', 'N/A')
        user_data['public_repos'] = data['public_repos']
        user_data['followers'] = data['followers']
        user_data['following'] = data['following']
        user_data['profile_url'] = data['html_url']
    else:
        print(f'Failed to retrieve user data. Status code: {response.status_code}')  # Handle errors
        return  # Exit if user data cannot be fetched

    # Fetch additional user details
    repos_url = f'https://api.github.com/users/{username}/repos'
    orgs_url = f'https://api.github.com/users/{username}/orgs'
    
    repos_response = requests.get(repos_url, headers=headers)
    orgs_response = requests.get(orgs_url, headers=headers)

    user_data['repositories'] = []
    if repos_response.status_code == 200:
        repos_data = repos_response.json()
        for repo in repos_data:
            repo_info = {
                'name': repo['name'],
                'url': repo['html_url'],
                'contents': []
            }
            
            # Fetch code from each repository
            contents_url = f'https://api.github.com/repos/{username}/{repo["name"]}/contents'
            contents_response = requests.get(contents_url, headers=headers)
            if contents_response.status_code == 200:
                contents_data = contents_response.json()
                if not contents_data:  # Check if the repository is empty
                    print(f'Repository {repo["name"]} is empty.')  # Log empty repository
                else:
                    for item in contents_data:
                        if item['type'] == 'file':  # Only fetch files
                            file_url = item['download_url']
                            file_response = requests.get(file_url, headers=headers)
                            if file_response.status_code == 200:
                                repo_info['contents'].append({
                                    'file_name': item['name'],
                                    'file_content': file_response.text
                                })
                            else:
                                print(f'Failed to retrieve content for {item["name"]}. Status code: {file_response.status_code}')  # Handle errors
                        else:
                            print(f'Skipping non-file item: {item["name"]}')  # Log non-file items
            else:
                print(f'Failed to retrieve contents for {repo["name"]}. Status code: {contents_response.status_code}')  # Handle errors
            
            user_data['repositories'].append(repo_info)
    else:
        print(f'Failed to retrieve repositories. Status code: {repos_response.status_code}')  # Handle errors

    if orgs_response.status_code == 200:
        orgs_data = orgs_response.json()
        user_data['organizations'] = [org['login'] for org in orgs_data]  # List of organization names
    else:
        print(f'Failed to retrieve organizations. Status code: {orgs_response.status_code}')  # Handle errors

    # Instead of saving to a file, display the data on Streamlit
    st.title(f"GitHub User Data for {username}")  # Set the title for the Streamlit app
    st.json(user_data)  # Display the user data as JSON on the Streamlit page

# Example usage
if __name__ == "__main__":
    GITHUB_TOKEN = 'token'  # Replace with your GitHub personal access token
    st.sidebar.header("GitHub User Fetcher")  # Add a sidebar header
    
    # Dropdown for selecting GitHub usernames
    user_ids = ["Dhanush-4554", "Dhanush834", "Rajdeep37", "AshOG-05", "PavanJ-16"]
    username = st.sidebar.selectbox("Select GitHub Username", user_ids)  # Dropdown for GitHub username selection
    
    if st.sidebar.button("Fetch Data"):  # Button to fetch data
        fetch_github_data(username, GITHUB_TOKEN)  # Fetch data for the selected username
