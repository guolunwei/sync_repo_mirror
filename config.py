import os

GITHUB_TOKEN = os.environ.get("github_token", "")
GITEE_TOKEN = os.environ.get("gitee_token", "")

SYNC_DIRECTION = os.environ.get("sync_direction", "github2gitee")

REPO_LIST = ["ansible-zabbix"]
# REPO_LIST = []
EXCLUDED_REPO_LIST = [
    "get_info",
    "KeepAliveE5",
    "cloud_network"
]
