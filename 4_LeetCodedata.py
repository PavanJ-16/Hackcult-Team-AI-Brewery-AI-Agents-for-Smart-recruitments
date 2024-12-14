import streamlit as st
import requests
import json

st.title("LeetCode Profile Checker")

# Input field for list of LeetCode usernames


# Button to trigger API calls and print results
if st.button("Fetch and Print Profiles"):
    # Split input string into list of usernames
    usernames_list = ["Dhanush_B_4554","PavanJ-16","Dhanush_U"]

    # Iterate over each username and fetch profile data
    for username in usernames_list:
        url = f'https://leetcode-stats-api.herokuapp.com/{username}'
        response = requests.get(url)

        # Check if API call was successful
        if response.status_code == 200:
            # Parse JSON response
            profile_data = response.json()
            # Format profile data into pretty print and limit to first 300 characters
            formatted_data = json.dumps(profile_data, indent=4)[:500]

            # Print profile data in Streamlit
            st.write(f"**{username}'s Profile:**")
            st.write(formatted_data)
        else:
            st.error(f"Failed to fetch profile for {username}")

