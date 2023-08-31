import gzip
import json
import tempfile
from io import BytesIO
from io import StringIO
from pathlib import Path

import requests
import wget
from tqdm import tqdm
from wget import bar_thermometer

MB = 1024 * 1024


def _get_gitlfs_url(repo: str, branch: str, path: str):
    return f"https://api.github.com/repos/Solratic/{repo}/contents/{path}?ref={branch}"


def download_and_save_json(url: str, path: Path):
    wget.download(url, str(path))


def download_and_save_csv(chain: str, save_path: Path):
    # Download spec from git-lfs
    repo = "function-signature-registry"
    branch = "main"
    remote_path = f"data/{chain}/func_sign.csv.gz"
    url = _get_gitlfs_url(repo=repo, branch=branch, path=remote_path.format(chain=chain))
    spec = requests.get(url)
    spec.raise_for_status()
    spec = json.loads(spec.text)
    download_url = spec["download_url"]

    # Tempfile to store gzipped data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir).joinpath("func_sign.csv.gz")

        # Download file and decompress
        wget.download(download_url, str(temp_path))
        with open(temp_path, "rb") as f:
            compressed_data = BytesIO(f.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_data)
        csv_text = decompressed_file.read().decode("utf-8")
        total_write_size = len(csv_text) / (MB)

    with open(save_path, "w", newline="") as f:
        t = tqdm(
            total=total_write_size,
            unit="MiB",
            unit_scale=True,
            unit_divisor=1,
            desc="Writing CSV",
        )

        batch = []
        written_size = 0

        csv_file = StringIO(csv_text)
        while True:
            line = csv_file.readline()
            if not line:
                break

            batch.append(line)
            written_size += len(line.encode("utf-8"))

            if written_size >= MB:  # 1 MiB
                f.writelines(batch)
                t.update(written_size / (MB))
                batch = []
                written_size = 0  # Reset for next batch

        # Write any remaining lines
        if batch:
            f.writelines(batch)
            t.update(written_size / (MB))

        t.close()
