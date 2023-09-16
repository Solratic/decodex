from typing import Dict


def get_github_api_url(org: str, repo: str, branch: str, path: str) -> str:
    return f"https://api.github.com/repos/{org}/{repo}/contents/{path}?ref={branch}"


def get_github_rawfile_url(org: str, repo: str, branch: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{org}/{repo}/{branch}/{path}"


def get_github_url(org: str, repo: str, branch: str, path: str, use_api: bool) -> str:
    if use_api:
        return get_github_api_url(org=org, repo=repo, branch=branch, path=path)
    else:
        return get_github_rawfile_url(org=org, repo=repo, branch=branch, path=path)
