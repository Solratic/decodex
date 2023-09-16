from . import constant
from . import convert
from . import decode
from . import installer
from . import search
from . import translate
from . import type
from . import utils

installer.download_github_file(
    save_path=str(constant.DECODEX_DIR.joinpath("ethereum", "tags.json")),
    org="brianleect",
    repo="etherscan-labels",
    branch="main",
    path="data/etherscan/combined/combinedAllLabels.json",
    is_lfs=False,
    verify_ssl=False,
    use_tempfile=False,
)


installer.download_github_file(
    save_path=str(constant.DECODEX_DIR.joinpath("ethereum", "signatures.csv")),
    org="Solratic",
    repo="function-signature-registry",
    branch="main",
    path="data/ethereum/func_sign.csv.gz",
    is_lfs=True,
    verify_ssl=False,
    use_tempfile=True,
)

__all__ = [
    "convert",
    "decode",
    "search",
    "translate",
    "type",
    "utils",
    "installer",
]
