# LN Test Vectors

From BOLT3 [Appendix](https://github.com/lightningnetwork/lightning-rfc/blob/master/03-transactions.md#appendix-c-commitment-and-htlc-transaction-test-vectors)

Generate to local_funding_pubkey and remote_funding_pubkey

## Setup

Generate to local_funding_pubkey and remote_funding_pubkey:

    
    local_funding_pubkey: 023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb
    remote_funding_pubkey: 030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c1

<details><summary>Other Info</summary>
<p>

    local_funding_privkey: 30ff4956bbdd3222d44cc5e8a1261dab1e07957bdac5ae88fe3261ef321f374901
    remote_funding_privkey: 1552dfba4f6cf29a62a0af13c8d6981d36d0ef8d61ba10fb0fe90da7634d7e1301

    funding witness script = 5221023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb21030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c152ae

    local_privkey: bb13b121cdc357cd2e608b0aea294afca36e2b34cf958e2e6451a2f27469449101
    localpubkey: 030d417a46946384f88d5f3337267c5e579765875dc4daca813e21734b140639e7

    remotepubkey: 0394854aa6eab5b2a8122cc726e9dded053a2184d88256816826d6231c068d4a5b

    local_delayedpubkey: 03fd5960528dc152014952efdb702a88f71e3c1653b2314431701ec77e57fde83c
    local_revocation_pubkey: 0212a140cd0c6539d07cd08dfe09984dec3251ea808b892efeac3ede9402bf2b19
</p>
</details>


## Funding Tx

Funding tx hex:

    0200000001adbb20ea41a8423ea937e76e8151636bf6093b70eaff942930d20576600521fd000000006b48304502210090587b6201e166ad6af0227d3036a9454223d49a1f11839c1a362184340ef0240220577f7cd5cca78719405cbf1de7414ac027f0239ef6e214c90fcaab0454d84b3b012103535b32d5eb0a6ed0982a0479bbadc9868d9836f6ba94dd5a63be16d875069184ffffffff028096980000000000220020c015c4a6be010e21657068fc2e6a9d02b27ebe4d490a25846f7237f104d1a3cd20256d29010000001600143ca33c2e4446f4a305f23c80df8ad1afdcf652f900000000

<details><summary>funding tx decoded</summary>
<p>

    {
        "txid": "8984484a580b825b9972d7adb15050b3ab624ccd731946b3eeddb92f4e7ef6be",
        "hash": "8984484a580b825b9972d7adb15050b3ab624ccd731946b3eeddb92f4e7ef6be",
        "version": 2,
        "size": 232,
        "vsize": 232,
        "weight": 928,
        "locktime": 0,
        "vin": [
            {
                "txid": "fd2105607605d2302994ffea703b09f66b6351816ee737a93e42a841ea20bbad",
                "vout": 0,
                "scriptSig": {
                    "asm": "304502210090587b6201e166ad6af0227d3036a9454223d49a1f11839c1a362184340ef0240220577f7cd5cca78719405cbf1de7414ac027f0239ef6e214c90fcaab0454d84b3b[ALL] 03535b32d5eb0a6ed0982a0479bbadc9868d9836f6ba94dd5a63be16d875069184",
                    "hex": "48304502210090587b6201e166ad6af0227d3036a9454223d49a1f11839c1a362184340ef0240220577f7cd5cca78719405cbf1de7414ac027f0239ef6e214c90fcaab0454d84b3b012103535b32d5eb0a6ed0982a0479bbadc9868d9836f6ba94dd5a63be16d875069184"
                },
                "sequence": 4294967295
            }
        ],
        "vout": [
            {
                "value": 0.1,
                "n": 0,
                "scriptPubKey": {
                    "asm": "0 c015c4a6be010e21657068fc2e6a9d02b27ebe4d490a25846f7237f104d1a3cd",
                    "hex": "0020c015c4a6be010e21657068fc2e6a9d02b27ebe4d490a25846f7237f104d1a3cd",
                    "reqSigs": 1,
                    "type": "witness_v0_scripthash",
                    "addresses": [
                        "bc1qcq2uff47qy8zzetsdr7zu65aq2e8a0jdfy9ztpr0wgmlzpx350xssax7mx"
                    ]
                }
            },
            {
                "value": 49.8998608,
                "n": 1,
                "scriptPubKey": {
                    "asm": "0 3ca33c2e4446f4a305f23c80df8ad1afdcf652f9",
                    "hex": "00143ca33c2e4446f4a305f23c80df8ad1afdcf652f9",
                    "reqSigs": 1,
                    "type": "witness_v0_keyhash",
                    "addresses": [
                        "bc1q8j3nctjygm62xp0j8jqdlzk34lw0v5he6hfyhh"
                    ]
                }
            }
        ]
    }
    
</p>
</details>


## Commitment without HTLCs

hex:

    02000000000101bef67e4e2fb9ddeeb3461973cd4c62abb35050b1add772995b820b584a488489000000000038b02b8002c0c62d0000000000160014ccf1af2f2aabee14bb40fa3851ab2301de84311054a56a00000000002200204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e0400473044022051b75c73198c6deee1a875871c3961832909acd297c6b908d59e3319e5185a46022055c419379c5051a78d00dbbce11b5b664a0c22815fbcc6fcef6b1937c383693901483045022100f51d2e566a70ba740fc5d8c0f07b9b93d2ed741c3c0860c613173de7d39e7968022041376d520e9c0e1ad52248ddf4b22e12be8763007df977253ef45a4ca3bdb7c001475221023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb21030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c152ae3e195220


<details><summary>commitment (no HTLC) decoded</summary>
<p>

    {
        "txid": "bbd60778feb257051f2b65679a6ed4d2e1275d46a05dc4e69eb7d5ae001df947",
        "hash": "03169d59fe0d63c84c8ba82a124791ab37a0d5cd14685fab18f4ba29b757d7c2",
        "version": 2,
        "size": 346,
        "vsize": 181,
        "weight": 721,
        "locktime": 542251326,
        "vin": [
            {
                "txid": "8984484a580b825b9972d7adb15050b3ab624ccd731946b3eeddb92f4e7ef6be",
                "vout": 0,
                "scriptSig": {
                    "asm": "",
                    "hex": ""
                },
                "txinwitness": [
                    "",
                    "3044022051b75c73198c6deee1a875871c3961832909acd297c6b908d59e3319e5185a46022055c419379c5051a78d00dbbce11b5b664a0c22815fbcc6fcef6b1937c383693901",
                    "3045022100f51d2e566a70ba740fc5d8c0f07b9b93d2ed741c3c0860c613173de7d39e7968022041376d520e9c0e1ad52248ddf4b22e12be8763007df977253ef45a4ca3bdb7c001",
                    "2 023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb 030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c1 2 OP_CHECKMULTISIG"
                ],
                "sequence": 2150346808
            }
        ],
        "vout": [
            {
                "value": 0.03,
                "n": 0,
                "scriptPubKey": {
                    "asm": "0 ccf1af2f2aabee14bb40fa3851ab2301de843110",
                    "hex": "0014ccf1af2f2aabee14bb40fa3851ab2301de843110",
                    "reqSigs": 1,
                    "type": "witness_v0_keyhash",
                    "addresses": [
                        "bc1qenc67te240hpfw6qlgu9r2erq80ggvgsaqzysf"
                    ]
                }
            },
            {
                "value": 0.0698914,
                "n": 1,
                "scriptPubKey": {
                    "asm": "0 4adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
                    "hex": "00204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
                    "reqSigs": 1,
                    "type": "witness_v0_scripthash",
                    "addresses": [
                        "bc1qftd5utcqvs7m89kazgx5ulwpwcjltukprfqds4avejrz66mamq8qshjans"
                    ]
                }
            }
        ]
    }

</p>
</details>


## Commitment with 1 HTLC

From BOLT3 appendix, these are called commitment tx with three outputs untrimmed (minimum fee) + HTLC4:

commitment tx hex:

    02000000000101bef67e4e2fb9ddeeb3461973cd4c62abb35050b1add772995b820b584a488489000000000038b02b8003a00f0000000000002200208c48d15160397c9731df9bc3b236656efb6665fbfe92b4a6878e88a499f741c4c0c62d0000000000160014ccf1af2f2aabee14bb40fa3851ab2301de843110eb936a00000000002200204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e0400473044022047305531dd44391dce03ae20f8735005c615eb077a974edb0059ea1a311857d602202e0ed6972fbdd1e8cb542b06e0929bc41b2ddf236e04cb75edd56151f4197506014830450221008b7c191dd46893b67b628e618d2dc8e81169d38bade310181ab77d7c94c6675e02203b4dd131fd7c9deb299560983dcdc485545c98f989f7ae8180c28289f9e6bdb001475221023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb21030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c152ae3e195220

<details><summary>commitment decoded</summary>
<p>

    {
        "txid": "6d20ef35f1b05feeced43431bf4ba87e2204c93294f60dd160743dfba76a071c",
        "hash": "eaf1db4d60e456678007df6189e6e74e24139d528ce2b0e83c90e78e0a00eae0",
        "version": 2,
        "size": 389,
        "vsize": 224,
        "weight": 893,
        "locktime": 542251326,
        "vin": [
            {
                "txid": "8984484a580b825b9972d7adb15050b3ab624ccd731946b3eeddb92f4e7ef6be",
                "vout": 0,
                "scriptSig": {
                    "asm": "",
                    "hex": ""
                },
                "txinwitness": [
                    "",
                    "3044022047305531dd44391dce03ae20f8735005c615eb077a974edb0059ea1a311857d602202e0ed6972fbdd1e8cb542b06e0929bc41b2ddf236e04cb75edd56151f419750601",
                    "30450221008b7c191dd46893b67b628e618d2dc8e81169d38bade310181ab77d7c94c6675e02203b4dd131fd7c9deb299560983dcdc485545c98f989f7ae8180c28289f9e6bdb001",
                    "2 023da092f6980e58d2c037173180e9a465476026ee50f96695963e8efe436f54eb 030e9f7b623d2ccc7c9bd44d66d5ce21ce504c0acf6385a132cec6d3c39fa711c1 2 OP_CHECKMULTISIG"
                ],
                "sequence": 2150346808
            }
        ],
        "vout": [
            {
                "value": 0.00004,
                "n": 0,
                "scriptPubKey": {
                    "asm": "0 8c48d15160397c9731df9bc3b236656efb6665fbfe92b4a6878e88a499f741c4",
                    "hex": "00208c48d15160397c9731df9bc3b236656efb6665fbfe92b4a6878e88a499f741c4",
                    "reqSigs": 1,
                    "type": "witness_v0_scripthash",
                    "addresses": [
                        "bc1q33ydz5tq897fwvwln0pmydn9dmakve0ml6ftff5836y2fx0hg8zq3u2y54"
                    ]
                }
            },
            {
                "value": 0.03,
                "n": 1,
                "scriptPubKey": {
                    "asm": "0 ccf1af2f2aabee14bb40fa3851ab2301de843110",
                    "hex": "0014ccf1af2f2aabee14bb40fa3851ab2301de843110",
                    "reqSigs": 1,
                    "type": "witness_v0_keyhash",
                    "addresses": [
                        "bc1qenc67te240hpfw6qlgu9r2erq80ggvgsaqzysf"
                    ]
                }
            },
            {
                "value": 0.06984683,
                "n": 2,
                "scriptPubKey": {
                    "asm": "0 4adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
                    "hex": "00204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
                    "reqSigs": 1,
                    "type": "witness_v0_scripthash",
                    "addresses": [
                        "bc1qftd5utcqvs7m89kazgx5ulwpwcjltukprfqds4avejrz66mamq8qshjans"
                    ]
                }
            }
        ]
    }

</p>
</details>

output htlc_success_tx hex:

    020000000001011c076aa7fb3d7460d10df69432c904227ea84bbf3134d4ceee5fb0f135ef206d0000000000000000000175050000000000002200204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e0500473044022044f65cf833afdcb9d18795ca93f7230005777662539815b8a601eeb3e57129a902206a4bf3e53392affbba52640627defa8dc8af61c958c9e827b2798ab45828abdd01483045022100b94d931a811b32eeb885c28ddcf999ae1981893b21dd1329929543fe87ce793002206370107fdd151c5f2384f9ceb71b3107c69c74c8ed5a28a94a4ab2d27d3b0724012004040404040404040404040404040404040404040404040404040404040404048a76a91414011f7254d96b819c76986c277d115efce6f7b58763ac67210394854aa6eab5b2a8122cc726e9dded053a2184d88256816826d6231c068d4a5b7c8201208763a91418bc1a114ccf9c052d3d23e28d3b0a9d1227434288527c21030d417a46946384f88d5f3337267c5e579765875dc4daca813e21734b140639e752ae677502f801b175ac686800000000

<details><summary>htlc decoded</summary>
<p>   
    
    {
      "txid": "fd01ae006484dba328328a18dadbe046ffc264edea1cff02819999d20076d408",
      "hash": "131636fe546c0a057cfe9677491d698db475b5b7ea30bf486fd974cf81a1507e",
      "version": 2,
      "size": 415,
      "vsize": 175,
      "weight": 697,
      "locktime": 0,
      "vin": [
        {
          "txid": "6d20ef35f1b05feeced43431bf4ba87e2204c93294f60dd160743dfba76a071c",
          "vout": 0,
          "scriptSig": {
            "asm": "",
            "hex": ""
          },
          "txinwitness": [
            "",
            "3044022044f65cf833afdcb9d18795ca93f7230005777662539815b8a601eeb3e57129a902206a4bf3e53392affbba52640627defa8dc8af61c958c9e827b2798ab45828abdd01",
            "3045022100b94d931a811b32eeb885c28ddcf999ae1981893b21dd1329929543fe87ce793002206370107fdd151c5f2384f9ceb71b3107c69c74c8ed5a28a94a4ab2d27d3b072401",
            "0404040404040404040404040404040404040404040404040404040404040404",
            "OP_DUP OP_HASH160 14011f7254d96b819c76986c277d115efce6f7b5 OP_EQUAL OP_IF OP_CHECKSIG OP_ELSE 0394854aa6eab5b2a8122cc726e9dded053a2184d88256816826d6231c068d4a5b OP_SWAP OP_SIZE 32 OP_EQUAL OP_IF OP_HASH160 18bc1a114ccf9c052d3d23e28d3b0a9d12274342 OP_EQUALVERIFY 2 OP_SWAP 030d417a46946384f88d5f3337267c5e579765875dc4daca813e21734b140639e7 2 OP_CHECKMULTISIG OP_ELSE OP_DROP 504 OP_CHECKLOCKTIMEVERIFY OP_DROP OP_CHECKSIG OP_ENDIF OP_ENDIF"
          ],
          "sequence": 0
        }
      ],
      "vout": [
        {
          "value": 0.00001397,
          "n": 0,
          "scriptPubKey": {
            "asm": "0 4adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
            "hex": "00204adb4e2f00643db396dd120d4e7dc17625f5f2c11a40d857accc862d6b7dd80e",
            "reqSigs": 1,
            "type": "witness_v0_scripthash",
            "addresses": [
              "bc1qftd5utcqvs7m89kazgx5ulwpwcjltukprfqds4avejrz66mamq8qshjans"
            ]
          }
        }
      ]
    }
    
</p>
</details>
