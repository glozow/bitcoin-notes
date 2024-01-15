# Index of Discussion on RBF Pinning, V3, EA

## Background and Motivation

### LN discussions about pinning

Q: Has LN ever cared about or done anything to work around pinning? [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1876316575)

- Original [RBF Pinning with Counterparties and Competing Interest](https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-April/002639.html) post describes RBF pinning including non-inherited signaling, Rule 3, and package limits
- [Pinning : The Good, The Bad, The Ugly](https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-June/002758.html)
- [Tx introspection to stop RBF pinning](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-May/020458.html) 
- [pinning attacks](https://github.com/t-bast/lightning-docs/blob/master/pinning-attacks.md)

Q: Are there any cool future protocols that would be hurt by pinning? Does this "only" benefit LN?
- [eltoo pinning](https://gist.github.com/instagibbs/60264606e181451e977e439a49f69fe1)
- [vaults](https://jameso.be/vaults.pdf) (see "Managing fees safely" on page 8)
<!-- - [ark](fixme) -->

## The proposal itself

### V3 design decisions

#### Why is the child size 1000vB?

- Previously 4000vB, but reduced after realizing 1000vB was sufficient [1](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1198039341) [2](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1198946822) [3](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1201038111)

- Discussion about making it even smaller than 1000vB to make the pinning window even more narrow [1](https://petertodd.org/2023/v3-txs-pinning-vulnerability#restrict-v3-children-even-further)
  - Taproot output numbers:
    - 4-inputs-1-output: 283.5 vbytes
    - 7-inputs-2-outputs: 499 vbytes
    - 15-inputs-2-outputs: 959 vbytes

#### Why not allow multiple parents?

Q: Why not allow multiple parents to enable batched fee-bumping? [1](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/20?)

- This was the original plan, but it doesn't work. The pinning mitigation would be undermined by an attacker being able to bring in another parent [1](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1320295394)

### Why not incorporate PR 22871?

Q: Why not use this opportunity to discourage usage of disable locktime bit? [1](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1303979737)

Response:
- Summarized reasoning: [1](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1828052025)
- That proposal seems to break some things [2](https://github.com/bitcoin/bitcoin/pull/25038#pullrequestreview-1196723893)
- Not a true "standard version bump" and maybe not useful for upgrades [3](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1828066579)

### Why do only v3 transactions get to be 0 fee?

Q: Why not allow non-v3 transactions to be 0 fee?

- Allowing bypass of minrelayfeerate in general was originally merged in [PR #22674](https://github.com/bitcoin/bitcoin/pull/22674)
- There was discussion about unsafety and DoS:
  - [logs](https://gnusha.org/bitcoin-core-dev/2022-12-16.log)
  - [description of problems](https://github.com/bitcoin/bitcoin/pull/26933#issue-1550856696)
  - [implementation in test](https://github.com/glozow/bitcoin/commit/5a1df55c0be859632f85abe7acc2eb903964fa03)
  - [#26933](https://github.com/bitcoin/bitcoin/pull/26933) and [#27018](https://github.com/bitcoin/bitcoin/pull/27018) were the two solutions considered
    - [1](https://github.com/bitcoin/bitcoin/pull/26933#issuecomment-1412320818) motivated #27018
    - but #27018 had problems too [2](https://github.com/bitcoin/bitcoin/pull/27018#issuecomment-1424742766)
    - [3](https://github.com/bitcoin/bitcoin/pull/27018#issuecomment-1426047213) pointed to this being a deeper issue
    - this is around the time eviction issues and cluster mempool started being discussed... [#27677](https://github.com/bitcoin/bitcoin/issues/27677) was opened
- We merged [#26933](https://github.com/bitcoin/bitcoin/pull/26933) disabling the bypass of minrelayfeerate through
  package CPFP
- We determined 0-fee would be safe with v3, and [#27018](https://github.com/bitcoin/bitcoin/pull/27018) would be okay due to
  restricted topology

## Criticisms of v3

Here is a list of concerns that people have had with v3, along with responses.

### Criticism: rule 3 pinning is possible with small transactions

- With very small transactions, attaching a 1000vB child could still add a significant amount of fees.[1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2023-December/022214.html) [2](https://petertodd.org/2023/v3-txs-pinning-vulnerability) 
  This means pinning isn't fixed.
- Responses
  - While the risk isn't 0, it has been reduced by a factor of 100x. This attack means you still might need to pay
  a little bit extra, but that's a huge improvement over the status quo. [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2023-December/022213.html) [2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1873490509) [3](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2023-December/022216.html) [4](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2024-January/022256.html)
  - The minimum transaction size should have at least 1 HTLC output, otherwise the attack does not cause funds to
    be stolen and is much less meaningful.
    [4](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2024-January/022256.html) [5](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/22)

### Criticism: rule 3 pinning is possible with large commitment transactions

- A revoked commitment transaction with 483 HTLCs (maximum allowed in protocol) could conflict, meaning you still might
  need to replace something large.
[1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1874723441)
[2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1886085872) 
A limit on HTLCs offered is needed, in addition to accepted [3](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1888377830).
- Responses:
  - This is a usage problem, not a policy problem. [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1887170261)
  - This issue isn't realistic, as LN implementation(s) already set the parameter to something much more reasonable/safe. [2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1887226712). You don't need a protocol change to explicitly limit the number offered. Just don't offer another HTLC. [3](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1888673524)

### Criticism: no consensus

Q: Do people think this is a good idea? Has there been "sufficient discussion?"

Links to indicate volume of discussion

- comments on the RBF improvements [thread](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-January/019817.html)
- comments on the RBF improvements [gist](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff)
- comments on the v3 [thread](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-September/020937.html)
- comments on [#25038](https://github.com/bitcoin/bitcoin/pull/25038)
- comments on [#28948](https://github.com/bitcoin/bitcoin/pull/28948)

<!-- Links to indicate L2 support for this idea... feels a little bit weird to do this -->
<!-- instagibbs "I really think this direction is somewhere we need to go" -->
<!-- - [link](https://github.com/bitcoin/bitcoin/pull/25038#discussion_r909641486) -->
<!-- ariard "it works well for Lightning usual flow and also upcoming dual-funding / splicing" -->
<!-- - [link](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1712350787) -->
<!-- - t-bast's eclair tests exercising v3 + package RBF logic [commit](https://github.com/ACINQ/eclair/commit/4f583b5725cba6594388d54c0b31affc1bf8cddf) [comment](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1161852823) -->
<!-- - t-bast "I'd rather wait for v3 transactions and package relay to move to a single ephemeral anchor, which fixes this issue altogether." -->
<!-- - [comment](https://lists.linuxfoundation.org/pipermail/lightning-dev/2023-December/004248.html) -->

Q: Is v3 useful? Has anybody tried it out or designed/built anything with it?

- LN Penalty with 0-fee, single-anchor commitment transactions
  - "Intended usage for LN" in [v3 post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-September/020937.html)
  - BOLTs spec changes [branch](https://github.com/instagibbs/bolts/commits/zero_fee_commitment)
    - TODO: add any notes from [LN spec meeting](https://github.com/lightning/bolts/issues/1127)
  - Implementation in Core Lightning: [branch]([https://github.com/instagibbs/lightning/commit/197362f6bd07fb9beac85c03a3fe770e01c52f15](https://github.com/instagibbs/lightning/commits/commit_zero_fees))
- [ephemeral anchors](https://github.com/bitcoin/bitcoin/pull/29001) is another policy proposal that builds on top of v3, with additional features
- eltoo implementation using v3 + ephemeral anchors: [post](https://delvingbitcoin.org/t/ln-symmetry-project-recap/359) [branch](https://github.com/instagibbs/lightning/tree/eltoo_support)
- eclair tests exercising v3 + package RBF logic: [commit](https://github.com/ACINQ/eclair/commit/4f583b5725cba6594388d54c0b31affc1bf8cddf), [comment](https://github.com/bitcoin/bitcoin/pull/25038#issuecomment-1161852823)

Q: Why hasn't a BIP been written and "accepted" before opening this PR? [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1874723441) [2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1876316575)

- There is no precedent that specifically a BIP is required for a policy change. BIPs are not an indication that an idea is good or approved. [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1875164441) [2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1876929590)

### Criticism: CPFP and anchors are bad

- Arguments / Links [1](https://petertodd.org/2023/v3-transactions-review#anchor-outputs-are-a-danger-to-mining-decentralization)
  - It takes up a lot of space to create + spend an output, and thus is inefficient and costly. It's inefficient, and thus "hurts decentralization".
  - Saving an output for CPFP cuts into how much money you can use for payments.
- Response
  - This is an argument to avoid exogenous fees as a user, not for CPFP improvements to be rejected. Yes, people use bad, centralized alternatives because the decentralized one is not efficient enough. That's exactly why we are trying to improve it.
    [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1873490509) [2](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/18?)
  - Part of the advantage of EA is reducing the footprint of anchor creation + spend. [2](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/6)

## Proposed Alternative Solutions

Q: What alternatives were considered?

Note that there is a longer term plan for cluster-based mempool including improved RBF rules, and v3 is part of the
roadmap because [removal of CPFP carve out is necessary](https://delvingbitcoin.org/t/an-overview-of-the-cluster-mempool-proposal/393#the-cpfp-carveout-rule-can-no-longer-be-supported-12).
Also note the ephemeral anchors proposal built on top of v3 which adds another set of features solving more problems.

Here is a list of alternative proposals and suggestions, grouped by category, starting with the ones that tend to come
to people's minds first.

### Alternatives: Knee-jerk solutions

These are knee-jerk and strawman suggestions that are always tossed in at the start. They help reminds us why some of
these RBF rules exist in the first place.

- Throw out Rule 3+4, replace by feerate only:  [summary and why it doesn't work](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#replace-by-feerate-only)
  - Relevant links: [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-February/019894.html) [2](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4093100#gistcomment-4093100) [3](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-February/019921.html) [4](https://petertodd.org/2023/v3-txs-pinning-vulnerability#replace-by-feerate)
- Bribe a miner to include or prioritize your transactions. Generally, out of band fees are bad, and not a good option for protocol design [1](https://github.com/t-bast/lightning-docs/blob/master/pinning-attacks.md#out-of-band-package-relay) [2](https://bitcoinops.org/en/topics/out-of-band-fees) [3](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/23?)
- Just use some static value (like ancestor score) as a miner score [4 options and why all of them are insufficient](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#mining-score-of-a-mempool-transaction).
  - Also see [incentive compatibility requirement](#Add-incentive-compatibility-requirement) below.
- (Big Hammer) just shrink the default descendant limit [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081602#gistcomment-4081602)
  - Concerns: too big hammer, would require shrinking default tx size too [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081617#gistcomment-4081617)
- (Huge Hammer) "If we had a blank slate," just don't allow unconfirmed outputs to be spent [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4046995#gistcomment-4046995)
- Add package relay [1](https://petertodd.org/2023/v3-transactions-review#recommendations) [2](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2021-September/019464.html)
  - Simply adding package RBF with existing RBF rules does not address the pinning problem [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#package-rbf)

### Alternatives: Skip Rule 3+4 in special scenarios

When it is obvious that a replacement is going to confirm way faster but is pinned (e.g. because it would confirm in the next block), skip Rule 3+4, since they get in the way.

- Allow an "Emergency RBF" to bypass 3+4+5 if it would be in the next block. [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2019-June/016998.html) [2](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2019-June/017004.html)
- Have different rules for “next block” replacements vs “rest of mempool” (requires next block template to be cached) [2](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#fees-in-next-block-and-feerate-for-the-rest-of-the-mempool) 
- Concerns
  - Incentive compatibility, free relay, DoS [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2019-June/017002.html) [2](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2019-June/017020.html)
  - Assessing "top of mempool" and "close to confirming" is clunky and messy [3](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4044451#gistcomment-4044451) [4](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-February/019879.html)

### Alternatives: fix LN instead

Q: Is this just a problem with how LN anchors are used?
Q: Can this be fixed in the LN spec instead?

#### Alternatives: Presign Transactions at different feerates

- Presign transactions at different feerates [1](https://github.com/lightning/bolts/pull/1036) [2](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1873517708)
- Responses
  - Balance allocated for high feerate dramatically reduces the amount that can be used for payments [1](https://github.com/bitcoin/bitcoin/pull/28948#issuecomment-1873793179)
  - Cumbersome for nodes to manage the state and keep track of so many more signatures
  - Protocol will be more convoluted to negotiate what feerates to sign everything and figure out what's trimmed for each version of the tx <!-- [link](FIXME) -->
  - You still run the risk of not having predicted how high the feerates would go - need at least 1 anchor to add more fees
  - Introduces huge delays and risk of redundant overpayments due to the amount of signatures needed
    [2](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/6) [3](https://delvingbitcoin.org/t/v3-transaction-policy-for-anti-pinning/340/5)

#### Alternatives: Get rid of to_remote anchor

- The remote anchor output is "redundant" [1](https://lists.linuxfoundation.org/pipermail/lightning-dev/2023-December/004246.html)
- Response
  - Note rationale for having 2 anchors + carve out [1](https://github.com/lightning/bolts/blob/master/03-transactions.md#to_local_anchor-and-to_remote_anchor-output-option_anchors) [2](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-November/016518.html)
  - No [3](https://lists.linuxfoundation.org/pipermail/lightning-dev/2023-December/004248.html)

### Alternatives: Add incentive compatibility requirement

This is a crucial part of the long term solution. However, mempool today (i.e. no cluster tracking/limits) is unable to
support it. V3 is designed to be cluster size 2 so that we can add this rule for v3 transactions. Adding this rule for
all RBFs is something we can do in the future.

- Just use some static value (like ancestor score) as a miner score: [4 options and why all of them are insufficient](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#mining-score-of-a-mempool-transaction).
  - Relevant links (this was explored a lot) [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-January/019841.html) [2](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081349#gistcomment-4081349)
- Just add a miner score calculator: see [implementation in Bitcoin Core](https://github.com/bitcoin/bitcoin/pull/27021) which is only used in wallet. Cluster limits are theoretically unbounded [1](https://github.com/bitcoin/bitcoin/blob/17e33fb57842e4080e6768c074654bd1fd7f8696/src/test/miniminer_tests.cpp#L623-L628) and can be very large in practice [2](https://twitter.com/murchandamus/status/1352850189686599680) so this isn't appropriate for p2p-side validation.

### Alternatives: Rate-limiting

Rule 3+4 are anti-DoS rules. Instead of using fee-related rules, implement rate-limiting elsewhere.

- Remember the relay bandwidth used per transaction (and its replacements) and add fee rule based on that [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2019-June/017024.html)
- Rate limit replacements, e.g. by outpoint (instead of using Rule 3+4 for DoS)
  [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081349#gistcomment-4081349)
  [2](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-January/019820.html )
  [3](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081349#gistcomment-4081349)
  - Concerns
    - Free relay problems and high complexity/difficulty of enforcing rate-limiting [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4081559#gistcomment-4081559)
  - Rate limiting per node doesn't really work either [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-February/019921.html)

### Alternatives: Other opt-in schemes

Enable users to opt in to some different set of policy rules.

- Opt-in descendant limits: set a bit meaning “don’t add more than X descendants”. This comment is what v3 was originally based on. [1](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4058140#gistcomment-4058140)
- Original “Priority Tx” idea: set a bit meaning don’t add descendants unless it would be confirmed “really soon” [2](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff?permalink_comment_id=4044451#gistcomment-4044451)

### Alternatives: protocol changes

#### Alternatives: Change how transactions are relayed

- To support RBFs and especially iterative batched RBFs, allow relaying "txdiffs" which only require re-relay of signatures + new/modified outputs. This means you don’t need to pay for as much extra bandwidth in Rule 3 [1](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-January/019820.html)

### Alternatives: soft forks

- [SIGHASH\_GROUP](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2023-January/021334.html)
- [Transaction sponsors](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2020-September/018168.html)
