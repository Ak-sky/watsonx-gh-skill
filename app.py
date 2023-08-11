#!/usr/bin/python3

import requests
import os
from fastapi import FastAPI
from fastapi import Response
import uvicorn
import logging

#
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a" 
)

# Create a logger
logger = logging.getLogger()

# Create a console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO) 

formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(handler)


app = FastAPI()


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
# REPO_OWNER = os.getenv("REPO_OWNER", None)
# ORG_NAME = os.getenv("ORG_NAME", None)

# GITHUB_API_URL = 'https://api.github.com/users/'
#TODO: Make these inputs like Repo owner etc as Env vars
GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "Ak-sky"
ORG_NAME = "terraform-ibm-modules"
# COLLABORATOR = "Ak-sky"

@app.get('/health')
def health_check():
    logger.info("API Health: Healthy")
    return {"health": "ok"}

@app.get('/get_user')
def get_github_user(username: str): 
    url = GITHUB_API_BASE
    try:
        logger.info(f"Getting github user: {username}")
        response = requests.get(GITHUB_API_BASE + "/users/" + username)
        if response.status_code == 200:
            logger.info("Successfully received user info.")
            user_data = response.json()
            return {"user_data": user_data}
        else:
            logger.error("User does not exists")
            return {"error": "User not found"}
    except Exception as e:
        logger.error(e)
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
        logger.info( "Successfully recieved total commits.")
        return {"username": username, "total_commits": total_commits}
    else:
        logger.error( "User does not exists.")
        return {"error": "User not found"}
    

@app.get('/get_collaborator_commits')
def get_collaborator_commits(username: str):
    url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
    headers = {
    'Authorization': f'Token {ACCESS_TOKEN}'
    }
    total_commits_weekly = 0
    logger.info( "Getting collab commits..")

    response = requests.get(url, headers=headers)
    repos = response.json()
    
    for repo in repos:
        repo_name = repo['name']
        commits_url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/stats/contributors'
        
        response = requests.get(commits_url, headers=headers)
        repo_stats = response.json()
        logger.info(f"Repo stats : {repo_stats}")
        for contributor in repo_stats:
            if contributor['author']['login'] == username:
                print(contributor['author']['login'])
                total_commits_weekly += sum(week['c'] for week in contributor['weeks'])
                break

    if total_commits_weekly is not None:
        logger.info("Success: Collaborator commits")
        return {"contributor": contributor['author']['login'], "total_commits_weekly": total_commits_weekly}
    else:
        logger.error( "User does not exists")
        return {"error": "User not found"}

@app.get('/get_total_pr_count')
def get_total_pr_count(username: str):
    headers = {
    'Authorization': f'Token {ACCESS_TOKEN}'
        }
    logger.info( "GETTING TOTAL PR COUNT..")
    
    query = f"author:{username} is:pr"

    search_url = f"{GITHUB_API_BASE}/search/issues?q={query}"
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        logger.info( "PR COUNT : Success")
        data = response.json()
        total_count = data.get("total_count", 0)
    
    if total_count is not None:
        logger.info( "Invalid PR Count")
        return {"total_PR_count": total_count}
    else:
        logger.error( "User not found")
        return {"error": "User not found"}




if __name__ == '__main__':
    # app.run(debug=True)
    logger.info( "STARTING SERVER")
    uvicorn.run(app, host='0.0.0.0', port=8000)