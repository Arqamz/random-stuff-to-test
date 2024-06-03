import webbrowser
import requests
import os
import json
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define OAuth 2.0 credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = f"https://api.notion.com/v1/oauth/authorize?client_id={CLIENT_ID}&response_type=code&owner=user&redirect_uri={REDIRECT_URI}"
TOKEN_URL = "https://api.notion.com/v1/oauth/token"
SCOPE = "databases:write"
NOTION_DATABASE_ID = "4abd649a047b4909968db2100d8a9a14"
NOTION_API_URL = "https://api.notion.com/v1/pages"
TOKEN_FILE = "notion_token.json"
NOTION_VERSION = "2022-06-28"

def authenticate_with_oauth():
    if os.path.exists(TOKEN_FILE):
        # Load access token from file
        with open(TOKEN_FILE, "r") as file:
            token_data = json.load(file)
            access_token = token_data.get("access_token")
            if access_token:
                return access_token

    # Step 1: Construct Authorization URL
    auth_url = AUTHORIZATION_URL
    print("Please go to the following URL and authorize the application:")
    webbrowser.open(auth_url)

    # Step 2: Retrieve Authorization Code
    authorization_code = input("Enter the authorization code from the URL: ")

    # Step 3: Exchange Authorization Code for Access Token
    # Encode client ID and client secret in base64
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {client_credentials_base64}",
        "Content-Type": "application/json"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }

    token_response = requests.post(TOKEN_URL, headers=headers, json=token_data)

    if token_response.status_code != 200:
        print(f"Failed to retrieve access token: {token_response.json()}")
        return None

    access_token = token_response.json().get("access_token")

    # Save access token to file
    with open(TOKEN_FILE, "w") as file:
        json.dump({"access_token": access_token}, file)

    return access_token

def clear_notion_database(access_token):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    print("Fetching all pages in the database...")
    response = requests.post(url, headers=headers)
    data = response.json()
    print(f"Fetched {len(data.get('results', []))} pages.")

    # Archive each page
    for page in data.get('results', []):
        page_id = page['id']
        print(f"Archiving page with ID: {page_id}")
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        update_data = {"archived": True}
        response = requests.patch(update_url, headers=headers, json=update_data)
        if response.status_code == 200:
            print(f"Successfully archived page with ID: {page_id}")
        else:
            print(f"Failed to archive page with ID: {page_id}. Response: {response.json()}")

def create_notion_page(task, access_token):
    # Update Authorization Header with Access Token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    # Make request to Notion API
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Completed": {"checkbox": task['status'] != 'needsAction'},
            "Name": {"title": [{"text": {"content": task['title']}}]},
            "Description": {"rich_text": [{"text": {"content": task['notes']}}]},
            "Due Date": {"date": {"start": task.get('due', None)}}
        }
    }

    response = requests.post(NOTION_API_URL, headers=headers, json=data)
    return response.status_code == 200

def main():
    access_token = authenticate_with_oauth()
    # if not access_token:
    #     print("Authentication failed.")
    #     return
    # print("Access Token:", access_token)
    # task = {
    #     "completed": {"checkbox": task.get('completed', False)},
    #     "title": "Sample Task 7", 
    #     "description": "This is a sample task description.",
    #     "due": "2024-07-25"
    # }
    # print("Creating Notion page...")
    # success = create_notion_page(task, access_token)
    # if success:
    #     print("Notion page created successfully!")
    # else:
    #     print("Failed to create Notion page.")
    clear_notion_database(access_token)

if __name__ == "__main__":
    main()