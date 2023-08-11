#!/usr/bin/python3

import requests
import os
from fastapi import FastAPI
from fastapi import Response
import uvicorn
import logging
from datetime import datetime, timedelta

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
GITHUB_API_BASE = "https://api.github.com"

@app.get('/health')
def health_check():
    logger.info("API Health: Healthy")
    return {"health": "ok"}

@app.get('/get_user')
def get_github_user(username: str): 
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


@app.get('/get_total_pr_count')
def get_total_pr_count(username: str):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    url = f'https://api.github.com/search/issues?q=type:pr+author:{username}'
    
    response = requests.get(url, headers=headers)
    data = response.json()

    total_pr_count = data['total_count']
    
    if total_pr_count is not None:
        logger.info( "Successfully recieved total PR count.")
        return {"username": username, "total_pr_count": total_pr_count}
    else:
        logger.error( "User does not exists.")
        return {"error": "User not found"}
    

@app.get('/get_user_issues')
def get_total_issue_count(username: str, repository: str, state: str):
    headers = {
        'Authorization': f'Token {ACCESS_TOKEN}'
    }

    base_url = f"https://api.github.com/repos/{username}/{repository}/issues"
    params = {
        "state": state,  # Valid Values'open', 'closed', or 'all' 
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        issues = response.json()
        return {"username": username, "total_issues": len(issues)}
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None




git_header = headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
git_url = "https://api.github.com/graphql"

def run_query(url, header, query, variables):
    request = requests.post(url, json={'query': query, 'variables': variables}, headers=header)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


query = '''
    query($username: String!, $from : DateTime!, $to: DateTime! ) {
        user(login: $username) { 
            contributionsCollection(from: $from, to: $to) {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }
'''
@app.get('/get_user_contribution')
def get_user_contribution(username: str, range_val: int):
    users = [username]  #List of your organization users
    user_insights = [] 
    range=range_val #Date range to retrieve contributions
    now_str = (datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
    n_days_ago_str = (datetime.now() - timedelta(days=range)).strftime("%Y-%m-%dT%H:%M:%SZ")
    input_variables = {}
    input_variables['from'] = n_days_ago_str
    input_variables['to'] = now_str

    for user in users:
        input_variables['username'] = user
        resp_data = run_query(git_url, git_header, query, input_variables)
        user_contributions  = resp_data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
        user_insights.append([user, user_contributions])        

    return {"user": user_insights[0][0], "contribution": user_insights[0][1]}


@app.get('/get_last_comments_by_user')
def get_last_comments_by_user(username: str):
    all_repo_comments = []
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of repositories for the user
    user_repositories_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(user_repositories_url, headers=headers)
    repositories = response.json()
    

    # Iterate over each repository
    for repo in repositories:
        repo_name = repo["name"]
        issues_url = f"https://api.github.com/repos/{username}/{repo_name}/issues"
        params = {"state": "open"}
        response = requests.get(issues_url, headers=headers, params=params)
        issues = response.json()

        # Iterate over each open issue
        for issue in issues:
            issue_number = issue["number"]
            comments_url = f"https://api.github.com/repos/{username}/{repo_name}/issues/{issue_number}/comments"
            response = requests.get(comments_url, headers=headers)
            comments = response.json()
            all_repo_comments.append(comments)

    if all_repo_comments is not None:
        for cmnts in all_repo_comments:
            last_comment = cmnts[-1]
            logger.info( "Successfully recieved last comment.")
            return {"username": username, "Repository": repo_name, "Last_Comment": last_comment["body"], "Issue":  last_comment['issue_url'],"Author": last_comment['user']['login'], "Comment": last_comment['body'], "Created_At": last_comment['created_at']} 
    else:
        logger.error( "User does not exists.")
        return {"error": "User not found"}

    



if __name__ == '__main__':
    # app.run(debug=True)
    logger.info( "STARTING SERVER")
    uvicorn.run(app, host='0.0.0.0', port=8000)