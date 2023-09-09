import json
import os

from decodex.decode import eth_decode_input
from decodex.decode import eth_decode_log


class TestEthDecode:
    with open(os.path.join("tests", "abi", "seaport", "function", "matchAdvancedOrders.json")) as F:
        abi_matchAdvancedOrders = json.load(F)

    with open(os.path.join("tests", "abi", "seaport", "event", "orderFulfilled.json")) as F:
        abi_orderFulfilled = json.load(F)

    def test_eth_decode_input_matchAdvancedOrders(self):
        input_data = "0x55944a4200000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000a400000000000000000000000000000000000000000000000000000000000000cc00000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000005e000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000900000000000000000000000000000000000000000000000000000000000005200000000000000000000000000000000000000000000000000000000000000580000000000000000000000000625bd97f041d481ade1c384b5580a97fc164955c000000000000000000000000004c00500000ad104d7dbd00e3ae0a5c00560c0000000000000000000000000000000000000000000000000000000000000001600000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000640013000000000000000000000000000000000000000000000000000000000064094d530000000000000000000000000000000000000000000000000000000000000000360c6ebe0000000000000000000000000000000000000000bf1740fff91324a70000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000631ee6f53bc00000000000000000000000000000000000000000000000000000631ee6f53bc00000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004000000000000000000000000a96b8bce15de1cd8abe539fefd2d87b5109f9eb85df9890d5ac24f728cda271f41ba0b113cff6b35ab22271cde0e6218ea632cbc00000000000000000000000000000000000000000000000000000000000000090000000000000000000000000000000000000000000000000000000000000009000000000000000000000000625bd97f041d481ade1c384b5580a97fc164955c0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007edfdff2380000000000000000000000000000000000000000000000000000007edfdff238000000000000000000000000000000a26b00c1f0df003000390027140000faa7190000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007edfdff2380000000000000000000000000000000000000000000000000000007edfdff2380000000000000000000000000053ec4ad6515cf55ace32c012332ecc87309cc17e0000000000000000000000000000000000000000000000000000000000000040a90a019ed784b5a433c068d3881e3ed570b4775832b0382c03e965e4423b8d545e1c7db5205538e4b896df8de01d611ecf342a3a1fa163604d35fdf912917fc2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003a000000000000000000000000000000000000000000000000000000000000003c00000000000000000000000006bbf15ec4120bb502526f7c311e4d469faf4ac6a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001600000000000000000000000000000000000000000000000000000000000000220000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000640013000000000000000000000000000000000000000000000000000000000064094d530000000000000000000000000000000000000000000000000000000000000000360c6ebe0000000000000000000000000000000000000000e2f249f2c79db9410000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000a96b8bce15de1cd8abe539fefd2d87b5109f9eb800000000000000000000000000000000000000000000000000000000000002e90000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ae73d3ed0d000000000000000000000000000000000000000000000000000000ae73d3ed0d0000000000000000000000000006bbf15ec4120bb502526f7c311e4d469faf4ac6a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e900000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000c9ce549e02107a39b1873d42d892c7c2a95f7285d2a02b7f3b504ff4bd3da0ece5edec2cbb46f1f9c19e60fbdeae153fe6030a3cdf58368976a0aacfca758a3452c4be1b679e63d2ff64ebe6fed007bdea8a629174d1ab3a4908f5486efaae865a28b35c869d3acb62713939e65cbabfb8a5d1f8980ae49bf416cb939c933fde61f5675cad8dce435ef8d2e831f18ee59b278a2be8c21f10f696e229713cafe4802599247abc6dd39b7087064ff8af3709a8e9500b95828d3649fdcf3a900966cc2882f6c065059731b8058f737e0e53c010090cfe43ed4ebe4eb2878d3d1c67dcc37128d5210efe122d4e49f8814a0b1304311c2035dc74e8e610e056f6f61f3d2fbbd41f2acdcb1a10da20196be090c9a881b3679a5f10db05c4d6e0d4ff89c2bc736295f05b1408d710a636d500a6e6c32e99cab112bbadec88ea3bd945795177aec754a2d5e29b29a0b40e2695c42cd99ddf9fb4906aa5aa3f7e307d4cda437e844c5d1b7931ecb8a902742bdae4878a705bb709fa1b6a12fd71da37b5ca700000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000002800000000000000000000000000000000000000000000000000000000000000380000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000360c6ebe"
        text_sig, params = eth_decode_input(self.abi_matchAdvancedOrders, input_data)
        expect_text_sig = "matchAdvancedOrders(((address,address,(uint8,address,uint256,uint256,uint256)[],(uint8,address,uint256,uint256,uint256,address)[],uint8,uint256,uint256,bytes32,uint256,bytes32,uint256),uint120,uint120,bytes,bytes)[],(uint256,uint8,uint256,uint256,bytes32[])[],((uint256,uint256)[],(uint256,uint256)[])[])"
        expect_params = {
            "advancedOrders": [
                {
                    "parameters": {
                        "offerer": "0x625bd97f041d481ade1c384b5580a97fc164955c",
                        "zone": "0x004c00500000ad104d7dbd00e3ae0a5c00560c00",
                        "offer": [
                            {
                                "itemType": 1,
                                "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                                "identifierOrCriteria": 0,
                                "startAmount": 27900000000000000,
                                "endAmount": 27900000000000000,
                            }
                        ],
                        "consideration": [
                            {
                                "itemType": 4,
                                "token": "0xa96b8bce15de1cd8abe539fefd2d87b5109f9eb8",
                                "identifierOrCriteria": 42505985736660449685331588358365252158395681542939889013924093403254516559036,
                                "startAmount": 9,
                                "endAmount": 9,
                                "recipient": "0x625bd97f041d481ade1c384b5580a97fc164955c",
                            },
                            {
                                "itemType": 1,
                                "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                                "identifierOrCriteria": 0,
                                "startAmount": 139500000000000,
                                "endAmount": 139500000000000,
                                "recipient": "0x0000a26b00c1f0df003000390027140000faa719",
                            },
                            {
                                "itemType": 1,
                                "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                                "identifierOrCriteria": 0,
                                "startAmount": 139500000000000,
                                "endAmount": 139500000000000,
                                "recipient": "0x53ec4ad6515cf55ace32c012332ecc87309cc17e",
                            },
                        ],
                        "orderType": 3,
                        "startTime": 1677726464,
                        "endTime": 1678331219,
                        "zoneHash": "0000000000000000000000000000000000000000000000000000000000000000",
                        "salt": 24446860302761739304752683030156737591518664810215442929814152234289100694695,
                        "conduitKey": "0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000",
                        "totalOriginalConsiderationItems": 3,
                    },
                    "numerator": 1,
                    "denominator": 9,
                    "signature": "a90a019ed784b5a433c068d3881e3ed570b4775832b0382c03e965e4423b8d545e1c7db5205538e4b896df8de01d611ecf342a3a1fa163604d35fdf912917fc2",
                    "extraData": "",
                },
                {
                    "parameters": {
                        "offerer": "0x6bbf15ec4120bb502526f7c311e4d469faf4ac6a",
                        "zone": "0x0000000000000000000000000000000000000000",
                        "offer": [
                            {
                                "itemType": 2,
                                "token": "0xa96b8bce15de1cd8abe539fefd2d87b5109f9eb8",
                                "identifierOrCriteria": 745,
                                "startAmount": 1,
                                "endAmount": 1,
                            }
                        ],
                        "consideration": [
                            {
                                "itemType": 1,
                                "token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                                "identifierOrCriteria": 0,
                                "startAmount": 3069000000000000,
                                "endAmount": 3069000000000000,
                                "recipient": "0x6bbf15ec4120bb502526f7c311e4d469faf4ac6a",
                            }
                        ],
                        "orderType": 1,
                        "startTime": 1677726464,
                        "endTime": 1678331219,
                        "zoneHash": "0000000000000000000000000000000000000000000000000000000000000000",
                        "salt": 24446860302761739304752683030156737591518664810215442929816735902939268102465,
                        "conduitKey": "0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000",
                        "totalOriginalConsiderationItems": 1,
                    },
                    "numerator": 1,
                    "denominator": 1,
                    "signature": "",
                    "extraData": "",
                },
            ],
            "criteriaResolvers": [
                {
                    "orderIndex": 0,
                    "side": 1,
                    "index": 0,
                    "identifier": 745,
                    "criteriaProof": [
                        "9ce549e02107a39b1873d42d892c7c2a95f7285d2a02b7f3b504ff4bd3da0ece",
                        "5edec2cbb46f1f9c19e60fbdeae153fe6030a3cdf58368976a0aacfca758a345",
                        "2c4be1b679e63d2ff64ebe6fed007bdea8a629174d1ab3a4908f5486efaae865",
                        "a28b35c869d3acb62713939e65cbabfb8a5d1f8980ae49bf416cb939c933fde6",
                        "1f5675cad8dce435ef8d2e831f18ee59b278a2be8c21f10f696e229713cafe48",
                        "02599247abc6dd39b7087064ff8af3709a8e9500b95828d3649fdcf3a900966c",
                        "c2882f6c065059731b8058f737e0e53c010090cfe43ed4ebe4eb2878d3d1c67d",
                        "cc37128d5210efe122d4e49f8814a0b1304311c2035dc74e8e610e056f6f61f3",
                        "d2fbbd41f2acdcb1a10da20196be090c9a881b3679a5f10db05c4d6e0d4ff89c",
                        "2bc736295f05b1408d710a636d500a6e6c32e99cab112bbadec88ea3bd945795",
                        "177aec754a2d5e29b29a0b40e2695c42cd99ddf9fb4906aa5aa3f7e307d4cda4",
                        "37e844c5d1b7931ecb8a902742bdae4878a705bb709fa1b6a12fd71da37b5ca7",
                    ],
                }
            ],
            "fulfillments": [
                {
                    "offerComponents": [{"orderIndex": 1, "itemIndex": 0}],
                    "considerationComponents": [{"orderIndex": 0, "itemIndex": 0}],
                },
                {
                    "offerComponents": [{"orderIndex": 0, "itemIndex": 0}],
                    "considerationComponents": [{"orderIndex": 0, "itemIndex": 1}],
                },
                {
                    "offerComponents": [{"orderIndex": 0, "itemIndex": 0}],
                    "considerationComponents": [{"orderIndex": 0, "itemIndex": 2}],
                },
                {
                    "offerComponents": [{"orderIndex": 0, "itemIndex": 0}],
                    "considerationComponents": [{"orderIndex": 1, "itemIndex": 0}],
                },
            ],
        }
        assert text_sig == expect_text_sig
        assert params == expect_params

    def test_eth_decode_log_orderFulfilled(self):
        # https://etherscan.io/tx/0x8605571efe3144b47b6157a3d50c20d8fef99b901c466dc65b8f32e6430769ee#eventlog
        topics = [
            "0x9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31",
            "0x0000000000000000000000004b2c444ba3a88d26825ccc310ab54ad679dc1949",
            "0x0000000000000000000000000000000000000000000000000000000000000092",
        ]
        data = "0xb36a7b9f3130afcd380c609708ffc0cd2847358ae16c9018feeebf2c844fec43000000000000000000000000864e3af0d1a532bb92e6da167f67d2bd033af00f00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000003d049adb773faddef681fbe565466c4f9736a0090000000000000000000000000000000000000000000000000000000000000d6a00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012901c1cf3900000000000000000000000000004b2c444ba3a88d26825ccc310ab54ad679dc19490000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007d0e36a8180000000000000000000000000008ca8a587710ceda4232ac33d9da8b7421ffc90be0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007d0e36a8180000000000000000000000000001bad6364b01013ff20193bf6562db1247fe342ed"
        text_sig, params = eth_decode_log(self.abi_orderFulfilled, topics, data)
        expected_text_sig = "OrderFulfilled(bytes32,address,address,address,(uint8,address,uint256,uint256)[],(uint8,address,uint256,uint256,address)[])"
        assert text_sig == expected_text_sig
        assert params == {
            "offerer": "0x4b2c444ba3a88d26825ccc310ab54ad679dc1949",
            "__idx_1": "0x4b2c444ba3a88d26825ccc310ab54ad679dc1949",
            "zone": "0x0000000000000000000000000000000000000092",
            "__idx_2": "0x0000000000000000000000000000000000000092",
            "orderHash": "b36a7b9f3130afcd380c609708ffc0cd2847358ae16c9018feeebf2c844fec43",
            "__idx_0": "b36a7b9f3130afcd380c609708ffc0cd2847358ae16c9018feeebf2c844fec43",
            "recipient": "0x864e3af0d1a532bb92e6da167f67d2bd033af00f",
            "__idx_3": "0x864e3af0d1a532bb92e6da167f67d2bd033af00f",
            "offer": [
                {"itemType": 2, "token": "0x3d049adb773faddef681fbe565466c4f9736a009", "identifier": 3434, "amount": 1}
            ],
            "__idx_4": [
                {"itemType": 2, "token": "0x3d049adb773faddef681fbe565466c4f9736a009", "identifier": 3434, "amount": 1}
            ],
            "consideration": [
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 83600000000000000,
                    "recipient": "0x4b2c444ba3a88d26825ccc310ab54ad679dc1949",
                },
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 2200000000000000,
                    "recipient": "0x8ca8a587710ceda4232ac33d9da8b7421ffc90be",
                },
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 2200000000000000,
                    "recipient": "0x1bad6364b01013ff20193bf6562db1247fe342ed",
                },
            ],
            "__idx_5": [
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 83600000000000000,
                    "recipient": "0x4b2c444ba3a88d26825ccc310ab54ad679dc1949",
                },
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 2200000000000000,
                    "recipient": "0x8ca8a587710ceda4232ac33d9da8b7421ffc90be",
                },
                {
                    "itemType": 0,
                    "token": "0x0000000000000000000000000000000000000000",
                    "identifier": 0,
                    "amount": 2200000000000000,
                    "recipient": "0x1bad6364b01013ff20193bf6562db1247fe342ed",
                },
            ],
        }