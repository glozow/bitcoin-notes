# Lifecycle of a Transaction

## Transaction Creation through Bitcoin Core Wallet

The process of creating a transaction does not need to be done on a node. Users can generate their
transactions on another wallet and/or entirely offline, and then submit raw transactions to their
Bitcoin Core node via one of its user interfaces (i.e. `submitrawtransaction` through CLI or RPC).

The Bitcoin Core wallet also allows users to create transactions with varying levels of
customization. The steps are roughly as follows:

### Wallet Parameters

The wallet is configured (either automatically using defaults or through user input) with options
such as change output types, etc. It grabs feerate estimates from the node based on the user's
preferences, historical blocks and current mempool contents.  FIXME

### Transaction Payload

Relevant code:

Every transaction has metadata, inputs, and outputs. The first part of the transaction to be
determined is typically the outputs; a payee provides an invoice to pay to. If the payee has a
special redeem script for these coins (e.g. multisig or timelock), they generate the script ahead of
time and embed the script hash into the destination.

The user specifies what payments are to be made in this transaction. These comprise the "recipient"
or "payment" outputs.  FIXME

### Coin Selection

Relevant code: src/wallet/coinselection.h, `CWallet::CreateTransactionInternal()`

The transaction is "funded" using a set of UTXOs available in the wallet; these comprise the inputs.
A change output may or may not be added to the transaction.  FIXME

### Signing

Signatures and scripts are added. This process may involve various steps based on how many
signatures are needed and where the keys are stored.  FIXME

## Validation and Submission to Mempool

Regardless of where the transaction originated from, before being broadcast to the network, the
transaction must be accepted into the node's mempool. The mempool is designed to be a cache of
unconfirmed transactions that helps miners select the best transactions to include in the next
block. For non-mining nodes, keeping a mempool helps increase block validation performance and aid
transaction relay. In addition to enforcing consensus rules, Bitcoin Core nodes apply a set of rules
known as mempool _policy_ (also sometimes called "standardness" rules).

### Mempool Validation

Relevant code: `MemPoolAccept`, policy.h

Beyond applying consensus rules correctly, the primary consideration in mempool validation is DoS
prevention. Malicious nodes can create fake transactions very cheaply (both monetarily and
computationally): fees are not paid until transactions are included in a block, and there are no
Proof of Work requirements on transactions. As such, mempool validation logic is designed to fail
fast and protect the node from expending any unnecessary resources.

We might categorize transaction validation checks in a few different ways:

- Consensus vs Policy: These can also be thought of as mandatory vs non-mandatory checks. They are
  not mutually exclusive, but we make all possible efforts to
  compartamentalize consensus rules to avoid making mempool logic consensus-critical.

- Script vs Non-script: We make this distinction because script checking is the most computationally
  intensive part of transaction validation.

- Contextual vs Context-Free: The context refers to the current state of the block chain (thinking
  about the Bitcoin network as a distributed state machine). Contextual checks might require the
current block height or knowledge of the current UTXO set, while context-free checks only need the
transaction itself.

#### Context-Free Non-Script Checks

Relevant code: `CheckTransaction()`

Mempoool validation in Bitcoin Core starts off with non-script checks (sometimes called `PreChecks`,
the name of the function in which these checks run).

As a defensive strategy, the node starts with context-free and/or easily computed checks.
Here are some examples:

- None of the outputs are trying to send a value less than 0 or greater than 21 million BTC.

- The transaction isn't a coinbase - there can't be any coinbase transactions outside of blocks.

- The transaction isn't more than 400,000 weight units. It's possible for a larger transation to be
  consensus-valid, but it would occupy too much space in the mempool. If we allowed these
transactions, an attacker could try to cripple our mempool by sending very large transactions that
are later conflicted out by blocks.

#### Contextual Non-Script Checks

Relevant code: `MemPoolAccept::PreChecks()`

