from pathlib import Path
import os


HOME = Path(os.getenv("VIRTUAL_ENV", Path.home()))
DECODEX_DIR = HOME.joinpath(".decodex")
