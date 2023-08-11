#!/usr/bin/python3

import requests
import os
from fastapi import FastAPI
from fastapi import Response
import uvicorn
import logging
from datetime import datetime, timedelta
from tabulate import tabulate

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
def get_user_issues(username: str):
    print("get in")

    # base_url = f'https://api.github.com/users/{username}/issues'
    response = requests.get(f'https://api.github.com/users/{username}/issues?filter=subscribed')
    print(response)
    
    # if response.status_code == 200:
    #     issues = response.json()
    #     print(issues)
    #     return {"Total issues raised": issues}
    # else:
    #     return {"Total issues raised": issues}
    
    # try:
    #     response = requests.get(f"{GITHUB_API_BASE}/repos/{username}/{REPO_NAME}/issues", params={"creator": user})
        
    #     if response.status_code == 200:
    #         issues = response.json()
    #         return jsonify(issues)
    #     else:
    #         return jsonify({"error": "Failed to retrieve issues"}), response.status_code
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

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

    # head = ["User", "Contributions"]
    # print(tabulate(user_insights, headers=head, tablefmt="grid"))
    return {"user": user_insights[0][0], "contribution": user_insights[0][1]}




if __name__ == '__main__':
    # app.run(debug=True)
    logger.info( "STARTING SERVER")
    uvicorn.run(app, host='0.0.0.0', port=8000)