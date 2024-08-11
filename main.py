import tempfile
import time

from github import Auth, Github, GithubException
from git import Repo


class GitClient:
    def __init__(self, access_token, website='github'):
        self.access_token = access_token
        self.website = website
        self.client = self.get_git_client()
        self.user = self.client.get_user()
        self.repos = self.client.get_user().get_repos()

    def get_git_client(self):
        auth = Auth.Token(self.access_token)
        base_url = "https://gitee.com/api/v5" if self.website.lower().strip() == 'gitee' else "https://api.github.com"
        g = Github(auth=auth, base_url=base_url)
        return g


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
                i += 1
                print("\n")
        else:
            return


if __name__ == '__main__':
    import config

    if not config.GITHUB_TOKEN or not config.GITEE_TOKEN:
        raise ValueError("GITHUB_TOKEN or GITEE_TOKEN is empty.")

    github = GitClient(config.GITHUB_TOKEN)
    gitee = GitClient(config.GITEE_TOKEN, 'gitee')

    if config.SYNC_DIRECTION == 'github2gitee':
        SyncRepoMirror(github, gitee).run()
    else:
        SyncRepoMirror(gitee, github).run()
