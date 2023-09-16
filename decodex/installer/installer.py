import os
import pathlib
import tempfile
import warnings
from typing import Dict

import requests
from tqdm import tqdm

from .callbacks import ChecksumPostCallback
from .callbacks import GithubLFSBeforeCallback
from .callbacks import GithubRawBeforeCallback
from .callbacks import GzipPostCallback

warnings.filterwarnings("ignore")


def _get_github_url(save_path: str, org: str, repo: str, branch: str, path: str, is_lfs: bool) -> str:
    if is_lfs:
        cls = GithubLFSBeforeCallback
    else:
        cls = GithubRawBeforeCallback

    return cls.before_download(
        save_path=save_path,
        org=org,
        repo=repo,
        branch=branch,
        path=path,
    )


def download_from_url(url: str, save_path: str, verify_ssl: bool, retry_with_proxy: bool = True) -> None:
    try:
        response = requests.get(url=url, verify=verify_ssl, stream=True)
        file_size = int(response.headers.get("content-length", 0))
        with tqdm(total=file_size, unit="iB", unit_scale=True) as pbar:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    except Exception as e:
        if not retry_with_proxy:
            raise e
        proxy = os.getenv("PROXY_URL", None)
        if proxy:
            download_from_url(url, save_path, verify_ssl, retry_with_proxy=False)


def download_github_file(
    save_path: str,
    org: str,
    repo: str,
    branch: str,
    path: str,
    is_lfs: bool = False,
    verify_ssl: bool = False,
    use_tempfile: bool = False,
) -> None:
    # Create parent directory if not exist
    pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        url = _get_github_url(save_path, org, repo, branch, path, is_lfs)
    except FileExistsError as e:
        print(f"Skip Downloading: {e}")
        return
    except Exception as e:
        print(f"Error getting download URL: {e}")
        return

    try:
        src_path = tempfile.mktemp() if use_tempfile else save_path
        download_from_url(url, src_path, verify_ssl)
    except Exception as e:
        print(f"Error downloading file: {e}")
        return

    post_cls = GzipPostCallback if is_lfs else ChecksumPostCallback
    try:
        post_cls.post_download(src_path, save_path)
    except Exception as e:
        print(f"Error in post-download steps: {e}")
        return
