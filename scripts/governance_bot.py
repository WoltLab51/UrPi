import requests
from typing import Dict

class GovernanceBot:
    def __init__(self, core_url: str = "http://localhost:8000"):
        self.core_url = core_url

    def get_next_task(self) -> Dict:
        response = requests.get(f"{self.core_url}/tasks/next")
        if response.status_code == 200:
            return response.json()
        return None

    def assign_task(self, task_id: str, agent: str) -> bool:
        response = requests.put(
            f"{self.core_url}/tasks/{task_id}",
            json={"assignee": agent, "status": "in_progress"}
        )
        return response.status_code == 200

if __name__ == "__main__":
    bot = GovernanceBot()
    next_task = bot.get_next_task()
    if next_task:
        print(f"Nächster Task: {next_task['title']} (ID: {next_task['id']})")
    else:
        print("Keine offenen Tasks.")
