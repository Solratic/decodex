import os
from textwrap import indent
from typing import Literal
from typing import Union

import click
import pyfiglet
from colorama import Fore
from colorama import Style
from jinja2 import Template
from tabulate import tabulate

from .installer import download_and_save_csv
from .installer import download_and_save_json
from decodex.constant import DECODEX_DIR
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
@click.option("--txhash", type=str, help="Hash of the transaction", default=None)
@click.option("--from-addr", type=str, help="Address of the sender", default=None)
@click.option("--to-addr", type=str, help="Address of the receiver", default=None)
@click.option("--value", type=float, help="Value in ether", default=None)
@click.option("--input-data", type=str, help="Input data of the transaction", default="0x")
@click.option("--block", type=str, help="Block number of the transaction", default="latest")
@click.option("--chain", "-c", type=click.Choice(["ethereum"]), default="ethereum", help="Chain to use for decoding")
@click.option("--provider-uri", "-p", type=str, default=os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545"))
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode", default=False)
def explain(
    txhash: str,
    from_addr: str,
    to_addr: str,
    value: int,
    input_data: str,
    block: Union[Literal["latest"], int],
    chain: str,
    provider_uri: str,
    verbose: bool,
):
    translator = Translator(provider_uri=provider_uri, chain=chain, verbose=verbose)
    if txhash is None:
        # If txhash is not provided, then from_addr, to_addr, value, input_data must be provided to simulate a transaction
        assert (
            from_addr is not None and to_addr is not None and value is not None and input_data is not None
        ), "Either txhash or [from_addr, to_addr, value, input_data] must be provided"
        assert (
            from_addr.startswith("0x") and to_addr.startswith("0x") and input_data.startswith("0x")
        ), "from_addr, to_addr, input_data must be hex string"
        assert value >= 0, "value must be non-negative"
        value = int(value * 1e18)
        block = int(block) if block != "latest" else block
        tagged_tx = translator.simulate(
            from_address=from_addr,
            to_address=to_addr,
            value=value,
            data=input_data,
            block=block,
        )
    else:
        # If txhash is provided
        tagged_tx = translator.translate(txhash=txhash)

    tmpl = Template(
        """\
Transaction: {{txhash}}
Blocktime: {{blocktime}}
From: {{from_addr}}
To: {{to_addr}} {% if contract_created %} (Contract Created: {{contract_created}}){% endif %}
Value: {{value}}
GasUsed: {{gas_used}}
Gas Price: {{gas_price}}
Status: {{status}}{% if reason %} ({{reason}}){% endif %}
{% if method -%}
Method: {{method}}
{% endif -%}
{% if actions -%}

Actions
------
{{actions}}
{% endif -%}
{% if balance_change -%}

Balance Changes
--------------
{{balance_change}}
{% endif -%}
"""
    )
    txhash = tagged_tx["txhash"]
    blocktime = fmt_blktime(tagged_tx["block_time"])
    from_addr = fmt_addr(tagged_tx["from"])
    to_addr = fmt_addr(tagged_tx["to"]) if tagged_tx["to"] else None
    contract_created = fmt_addr(tagged_tx["contract_created"]) if tagged_tx["contract_created"] else None
    value = fmt_value(tagged_tx["value"])
    gas_used = f'{tagged_tx["gas_used"]}'
    gas_price = fmt_gas(tagged_tx["gas_price"])
    status = fmt_status(tagged_tx["status"])
    reason = tagged_tx["reason"]

    action_str = "\n".join(f"- {a}" for a in tagged_tx["actions"])
    indented_actions = indent(action_str, " " * 4)

    render = tmpl.render(
        txhash=txhash,
        blocktime=blocktime,
        from_addr=from_addr,
        to_addr=to_addr,
        contract_created=contract_created,
        value=value,
        gas_used=gas_used,
        gas_price=gas_price,
        status=status,
        reason=reason,
        method=tagged_tx["method"],
        actions=indented_actions,
    )

    for acc in tagged_tx["balance_change"]:
        render += "\n"
        render += "Account: " + fmt_addr(acc["address"], truncate=False)
        render += "\n"
        table_data = []
        for asset in acc["assets"]:
            table_data.append(
                [
                    fmt_addr(asset["asset"], truncate=False),
                    asset["balance_change"],
                ]
            )

        render += tabulate(table_data, headers=["Asset", "Balance Change"], tablefmt="grid")
        render += "\n"

    indented_render = indent(render, "  ")  # Indent entire tmpl by 2 spaces
    print(indented_render)


if __name__ == "__main__":
    cli()
