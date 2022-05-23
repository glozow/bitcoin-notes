# Lifecycle of a Transaction

## Table of Contents

- [Transaction Creation](#Transaction-Creation)
  - [What is a Transaction?](#What-is-a-Transaction)
  - [Transaction Creation through Bitcoin Core Wallet](#Transaction-Creation-through-Bitcoin-Core-Wallet)
  - [Transaction Children](#Transaction-Children)
- [Validation and Submission to Mempool](#Validation-and-Submission-to-Mempool)
  - [Mempool Validation](#Mempool-Validation)
    - [Context-Free Non-Script Checks](#Context-Free-Non-Script-Checks)
    - [Contextual Non-Script Checks](#Contextual-Non-Script-Checks)
    - ["Contextual" Script Checks](#Contextual-Script-Checks)
    - [Context-Free Signature and Script Checks](#Context-Free-Signature-and-Script-Checks)
  - [Submission to Mempool](#Submission-to-Mempool)
- [P2P Transaction Relay](#P2P-Transaction-Relay)
  - [Transaction Announcement and Broadcast](#Transaction-Announcement-and-Broadcast)
  - [Transaction Request and Download](#Transaction-Request-and-Download)
  - [Orphans](#Orphans)
- [Inclusion in a Block](#Inclusion-in-a-Block)
  - [Mining](#Mining)
  - [Block Relay](#Block-Relay)
  - [Block Validation](#Block-Validation)
- [After Consensus](#After-Consensus)
  - [Transaction Finality](#Transaction-Finality)
  - [State Changes and Persistence to Disk](#State-Changes-and-Persistence-to-Disk)
  - [Wallet Updates](#Wallet-Updates)
  - [Conclusion](#Conclusion)

## Transaction Creation

### What is a Transaction?

Many people think of Bitcoin transactions as financial ones representing an exchange between payer
and payee. Here, we will think of the Bitcoin network as a distributed state machine where state is
(primarily):

- the current set of available coins (aka Unspent Transaction Outputs or UTXOs), each listing an amount
and commitment to some spending conditions
- the most-work-chain tip,

and a transaction is an atomic state change, redistributing existing coins or minting new ones.

Periodically, a node proposes an ordered set of state changes batched in a block; nodes in the
network enforce a predetermined consensus protocol to decide whether or not to accept it. The
Bitcoin block chain serves as a tamper-evident [transaction
log](https://en.wikipedia.org/wiki/Transaction_log) or journal which can be downloaded from peers,
validated, and used to reconstruct the current state. Before a transaction is included in a block
("confirmed") accepted by the rest of the network, it is only a proposed state change.

A Bitcoin
[transaction](https://github.com/bitcoin/bitcoin/blob/master/src/primitives/transaction.h#L259)
consists of:

- [outputs](https://github.com/bitcoin/bitcoin/blob/master/src/primitives/transaction.h#L128)
  specifying what coins are created by this transaction
- [inputs](https://github.com/bitcoin/bitcoin/blob/master/src/primitives/transaction.h#L65)
  each referring to a UTXO created by a previous transaction
- data used to satisfy the spending conditions of the UTXOs being spent, such as signatures
- metadata

### Transaction Creation through Bitcoin Core Wallet

The process of creating a transaction does not need to be done on a node. For example,
users can generate their transactions on another wallet and/or entirely offline, and then submit raw
transactions to their Bitcoin Core node via the
[`sendrawtransaction`](https://developer.bitcoin.org/reference/rpc/sendrawtransaction.html) RPC.

The Bitcoin Core wallet allows users to create transactions with varying levels of
customization. The steps are roughly as follows:

1. A recipient provides an [invoice or destination](https://en.bitcoin.it/wiki/Invoice_address) to
   pay to, committing to the spending conditions. This helps the wallet create
[outputs](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/outputtype.h#L23-L26),
which comprise the payments.

2. The wallet calculates feerate estimates,
output types, and other options based on the user's input, pre-configured defaults and preferences,
historical blocks and current mempool contents queried from the node.

3. The transaction is
    ["funded"](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/spend.cpp#L373)
by selecting inputs from the set of
[UTXOs](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/spend.cpp#L67)
available in the wallet; these comprise the inputs. Change [may or may not be
added](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/spend.cpp#L767-L778)
to the transaction.

4. Some combination of signatures and other data is added to each input to satisfy their
   corresponding outputs' spending conditions. This process involves various steps that depend on
how many signatures are needed and where the key(s) are stored.

### Transaction Children

A child transaction is one that spends another transaction's outputs. A child can be created as soon
as the transaction has a txid - this can happen before it's even signed, which the Lightning Network
takes advantage of to open payment channels without potentially locking counterparties into a
multisig they can't get out of.

It's possible - and quite common - for transactions to have children and grandchildren before they
are confirmed. Theoretically, a user can create 1000 generations of transactions or multiple
children from the same output (conflicting transactions or "double spends"). There are no
limitations on what transactions a user can create because they are nothing more than proposed state
changes until they are included in a block.

## Validation and Submission to Mempool

Regardless of where the transaction originated from, the transaction must be accepted into the
node's [mempool](https://doxygen.bitcoincore.org/class_c_tx_mem_pool.html) to be broadcast to the
network. The mempool is a cache of unconfirmed transactions, designed to help miners select the
highest feerate candidates for inclusion in a block. Even for non-mining nodes, it is also useful
as a cache for boosting block relay and validation performance, aiding transaction relay, and
generating feerate estimations.

Peer-to-peer transaction relay contributes to the censorship-resistance, privacy and
decentralization of the network. We can imagine a simple system where users submit their
transactions directly to miners, similar to many software services in which users visit a website
hosted on servers controlled by a few companies. However, the miners in this hypothetical system -
and, by extension, governments and organizations which can bribe or exert legal pressure on them -
can trivially identify transaction origins and censor users.

In the Bitcoin network, we want any node to be able to broadcast their transactions without special
permissions or unreasonable fees. Running a full node (with all privacy settings enabled) should be
accessible and cheap, even in periods of high transaction volume.  This is not always easy, as a
permissionless network designed to let any honest node participate also exposes the transaction
validation engine to DoS attacks from malicious peers.  Malicious nodes can create fake transactions
very cheaply (both monetarily and computationally); there are no Proof of Work requirements on
transactions.

### Mempool Validation

Selecting the best transactions for the resource-constrained mempool involves a tradeoff between
optimistically validating candidates to identify the highest feerate ones and protecting the node
from DoS attacks. As such, we apply a set of validation rules known as mempool _policy_ in addition
to consensus.

We might categorize transaction validation checks in a few different ways:

- Consensus vs Policy: These can also be thought of as mandatory vs non-mandatory checks. These two
  are not mutually exclusive, but we make efforts to compartamentalize consensus rules.

- Script vs Non-script: [Script](https://en.bitcoin.it/wiki/Script) refers to the instructions and
  data used to specify and satisfy spending conditions. We make this distinction because script
checking (specifically, signature verification) is the most computationally intensive part of
transaction validation.

- Contextual vs Context-Free: The context refers to our knowledge of the current state, represented as
  [ChainState](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.h#L566).
Contextual checks might require the current block height or knowledge of the current UTXO set,
while context-free checks only need the transaction itself. We also need to look into our mempool to
validate a transaction that spends unconfirmed parents or conflicts with another transaction already
in our mempool.

#### Context-Free Non-Script Checks

Mempool validation in Bitcoin Core starts off with non-script checks (sometimes called
["PreChecks"](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L541),
the name of the function in which these checks run).

As a defensive strategy, the node starts with context-free and/or easily computed checks.
Here are some examples:

- None of the outputs are trying to send a value [less than 0 or greater than 21 million
  BTC](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/consensus/tx_check.cpp#L25-L27).

- The transaction [isn't a
  coinbase](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L568),
as there can't be any coinbase transactions outside of blocks.

- The transaction isn't [more than 400,000 weight
  units](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/policy/policy.cpp#L88).
It's possible for a larger transation to be consensus-valid, but it would occupy too much space in
the mempool. If we allowed these transactions, an attacker could try to dominate our mempool with
very large transactions that are never mined.

#### Contextual Non-Script Checks

Perhaps the most obvious non-script contextual check here is to [make sure the inputs are
available](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L641-L662),
either in the current chainstate or an unspent output of an in-mempool transaction. Instead of
looking through the entire blockchain (hundreds of gigabytes stored on disk), Bitcoin Core nodes
keep a [layered
cache](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.h#L517-L541)
of the available
[coins](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/coins.h#L30)
(a few gigabytes, much of which can be kept in memory). To make this process more efficient, coins
fetched from disk during mempool validation are [kept in
memory](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1116-L1124)
if the transaction is accepted to the mempool.

Timelocks are also checked here - the node grabs the Median Time Past
([BIP113](https://github.com/bitcoin/bips/blob/master/bip-0113.mediawiki)) and/or block height at
the current chainstate to check transaction
[`nLockTime`](https://doxygen.bitcoincore.org/class_c_transaction.html#a54d5948c11f499b28276eab6bbfdf0c5)
and input
[`nSequence`](https://doxygen.bitcoincore.org/class_c_tx_in.html#a635deeaf3ca4e8b3e1a97054607211b9).

#### "Contextual" Script Checks

Transaction [script
checks](https://doxygen.bitcoincore.org/validation_8cpp.html#a6a96a3e1e6818904fdd5f51553b7ea60) are
actually context-free in isolation; the
[`scriptSig`](https://doxygen.bitcoincore.org/class_c_tx_in.html#aba540fd902366210a6ad6cd9a18fe763)
and [`witness`](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#specification) for
each input, paired with the
[`scriptPubKey`](https://doxygen.bitcoincore.org/class_c_tx_out.html#a25bf3f2f4befb22a6a0be45784fe57e2)
in the [corresponding
UTXO](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1469)
can be passed into the script interpreter and validated without state. The [script
interpreter](https://doxygen.bitcoincore.org/interpreter_8h.html) simply evaluates the series of
opcodes and data based on the arguments passed to it.

The "context" passed to the script interpreter is a set of [script
verification
flags](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/script/interpreter.h#L42-L143)
indicating which rules to apply during script verification. For example, the `OP_CHECKSEQUENCEVERIFY` opcode
[repurposed](https://github.com/bitcoin/bips/blob/master/bip-0112.mediawiki) `OP_NOP3`. The script
verification flag `SCRIPT_VERIFY_CHECKSEQUENCEVERIFY` instructs the script interpreter [to
interpret](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/script/interpreter.cpp#L587)
the opcode `0xb2` as the instruction to
[check](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/script/interpreter.cpp#L1760)
that the input's `nSequence` is greater than the stack value or as a no-op. Starting at the BIP112 activation
height, [nodes
pass](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1695-L1697)
`SCRIPT_VERIFY_CHECKSEQUENCEVERIFY=1` into the script interpreter during consensus script checks.

#### Context-free Signature and Script Checks

Mempool validation performs two sets of script checks:
[`PolicyScriptChecks`](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L917)
and
[`ConsensusScriptChecks`](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L943).
The former [runs the script
interpreter](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L926)
using [consensus and policy
flags](https://doxygen.bitcoincore.org/policy_8h.html#ab28027bf27efcdd6535a13175a89ca5a) and caches
the signature result (if successful) in the [signature
cache](https://github.com/bitcoin/bitcoin/blob/d67330d11245b11fbdd5e2dd5343ee451186931e/src/script/sigcache.cpp#L21-L26).
The latter runs the script interpreter using [consensus flags
only](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L965)
and [caches the full validation
result](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1490),
identified by the wtxid and script verification flags. If a new consensus rule
is activated between now and the block in which this transaction is included, the cached result is
no longer valid, but this is easily detected based on the script verification flags.

For example, before taproot rules are enforced in consensus, they are in policy
(`SCRIPT_VERIFY_TAPROOT` included in policy but not consensus script verification flags); nodes
won't relay and accept taproot-invalid version 1 transactions into their mempools, even though they
aren't breaking any consensus rules yet. All script checks will be cached without
`SCRIPT_VERIFY_TAPROOT`. After taproot activation, if a previously-validated transaction is seen,
the cache entry's script verification flags won't match current consensus flags, so the node will
re-run script checks for that transaction.

The most computationally-intensive part of script validation is signature verification (indicated in
a script by opcodes such as `OP_CHECKSIG`), which doesn't change based on context. To save the node
from repetitive work, at the very start of script checks, parts of the transaction are [serialized,
hashed, and
stored](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/script/interpreter.cpp#L1423)
in a
[`PrecomputedTransactionData`](https://doxygen.bitcoincore.org/struct_precomputed_transaction_data.html)
struct for use in signature verification. This is especially handy in transactions that have
multiple inputs and/or signatures. Additionally, the cached result from `PolicyScriptChecks` can be
used immediately in `ConsensusScriptChecks`; we almost never need to verify the same signature more
than once!

### Submission to Mempool

Every [entry](https://doxygen.bitcoincore.org/class_c_tx_mem_pool_entry.html) in the mempool
contains a transaction, and various metadata such as the time it was received, its fees (for faster
lookup), the height and/or time needed to satisfy its timelocks, and pointers to any parents and
children in the mempool.

Much of the mempool is devoted to keeping track of a transaction's in-mempool ancestors (parents,
parents of parents, etc.) and descendants (children, children of children, etc.) and their
aggregated fees. A transaction is only valid if its ancestors exist: a transaction can't be mined
unless its parents are mined, and its parents can't be mined unless their parents are mined, and so
on. Conversely, if a transaction is evicted from the mempool, its descendants must be too.

As such, a transaction's effective feerate is not just its base feerate divided by weight, but that
of itself and all of its ancestors. This information is also taken into account when the mempool
fills up and the node must choose which transactions to evict (also based on fees). Of course, all
of this information can be calculated on the fly, but constructing a block is extremely
time-sensitive, so the mempool opts to cache this information rather than spend more time
calculating it. As one might imagine, the family DAGs can get quite hairy and a source of resource
exhaustion, so one part of mempool policy is to limit individual transactions' connectivity.

A transaction being added to the mempool is an event that clients of
[`ValidationInterface`](https://doxygen.bitcoincore.org/class_c_validation_interface.html) may be
[notified
about](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1046)
if they subscribed to the `TransactionAddedToMempool()` event. If the transaction is of interest to
the wallet (e.g. a sent or received payment), it
[notes](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/wallet.cpp#L1187)
that it has been added to mempool.

## P2P Transaction Relay

A node participating in transaction relay announces all of the transactions in its mempool. The goal
in transaction relay is to propagate all valid candidates for inclusion in a block to every node in
the network in a timely manner, while making an effort to conceal transaction origins and not reveal
the exact contents of our mempool. We consider a delay of a few seconds acceptable if it helps
obfuscate some information and avoid clogging up the network with redundant transaction messages.

Technically, the Bitcoin P2P protocol specifies that transactions are communicated using a [`tx`
message](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/protocol.h#L118-121).
Most nodes relay transactions using a three-part dialogue:

1. The sender sends an [`inv`
   (Inventory)](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L4650)
announcing the new transaction by its txid or wtxid.

2. Nodes [manage](https://doxygen.bitcoincore.org/class_tx_request_tracker.html) various
   transaction announcements from peers to decide which transactions they are interested in and
which peer(s) to request them from. To request a transaction, a node sends a
[`getdata`](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/protocol.h#L97-100)
message to a peer with a list of transactions identified by txid or wtxid.

3. The sender [responds to
   `getdata`s](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L1876-L1906)
by sending the full transaction in a `tx` message.

### Transaction Announcement and Broadcast

With respect to privacy in transaction relay, we specifically want to hide the origin (by network
address) of a transaction. We also want to prevent peers from probing the exact contents of our
mempool or learn when a transaction enters our mempool, which is information that can be used to
trace transaction propagation. For each peer, nodes send a batch of transaction announcements at
[random
intervals](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L4584-L4588)
(poisson timer with 2-second average for outbound peers and 5-second average for inbound peers).
This decreases the precision with which peers can learn the time we first accepted a transaction to
our mempool by probing us with `getdata`s.

A transaction might need to be rebroadcasted if propagation fails for some reason - this could be
anything from censorship to simple spurious network failures.  We might imagine rebroadcast to be
the responsibility of the transaction owner's node, but the behavior of treating our own
transactions differently from others' constitutes a privacy leak. Bitcoin Core nodes attempt to aid
initial broadcast for _all_ transactions by tracking the set of ["unbroadcast"
transactions](https://doxygen.bitcoincore.org/class_c_tx_mem_pool.html#a3df5ff43adfe0f407daa6fdef8965ba8)
and rebroadcasting them periodically until they see `getdata` for it.

### Transaction Request and Download

Since a node typically has several peers relaying transactions, it will likely receive multiple
announcements for the same transaction. To avoid redundant network traffic, nodes only request a
transaction from one peer at a time. However, it's also possible for a request to fail. A peer might
evict the transaction from their mempool, take too long to respond, terminate the connection, or
respond with garbage. Malicious nodes may also try to take advantage of flaws in the transaction
request logic to censor or stall its propagataion to miners. In these cases, nodes must remember
which other peers announced the same transaction in order to re-request it.

Rather than responding to transaction `inv`s with `getdata`s immediately, the node [stores all the
announcements
received](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L2859),
batches them by txid/wtxid, and then selects the best candidate to request the
transaction from based on connection type and how many requests are already in flight to each
peer. Nodes [prefer to
download](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L1053-L1066)
from manual connections, outbound connections, and peers using [wtxid
relay](https://github.com/bitcoin/bips/blob/master/bip-0339.mediawiki). If the first
announcement(s) to arrive are from non-preferred peers, the node waits a few seconds before sending
the request to give other, preferred peers time to announce the same transaction.

### Orphans

Occasionally, a node may receive a transaction spending input(s) that don't seem to exist. Perhaps
the inputs don't exist, but perhaps the node just hasn't heard about the parent
transaction(s) yet; transactions are not guaranteed to propagate in order. Since it's impossible to
distinguish between the two scenarios, the node optimistically requests unknown parents from the
originating node and stores the transaction in an [orphan
pool](https://doxygen.bitcoincore.org/txorphanage_8h.html) for a while.

## Inclusion in a Block

A signature indicates that the owner of the private key has agreed to spend the coins, but no money
has moved until there is network consensus that the coins have been sent. Bitcoin's consensus
protocol requires transactions to be included in a block containing a valid Proof of Work solution
and accepted by the network as part of the most-work chain.

### Mining

Miners can start working on a block as soon as they have the previous block hash. The process of
creating a new block might look something like this:

1. The miner calls the Bitcoin Core RPC
   [`getblocktemplate`](https://developer.bitcoin.org/reference/rpc/getblocktemplate.html) to
determine the best set of transactions from the mempool that fit into a block's [weight and sigop
limits](https://github.com/bitcoin/bitcoin/blob/7fcf53f7b4524572d1d0c9a5fdc388e87eb02416/src/consensus/consensus.h#L14-L17).
This generates a [_block template_](https://github.com/bitcoin/bips/blob/master/bip-0022.mediawiki)
containing a consensus-valid set of transactions and block header, just mising the nonce.

2. The miner uses the block template to dispatch work tasks to other hardware (a dedicated rack of
   ASICs, a cloud instance, or other nodes operated by mining pool members) dedicated to exploring
the nonce space and brute force hashing. "Mining" typically refers to this specific step of making
hashing many variations of the same block (e.g. with different nonces) until the block is within the
target.

3. If a solution is found, the miner calls
   [`submitblock`](https://developer.bitcoin.org/reference/rpc/submitblock.html) to submit the block
to their node and broadcast it.

### Block Relay

Once a new block is found, propagation speed is
[crucial](https://podcast.chaincode.com/2020/03/12/matt-corallo-6.html) to the decentralization of
the network. One part of this is block relay (measured by the latency between two peers), and the
other is block validation performance.

Blocks can contain megabytes worth of transactions, so block propagation by flooding would cause
huge spikes in network traffic. We also know that nodes that keep a mempool have typically seen [the
vast majority](https://www.youtube.com/watch?v=EHIuuKCm53o) of block transactions already. This
suggests we should use the `inv`/`getdata` dialogue similar to transaction relay, where data is only
sent to peers who request them, but this would significantly lengthen the latency of block propagation.

The Bitcoin P2P protocol specifies a few different ways of communicating blocks, and each individual
node typically uses some combination of them. Peers negotiate which block relay communication method
to use when they initially establishing the connection.

- Headers-First Sync: Since v0.10, Bitcoin Core nodes [sync
  headers-first](https://github.com/bitcoin/bitcoin/pull/4468), optimistically accepting 80-byte
headers bytes to build their block chain (technically, tree, since forks, stale blocks, and invalid
blocks are possible). After validating a block
header, the recipient can request the rest of the
[block](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L2093).

- `inv`/`getdata` dialogue: This works very similarly to the transaction relay dialogue.
  Announcements are sent using `inv` messages, and peers may request blocks by hash using `getdata`.

- Compact Blocks: [BIP152](https://github.com/bitcoin/bips/blob/master/bip-0152.mediawiki) compact blocks contain
only the block header, prefilled coinbase transaction, and shortids for all other transactions. If
the receiver does not recognize a transaction shortid, it [may
request](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/net_processing.cpp#L3434)
it through `getblocktxn`.

  - Nodes can request a compact block instead of a full block in an `inv`/`getdata` dialogue, or
    following block header validation.
  - Additionally, Bitcoin Core nodes select up to three peers as High Bandwidth Compact Block peers
    from which they wish to receive compact blocks directly, i.e., without waiting for an
announcement and request. Nodes serving high bandwidth compact blocks will also expedite this even
further by sending them as soon as they see a valid Proof of Work solution, before validating the
block's transactions.

### Block Validation

To fully validate new blocks, nodes only need to consult their UTXO set and knowledge of the current
consensus rules.  Since consensus rules depend on block height and time (both of which can decrease
in a reorg), they are recalculated for each block prior to validation. Regardless of whether or not
transactions
have already been previously validated and accepted to the mempool, nodes check block-wide consensus
rules (e.g. [total sigop
cost](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L1935),
[duplicate
transactions](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L1778-L1866),
[timestamps](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L3172-L3179),
[witness
commitments](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L3229-L3255),
[block subsidy
amount](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L1965-L1969))
and transaction-wide consensus rules (e.g. availability of inputs, locktimes, and [input
scripts](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L1946))
for each block.

As already mentioned, script checks are expensive. Script checks in block validation are run in
parallel and utilize the script cache. Checks for each input are added to a [work
queue](https://github.com/bitcoin/bitcoin/blob/9df1906091f84d9a3a2e953a0424a88e0931ea33/src/validation.cpp#L1887)
delegated to a set of threads while the main validation thread is working on other things. While
failures should be rare - creating a valid proof of work for an invalid block is quite expensive -
any consensus failure on a transaction invalidates the entire block and no state changes are saved
until all threads successfully complete. If the node already validated a transaction before it was
included in a block, no consensus rules have changed, and the script cache has not evicted this
transaction's entry, it just [uses the script
cache](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/validation.cpp#L1419-L1430)!

## After Consensus

Once a transaction has been included in a Proof of Work-valid block accepted by the network, it is
said to be _confirmed_ and we might begin to consider the transfer of coins completed. As more
Proof of Work-valid blocks are built on top of the block which contains the transaction, it has more
_confirmations_, and we can be reasonably certain that the money has changed hands for good.

### Transaction Finality

Measuring the _finality_ of a transaction using the amount of work done on top of it - commonly
quantified by its number of confirmations - makes sense, because it represents the chances of the
network creating and accepting a competing chain in which the transaction does not exist.

An attacker may try to do this intentionally, and we can measure the security based on the economic
cost to do so. As one might imagine, the attack is much more expensive with higher block difficulty,
since it requires doing more work, and higher network hashrate, since the attacker must compete with
(or bribe) the rest of the network to create a more-work chain.

This also means we should factor transaction value into our measurement of finality; security is
economics. If we received a transaction worth $100 million a few blocks ago, we might want to hold
off on popping the champagne, as it could still be economic for the sender to try to reverse the
transaction by mining (or bribing miners to mine) a more-work fork.

### State Changes and Persistence to Disk

Since historical block data is not needed regularly and is quite large, it is stored on disk and
only fetched when needed. The node keeps an
[index](https://doxygen.bitcoincore.org/class_c_block_index.html) to quickly look up their locations
on disk by hash. Additionally, the node should be prepared for a reorg - the block may become stale
if a new most-work chain is found, and the changes to the UTXO set will need to be undone. As such,
every block has a set of corresponding [undo
data](https://doxygen.bitcoincore.org/class_c_block_undo.html).

Blocks and undo data are persisted to disk in the `blocks/` directory. Each `blkNNNNN.dat` file stores
raw block data, and its corresponding undo data is stored in a `revNNNNN.dat` file in the same
directory. If the node operator has configured a maximum disk space for old blocks, this process
will also [automatically prune](https://github.com/bitcoin/bitcoin/pull/5863) blocks by oldest-first
to stay within limits.

While the UTXO set is comparatively smaller than the block chain, it doesn't always fit in memory.
A node's view of available coins is implemented in
[layers](https://github.com/bitcoin/bitcoin/blob/21438d55d553ae5bf3be7c0d4431aaf136db6c6b/src/validation.h#L505)
of
[maps](https://github.com/bitcoin/bitcoin/blob/21438d55d553ae5bf3be7c0d4431aaf136db6c6b/src/coins.h#L157)
from
[outpoints](https://github.com/bitcoin/bitcoin/blob/774a4f517cf63df345e6a4852cc0b135b0a9ab76/src/primitives/transaction.h#L26)
to
[coins](https://github.com/bitcoin/bitcoin/blob/774a4f517cf63df345e6a4852cc0b135b0a9ab76/src/coins.h#L30).
Every validation session (for both [block
validation](https://github.com/bitcoin/bitcoin/blob/6312b8370c5d3d9fb12eab992e3a32176d68f006/src/validation.cpp#L2380)
on top of the current tip and unconfirmed [transaction
validation](https://github.com/bitcoin/bitcoin/blob/6312b8370c5d3d9fb12eab992e3a32176d68f006/src/validation.cpp#L427)
on top of current chainstate and mempool) creates a temporary view of the state and flushes it to
the appropriate view.

### Wallet Updates

The Bitcoin Core wallet tracks incoming and outgoing transactions and subscribes to major events by
[implementing](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/wallet.cpp#L1187-L1265)
the node's
[`ValidationInterface`](https://github.com/bitcoin/bitcoin/blob/3d9cdb16897bf5f5eed525fd3fbc07e57dbe5f54/src/validationinterface.h#L63-L177).
The most relevant information for the wallet is which of [its own
coins](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/wallet.cpp#L1296-L1330)
are available and how likely they are to remain spendable, measured by the
[number](https://github.com/bitcoin/bitcoin/blob/55a156fca08713b020aafef91f40df8ce4bc3cae/src/wallet/spend.h#L25)
of confirmations on the transaction and its sender. A UTXO made available by a
transaction sent by the wallet itself, 100 blocks deep in the most-work chain, is considered pretty
safe. On the other hand, if a newly confirmed transaction conflicts with one that sent coins to the
wallet, those coins have a "depth" of -1 and [are not
considered](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/wallet/spend.cpp#L94)
a probable source of funds.

### Conclusion

At the end of a transaction's lifecycle, it has deleted and added UTXOs to the network state, added
an entry to the blockchain, and facilitated a transfer of value between two Bitcoin users anywhere
in the world.

It has been represented in many forms: a raw hex string, a series of TCP packets, a wallet's
probable payment, and a collection of spent and added coins in the coins cache.

In its journey, the transaction (and you, the reader!) swam through the mempool, zipped around the
p2p network, and found a home in the block database of thousands of Bitcoin nodes. FIXME WHY IS THIS
SO CHEESEY