Perhaps the most obvious non-script consensus check here is to make sure the inputs are available. Each
input in the transaction must refer to a UTXO created by previous transaction by the txid and index
in the output vector. Rather than looking through the entire blockchain (hundreds of gigabytes
stored on disk), Bitcoin Core nodes keep a layered cache of the available coins (a few gigabytes,
much of which can be kept in memory) to make this process more efficient Coins fetched from disk
during mempool validation are kept in memory if and only if the transaction is accepted to the
mempool. This prevents a peer from thrashing the coins cache (also bottlenecking block validation
performance) by creating invalid transactions spending random coins - remember that malicious nodes
would be able to do this without providing a valid signature.

Timelocks are also checked here - the node grabs the Median Time Past (BIP113) and/or block height
at the current chainstate to check the transaction `nLockTime` and input(s) `nSequence`. The node
freezes chainstate for the duration of this validation session to ensure those values don't change.
Even if a new block (which could extend or invalidate the chain tip) arrives on the wire, the
node won't process it until it has finished validating this transaction.

#### Signature and Script Checks

Relevant code: src/script/interpreter.h, `CheckInputScripts()`, `PrecomputedTransactionData`,
`g_scriptExecutionCache`, `CScriptCheck`, `STANDARD_SCRIPT_VERIFY_FLAGS`

Transaction script checks are actually context-free; the unlocking script (`scriptSig`,
`redeemScript`, and `witness`) in each input is paired with the locking script (`scriptPubKey`) in
the corresponding UTXO and passed into the script interpreter. The script interpreter simply
evaluates the series of opcodes and data based only on the arguments passed to it. One such argument
is a set of script verification flags indicating which rules to apply during script verification.

For example, the `OP_CHECKSEQUENCEVERIFY` opcode repurposed `OP_NOP3`. The script verification flag
`SCRIPT_VERIFY_CHECKSEQUENCEVERIFY` instructs the script interpreter to interpret the opcode `0xb2`
as "check that the input sequence is greater than the stack value" or as a no-op. At the BIP113
activation height, nodes pass `SCRIPT_VERIFY_CHECKSEQUENCEVERIFY=1` into the script interpreter.

Another part of script validation is signature verification (indicated in a script by opcodes such
as `OP_CHECKSIGVERIFY`), which is the most expensive part of transaction validation.

Transactions might have multiple signatures on various parts of the transaction. For example,
multiple parties might have contributed to funding the transaction, each signing on some combination
of the outputs that they care about. Even in the most basic, single signature transaction, we need
to serialize and hash parts of the transaction according to the sighash flag(s) used. To save the
node from repetitive work, at the very start of script checks, subparts of the transaction are
serialized, hashed, and stored in a `PrecomputedTransactionData` struct for use in signature
verification.

`MemPoolAccept` performs two sets of script checks: `PolicyScriptChecks` and
`ConsensusScriptChecks`. The former runs the script interpreter using consensus and policy flags and
caches the result in the signature cache. The latter runs the script interpreter using consensus
flags only and caches the full validation result, identified by the wtxid and script verification
flags, in the script cache. If a new consensus rule is activated between now and the block in which
this transaction is included, the cached result is no longer valid, but this is easily detected
based on the script verification flags. The cached signature verification - which does not have
specific script verification flags - result from `PolicyScriptChecks` is used immediately in
`ConsensusScriptChecks`; we almost never need to verify the same signature twice!

### Submission to Mempool

Relevant code: `MemPoolAccept::Finalize()`, `CWallet::transactionAddedToMempool`


The mempool primarily serves as a size-limited cache of the best candidates for inclusion in the
next block. Thus, transactions are evicted based on their descendant feerate.

A transaction being added to the mempool is an event that implementers of `ValidationInterface` are
notified about. If the transaction originated from the node's wallet, the wallet notes that it has
been added to mempool.

## P2P Transaction Relay

Relevant code: `PeerManagerImpl::RelayTransaction()`

