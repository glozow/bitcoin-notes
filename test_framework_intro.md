# Functional Test Framework

WIP Personal notes on the functional tests in bitcoin core... not guaranteed to be up-to-date

TODO: add links in places where I'm referencing the code

## Basics - Data Structures

### TestNodes
TestNode represents a bitcoind node for use in functional tests. It uses whatever you have compiled as `bitcoind`
(don't forget to `make` before expecting changes to be reflected in functional tests).
For the most part, you will likely spin up a TestNode and use its interfaces (i.e. RPC) to verify behavior of nodes.
If you want more fine-grained control over what your node is doing (e.g. you want it to ignore messages or have
some specific malicious behavior), you want to use a mininode. 

### Mininodes or P2PConnections
Mininodes refer to simplistic peers (we don't want to call them "nodes" because they aren't created from bitcoind and
don't implement the vast majority of node logic) that implement the bare minimum P2P interface to interact with each other and with TestNodes. 
Typically, you want to use a mininode if you need it to interact with a bitcoind node in a particular way;
then, you test that the node behaves accordingly.
The most basic P2PConnection can initiate connections with TestNodes, send P2P messages, and respond to P2P messages.
We also ahve P2PInterface, which a tiny bit more sophisticated - it sends `pong`s in response to `ping`s, sends `getdata` in response to `inv`s, etc.
You probably want to extend this interface for all your basic needs.

TODO: update to p2p, explain why

### BitcoinTestFramework

The BitcoinTestFramework class is a base class for all functional tests.
It sets up a chain for you in -regtest mode (which mostly means that you can speed things up and not wait 10 minutes for a block).
It will also spin up any number of TestNodes (from your compiled bitcoind) for you, and you can configure them using the same command-line args you normally would.

TODO: more explanation on the setup and config options

You can customize the setup to fund a few nodes, have some blocks mined, start with the network partitioned, etc.
By default, everyone starts out with some money (i.e. mined some blocks) and is connected to one another.
Most importantly, every instance of BitcoinTestFramework has a `run_test` method. 
The base class' `run_test` method is empty, obviously, and you must override it with your test logic.
At the end, it will handle teardown for you.

## Common Things You Want To Do

Easy way to do things that you usually want to do in a functional test.

### Send money.

Easiest way is through the wallet RPC `sendtoaddress` (just make sure you have an address):

```py
address = node.getnewaddress()
txid = node.sendtoaddress(address, 0.1)
```

If you started with a clean chain or you got an "insufficient funds error": you need to mine blocks.
```py
self.nodes[0].generate(100)
```
This funds node0's wallet with outputs from the coinbase transactions.
You need 100 because coinbase transactions require 100 confirmations before they can be spent

### Test responses to P2P Messages

Connect some mininodes and use them to send messages.

```py
from test_framework.messages import msg_* # Whichever messages you need
peer = P2PInterface() # P2PConnection would work too, but doesn't have send_and_ping
node.add_p2p_connection(peer)
msg = custom_message()
peer.send_with_ping(msg)

assert_expected_behavior() # Whatever behavior you're expecting
```

### Create Transactions 
TODO

### Create Blocks
TODO

### Make Malformed Messages
TODO

### Speed Things Up (setmocktime, mockforward)
TODO

## Synchronization

TLDR:
- Don't expect things to happen in order inside your test logic.
- Grab the `mininode_lock`.
- Use `wait_until` instead of `assert` when you expect things to happen.
- Use `sync_with_ping` to sync a single connection, especially when you don't expect anything to happen, but want to make sure it's not because it didn't happen _yet_.

### General Idea

We have a lot of independent threads in a given functional test: TestNodes, mininodes, and the test logic itself that are not guaranteed to execute in the order we expect.

For example, here we're having the node use the `sendtoaddress` RPC to create and broadcast a transaction:

```py
peer_conn = P2PInterface() # It keeps a dictionary of last messages received in last_message
node.add_p2p_connection(peer_conn)
txid = node.sendtoaddress(self.nodes[0].getnewaddress(), 10)
assert peer_conn.last_message['tx].tx.rehash() == txid
```

What's the problem with this?
It might take some time for the node to announce this transaction (`inv`), for the mininode to request it (`getdata`), the node to send it (`tx`), and the mininode to store it in its `last_message` data structure.
There's no guarantee that it will happen before we execute the assert statement.

### Wait Until and Wait Fors

The obvious solution for synchronization is to wait for everyone to finish before continuing.
You might notice a lot of wonderful `wait_until` and `wait_for*` functions sitting in the Test Framework.
How convenient! Note that they may not quite be thread safe and you'll usually need
to pass in a lock (see the `mininode_lock` section).

The `wait_for*` functions are abundant in the mininodes, and are often the bread and butter when testing expected behavior in functional tests.
They include `wait_for_tx`, which allows you to ensure that a mininode receives a transaction (by tx hash), `wait_for_disconnect`, which allows you to verify that your node is correctly punishing bad behavior from its peers, and many more!

The `wait_until`s are even cooler: they allow you to make your test wait for an arbitrary predicate to evaluate to true.
You'll use these all the time when writing functional tests too, since they're so versatile, but you need to make sure you're syncrhonizing properly.


### Test Framework Sync* Functions

The `TestFramework` class has a few syncing functions:

-`sync_blocks` waits for all nodes to have the same tip.

-`sync_mempools` waits for all nodese to have the same transactions in their mempools.

-`sync_all` does both.

The caveat here is that, in many situations, we don't expect all nodes to be on the same page.
We might be testing a situation in which nodes are disconnected,
or configured our nodes to do things differently. 
Regardless, these are useful functions especially if you want to sync blocks (obviously); a good place to use them is between subtests within your functional test to get everyone on the same page before proceeding.

### Mininode Synchronization with Pings

Maybe you just want to make sure two peers in a connection (and not the whole network) are on the same page.

The simplest thing to do is: always use `send_and_ping(message)` when sending a message; it's the best way to make sure the node receives and processes the message.

The `sync_with_ping` is a mininode function and a really cheap way to do this.
Here's how it works: the mininode message sends a `ping` message to the node, and then waits to receive a `pong` before continuing.
It's based on: (1) nodes always respond to `ping`s with `pong`s and (2) nodes process their messages from a single peer in the order they received them.
In other words: if you've gotten your pong back, you know for a fact that all your other messages have been processed.

This is extremely useful after sending a request (sync to make sure they respond to it). 
But it's even more useful for synchronization when you _don't_ expect things to happen.
For instance, if you're testing transaction filters (i.e. node does _not_ send a peer a transaction if it doesn't meet the filter they've agreed upon):

```py
stingy_peer = P2PInterface()
node.add_p2p_connection(stingy_peer)
stingy_peer.send_fee_filter(...) # the peer sets up a filter
node.send_cheap_transaction() # this transaction doesn't pass stingy_peer's filter
???
aassert txid != stingy_peer.last_message['tx].tx.rehash()
```
What do we put in the (???) section?
We shouldn't leave it empty. 
That would leave room for the test succeeding simply because we executed the assertion too early, and the transaction _was_ sent to the peer a little bit later.
It can't be a `wait_until(?)` because we don't expect anything to happen.
You might be tempted to add a `sleep(5)` because you definitely expect transaction relay to be faster than 5 seconds.
But that doesn't solve the race condition.

Instead, we can do something like:
```py
stingy_peer = P2PInterface()
node.add_p2p_connection(stingy_peer)
stingy_peer.send_fee_filter(...) # the peer sets up a filter
node.send_cheap_transaction() # this transaction doesn't pass stingy_peer's filter
stingy_peer.sync_with_ping() # If node were to send an inv, it would happen here
stingy_peer.sync_with_ping() # If peer sent a getdata in response to the imaginary inv, it would receive apong after the tx
assert txid != stingy_peer.last_message['tx].tx.rehash()
```
This isn't the only way to do it, and it doesn't change the behavior of your tests, but eliminating race conditions necessary to make sure your results are correct.

### Mininode Lock

The mininode.py file has a tiny little line hidden in the middle:

```py
mininode_lock = threading.Lock()
```

The `mininode_lock` is a mutex.
This lock synchronizes all data accesses between the mininodes and your test logic.
More specifically, as long as you have the `mininode_lock`, you can rest assured that you are thread-safely accessing the data structures in _all_ your mininodes.
Conversely, if you don't have the `mininode_lock`, you are exposing yourself to data races galore.


This is most relevant when you're creating your own mininode as a subclass of `P2PInterface`, maybe something that collects information about the p2p messages it receives.
You need to make sure that your data accesses are thread-safe.

For example, the P2PTxInvStore is a mininode that keeps track of the transaction invs it receives.
Here's `on_inv` and `get_invs` for reference; particularly notice how we grab the mininode lock in `get_invs`:

```py
def on_inv(self, message):
    super().on_inv(message) # Send getdata in response.
    # Store how many times invs have been received for each tx.
    for i in message.inv:
        if (i.type == MSG_TX) or (i.type == MSG_WTX):
            # save txid
            self.tx_invs_received[i.hash] += 1

def get_invs(self):
    with mininode_lock:
        return list(self.tx_invs_received.keys())
```

Why not just access `peer.tx_invs_received` in the test logic directly?
Because we might encounter a race condition in accessing `tx_invs_received`: if we don't grab the mininode_lock, we might be trying to access the it at the same time the mininode itself is writing to it. Then, our test reslut (asserting we did/didn't receive a tx inv) would depend on whether the test logic thread or the mininode thread gets scheduled first.
