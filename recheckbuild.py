import requests
import time
import sys

def check_run_status(token, repo):
    if not repo:
        print("Repository name is not provided or invalid.")
        return
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    url = f'https://api.github.com/repos/{repo}/actions/workflows'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f'Failed to fetch workflows. Status code: {response.status_code}')
        return
    
    workflows = response.json().get('workflows', [])
    
    if not workflows:
        print("No workflows found.")
        return
    
    for workflow in workflows:
        workflow_id = workflow['id']
        runs_url = f'https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs'
        runs_response = requests.get(runs_url, headers=headers)
        
        if runs_response.status_code != 200:
            print(f'Failed to get runs for workflow ID: {workflow_id}, Status code: {runs_response.status_code}')
            return
        
        runs = runs_response.json().get('workflow_runs', [])
        
        if not runs:
            print("No runs found for workflow ID:", workflow_id)
            continue
        
        if len(runs) < 2:
            print('Less than 2 runs found. Stopping search.')
            return
        
        second_run = runs[1]
        run_id = second_run['id']
        GITHUB_RUN_ID = "${{ github.run_id }}"
        
        if str(run_id) == GITHUB_RUN_ID:
            print(f'Run ID: {run_id} matches the specified ID. Stopping search.')
            return
        
        status = second_run['status']
        conclusion = None
        
        while status == 'in_progress':
            print(f'Run ID: {run_id} is still in progress. Checking again...')
            time.sleep(10)
            
            run_details_url = f'https://api.github.com/repos/{repo}/actions/runs/{run_id}'
            run_details_response = requests.get(run_details_url, headers=headers)
            
            if run_details_response.status_code != 200:
                print(f'Failed to get run details for run ID: {run_id}, Status code: {run_details_response.status_code}')
                break
            
            run_details = run_details_response.json()
            status = run_details['status']
            conclusion = run_details['conclusion']
        
        print(f'Run ID: {run_id} has completed. Final status: {status}, Conclusion: {conclusion}')
        return

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python recheckbuild.py <repository> <token>")
        print("Example: python recheckbuild.py \"owner/repo\" \"ghp_token\"")
        sys.exit(1)
    
    repo = sys.argv[1]
    token = sys.argv[2]
    
    if token:
        check_run_status(token, repo)
    else:
        print("Failed to retrieve token")