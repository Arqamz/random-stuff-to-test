import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/tasks']

def authenticate_google_tasks():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Authenticating with Google...")
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GOOGLE_CREDENTIALS_PATH'), SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('tasks', 'v1', credentials=creds)
    return service

def fetch_google_tasks(service):
    tasks = []
    task_lists = service.tasklists().list().execute().get('items', [])
    for task_list in task_lists:
        task_list_id = task_list['id']
        print(f"Fetching tasks for task list with ID: {task_list_id}")
        tasks_result = service.tasks().list(tasklist=task_list_id).execute()
        tasks.extend(tasks_result.get('items', []))
    return tasks
