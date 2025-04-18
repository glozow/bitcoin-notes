# Warnet testing 1p1c packages

## Install
Super easy, warnet/install.md.
### Make Network
pinheadmz was kind enough to push up a prebuilt image for v29.0rc2

1. Start docker
2. Use `warnet init` to create the network. I called it `29.0rc2-50` . Pick any version as the default since there's no option for v29.0rc2.
3. In the network.yaml change the image to `tag : 'v29.0-rc2` 
4. In the node-defaults.yaml change `metricsExport: true` so grafana works.
5. Use `warnet deploy networks/29.0rc2-50` 
6. Use `warnet status` to see all the nodes running
7. Use `warnet bitcoin rpc tank-0000 --version` to see that it's actually running v29.0rc2.
8. At this point you can open localhost/fork-observer and localhost/grafana/dashboards though nothing will be happening until you run a scenario

### Scenario

#### Miner_std
Can quickstart wallets with mature coinbases for everybody: warnet run `scenarios/miner_std.py --allnodes --mature`. This does a round every 60 seconds, so it'll take n minutes to fund each node.

I used the grafana dashboard to watch blocks being mined, and then stopped this with `warnet stop`.

#### TxPackage_flood

And then run this scenario (which either mines or makes 1p1c packages depending on whether the wallet has any utxos to spend):
```
warnet run scenarios/txpackage_flood.py
```

I found it helpful to print a lot of things from the scenario scripts and run `warnet logs -f` and follow the logs from the commanders.

```python
#!/usr/bin/env python3

import threading
from random import choice, randrange
from time import sleep
from decimal import Decimal

from commander import Commander


class TxPackageFlood(Commander):
    def set_test_params(self):
        self.num_nodes = 1
        self.addrs = []
        self.threads = []

    def add_options(self, parser):
        parser.description = (
            "Sends random transactions between all nodes with available balance in their wallet"
        )
        parser.usage = "warnet run /path/to/tx_flood.py [options]"
        parser.add_argument(
            "--interval",
            dest="interval",
            default=10,
            type=int,
            help="Number of seconds between TX generation (default 10 seconds)",
        )

    def edit_version(self, raw_tx):
        # Edit the first byte (which is the version field) to equal 3
        tx_bytes = bytearray.fromhex(raw_tx)
        tx_bytes[0] = 3
        return tx_bytes.hex()

    def orders(self, node):
        wallet = self.ensure_miner(node)
        for address_type in ["legacy", "p2sh-segwit", "bech32", "bech32m"]:
            addr = wallet.getnewaddress(address_type=address_type)
            self.addrs.append(addr)
        while True:
            sleep(self.options.interval)
            try:
                confirmed_utxos = node.listunspent(minconf=1)
                if len(confirmed_utxos) == 0:
                    continue
                utxo = confirmed_utxos[0]
                # Amount is identical: zero fees
                outputs = { node.getnewaddress() : utxo["amount"] }
                parent_raw_v2 = node.createrawtransaction([{ "txid" : utxo["txid"], "vout" : utxo["vout"]}], outputs)
                # TODO: change when createrawtransaction supports version param
                parent_raw_v3 = self.edit_version(parent_raw_v2)
                parent_signraw = node.signrawtransactionwithwallet(parent_raw_v3)
                assert parent_signraw["complete"]
                parent_json = node.decoderawtransaction(parent_signraw["hex"])
                assert parent_json["version"] == 3

                child_inputs = [{ "txid": parent_json["txid"], "vout" : 0 }]
                # large fee on child
                output_amount = utxo["amount"] - Decimal("0.0001")
                child_outputs = { node.getnewaddress() : output_amount }
                child_raw_v2 = node.createrawtransaction(child_inputs, child_outputs)
                child_raw_v3 = self.edit_version(child_raw_v2)
                child_inputs[0]["scriptPubKey"] = parent_json["vout"][0]["scriptPubKey"]["hex"]
                child_inputs[0]["amount"] = parent_json["vout"][0]["value"]
                child_signraw = node.signrawtransactionwithwallet(child_raw_v3, child_inputs)
                assert child_signraw["complete"]
                child_json = node.decoderawtransaction(child_signraw["hex"])
                assert child_json["version"] == 3

                # We now have full package; submit it.
                package_hex = [parent_signraw["hex"], child_signraw["hex"]]
                package_result = node.submitpackage(package_hex)
                assert package_result["package_msg"] == "success"

                self.log.info(f"node {node.index} sent 1p1c package {parent_json['txid']} + {child_json['txid']}")
            except Exception as e:
                self.log.error(f"node {node.index} error: {e}")

    def run_test(self):
        self.log.info(f"Starting Txpackage mess with {len(self.nodes)} threads")
        for node in self.nodes:
            sleep(1)  # stagger
            t = threading.Thread(target=lambda n=node: self.orders(n))
            t.daemon = False
            t.start()
            self.threads.append({"thread": t, "node": node})

        while len(self.threads) > 0:
            for thread in self.threads:
                if not thread["thread"].is_alive():
                    self.log.info(f"restarting thread for node {thread['node'].index}")
                    thread["thread"] = threading.Thread(
                        target=lambda n=thread["node"]: self.orders(n)
                    )
                    thread["thread"].daemon = False
                    thread["thread"].start()
            sleep(30)


def main():
    TxPackageFlood().main()


if __name__ == "__main__":
    main()

```
