import sys
import time
import requests

if len(sys.argv) != 4:
    print("Usage: python safecheckrunning.py <repository> <github_token> <current_run_id>")
    sys.exit(1)

repo = sys.argv[1]
token = sys.argv[2]
current_run_id = sys.argv[3]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

has_new_run = "false"

while True:
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1&status=queued&status=in_progress"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Failed to fetch runs. Status code: {r.status_code}")
        time.sleep(10)
        continue

    runs = r.json().get("workflow_runs", [])
    if not runs:
        time.sleep(10)
        continue

    latest_run_id = str(runs[0]["id"])
    if latest_run_id != current_run_id:
        has_new_run = "true"
        break

    time.sleep(10)

print(f"has_new_run={has_new_run}")
if has_new_run == "true":
    sys.exit(0)
else:
    time.sleep(60)