A node participating in transaction relay broadcasts all of the transactions in its mempool.
The primary goal in transaction relay is to propagate transactions to every node in the network in a
timely manner, but _privacy_ and network bandwidth are also important consideration in Bitcoin. Since the
average block interval is about 10 minutes, we'll consider a few second-delay acceptable if it helps
obfuscate transaction origins and avoids clogging up the network with redundant transaction messages.

Technically, the Bitcoin P2P protocol specifies that transactions are communicated using a `TX`
message.  Most nodes relay transactions using a three-part dialogue:

1. The sender sends an `INV` (Inventory) message announcing the new transaction by its witness hash.
   Non-segwit nodes or those implementing an older protocol version may communicate using txids.

2. The receiver sends a `GETDATA` to request transactions they are interested in (i.e. don't already
   have), also identified by their hash.

3. The sender sends the full transaction in a `TX` message.

### Transaction Announcement and Broadcast

Relevant code: `CTxMemPool::m_unbroadcast_txids`, `PeerManagerImpl::ReattemptInitialBroadcast()`

With respect to privacy in transaction relay, we specifically want to hide the origin (IP address)
of a transaction. For each peer, nodes send a batch of transaction announcements at random intervals
(poisson timer with 2-second average for outbound peers and 5-second average for inbound peers).

After broadcasting a transaction for the first time, Bitcoin Core nodes store them in an
_unbroadcast_ set until they see an `INV` for it, indicating that the transaction has been accepted
to a peer's mempool.

### Transaction Request and Download

Relevant code: PR#19988, txrequest.h

Since a node typically has at least 8 peers relaying transactions (there are 8 full relay outbound
connections even with inbounds disabled), it will likely receive multiple announcements, but only
requests the transaction from one peer at a time to avoid redundant network traffic. At the same
time, it's possible for a request to fail. A peer might evict the transaction from their mempool,
take too long to respond, terminate the connection, etc. Malicious nodes may also try to take
advantage of flaws in the transaction request logic to censor or stall a transaction from being
propagated to miners. In these cases, nodes must remember which other peers announced the same
transaction in order to re-request it.

Rather than responding to transaction `INV`s with `GETDATA`s immediately, nodes store all the
announcements received, batching ones corresponding to the same transaction, selecting the best
candidate to request the transaction from based on connection type and how many requests are already
in flight. Nodes prefer to download from manual connections, outbound connections, and peers using
WTXID relay. If the first announcement(s) to arrive are from non-preferred peers, the node waits for
other peers to announce the same transaction for a short period of time (several seconds) before
sending the request.

### Orphans

Relevant code: src/txorphanage.h

FIXME: orphans

### Future Updates in Transaction Relay

- Erlay: this would introduce an additional method of transaction announcements that reduces `INV`
  and `GETDATA` traffic (much of which is redundant, since each node may hear about a transaction
from dozens of peers). Rather than sending `INV`s for each transaction, peers periodically use set
reconciliation to determine which transactions to send to each other.

- Package Relay: Package validation (rather than just individual transaction validation) may produce
  a more accurate evaluation of transaction validity. With package relay, in addition to (or perhaps
as a substite for) relaying transactions individually, nodes may instruct peers to validate specific
transactions together as packages.

## Inclusion in a Block

A signature on a transaction indicates that the owner of the private key has agreed to spend the
coins, but the transaction should be untrusted until there is network consensus that the coins have
been sent - it is trivially cheap for a private key owner to sign multiple transactions sending the
same coins. In Bitcoin, our consensus protocol requires the transaction to be included in a block
containing a valid Proof of Work and accepted by the network as part of the most-work chain - it is
prohibitively expensive for a private owner to reverse a transaction by rewriting (and recomputing
Proof of Work for) these blocks.

### Mining

Relevant code: src/miner.h, `BlockAssembler::CreateNewBlock()`

Miners can start working on a block as soon as they have the previous block hash. The process of
creating a new block might look something like this:

1. The miner calls the Bitcoin Core RPC `getblocktemplate` to generate a block _template_ containing
   a consensus-valid set of transactions and header, just mising the nonce.

