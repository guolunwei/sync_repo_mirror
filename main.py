<<<<<<< HEAD
#!/user/bin/env python3
# @author Lunwei Guo
# @email Lunwei.guo@hotmail.com

import tempfile
import time

from github import Auth, Github, GithubException
=======
import time
import tempfile
from github import Auth, Github
>>>>>>> 7bb864d671343656653df57557a303182d2f7b8d
from git import Repo


class GitClient:
    def __init__(self, access_token, website='github'):
        self.access_token = access_token
        self.website = website
        self.client = self.get_git_client()
<<<<<<< HEAD
        self.user = self.client.get_user()
        self.repos = self.client.get_user().get_repos()
=======
        self.owner = self.client.get_user().login
        self.repo_names = self.get_repo_names()
>>>>>>> 7bb864d671343656653df57557a303182d2f7b8d

    def get_git_client(self):
        auth = Auth.Token(self.access_token)
        base_url = "https://gitee.com/api/v5" if self.website.lower().strip() == 'gitee' else "https://api.github.com"
        g = Github(auth=auth, base_url=base_url)
        return g

<<<<<<< HEAD

class SyncRepoMirror:
    def __init__(self, origin: GitClient, mirror: GitClient):
        self.origin = origin
        self.mirror = mirror
        self.sync_repos = self.get_sync_repos()
        self.mirror_repo_names: list[str] = [i.name for i in self.mirror.repos]

    def get_sync_repos(self):
        if config.REPO_LIST:
            repos = [i for i in self.origin.repos if i.name in config.REPO_LIST]
        else:
            repos = self.origin.repos
        return [i for i in repos if i.name not in config.EXCLUDED_REPO_LIST]

    def create_mirror_repo(self, repo):
        return self.mirror.user.create_repo(
            name=repo.name,
            description=repo.description
        )

    def check_mirror_repo(self, repo):
        latest_commit_sha = repo.get_commits()[0].raw_data['sha']
        mirror_repo = self.mirror.client.get_repo(repo.full_name)
        try:
            latest_commit = mirror_repo.get_commit(latest_commit_sha)
        except GithubException:
            latest_commit = None
        return latest_commit

    def update_mirror_repo(self, repo):
        if self.check_mirror_repo(repo):
            print(f"Already the latest commit '{self.check_mirror_repo(repo).sha}'")
        else:
            clone_url = repo.clone_url if repo.clone_url else repo.html_url
            with tempfile.TemporaryDirectory() as tmp_dir:
                print(f"Cloning repository '{repo.name}' from '{clone_url}' to temp directory '{tmp_dir}'")
                temp_repo = Repo.clone_from(clone_url, tmp_dir)
                origin = temp_repo.remotes.origin
                print(f"Repository '{repo.name}' cloned successfully")

                url = clone_url.replace(self.origin.website, self.mirror.website)
                auth_url = url.replace('//', f"//{self.mirror.user.login}:{self.mirror.access_token}@")
                origin.set_url(url)

                print(f"Pushing to remote '{url}'")
                temp_repo.git.push("--all", auth_url)
                temp_repo.git.push("--tags", auth_url)
                print(f"Pushed to remote '{url}' successfully")

                time.sleep(5)
                if self.check_mirror_repo(repo):
                    print(f"Updated to latest commit '{self.check_mirror_repo(repo).sha}'")
                else:
                    print(f"Failed updating to latest commit '{self.check_mirror_repo(repo).sha}'")

    def run(self):
        if self.sync_repos:
            i = 1
            for repo in self.sync_repos:
                print(f"[{i}/{len(self.sync_repos)}] start scan repo: {repo.full_name}")
                if repo.name not in self.mirror_repo_names:
                    self.create_mirror_repo(repo)
                else:
                    self.update_mirror_repo(repo)
                print("")
                i += 1
        else:
            return
=======
    def get_repo_names(self):
        user = self.client.get_user()
        repos = user.get_repos()
        return [i.name for i in repos]

    def get_latest_commit_id(self, repo_name):
        repo = self.client.get_repo(f"{self.owner}/{repo_name}")
        commits = repo.get_commits()
        commit_id = commits[0].raw_data['sha']
        return commit_id


