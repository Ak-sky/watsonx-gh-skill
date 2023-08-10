from flask import Flask, render_template, request, jsonify
import requests
from fastapi import FastAPI
from fastapi import Response
import uvicorn

app = FastAPI()


ACCESS_TOKEN = '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'

# GITHUB_API_URL = 'https://api.github.com/users/'

GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "Ak-sky"
ORG_NAME = "terraform-ibm-modules"
# COLLABORATOR = "Ak-sky"

@app.get('/get_user')
def get_github_user(username: str): 
    url = GITHUB_API_BASE
    try:
        response = requests.get(GITHUB_API_BASE + "/users/" + username)
        if response.status_code == 200:
            user_data = response.json()
            return {"user_data": user_data}
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    

@app.get('/get_total_commits')
def total_commits(username: str):

    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    
    if response.status_code == 200:
        repositories = response.json()
        total_commits = 0
        
        for repo in repositories:
            repo_name = repo['name']
            commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
            commits_response = requests.get(commits_url)
            
            if commits_response.status_code == 200:
                commits = commits_response.json()
                total_commits += len(commits)
    
    if total_commits is not None:
        return {"username": username, "total_commits": total_commits}
    else:
        return {"error": "User not found"}
    

@app.get('/get_collaborator_commits')
def get_collaborator_commits(username: str):
    url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
    headers = {
    'Authorization': f'Token {ACCESS_TOKEN}'
    }
    total_commits_weekly = 0

    response = requests.get(url, headers=headers)
    repos = response.json()
    
    for repo in repos:
        repo_name = repo['name']
        commits_url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/stats/contributors'
        
        response = requests.get(commits_url, headers=headers)
        repo_stats = response.json()
        print(repo_stats)
        for contributor in repo_stats:
            if contributor['author']['login'] == username:
                print(contributor['author']['login'])
                total_commits_weekly += sum(week['c'] for week in contributor['weeks'])
                break

    if total_commits_weekly is not None:
        return {"contributor": contributor['author']['login'], "total_commits_weekly": total_commits_weekly}
    else:
        return {"error": "User not found"}

@app.get('/get_total_pr_count')
def get_total_pr_count(username: str):
    headers = {
    'Authorization': f'Token {ACCESS_TOKEN}'
        }
    
    query = f"author:{username} is:pr"

    search_url = f"{GITHUB_API_BASE}/search/issues?q={query}"
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        total_count = data.get("total_count", 0)
    
    if total_count is not None:
        return {"total_PR_count": total_count}
    else:
        return {"error": "User not found"}




if __name__ == '__main__':
    # app.run(debug=True)
    uvicorn.run(app, host='0.0.0.0', port=8000)