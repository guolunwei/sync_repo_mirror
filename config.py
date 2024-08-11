import os

GITHUB_TOKEN = os.environ.get("github_token", "your_github_access_token_here")
GITHUB_PRIVATE_KEY = os.environ.get("github_private_key", "")
GITEE_TOKEN = os.environ.get("gitee_token", "your_gitee_access_token_here")
GITEE_PRIVATE_KEY = os.environ.get("gitee_private_key", "")

# REPO_LIST = ["ansible-prometheus"]
REPO_LIST = ["test"]
EXCLUDED_REPO_LIST = [
    "get_info",
    "KeepAliveE5",
    "cloud_network"
]
