#!/usr/bin/env python3
"""
Validate today's Todoist tasks have required context labels.

Checks every task due today and reports any that lack a context label
(home, computer, or outside) so they can be triaged.
"""
import os
import sys

import requests

REQUIRED_LABELS = {"home", "computer", "outside"}
API_BASE = "https://api.todoist.com/api/v1"
TASK_URL_BASE = "https://app.todoist.com/app/task"


def get_token():
    token = os.environ.get("TODOIST_TOKEN")
    if not token:
        print("Error: TODOIST_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return token


def get_tasks_due_today(token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"query": "today", "limit": 200}
    tasks = []
    while True:
        response = requests.get(
            f"{API_BASE}/tasks/filter",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        tasks.extend(data.get("results", []))
        cursor = data.get("next_cursor")
        if not cursor:
            break
        params = {"query": "today", "limit": 200, "cursor": cursor}
    return tasks


def main():
    token = get_token()
    tasks = get_tasks_due_today(token)

    unlabeled = [
        task for task in tasks
        if not REQUIRED_LABELS.intersection(task.get("labels", []))
    ]

    if not unlabeled:
        print("All today's tasks have a context label.")
        return

    print(f"Found {len(unlabeled)} task(s) today without a context label (home/computer/outside):\n")
    for task in unlabeled:
        labels = task.get("labels") or []
        label_str = ", ".join(labels) if labels else "(no labels)"
        task_id = task.get("id", "")
        url = f"{TASK_URL_BASE}/{task_id}" if task_id else ""
        print(f"  {task['content']}")
        print(f"    Labels : {label_str}")
        if url:
            print(f"    Link   : {url}")
        print()


if __name__ == "__main__":
    main()
