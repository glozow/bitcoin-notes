# Pinning Zoo

A pinning attack is a type of censorship in which the attacker takes advantage of mempool policy to prevent a transaction from confirming.
Mempool validation uses imperfect heuristics to protect against DoS (and other reasons), so if you don't have full control over your transaction (sharing inputs with counterparty or signing ANYONECANPAY), there's almost always opportunity for pinning.
Our job in writing mempool code is to protect the node operator from DoS or incentive-incompatible transactions; protecting transaction senders from pinning attacks (especially if easily avoidable) is important but secondary.

## Categorizations

### Type

The attack might (1) prevent your transaction from entering the mempool or (2) prevent your mempool transaction from being mined.

### Whether or not the transaction is modified

Again, all pinning attacks arise from your transaction not being entirely controlled by you. You might distinguish pinning attacks based on whether (1) the attacker mutates/modifies your transaction or (2) doesn't. Maybe they just attach descendants or publish their own transaction.

## Examples

### Witness Mutations

Same txid different witness, [Witness Replacement](https://gist.github.com/glozow/d1ebe458ab2b6b60c3396ddcaef27bab) and [PR #19645](https://github.com/bitcoin/bitcoin/pull/19645)

### RBF

LN Penalty Commitment Transactions cannot replace each other. Described in part 4 of [This Talk](https://github.com/glozow/bitcoin-notes/blob/master/Tx%20Relay%20Policy%20for%20L2%20Devs%20-%20Adopting%20Bitcoin%202021.pdf)

#### ANYONECANPAYs are all vulnerable to pinning by RBF

Transactions signed ANYONECANPAY | SINGLE or ANYONECANPAY |NONE can always be pinned, since attackers can change the transaction to add inputs and outputs

Transactions signed with ANYONECANPAY | ALL can still be pinned: [PR #23121](https://github.com/bitcoin/bitcoin/pull/23121). More specific Revault example:
![image](https://user-images.githubusercontent.com/25183001/145044333-2f85da4a-af71-44a1-bc21-30c388713a0d.png)

## Solutions

- Improve the heuristics used to narrow the window of pinning opportunity
- Make RBF better
- Implement the ability to reason about multiple transactions together, aka Package Mempool Accept

## Mitigations

Almost every pinning attack is mitigated if you can put a good feerate on the transaction.

## More resources

- Bitcoin Development Podcast episode 3
- T-Bast's [Lightning Pinning Attacks](https://github.com/t-bast/lightning-docs/blob/master/pinning-attacks.md)
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2020-May/017835.html
