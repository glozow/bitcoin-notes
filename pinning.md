# Pinning Zoo

A pinning attack is a type of censorship in which the attacker takes advantage of mempool policy to prevent a transaction from entering the mempool, or an in-mempool transaction from getting mined.
Mempool validation uses imperfect heuristics to protect against DoS (and other reasons), so if you don't have full control over your transaction (sharing inputs with counterparty or signing ANYONECANPAY), there's almost always opportunity for pinning.
Our job in writing mempool code is to protect the node operator from DoS or incentive-incompatible transactions; protecting transaction senders from pinning attacks (especially if easily avoidable) is important but secondary.

## Examples

- Same txid different witness, [Witness Replacement](https://gist.github.com/glozow/d1ebe458ab2b6b60c3396ddcaef27bab) and [PR #19645](https://github.com/bitcoin/bitcoin/pull/19645)
- Transactions signed with ANYONECANPAY and signaling RBF can be pinned: [PR #23121](https://github.com/bitcoin/bitcoin/pull/23121)
- LN Penalty Commitment Transactions cannot replace each other. Described in part 4 of [This Talk](https://github.com/glozow/bitcoin-notes/blob/master/Tx%20Relay%20Policy%20for%20L2%20Devs%20-%20Adopting%20Bitcoin%202021.pdf)

## Solutions

- Improve the heuristics used to narrow the window of pinning opportunity
- Make RBF better
- Implement the ability to reason about multiple transactions together, aka Package Mempool Accept

## Mitigations

Almost every pinning attack is mitigated if you can put a good feerate on the transaction.

## More resources

- Bitcoin Development Podcast episode 3
- T-Bast's [Lightning Pinning Attacks](https://github.com/t-bast/lightning-docs/blob/master/pinning-attacks.md)
