# Decodex

The python decoder for DeFi actions, similar to transaction action on Etherscan.

## Installation

```bash
pip3 install decodex
```

## CLI Usage

Explain a transaction by the txhash

```bash
# Export the uri of the web3 provider
export WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/<projectID>

# Download tag and signature files (runs for the first time)
decodex download ethereum

# Explain a transaction
decodex explain 0x2c744e19638b8dd14dafd03552a390f750e65dc7b0646585cf0ea40ef7a98743
```

The output should be like this :

```bash
  Transaction: 0x2c744e19638b8dd14dafd03552a390f750e65dc7b0646585cf0ea40ef7a98743
  Blocktime: 2023-08-26 10:29:47 UTC
  From: 0x7F65...5446
  To: 0xE592...1564
  Value: 0.8088 Ether
  GasUsed: 0.00019449
  Gas Price: 14.034892345 Gwei
  Status: Success
  Actions:
      - Swap 0.8088 Wrapped Ether [wrapped-token] for 1333.428458 Tether USD (USDT) [bitfinex, stablecoin] on 0x11b8...97F6
      - Swap 1333.428458 Tether USD (USDT) [bitfinex, stablecoin] for 0.8079914030453189 Wrapped Ether [wrapped-token] on 0x11b8...97F6
```

## Python Usage

Document coming soon

## Cite this tool

If you use Decodex in your research or project, please cite it using the following BibTeX entry:

```bibtex
@misc{decodex,
  title = {Decodex: The Python Decoder for DeFi Actions},
  author = {{Yu Lun Hsu}},
  email = {alan890104@gmail.com},
  year = {2023},
  howpublished = {\url{https://github.com/Solratic/decodex}},
}
```
