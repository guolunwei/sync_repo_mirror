import os
import time
import tempfile

from github import Auth, Github
from git import Repo


class GitClient:
    def __init__(self, access_token, website='github'):
        self.access_token = access_token
        self.website = website
        self.client = self.get_git_client()
        self.owner = self.client.get_user().login
        self.repo_names = self.get_repo_names()

    def get_git_client(self) -> Github:
        auth = Auth.Token(self.access_token)
        if self.website.lower().strip() == 'gitee':
            base_url = "https://gitee.com/api/v5"
        else:
            base_url = "https://api.github.com"
        g = Github(auth=auth, base_url=base_url)
        return g

    def get_repo_names(self) -> list[str]:
        user = self.client.get_user()
        repos = user.get_repos()
        return [i.name for i in repos]

    def get_latest_commit_id(self, repo_name: str) -> str:
        repo = self.client.get_repo(f"{self.owner}/{repo_name}")
        commits = repo.get_commits()
        commit_id = commits[0].raw_data['sha']
        return commit_id


class GitRepoSync:
    pass


def sync_repo_mirror(base_client: GitClient, mirror_client: GitClient):
    if config.REPO_LIST:
        repo_list = config.REPO_LIST
    else:
        repo_list = base_client.repo_names

    mirror_repo_list = mirror_client.repo_names

    cnt = 1
    scan_repo_names = [i for i in repo_list if i not in config.EXCLUDED_REPO_LIST]
    for repo_name in scan_repo_names:
        if cnt > 1:
            print("")
        print(f"[{cnt}/{len(scan_repo_names)}] start scan repo: {base_client.owner}/{repo_name}")
        cnt += 1

        if repo_name in mirror_repo_list:
            try:
                repo = base_client.client.get_repo(f"{base_client.owner}/{repo_name}")

                # Create new repository on mirror
                user = mirror_client.client.get_user()
                new_repo = user.create_repo(
                    name=repo.name,
                    description=repo.description,
                    private=repo.private
                )
                print(f"Repository '{repo_name}' created successfully.")

                # Clone repository from base and push it to mirror
                clone_url = repo.clone_url if repo.clone_url else repo.html_url
                with open tempfile.TemporaryDirectory() as tmp_dir:
                    print(f"Cloning repository '{repo_name}' from '{clone_url}' to temp directory: {tmp_dir}")
                    Repo.clone_from(clone_url, tmp_dir)
                    print(f"Repository '{repo_name}' cloned successfully.")

                    repo = Repo(tmp_dir)
                    origin = repo.remotes.origin
                    origin.set_url(f'https://{mirror_client.website}.com/{mirror_client.owner}/{repo_name}.git')
                    print(f"Pushed to url: {repo.remotes.origin.url}")
                    repo.git.push("--all")
                    repo.git.push("--tags")
                    time.sleep(5)
                    print(f"Pushed to mirror repository successfully.")

                # Update repository visibility (gitee not allow to create an empty public repository)
            except Exception as e:
                print(f"Error synchronizing base to mirror: {e}")
        else:
            try:
                # Compare commit id to decide whether synchronize or not
                base_commit_id = base_client.get_latest_commit_id(repo_name)
                mirror_commit_id = mirror_client.get_latest_commit_id(repo_name)

                if base_commit_id != mirror_commit_id:
                    print(f"Repository {mirror_client.owner}/{repo_name} newest commit id: {base_commit_id}, updating...")

                if base_commit_id == mirror_commit_id:
                    print(f"Repository {mirror_client.owner}/{repo_name} updated to latest. commit id: {base_commit_id}")
                else:
                    print(f"update failed, please check manually. commit id: {base_commit_id}")
            except Exception as e:
                print(f"Error updating mirror to latest: {e}")


if __name__ == '__main__':
    import config
    if not config.GITHUB_TOKEN or not config.GITEE_TOKEN:
        raise ValueError("GITHUB_TOKEN or GITEE_TOKEN is empty.")

    github = GitClient(config.GITHUB_TOKEN)
    gitee = GitClient(config.GITEE_TOKEN, 'gitee')

    # sync_repo_mirror(github, gitee)
    sync_repo_mirror(gitee, github)
