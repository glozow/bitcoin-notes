# Frequently Confused Terms in Bitcoin

### Blocksonly and block-relay-only

You can set your node to `-blocksonly` in order to _only_ validate blocks (including the transactions in them) and not care about unconfirmed transactions.
When a node is in `blocksonly` mode, it asks for only blocks from _all_ of its peers.
This is usually done to save space; it's not a good idea to do this if the node will be broadcasting any transactions because it's relatively easy to tell that the transaction originates from this node.

A `block-relay-only` connection is a type of outbound connection that is devoted to relaying blocks only (no transactions or addrs).
This is done by setting fRelay to false in the version handshake.
A `block-relay-only` peer is a peer to which your node has made this type of connection.

### OutPoint, Output

COutPoints are a data structure used to refer to transaction outputs. They consist of the transaction hash and the index `n` to indicate which output it is in vout.
COutPuts are transaction outputs themselves. They contain the `nValue` and `scriptPubKey`.

### Address, Addr

Addresses are hashes that correspond to "where" you're sending bitcoins to.
For example, a PKH address is the hash of a public key.
If you send a bitcoin to this address (i.e. create a transaction that has outputs with a scriptPubKey to this address), one needs the corresponding private key to spend it.
IIRC they are called "addresses" because the original idea was to be able to send bitcoins to someone based on their IP address.

Addrs are P2P messages that contain IP addresses of bitcoin nodes that you can connect to.
It's probably short for "IP address" but I'm not sure.
Nodes gossip addrs to help each other find peers to connect to.

### Pruned Node, SPV Node, Light Client

A Pruned node is a full node that doesn't keep all historical blocks.
It still stores the chainstate, i.e. the UTXO set and thus can fully validate all incoming blocks.
It must also store some number of recent blocks just in case there are reorgs, but it is defined by the fact that it "prunes" historical data.

SPV (Simplified Payment Verification) Node and Light Client are the same thing.
They are nodes that don't have the full state and verify to the best of their ability using limited information.
This typically involves connecting to other full nodes and asking them for blocks and transactions, trusting that the information they recieve is correct.

### Full Node, Mining Node

A full node is a node that stores complete chainstate (i.e. UTXO set) and can thus fully validate new blocks.
A mining node creates new blocks.

### The Scheduler, schedulers

Bitcoin Core nodes have a scheduler that stores tasks to be executed at some point in the future.
This is distinct from the scheduler in your computer's operating system, which schedules threads.
If something impacts "the scheduler" in Bitcoin Core, this does not affect any other process in your system.

### setmocktime, mockforward

The `setmocktime` RPC sets the system clock to a specified time.
This affects all stats that are based on clock, such as ping times.

The `mockforward` instructs the scheduler (Bitcoin Core's data structure that stores tasks to be executed in the future) to reduce the time on all of its tasks.
This affects scheduled routines like rebroadcast.
Calling `setmocktime` will not affect the scheduler, and `mockforward` will not change the system time.

### Cypherpunk, Cyberpunk, Cyberphunk

[Cypherpunks](https://www.activism.net/cypherpunk/manifesto.html) write code.

[Cyberpunk](https://en.wikipedia.org/wiki/Cyberpunk) is a genre of scifi. According to Wikipedia, "a subgenre of scifi in a dystopian futuristic setting that tends to focus on a 
'combination of low-life and high tech' featuring advanced technological and scientific achievements, 
such as artificial intelligence and cybernetics, juxtaposed with a degree of breakdown or radical change in the social order."

Cyberphunk is, I'm guessing, phunky music that relates to cyber stuff.