def sync_repo_mirror(base_client, mirror_client):
    if config.REPO_LIST:
        repo_list = config.REPO_LIST
    else:
        repo_list = base_client.repo_names

    mirror_repo_list = mirror_client.repo_names
    print(mirror_repo_list)

    cnt = 1
    scan_repo_names = [i for i in repo_list if i not in config.EXCLUDED_REPO_LIST]
    for repo_name in scan_repo_names:
        if cnt > 1:
            print("")
        print(f"[{cnt}/{len(scan_repo_names)}] start scan repo: {base_client.owner}/{repo_name}")
        cnt += 1

        if repo_name not in mirror_repo_list:
            new_repo = None
            try:
                repo = base_client.client.get_repo(f"{base_client.owner}/{repo_name}")

                # Create new repository on mirror
                user = mirror_client.client.get_user()
                new_repo = user.create_repo(
                    name=repo.name,
                    description=repo.description,
                    license_template=repo.license if repo.license else 'MIT'
                )
                print(f"Repository '{repo_name}' created successfully.")

                # Clone repository from base and push it to mirror
                clone_url = repo.clone_url if repo.clone_url else repo.html_url
                with tempfile.TemporaryDirectory() as tmp_dir:
                    print(f"Cloning repository '{repo_name}' from '{clone_url}' to temp directory: {tmp_dir}")
                    local_repo = Repo.clone_from(clone_url, tmp_dir)
                    print(f"Repository '{repo_name}' cloned successfully.")
                    print(dir(local_repo))

                    local_repo = Repo(tmp_dir)
                    print(dir(local_repo))
                    origin = local_repo.remotes.origin
                    print(origin)
                    origin.set_url(f'https://{mirror_client.website}.com/{mirror_client.owner}/{repo_name}.git')
                    print(f"Pushed to url: {repo.remotes.origin.url}")
                    repo_url = (f'https://{mirror_client.owner}:{mirror_client.access_token}@{mirror_client.website}.com'
                                f'/{mirror_client.owner}/{repo_name}.git')
                    print(repo_url)
                    local_repo.git.pull("--all", repo_url)
                    local_repo.git.push("--all", repo_url)
                    local_repo.git.push("--tags", repo_url)

                    # Set repository private property
                    new_repo.edit(private=repo.private)
                    time.sleep(5)
                    print(f"Pushed to mirror repository successfully.")

            except Exception as e:
                print(f"Error synchronizing base to mirror: {e}")
                if new_repo:
                    new_repo.delete()
                    print(f"Repository '{repo_name}' deleted successfully.")

        else:
            try:
                # Compare commit id to decide whether synchronize or not
                base_commit_id = base_client.get_latest_commit_id(repo_name)
                mirror_commit_id = mirror_client.get_latest_commit_id(repo_name)

                if base_commit_id != mirror_commit_id:
                    print(
                        f"Repository {mirror_client.owner}/{repo_name} newest commit id: {base_commit_id}, updating...")

                if base_commit_id == mirror_commit_id:
                    print(
                        f"Repository {mirror_client.owner}/{repo_name} updated to latest. commit id: {base_commit_id}")
                else:
                    print(f"Update failed, please check manually. commit id: {base_commit_id}")
            except Exception as e:
                print(f"Error updating mirror to latest: {e}")
>>>>>>> 7bb864d671343656653df57557a303182d2f7b8d


if __name__ == '__main__':
    import config

    if not config.GITHUB_TOKEN or not config.GITEE_TOKEN:
        raise ValueError("GITHUB_TOKEN or GITEE_TOKEN is empty.")

    github = GitClient(config.GITHUB_TOKEN)
    gitee = GitClient(config.GITEE_TOKEN, 'gitee')

    if config.SYNC_DIRECTION == 'github2gitee':
<<<<<<< HEAD
        SyncRepoMirror(github, gitee).run()
    else:
        SyncRepoMirror(gitee, github).run()
=======
        sync_repo_mirror(github, gitee)
    else:
        sync_repo_mirror(gitee, github)
>>>>>>> 7bb864d671343656653df57557a303182d2f7b8d
