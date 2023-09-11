import os
from pathlib import Path


HOME = Path(os.getenv("VIRTUAL_ENV", Path.home()))
DECODEX_DIR = HOME.joinpath(".decodex")
