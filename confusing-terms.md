# Frequently Confused Terms in Bitcoin

### Blocksonly and block-relay-only

You can set your node to `-blocksonly` in order to _only_ validate blocks (including the
transactions in them) and not care about unconfirmed transactions.  When a node is in `blocksonly`
mode, it asks for only blocks from _all_ of its peers.  This is usually done to save space; it's not
a good idea to do this if the node will be broadcasting any transactions because it's relatively
easy to tell that the transaction originates from this node.

A `block-relay-only` connection is a type of outbound connection that is devoted to relaying blocks
only (no transactions or addrs).  This is done by setting fRelay to false in the version handshake.
A `block-relay-only` peer is a peer to which your node has made this type of connection.

### OutPoint, Output

[COutPoint](https://doxygen.bitcoincore.org/class_c_out_point.html)s, sometimes also called
prevouts, are the data structure used to refer to a transaction you're spending from. They consist of
the transaction hash and index `n` within its vout.

[COutPut](https://doxygen.bitcoincore.org/class_c_output.html)s are the data structure within a
transaction representing payments. They contain the amount sent, `nValue`, and commitment to the
spending condition, `scriptPubKey`.

### Address, Addr

Addresses are strings representing "where" an output is sending bitcoins to. For example, a bech32
address includes a scriptPubKey with information/formatting to help reduce human error. If you send
a bitcoin to this address (i.e. create a transaction that has outputs with a scriptPubKey to this
address), one needs the corresponding private key to spend it. They are called "addresses" because
the original idea was to be able to send bitcoins to someone based on their IP address.

Addrs are P2P messages that contain IP addresses of bitcoin nodes that you can connect to.
It's probably short for "IP address" but I'm not sure.
Nodes gossip addrs to help each other find peers to connect to.

### Pruned Node, SPV Node, Light Client

A Pruned node is a full node that doesn't keep all historical blocks.  It still stores the
chainstate, i.e. the UTXO set and thus can fully validate all incoming blocks.  It must also store
some number of recent blocks just in case there are reorgs, but it is defined by the fact that it
"prunes" historical data.

SPV (Simplified Payment Verification) Node and Light Client are the same thing.  They are nodes that
don't have the full state and verify to the best of their ability using limited information.  This
typically involves connecting to other full nodes and asking them for blocks and transactions,
trusting that the information they recieve is correct.

### Full Node, Mining Node

A full node is a node that stores complete chainstate (i.e. UTXO set) and can thus fully validate new blocks.
A mining node creates new blocks.

### The Scheduler, schedulers

Bitcoin Core nodes have a [SchedulerThread](https://doxygen.bitcoincore.org/class_c_scheduler.html#a14d2800815da93577858ea078aed1fba) that stores tasks to be executed at some point in the future such as dumping contents to disk and asynchronous callbacks.
This is distinct from the scheduler in your computer's operating system, which schedules threads.
If something impacts "the scheduler" in Bitcoin Core, this does not affect any other process in your system.

### setmocktime, mockforward

The [setmocktime](https://github.com/bitcoin/bitcoin/blob/3b6d1b61d31674e033e821046baa95c66dedf623/src/rpc/misc.cpp#L360) RPC sets the system clock to a specified time.
This affects all stats that are based on clock, such as ping times.

The [mockscheduler](https://github.com/bitcoin/bitcoin/blob/3b6d1b61d31674e033e821046baa95c66dedf623/src/rpc/misc.cpp#L397) (previously `mockforward`) instructs the scheduler (Bitcoin Core's data structure that stores tasks to be executed in the future) to reduce the time on all of its tasks.
This affects scheduled routines like rebroadcast.
Calling `setmocktime` will not affect the scheduler, and `mockforward` will not change the system time.

### Stale blocks, Orphan blocks, Orphan transactions

[Stale blocks](https://bitcoin.stackexchange.com/questions/5859/what-are-orphaned-and-stale-blocks/)
are "are valid blocks which are not part of the main chain." Some other cryptocurrency projects call
stale blocks "orphan blocks." One could think of stale blocks as "orphaned" in the sense that they
didn't become a part of the main chain, but "orphan block" has a distinct meaning in Bitcoin.

From the perspective of a node, a block or transaction is an "orphan" when the node does not have
its previous block or transaction specified by the prevout of an input, respectively. When a node
encounters an orphan block, it can't connect it to its current best-work chain. Nodes typically keep
orphan transactions in an "orphan pool" and request the parent transaction from the originating
peer.

### Soft/Hard Fork, Repo Fork

A soft/hard fork occurs when there is a chain split in the network. Typically, the network picks a
fork (based on PoW consensus rules, the one with the most work) and continues building blocks on
that one, leaving the other fork behind. Some forks are unintentional (e.g. BIP 50 or stale
blocks). Some forks are intentional and result in altcoins (e.g. Bitcoin Cash).

You can also "fork" a git repository, i.e. make a copy of it for yourself, then continue to
read/write your own fork (e.g. Bitcoin Knots) and/or make a Pull Request from your fork to the
original fork. This is usually intentional, and can also result in altcoins.

### BCH, Bech32

[BCH](https://en.wikipedia.org/wiki/BCH_code) stands for Bose Chaudhuri Hocquenghem codes.
BCH is also an acronym for Bitcoin Cash.

Bech32 is a segwit address format, see [BIP 173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki).
There's some information on how they're related in [this stack exchange post](https://bitcoin.stackexchange.com/questions/74573/how-is-bech32-based-on-bch-codes)

### Coins, bitcoins, COIN

When you see "coins" in the codebase it usually means `CCoins`, i.e. UTXOs.  You have "coins" in
your wallet to spend. "Coin selection" refers to the process of picking which UTXOs to use to create
a transaction. Coins are different from bitcoins, since a UTXO can have many different values other
than 1 BTC.

In the codebase, the `COIN` constant is used to represent the number of satoshis in 1 BTC.

### Cypherpunk, Cyberpunk, Cyberphunk

[Cypherpunks](https://www.activism.net/cypherpunk/manifesto.html) write code.

[Cyberpunk](https://en.wikipedia.org/wiki/Cyberpunk) is a genre of scifi. According to Wikipedia, "a
subgenre of scifi in a dystopian futuristic setting that tends to focus on a 'combination of
low-life and high tech' featuring advanced technological and scientific achievements, such as
artificial intelligence and cybernetics, juxtaposed with a degree of breakdown or radical change in
the social order."

Cyberphunk is, I'm guessing, funky music that relates to cyber stuff.
