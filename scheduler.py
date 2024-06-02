import schedule
import time
from google_tasks import authenticate_google_tasks, fetch_google_tasks
from notion_api import create_notion_page

def sync_google_tasks_to_notion():
    print("Syncing Google Tasks to Notion...")
    service = authenticate_google_tasks()
    tasks = fetch_google_tasks(service)
    print(f"Fetched {len(tasks)} tasks from Google.")
    for task in tasks:
        success = create_notion_page(task)
        if success:
            print(f"Task '{task['title']}' synced successfully.")
        else:
            print(f"Failed to sync task '{task['title']}'.")

def start_scheduler():
    schedule.every(10).minutes.do(sync_google_tasks_to_notion)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    sync_google_tasks_to_notion()

if __name__ == '__main__':
    main()
