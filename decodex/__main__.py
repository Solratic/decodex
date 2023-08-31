import os
from textwrap import indent

import click
import pyfiglet
from colorama import Fore
from colorama import Style

from .constant import DECODEX_DIR
from .installer import download_and_save_csv
from .installer import download_and_save_json
from decodex.translate import Translator
from decodex.utils import fmt_addr
from decodex.utils import fmt_blktime
from decodex.utils import fmt_gas
from decodex.utils import fmt_status
from decodex.utils import fmt_value

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
)

WELCOME_MESSAGE = f"{Fore.YELLOW}{pyfiglet.figlet_format('decodex')}{Style.RESET_ALL}"

VERSION_INFO = f"version  |  %(version)s \n"


@click.group(
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
    no_args_is_help=True,
)
@click.version_option(
    package_name="decodex",
    message=f"{Fore.YELLOW}{pyfiglet.figlet_format('welcome to decodex')}{Style.RESET_ALL} {VERSION_INFO}",
)
def cli():
    pass


@cli.command(help="download tags and signatures for a chain")
@click.argument("chain", default="ethereum", type=click.Choice(["ethereum"]))
def download(chain: str):
    chain = chain.lower()
    dir = DECODEX_DIR.joinpath(chain)
    dir.mkdir(parents=True, exist_ok=True)

    if chain == "ethereum":
        download_and_save_json(
            "https://raw.githubusercontent.com/brianleect/etherscan-labels/main/data/etherscan/combined/combinedAllLabels.json",
            dir.joinpath("tags.json"),
        )
        download_and_save_csv(
            chain="ethereum",
            save_path=dir.joinpath("signatures.csv"),
        )
    else:
        raise ValueError(f"Chain {chain} is not yet supported.")


@cli.command(help="Explain the transaction by the given hash")
@click.argument("txhash", required=True, type=str)
@click.option(
    "--chain",
    "-c",
    default="ethereum",
    type=click.Choice(["ethereum"]),
    help="Chain to use for decoding",
)
@click.option(
    "--provider-uri",
    "-p",
    type=str,
    default=os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545"),
    help="Ethereum provider URI for transaction decoding",
)
def explain(txhash: str, chain: str, provider_uri: str):
    translator = Translator(provider_uri=provider_uri, chain=chain, verbose=True)
    tagged_tx = translator.translate(txhash)
    tmpl = """
Transaction: {txhash}
Blocktime: {blocktime}
From: {from_addr}
To: {to_addr}
Value: {value}
GasUsed: {gas_used}
Gas Price: {gas_price}
Status: {status}
{action_field}{actions}
"""
    txhash = tagged_tx["txhash"]
    blocktime = fmt_blktime(tagged_tx["block_time"])
    from_addr = fmt_addr(tagged_tx["from"])
    to_addr = fmt_addr(tagged_tx["to"])
    value = fmt_value(tagged_tx["value"])
    gas_used = f'{tagged_tx["gas_used"]}'
    gas_price = fmt_gas(tagged_tx["gas_price"])
    status = fmt_status(tagged_tx["status"])

    action_existed = len(tagged_tx["actions"]) != 0
    action_str = ""
    if action_existed:
        action_str += "\n".join(f"- {a}" for a in tagged_tx["actions"])
    indented_actions = indent(action_str, "    ")  # Indent actions by 4 spaces

    render = tmpl.format(
        txhash=txhash,
        blocktime=blocktime,
        from_addr=from_addr,
        to_addr=to_addr,
        value=value,
        gas_used=gas_used,
        gas_price=gas_price,
        status=status,
        action_field="Actions:\n" if action_existed else "",
        actions=indented_actions,
    )

    indented_render = indent(render, "  ")  # Indent entire tmpl by 2 spaces
    print(indented_render)


if __name__ == "__main__":
    cli()


# https://raw.githubusercontent.com/brianleect/etherscan-labels/main/data/etherscan/combined/combinedAllLabels.json
