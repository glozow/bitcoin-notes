# Cluster Mempool Migration Guide

This guide is intended for downstream software, to help them update for compatibility with Bitcoin Core v31's cluster mempool.

Key points to note:
- Policy changes are minimal. Most are more permissive than before.
- The main feature relevant to downstream users is **chunk feerate**, an all-inclusive "score" for incentive compatibility.
- For the next few years, a significant portion of the network will use both old and new policies. **Stay compatible with both** for best propagation results.

Tags: Wallet developers, L2 developers, miners, infrastructure operators, block explorers.

## 1. Changes to make when upgrading to v31 now

### 1.1 Startup options

Consider removing these startup options, which no longer affect mempool policy and will be removed in the future.

- **`-limitancestorsize` / `-limitdescendantsize`**: Hidden. Produce a startup warning and have **no effect** on mempool
  acceptance. It's safe to remove them from your configuration.
- **`-limitancestorcount` / `-limitdescendantcount`**: Deprecated (debug-only) but still used by the Bitcoin Core wallet
  for coin selection via `getPackageLimits()`. They have no effect on mempool acceptance, but the wallet uses them to
avoid creating transaction chains that won't propagate to pre-v31 nodes. They are safe to remove unless you rely on
custom values and the Bitcoin Core wallet for coin selection.

The new cluster limit options (`-limitclustercount`, `-limitclustersize`) are also debug-only. It is not recommended to
change their defaults, as non-default values may cause your mempool to diverge from the network, leading to issues with
fee estimation, block propagation, and transaction reliability.

### 1.2 RPC schema changes

See sections below for specific field additions, removals, and semantic changes in `getmempoolinfo`, `getmempoolentry`, and related RPCs. The following RPC results have been **removed**:

- `getmempoolinfo`
  - limitancestorcount
  - limitancestorsize
  - limitdescendantcount
  - limitdescendantsize

### 1.3 Validation error strings

If your software matches on specific error strings in mempool validation (i.e. sendrawtransaction and testmempoolaccept), update for these changes:

- **Error "too-long-mempool-chain"** is removed. Replaced by **"too-large-cluster"** for the equivalent error.
- **New error**: `"insufficient feerate: does not improve feerate diagram"` (RBF Rule 6, the new feerate diagram check).
- **Changed error**: `"too many conflicting clusters"` (previously referred to descendant count of conflicting transactions; now refers to the number of conflicting clusters).

### 1.4 `getTransactionAncestry` / chain interface

The second output parameter of `GetTransactionAncestry` changed from **descendant count** to **full cluster count**. A cluster includes ancestors, descendants, siblings, and all transitive relatives -- not just direct descendants.

Example: if your transaction is in a cluster of 64 transactions and has only 2 direct descendants, the returned cluster count is 64, not 2.

If you use this value in coin selection to avoid hitting limits, you likely don't need to change your logic -- just be aware that the metric now reflects a broader set of related transactions. Keep the limit-checking logic in place, and keep using the original default of 25, as it helps avoid violation of both the old ancestor/descendant limits (for pre-v31 propagation) and the new cluster limits.

### 1.5 `checkChainLimits` error message

The wallet-facing error from `checkChainLimits` changed from referencing ancestor/descendant limits to: **`"too many unconfirmed transactions in cluster"`**.

## 2. Changes to avoid transactions getting stuck

Make these changes to wallet software that will be submitting transactions to a v31 node. As the network adopts cluster mempool over the next few years, all wallet implementations should update:

### 2.1 CPFP carve-out is removed.

If you rely on this, migrate to TRUC (v3 transactions, BIP 431).

### 2.2 Adopt cluster limits

- **Adopt cluster limits.** The new limits are a maximum cluster count of **64** (hard cap in TxGraph, cannot be increased via configuration; `-limitclustercount` can only decrease it) and a maximum cluster size of **101 kvB**. If you previously respected the old ancestor/descendant limits (25 count, 101 kvB), your transactions will usually be within the new limits. However, clusters can grow larger than ancestor/descendant sets because they include all transitively connected transactions. A practical strategy: limit ancestor count to 25 and total cluster count to 25. A cluster of 25 transactions cannot have a descendant set larger than 25, covering both old and new limits.

### 2.3 Note new RBF restrictions

