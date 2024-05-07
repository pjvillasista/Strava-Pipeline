# Imports
import requests
import os
import json
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

# Function to create authorization URL
def create_auth_url(client_id, redirect_uri):
    """Generates the authorization URL for Strava OAuth."""
    scope = "read,read_all,profile:read_all,activity:read_all"
    url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope={scope}"
    return url

# Function to exchange code for a token
def exchange_token(client_id, client_secret, code):
    """Exchanges a code for a Strava OAuth token."""
    try:
        url = 'https://www.strava.com/oauth/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Token exchange failed: {e}")
        return None

# Function to fetch activities
def fetch_activities(access_token):
    """Fetches the list of recent activities for the authenticated user."""
    try:
        url = 'https://www.strava.com/api/v3/athlete/activities'
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch activities: {e}")
        return []

# Function to fetch activities by ID
def fetch_activities_by_id(activity_id, access_token):
    """Fetches detailed information for a specific activity by ID."""
    try:
        url = f'https://www.strava.com/api/v3/activities/{activity_id}'
        headers = {'Authorization': f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch activity {activity_id}: {e}")
        return None

# Main script execution
if __name__ == "__main__":
    AUTH_URL = create_auth_url(CLIENT_ID, 'http://127.0.0.1:5000/authorization')
    print("Visit this URL to authorize:", AUTH_URL)

    # Example placeholder values
    STRAVA_CODE = "..."  # This should be obtained through the callback after user authorization
    token_response = exchange_token(CLIENT_ID, CLIENT_SECRET, STRAVA_CODE)
    
    if token_response:
        access_token = token_response['access_token']
        activities = fetch_activities(access_token)
        detailed_activities = []

        for activity in activities:
            details = fetch_activities_by_id(activity['id'], access_token)
            if details:
                detailed_activities.append(details)

        # Saving activities and details
        with open('./data/activities/run_data.json', 'w') as file:
            json.dump(activities, file)
        with open('./data/activities/detailed_run_data.json', 'w') as file:
            json.dump(detailed_activities, file)
        logging.info("Data saved successfully.")
