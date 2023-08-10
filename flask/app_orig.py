from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


ACCESS_TOKEN = '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'

# GITHUB_API_URL = 'https://api.github.com/users/'

GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = "Ak-sky"
ORG_NAME = "terraform-ibm-modules"
COLLABORATOR = "Ak-sky"

@app.route('/get_user/<username>', methods=['GET'])
def get_github_user(username):
    try:
        response = requests.get(GITHUB_API_BASE + "/users/" + username)
        if response.status_code == 200:
            user_data = response.json()
            return jsonify(user_data)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
def get_total_commits(username):
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
        
        return total_commits
    else:
        return None

@app.route('/get_total_commits/<username>')
def total_commits(username):
    total_commits = get_total_commits(username)
    
    if total_commits is not None:
        return jsonify({"username": username, "total_commits": total_commits})
    else:
        return jsonify({"error": "User not found"}), 4
    

def get_total_commits_for_collaborator():
    url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
    headers = {
        'Authorization': f'Token {ACCESS_TOKEN}'
    }
    
    total_commits = 0
    
    response = requests.get(url, headers=headers)
    repos = response.json()
    
    for repo in repos:
        repo_name = repo['name']
        commits_url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/stats/contributors'
        
        response = requests.get(commits_url, headers=headers)
        repo_stats = response.json()
        
        for contributor in repo_stats:
            if contributor['author']['login'] == COLLABORATOR:
                print(contributor['author']['login'])
                total_commits += sum(week['c'] for week in contributor['weeks'])
                break
    return contributor['author']['login']
            
    
    

@app.route('/collaborator_commits')
def get_total_commits():
    total_commits = get_total_commits_for_collaborator()
    return jsonify({'total_commits': total_commits})


if __name__ == '__main__':
    app.run(debug=True)