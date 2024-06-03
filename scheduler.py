import schedule
import time
from google_tasks import authenticate_google_tasks, fetch_google_tasks
from notion_api import create_notion_page, authenticate_with_oauth, clear_notion_database

def sync_google_tasks_to_notion():
    print("Syncing Google Tasks to Notion...")
    access_token = authenticate_with_oauth()  # Authenticate with Notion API
    tasks = fetch_google_tasks(authenticate_google_tasks())  # Fetch tasks from Google
    print(f"Fetched {len(tasks)} tasks from Google.")

    if not tasks:
        print("No tasks found.")
        return

    # Clear existing entries in the Notion database
    clear_notion_database(access_token)

    # Add tasks to Notion
    for task in tasks:
        success = create_notion_page(task, access_token)
        if success:
            print(f"Notion page created successfully for task: {task['title']}")
        else:
            print(f"Failed to create Notion page for task: {task['title']}")

def start_scheduler():
    schedule.every(10).minutes.do(sync_google_tasks_to_notion)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    sync_google_tasks_to_notion()

if __name__ == '__main__':
    main()