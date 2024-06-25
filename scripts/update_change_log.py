import os
import sys
from github import Github


def get_pr_details(pr_number):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = "change_log"
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    return pr.title, pr.user.login, pr.merged_at


def update_changelog(pr_number, pr_title, pr_user, pr_merged_at):
    changelog_path = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
    new_entry = f"- PR #{pr_number}: {pr_title} by @{pr_user} on {pr_merged_at}\n"

    with open(changelog_path, "r+") as file:
        lines = file.readlines()
        file.seek(0, 0)
        file.write(new_entry)
        for line in lines:
            file.write(line)


if __name__ == "__main__":
    pr_number = int(os.getenv("GITHUB_EVENT_PULL_REQUEST_NUMBER"))
    pr_title, pr_user, pr_merged_at = get_pr_details(pr_number)
    update_changelog(pr_number, pr_title, pr_user, pr_merged_at)
    print(
        f"Changelog updated with PR #{pr_number}: {pr_title} by {pr_user} on {pr_merged_at}"
    )
