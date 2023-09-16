import gzip
import hashlib
import json
from abc import abstractstaticmethod
from io import BytesIO
from pathlib import Path

import requests

from .utils import get_github_url


class BaseBeforeCallback:
    @abstractstaticmethod
    def before_download(save_path: str, **kwargs) -> str:
        pass


class BasePostCallback:
    @abstractstaticmethod
    def post_download(src_path: str, save_path: str, **kwargs):
        pass


class GithubRawBeforeCallback(BaseBeforeCallback):
    """
    kwargs : Dict
        The arguments to pass to get_github_url.
        - org : str
            The name of the organization or user.
        - repo : str
            The name of the repository.
        - branch : str
            The name of the branch.
        - path : str
            The path to the file in the repository.
    """

    def before_download(save_path: str, **kwargs) -> str:
        url = get_github_url(use_api=False, **kwargs)
        return url


class GithubLFSBeforeCallback(BaseBeforeCallback):
    @staticmethod
    def before_download(save_path: str, **kwargs) -> str:
        """
        Get spec from Github API then check the checksum of the file to download.

        Parameters
        ----------
        save_path : str
            The path to save the file to.
        kwargs : Dict
            The arguments to pass to get_github_lfs_url.
            - org : str
                The name of the organization or user.
            - repo : str
                The name of the repository.
            - branch : str
                The name of the branch.
            - path : str
                The path to the file in the repository.
        Returns
        -------
        str
            The modified URL.

        Raises
        ------
        FileExistsError
            If the file already exists and is up to date.
        """
        spec_url = get_github_url(use_api=True, **kwargs)

        spec = requests.request(method="GET", url=spec_url)

        spec.raise_for_status()
        spec = json.loads(spec.text)
        download_url = spec["download_url"]
        checksum = spec["sha"]

        # Check if the file already exists
        path = Path(save_path)
        if path.exists() and path.with_suffix(".checksum").exists():
            # Check if the checksum is the same
            with path.with_suffix(".checksum").open("r") as cf:
                if cf.read() == checksum:
                    raise FileExistsError("File already exists and is up to date")
        # Save the checksum
        path.with_suffix(".checksum").write_text(checksum)
        return download_url


class GzipPostCallback(BasePostCallback):
    @staticmethod
    def post_download(src_path: str, save_path: str, **config):
        """
        Decompress a gzip file.

        Parameters
        ----------
        src_path : str
            The path to the file to decompress.
        save_path : str
            The path to save the decompressed file to.
        """
        in_path = Path(src_path)
        out_path = Path(save_path)
        with in_path.open("rb") as f, out_path.open("wb") as g:
            compressed_data = BytesIO(f.read())
            decompressed_file = gzip.GzipFile(fileobj=compressed_data)
            g.write(decompressed_file.read())


class ChecksumPostCallback(BasePostCallback):
    @staticmethod
    def post_download(src_path: str, save_path: str, **config):
        """
        Calculate the checksum of a file and save it to {save_path}.checksum.

        Parameters
        ----------
        src_path : str
            The path to the file to check.
        save_path : str
            The path to save the file to.
        """
        # Define the path objects
        checksum_path = Path(save_path).with_suffix(".checksum")

        # Calculate the checksum of the file
        hash_algorithm = config.get("hash_algorithm", config.get("algorithm", "sha256"))
        hash_object = hashlib.new(hash_algorithm)

        with Path(src_path).open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_object.update(chunk)

        checksum = hash_object.hexdigest()

        # Save the checksum to the specified path
        with checksum_path.open("w") as g:
            g.write(checksum)
