import os
import requests
from requests.auth import HTTPBasicAuth
from github import Github


def get_pr_details(pr_number):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return pr.title, pr.user.login, pr.updated_at


def update_confluence_page(pr_number):
    confluence_base_url = os.getenv(
        "CONFLUENCE_BASE_URL"
    )  # Example: https://parisrahman96.atlassian.net/wiki
    confluence_space_key = os.getenv(
        "CONFLUENCE_SPACE_KEY"
    )  # Example: ~712020852e0e27fe6f4a21a814a33587212877
    confluence_page_id = os.getenv("CONFLUENCE_PAGE_ID")  # Example: 33172
    confluence_token = os.getenv("CONFLUENCE_API_TOKEN")
    confluence_email = "parisrahman96@gmail.com"  # Replace with your Confluence email

    auth = HTTPBasicAuth(confluence_email, confluence_token)
    headers = {
        "Content-Type": "application/json",
    }

    # Fetch current page version
    url = f"{confluence_base_url}/rest/api/content/{confluence_page_id}?expand=body.storage,version"
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()

    page_data = response.json()
    version_number = page_data["version"]["number"] + 1
    existing_content = page_data["body"]["storage"]["value"]

    # Get PR details
    pr_title, pr_user, pr_updated_at = get_pr_details(pr_number)

    # Prepare updated content
    new_entry = f"<p>- Version {version_number}: PR #{pr_number} - {pr_title} by @{pr_user} on {pr_updated_at}</p>"
    updated_content = f"{new_entry}\n{existing_content}"

    # Prepare payload for updating the page
    update_payload = {
        "version": {"number": version_number},
        "type": "page",
        "title": page_data["title"],
        "body": {"storage": {"value": updated_content, "representation": "storage"}},
    }

    # Perform update request
    update_response = requests.put(url, auth=auth, headers=headers, json=update_payload)
    update_response.raise_for_status()

    print(f"Confluence page updated successfully with new content.")


if __name__ == "__main__":
    pr_number = int(os.getenv("GITHUB_EVENT_PULL_REQUEST_NUMBER"))
    update_confluence_page(pr_number)
