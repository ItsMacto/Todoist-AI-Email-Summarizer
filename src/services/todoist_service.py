import requests
from src.config.manager import ConfigManager
from src.utils.logger import logger

class TodoistService:
    def __init__(self):
        # Load configuration
        config = ConfigManager().load_config()
        self.api_key = config.get("TODOIST_API_KEY")
        if not self.api_key:
            raise ValueError("Todoist API key is not configured.")
        
        # Todoist REST API endpoint for creating tasks
        self.endpoint = "https://api.todoist.com/rest/v2/tasks"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_task(self, content, description):
        """Creates a new Todoist task with the given content and description."""
        payload = {
            "content": content,
            "description": description,
            "due_string": "today"
        }
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            if response.ok:
                logger.info("Successfully created Todoist task.")
                return True
            else:
                logger.error(f"Failed to create Todoist task. Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception while creating Todoist task: {e}")
            return False