2. The miner dispatches the block template to other hardware (perhaps a rack of ASICs, a cloud
   instance, or other nodes operated by mining pool members) dedicated to finding the nonce.

3. If a solution is found, the miner calls `submitblock` to broadcast the new block.

Bitcoin Core's mining code (used by `getblocktemplate`) uses the mempool, sorted by ancestor score
(ancestor feerate + manual prioritization by the miner), to determine which transactions to include
in the next block. This means a "package" consisting of a 5 sat/vB parent and 100 sat/vB child may
get picked over a 20 sat/vB transaction, but not over a singular 100 sat/vB transaction with no
dependencies.

### Block Relay

Relevant code: BIP152

Blocks can contain megabytes worth of transactions, and nodes that keep a mempool have seen
at least 98% of them already (FIXME source: gmax's block relay talk).

The methods for block relay are listed below, along with a description of how the transaction is
communicated with or without sending the full transaction data over P2P. Note that peers negotiate
which block relay communication method to use _before_ blocks are communicated.

- High Bandwidth Compact Blocks: the sender creates a BIP152 compact block comprising only the block
  header, prefilled coinbase transaction, and shortids for all other transactions. If the
receiver does not recognize a transaction shortid, it may request it through `GETBLOCKTXN`.

- Headers First: to prevent huge spikes in network traffic, senders flood block headers only (which
  is just 80 bytes). The recipient can choose to request the full block or compact block.

- `INV`/`GETDATA` Dialogue: the peers sacrifice latency for lower bandwidth usage by announcing blocks through
  `INV` messages. The recipient can request the full or compact block.

### Block Validation

Relevant code: `-par`, `g_scriptExecutionCache`, `CChainState::ActivateBestChain()`

FIXME: non-script checks

If the node already validated this transaction before it was included in a block, no consensus rules
have changed, and the script cache has not evicted this transaction's entry, it doesn't need to run
script checks again!

### State Changes and Persistence to Disk

Relevant code: src/undo.h, `CTxUndo`, `SaveBlockToDisk()`

To fully validate new blocks, nodes only need to store some representation of the current state and
knowledge of the current consensus rules. Archival nodes store the entire block chain and can thus
query any arbitrary block or transaction from Bitcoin history. Pruned nodes only store a portion of
the most recent blocks. Additionally, the node should be prepared for a reorg - the block may become
stale if a new most-work chain is found, and the changes to the UTXO set will need to be undone.

FIXME: coins cache flushing

Historical blocks are persisted to disk in the `blocks/` directory. Each `blkNNNNN.dat` file stores
raw block data, and its corresponding undo data is stored in a `revNNNNN.dat` file in the same
directory. If the node operator has configured a maximum memory allocation for this node, this
process will also prune blocks by oldest-first to stay within limits.

### Wallet Updates

Relevant code: src/wallet/spend.h, `CWallet::blockConnected`

The Bitcoin Core wallet tracks incoming and outgoing transactions and subscribes to major events by
implementing the node's `ValidationInterface`. The most relevant information for the wallet is which
coins are available and how likely they are to remain spendable - this is quantified by the number
of confirmations on the transaction (or on a _conflicting_ transaction, represented as negative
numbers). A UTXO made available by a transaction 100 blocks deep in the most-work chain is
considered pretty safe. On the other hand, if a newly confirmed transaction conflicts with one that
sent coins to the wallet, those coins now have a "depth" of -1 and will not be considered a probable
source of funds.

### Transaction Children

A transaction has a "child" when its outputs are used as the inputs to fund another transaction
(which may or may not be valid). Technically, a child can be created as soon as the transaction has
a txid (i.e. after the transaction has been signed), including some limitations:

* The Bitcoin Core wallet may not consider the coins reliable enough to spend. For example, the coin
  selection algorithm never selects unconfirmed UTXOs that originate from foreign sources.
* Transactions spending coinbase outputs are not considered consensus valid until 100 blocks later.

