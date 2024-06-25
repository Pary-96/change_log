import os
import requests
from github import Github
from requests.auth import HTTPBasicAuth


def get_pr_details(pr_number):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return pr.title, pr.user.login, pr.merged_at


def update_confluence(pr_number, pr_title, pr_user, pr_merged_at):
    confluence_base_url = os.getenv("CONFLUENCE_BASE_URL")
    confluence_space_key = os.getenv("CONFLUENCE_SPACE_KEY")
    confluence_page_id = os.getenv("CONFLUENCE_PAGE_ID")
    confluence_token = os.getenv("CONFLUENCE_API_TOKEN")

    auth = HTTPBasicAuth("parisrahman96@gmail.com", confluence_token)
    headers = {
        "Content-Type": "application/json",
    }

    url = f"{confluence_base_url}/rest/api/content/{confluence_page_id}?expand=body.storage,version"
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()

    page_data = response.json()
    version_number = page_data["version"]["number"] + 1
    existing_content = page_data["body"]["storage"]["value"]

    new_entry = f"<p>- PR #{pr_number}: {pr_title} by @{pr_user} on {pr_merged_at}</p>"
    updated_content = f"{new_entry}{existing_content}"

    update_payload = {
        "version": {"number": version_number},
        "title": page_data["title"],
        "type": "page",
        "body": {"storage": {"value": updated_content, "representation": "storage"}},
    }

    update_response = requests.put(url, auth=auth, headers=headers, json=update_payload)
    update_response.raise_for_status()


if __name__ == "__main__":
    pr_number = int(os.getenv("GITHUB_EVENT_PULL_REQUEST_NUMBER"))
    pr_title, pr_user, pr_merged_at = get_pr_details(pr_number)
    update_confluence(pr_number, pr_title, pr_user, pr_merged_at)
    print(
        f"Confluence page updated with PR #{pr_number}: {pr_title} by {pr_user} on {pr_merged_at}"
    )
