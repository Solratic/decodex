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

## Python Usage

Document coming soon
