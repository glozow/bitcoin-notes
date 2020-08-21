#!/usr/bin/env python3
# Copyright (c) 2017-2019 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""An example functional test (taken from test/functional/example_test.py)

I've added a bunch of comments to explain things

The module-level docstring should include a high-level description of
what the test is doing. It's the first thing people see when they open
the file and should give the reader information about *what* the test
is testing and *how* it's being tested
"""
# Imports should be in PEP8 ordering (std library first, then third party
# libraries then local imports).
from collections import defaultdict

# Avoid wildcard * imports
from test_framework.blocktools import (create_block, create_coinbase)
from test_framework.messages import CInv, MSG_BLOCK
from test_framework.mininode import (
    P2PInterface,
    mininode_lock,
    msg_block,
    msg_getdata,
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    connect_nodes,
    wait_until,
)

# P2PInterface is a class containing callbacks to be executed when a P2P
# message is received from the node-under-test. Subclass P2PInterface and
# override the on_*() methods if you need custom behaviour.
class BaseNode(P2PInterface):
    def __init__(self):
        """Initialize the P2PInterface

        Used to initialize custom properties for the Node that aren't
        included by default in the base class. Be aware that the P2PInterface
        base class already stores a counter for each P2P message type and the
        last received message of each type, which should be sufficient for the
        needs of most tests.

        Call super().__init__() first for standard initialization and then
        initialize custom properties."""
        super().__init__()
        # Stores a dictionary of all blocks received
        self.block_receive_map = defaultdict(int)

    def on_block(self, message):
        """Override the standard on_block callback

        Store the hash of a received block in the dictionary."""
        message.block.calc_sha256()
        self.block_receive_map[message.block.sha256] += 1

    def on_inv(self, message):
        """Override the standard on_inv callback"""
        # note that in the run_test below, we'll have it send the invs manually
        pass

def custom_function():
    """Do some custom behaviour

    If this function is more generally useful for other tests, consider
    moving it to a module in test_framework."""
    # self.log.info("running custom_function")  # Oops! Can't run self.log outside the BitcoinTestFramework
    pass


class ExampleTest(BitcoinTestFramework):
    # Each functional test is a subclass of the BitcoinTestFramework class.

    # Override the set_test_params(), skip_test_if_missing_module(), add_options(), setup_chain(), setup_network()
    # and setup_nodes() methods to customize the test setup as required.

    def set_test_params(self):
        """Override test parameters for your individual test.

        This method must be overridden and num_nodes must be explicitly set."""
        # Clean chain means you start with just the genesis block.
        # Non-clean means you use 200 blocks pulled from a cache,
        # mined by your test nodes. This funds each of their wallets.
        # As you'd expect, if you start with a clean chain, none
        # of your nodes will have any money to make transactions with.
        # To fund a node's wallet, the easiest way is to have it generate
        # 100 blocks (coinbases need 100 confirmations to be spent)
        self.setup_clean_chain = True
        # These 3 nodes start out connected by default unless you
        # change it in setup_network.
        self.num_nodes = 3
        # Use self.extra_args to change command-line arguments for the nodes
        # You can find these options in src/init.cpp
        self.extra_args = [[], ["-logips"], []]

        # self.log.info("I've finished set_test_params")  # Oops! Can't run self.log before run_test()

    # Use skip_test_if_missing_module() to skip the test if your test requires certain modules to be present.
    # This test uses generate which requires wallet to be compiled
    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    # Use add_options() to add specific command-line options for your test.
    # In practice this is not used very much, since the tests are mostly written
    # to be run in automated environments without command-line options.
    # def add_options()
    #     pass

    # Use setup_chain() to customize the node data directories. In practice
    # this is not used very much since the default behaviour is almost always
    # fine
    # def setup_chain():
    #     pass

    def setup_network(self):
        """Setup the test network topology

        Often you won't need to override this, since the standard network topology
        (linear: node0 <-> node1 <-> node2 <-> ...) is fine for most tests.

        If you do override this method, remember to start the nodes, assign
        them to self.nodes, connect them and then sync."""

        self.setup_nodes()

        # In this test, we're not connecting node2 to node0 or node1. Calls to
        # sync_all() should not include node2, since we're not expecting it to
        # sync.
        connect_nodes(self.nodes[0], 1)
        self.sync_all(self.nodes[0:2])

    # Use setup_nodes() to customize the node start behaviour (for example if
    # you don't want to start all nodes at the start of the test).
    # def setup_nodes():
    #     pass

    def custom_method(self):
        """Do some custom behaviour for this test

        Define it in a method here because you're going to use it repeatedly.
        If you think it's useful in general, consider moving it to the base
        BitcoinTestFramework class so other tests can use it."""
        # It's really common to make subtests this way
        # It makes the run_test function cleaner

        self.log.info("Running custom_method")

    def run_test(self):
        """Main test logic"""

        # Create P2P connections will wait for a verack to make sure the connection is fully up
        # This does the version handshake nodes send version messages to negotiate whether or not they
        # want to talk to each other. If yes, they send verack.
        # Before the verack, they won't send anything else to each other.
        # add_p2p_connection has a wait_for_verack option - you can also toggle to false
        self.nodes[0].add_p2p_connection(BaseNode())

        # Generating a block on one of the nodes will get us out of IBD
        # IBD is initial block download. While nodes are in IBD, they don't
        # think they have the most up-to-date blockchain and are only
        # interested in downloading blocks from their peers.
        # generate() is an easy way to make blocks (can be found in blocktools)
        # there are other ways too!
        blocks = [int(self.nodes[0].generate(nblocks=1)[0], 16)]
        # Sync all means we sync blocks (everyone has same chain tip) and mempools.
        # If you try to sync while nodes aren't connected, it will time out.
        self.sync_all(self.nodes[0:2])

        # Notice above how we called an RPC by calling a method with the same
        # name on the node object. Notice also how we used a keyword argument
        # to specify a named RPC argument. Neither of those are defined on the
        # node object. Instead there's some __getattr__() magic going on under
        # the covers to dispatch unrecognised attribute calls to the RPC
        # interface.

        # Logs are nice. Do plenty of them. They can be used in place of comments for
        # breaking the test into sub-sections.
        self.log.info("Starting test!")

        self.log.info("Calling a custom function")
        custom_function()

        self.log.info("Calling a custom method")
        self.custom_method()

        self.log.info("Create some blocks")
        # getblockcount, getbestblockhash, and getblock are RPCs in src/rpc/blockchain.cpp
        # we need to convert to an int with base 16 (hex) to use later
        self.tip = int(self.nodes[0].getbestblockhash(), 16)
        self.block_time = self.nodes[0].getblock(self.nodes[0].getbestblockhash())['time'] + 1

        height = self.nodes[0].getblockcount()

        for _ in range(10):
            # Use the mininode and blocktools functionality to manually build a block
            # Calling the generate() rpc is easier, but this allows us to exactly
            # control the blocks and transactions.
            # you can create_coinbase() without a funded wallet because they don't require any inputs
            block = create_block(self.tip, create_coinbase(height+1), self.block_time)
            # we can do this instantaneously (no actual PoW) because we are in regtest mode
            block.solve()
            # a msg_block is a p2p message that contains an entire block, serialized
            block_message = msg_block(block)
            # Send message is used to send a P2P message to the node over our P2PInterface
            # p2p in this case is the BaseNode, not the TestNode peers that node0 is connected to
            self.nodes[0].p2p.send_message(block_message)
            self.tip = block.sha256
            blocks.append(self.tip)
            self.block_time += 1
            height += 1

        self.log.info("Wait for node1 to reach current tip (height 11) using RPC")
        self.nodes[1].waitforblockheight(11)

        self.log.info("Connect node2 and node1")
        connect_nodes(self.nodes[1], 2)

        self.log.info("Wait for node2 to receive all the blocks from node1")
        self.sync_all()

        self.log.info("Add P2P connection to node2")
        self.nodes[0].disconnect_p2ps()

        self.nodes[2].add_p2p_connection(BaseNode())
        # After node2 connects to BaseNode, it will send invs for the blocks it knows about.
        # They don't just send everything directly because it would congest the network,
        # likely with a lot of redundant information.
        # inv message has a type (transaction, block, blockheader, etc.) and the hash
        # a peer would use the inv to see if it already has the data or needs to request
        # it from its peers.

        self.log.info("Test that node2 propagates all the blocks to us")

        # peers must send a getdata request for each of the invs it receives
        getdata_request = msg_getdata()
        for block in blocks:
            getdata_request.inv.append(CInv(MSG_BLOCK, block))
        self.nodes[2].p2p.send_message(getdata_request)
        # node2 will respond by sending all of these blocks

        # wait_until() will loop until a predicate condition is met. Use it to test properties of the
        # P2PInterface objects.
        # mininode_lock is needed because we're accessing the BaseNode's map from the test logic thread
        # A race condition occurs if we try to read it while BaseNode is writing to it without a lock
        wait_until(lambda: sorted(blocks) == sorted(list(self.nodes[2].p2p.block_receive_map.keys())), timeout=5, lock=mininode_lock)

        self.log.info("Check that each block was received only once")
        # The network thread uses a global lock on data access to the P2PConnection objects when sending and receiving
        # messages. The test thread should acquire the global lock before accessing any P2PConnection data to avoid locking
        # and synchronization issues. Note wait_until() acquires this global lock when testing the predicate.
        with mininode_lock:
            for block in self.nodes[2].p2p.block_receive_map.values():
                # BaseNode should have received exactly 1 of each block
                assert_equal(block, 1)

if __name__ == '__main__':
    ExampleTest().main()