The Replace-by-Fee policy has changed. Also see later sections on new features.

- **New RBF feerate diagram rule.** A replacement must improve the feerate diagram of the mempool. This replaces the old
  rule that the replacement must have a higher feerate than the transaction; it is stricter in some cases and more
permissive in others. The error is `"insufficient feerate: does not improve feerate diagram"`.
- **Amount of permitted conflicts.** A replacement cannot conflict with more than 100 clusters. Previously, this rule
  limited the summed descendant sets of directly conflicting transactions.
- The requirement of total fee increase has not changed: the replacement(s) must pay higher fee, and the difference must
  pay for its own relay at the incremental relay feerate.

## 3. Other things to be aware of immediately

- **Block assembly algorithm changed.** Transaction ordering in blocks produced by `getblocktemplate` is now based on
  chunk feerate rather than ancestor feerate, which produces more fee-optimal blocks. Contents and selection order may
be slightly different.
- The `getblocktemplate` interface has not changed.

## RPC changes in detail

### `getmempoolinfo`

Removed fields from pre-v31:
- `limitancestorcount`, `limitancestorsize`, `limitdescendantcount`, `limitdescendantsize`

New fields:
- `limitclustercount` (number): maximum transactions in a cluster (default 64)
- `limitclustersize` (number): maximum cluster size in vbytes
- `incrementalrelayfee` (amount): minimum fee rate increment for mempool limiting or replacement
- `optimal` (boolean): whether the mempool is in a known-optimal transaction ordering

### `getmempoolentry`

New fields:
- `chunkweight` (number): sigops-adjusted weight (BIP 141 weight modified by `-bytespersigop`) of this transaction's
  chunk. This is in **weight units**, not vsize.
- `fees.chunk` (amount): total fees of the chunk this transaction belongs to.

**Weight vs vsize in new fields:** The new cluster and chunk fields (`chunkweight`, `clusterweight`) use sigops-adjusted
weight units. The old `ancestorsize` and `descendantsize` fields continue to use sigops-adjusted vsize. To compute a
feerate from chunk data: `chunkfee / (chunkweight / 4)` gives a fee-per-vbyte rate.

Existing fields `ancestorcount`, `ancestorsize`, `descendantcount`, `descendantsize` and their fee counterparts are
still present but **now computed on-the-fly** via graph traversal rather than being cached.

### `getmempoolcluster`

Returns the full cluster for a given transaction, including `clusterweight`, `txcount`, and a `chunks` array with `chunkfee`, `chunkweight`, and transaction lists per chunk.

### `getmempoolfeeratediagram`

Returns the feerate diagram of the entire mempool. Note: this is an experimental RPC; its interface may change.

## Features to take advantage of in the future

Note that most features will not be reliable until a large portion of the network adopts v31.

- **Spending unconfirmed UTXOs in replacements.** You no longer need to omit unconfirmed UTXOs when creating replacement
  transactions. However, spending from a lower-feerate unconfirmed transaction may reduce the chunk feerate of your
replacement, potentially causing it to be rejected by the feerate diagram check. Prefer confirmed UTXOs when possible.
- **`getmempoolfeeratediagram`** for inspecting the global mempool feerate ordering (hidden RPC).
- **`getmempoolcluster`** for inspecting the full cluster of any mempool transaction.
- **Below-minrelayfeerate transactions in packages.** A non-TRUC transaction can have a 0-fee rate when bumped in a package.
- **Total ordering.** The mempool now has a total ordering. You can determine whether one transaction would be mined
  before another by comparing chunk feerates, without running a full block assembly algorithm.
- **Chunk feerate can be used directly.** Fee estimation services and explorers no longer need to calculate the "effective feerate" separately.

## Tips and pitfalls

- **Sigops-adjusted weight vs BIP 141 weight vs vsize.** New cluster/chunk fields use sigops-adjusted weight. Be careful
  when comparing with vsize-based fields.
- **RBF strategy.** RBF has never simply checked feerate and total fee increase. With the new feerate diagram rule, the
  best strategy remains trial and error: submit increasingly higher feerate replacement transactions until one is
accepted.
- **Package feerate != chunk feerate.** Chunk feerate is not necessarily the same as package feerate at acceptance. The
  chunk feerate of a transaction can change while it is in the mempool, e.g. because of a CPFP.
