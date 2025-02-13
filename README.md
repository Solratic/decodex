# Decodex - Decoder for Dex

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
```

### Example 1 : Explain an existing transaction

```
decodex explain --txhash 0x2c744e19638b8dd14dafd03552a390f750e65dc7b0646585cf0ea40ef7a98743
```

The output should be like this :

```bash
  Transaction: 0x2c744e19638b8dd14dafd03552a390f750e65dc7b0646585cf0ea40ef7a98743
  Blocktime: 2023-08-26 10:29:47 UTC
  From: 0x7F65...5446
  To: Uniswap V3: Router [dex]
  Value: 0.8088 Ether
  GasUsed: 194490
  Gas Price: 14.034892345 Gwei
  Status: Success
  Method: multicall(data=...)
  Actions
  ------
      - Swap 0.8088 Wrapped Ether [wrapped-token] for 1333.428458 Tether USD (USDT) [bitfinex, stablecoin] on 0x11b8...97F6
      - Swap 1333.428458 Tether USD (USDT) [bitfinex, stablecoin] for 0.8079914030453189 Wrapped Ether [wrapped-token] on 0x11b8...97F6

  Account: 0xe592427a0aece92de3edee1f18e0157c05861564 (Uniswap V3: Router) [dex]
  +----------------------------------------------------------------------------+------------------+
  | Asset                                                                      |   Balance Change |
  +============================================================================+==================+
  | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 (Wrapped Ether) [wrapped-token] |     -0.000808597 |
  +----------------------------------------------------------------------------+------------------+

  Account: 0x11b815efb8f581194ae79006d24e0d814b7697f6
  +----------------------------------------------------------------------------+------------------+
  | Asset                                                                      |   Balance Change |
  +============================================================================+==================+
  | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 (Wrapped Ether) [wrapped-token] |      0.000808597 |
  +----------------------------------------------------------------------------+------------------+

  Account: 0x7f65394e8208cd9ef2d411443bd99c57e3e75446
  +-----------------------------------------------------------------------------------------------------+------------------+
  | Asset                                                                                               |   Balance Change |
  +=====================================================================================================+==================+
  | 0x0000000000000000000000000000000000000000 (Platform Token (ETH Transfer)) [blocked, burn, genesis] |      -0.8088     |
  +-----------------------------------------------------------------------------------------------------+------------------+
  | 0xffffffffffffffffffffffffffffffffffffffff (Platform Token (Gas Fee)) [burn]                        |      -0.00272965 |
  +-----------------------------------------------------------------------------------------------------+------------------+
```

### Explain 2 : Swap Exact ETH For Tokens

```bash
decodex explain --txhash 0x24f2ec956281a73be103e4d38c995890114addb6a24608b1b55b3cc329a3b931
```

### Example 3 : Explain a reverted transaction

```bash
decodex explain --txhash 0x5f7468feaeb1cf37291c1176612bb4cd1e991ca321ece5736d9b89f9531b87b5
```

The output would be

```bash
  Transaction: 0x5f7468feaeb1cf37291c1176612bb4cd1e991ca321ece5736d9b89f9531b87b5
  Blocktime: 2023-06-20 16:21:59 UTC
  From: 0x6E8A...4DC0
  To: Uniswap V2: Router 2 [dex]
  Value: 0.23 Ether
  GasUsed: 31441
  Gas Price: 21.949839607 Gwei
  Status: Failed (execution reverted: UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT)
  Method: swapExactETHForTokens(amountOutMin=247897935450030016036864, path=('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', '0x1a3496c18d558bd9c6c8f609e1b129f67ab08163'), to=0x848f0f7c377644aa928cd89b7fec7c88ada7d90d, deadline=1687279010)
```

### Example 4 : Complex transaction on Seaport 1.1

```bash
decodex explain --txhash 0x8605571efe3144b47b6157a3d50c20d8fef99b901c466dc65b8f32e6430769ee
```

### Example 5 : Contract Creation

```bash
decodex explain --txhash 0xc0fcba2048a90f7430b3c78ce99110b7e24e6abf782df362e91bf8cb4643d215
```

### Example 5 : Explain a transaction by simulate on certain block

```bash
decodex explain --from-addr 0xE466B36058406cC1C8e3671919CB773901CFcE7A --to-addr 0x9B0b12b7a8BE25fe24D327a088840B5F514238D2 --value 0 --block 17954301 --input-data 0xe19c22530000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000001c0000000000000000000000000000000000000000000000000000000000000026000000000000000000000000000000000000000000000000000000000000000040000000000000000000000001ed641e2d1b815ac247dbb11507655d34a3aec49000000000000000000000000ede6bbd0fea926eab3010e23c67f60cf388894f6000000000000000000000000648bb1473ab0ede8f8995e0c3cbc958d4e214a40000000000000000000000000648bb1473ab0ede8f8995e0c3cbc958d4e214a400000000000000000000000000000000000000000000000000000000000000004000000000000000000000000933c24e7bf21a084ea8efe287472662ecaa6b0f1000000000000000000000000ed77fc707c34df41ae5f752c3eb7916602463c2d000000000000000000000000f1a03c930ce7f522304f986c1102448deabed73c00000000000000000000000098cf8ad9e190893d1fff37b6f8597985cc7892630000000000000000000000000000000000000000000000000000000000000004000000000000000000000000f723566a7c7687ea3a88705652e3bf4025f3610f0000000000000000000000000d1d52f7798c2b7d43ce2cb2454d8adca4f85567000000000000000000000000598119468dce79ba9c29a5a33d4b8ee529ac0b86000000000000000000000000703c30302c058abe5c175b1ec5ae59b80147a85a00000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000059682f0000000000000000000000000000000000000000000000006c6b935b8bbd40000000000000000000000000000000000000000000000000000000000000077359400000000000000000000000000000000000000000000000000000000011e1a300
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
