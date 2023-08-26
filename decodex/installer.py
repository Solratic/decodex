from tqdm import tqdm
import requests
from pathlib import Path
from io import BytesIO, StringIO
import gzip

MB = 1024 * 1024


def download_and_save_json(url: str, path: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    pbar = tqdm(
        total=total_size / (MB),
        unit="MiB",
        unit_scale=True,
        unit_divisor=1,
        desc="Downloading JSON",
    )
    with open(path, "wb") as f:
        for data in response.iter_content(MB):
            pbar.update(len(data) / (MB))
            f.write(data)
    pbar.close()


def download_and_save_csv(url: str, path: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    t = tqdm(
        total=total_size / (MB),
        unit="MiB",
        unit_scale=True,
        unit_divisor=1,
        desc="Downloading CSV",
    )

    compressed_data = BytesIO()
    for data in response.iter_content(MB):
        t.update(len(data) / (MB))
        compressed_data.write(data)
    t.close()

    compressed_data.seek(0)
    decompressed_file = gzip.GzipFile(fileobj=compressed_data)
    csv_text = decompressed_file.read().decode("utf-8")
    total_write_size = len(csv_text) / (MB)

    with open(path, "w", newline="") as f:
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
