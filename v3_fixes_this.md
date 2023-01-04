# RBF Problems (Part 2) and How V3 Fixes This

## RBF Problems and Limitations

Here is a summary imo the most problematic RBF limitations. Last year's
[post](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff) included most of these,
along with other more minor limitations and grievances voiced by devs.

### Package Limits

#### Descendant Count Overestimation

When a candidate transaction for submission to the mempool
would replace mempool entries, it may also decrease the descendant count of other mempool entries.
Since ancestor/descendant limits are calculated prior to removing the would-be-replaced
transactions, they may be overestimated. Also see [Single-Conflcit RBF Carve
Out](https://github.com/bitcoin/bitcoin/blob/master/doc/policy/mempool-limits.md#single-conflict-rbf-carve-out).

Note: also note the scenario in which multiple direct conflicts share mempool descendants and hit
the 'Rule 5' limit.

#### Below-Min-Relay-Fee Dependencies

"What happens if we replace something that was bumping an otherwise-too-low-feerate transaction?"
For example, if we replace something that was bumping a 0-fee transaction.

TLDR, we need to remove them from the mempool. See
[gist](https://gist.githubusercontent.com/glozow/f0ddaa36290d7263a67e64bd7c0b8a92/raw/c0005b7dedff3f376575de10892d0d4aee3844f8/rbf_fee_dependencies.md)
for a more detailed explanation.

We can call these "fee dependencies" perhaps; while they are not descendants of the to-be-replaced
transactions (and thus dependent due to consensus rules), their presence in the mempool depends on
these transactions' fees. After the replacement, they should not be kept in the mempool, as they
could be relayed and a new transaction would be allowed to spend their inputs.

There are 2 approaches, both of which can be quite complicated with current package limits:

1. Remove the transactions after the replacement happens. As shown in the "worst case scenario"
   in the gist, this could be 2400 additional transactions. This exceeds the amount of mempool
traversal we're comfortable with.

2. Calculate the transactions to include them in the 100-tx "Rule 5" limit. This approach can
   similarly increase the amount of work done; we would need to calculate the post-replacement
descendant feerate of all conflicts' ancestors.

For now, we should disallow all transactions below min-relay-feerate, even if package CPFP was used
(transactions below min mempool feerate are fine). This means no 0-fee transactions, even with
package relay.

See [IRC discussion logs](https://gnusha.org/bitcoin-core-dev/2022-12-16.log) on this subject.

### Fee-Related

#### Incentive Compatibility Checks

Theoretically, a replacement transaction should confirm faster than the one it replaced. This means
it should be more incentive compatible for the miner to include in a block.  With current possible
package topologies, the "incentive compatibility score" is difficult to precisely calculate short of
building a block template (see [this "mining score"
explainer](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#mining-score-of-a-mempool-transaction)
for more details).

Various heuristics exist (e.g. combination of comparisons using ancestor feerate and individual
feerate) but it is unclear whether they are acceptable; see discussion in
[#23121](https://github.com/bitcoin/bitcoin/pull/23121) and
[#26451](https://github.com/bitcoin/bitcoin/pull/26451).

#### Pinning Through Absolute Fee Rules

RBF rules require the replacement transaction pay a higher absolute fee than the aggregate fees paid
by all original transactions. This rule seems to be the [most
headache-causing](https://gist.github.com/instagibbs/b3095752d6289ab52166c04df55c1c19#bip125-rule3).

Suppose Alice and Mallory have presigned transactions A and B, respectively, which conflict with one
another (e.g. commitment transactions for an LN channel together). Mallory broadcasts B first and
can increase the fees required for Alice to replace B by attaching a low-feerate, high fee child of
B. Here are two variants:

1. Attaching transaction(s) that descend from B and pay a feerate too low to fee-bump B through
   CPFP. For example, assuming the default descendant size limit is 101KvB and B is 1000vB paying a
feerate of 2sat/vB, adding a 100KvB, 2sat/vB child increases the cost to replace B by 200Ksat.

2. Adding a high-fee descendant of B that also spends from a large, low-feerate mempool transaction,
   C. The child may pay a very large fee but not actually be fee-bumping B if its overall ancestor
feerate is still lower than B's individual feerate. For example, assuming the default ancestor size
limit is 101KvB, B is 1000vB paying 2sat/vB, and C is 99KvB paying 1sat/vB, adding a 1000vB child of
B and C increases the cost to replace B by 101Ksat.

### Signaling

Note: In most scenarios we can consider signaling and non-signaling-related RBF rules and
limitations to be orthogonal.

#### BIP125 Inherited Signaling

Any descendant of an in-mempool transaction which signals replaceability is also replaceable (i.e.
it will be evicted if its ancestor is replaced). As such, it "inherits" signaling, and a receiver
should treat it as replaceable. However, a transaction that only conflicts with this one will be
rejected due to it not signaling BIP125 replaceability *explicitly*.

#### Pinning Through Opt Out

If there is a way for a transaction to opt out of (or not opt in to) being replaceable, one of two
counterparties with conflicting transactions can "pin" by first broadcasting a transaction that does
so. The other counterparty cannot replace the first transaction regardless of fees. For more
specific examples, see [LN DoS
post](https://lists.linuxfoundation.org/pipermail/lightning-dev/2021-May/003033.html) from ariard.

AFAICT this problem exists as long as signaling requirements exist. Note this is just pointing out a
property of these rules; it is not an endorsement of full RBF.

## V3 Advantages

### v3 Properties

1. A v3 transaction in mempool cannot have more than 1 descendant.
2. A v3 transaction in mempool cannot have more than 1 ancestor.
3. When the descendant of a v3 transaction is being replaced, there must be exactly 1 replacement transaction and 1 to-be-replaced transaction.
4. When a v3 transaction is being replaced, it as either 0 or 1 fee dependencies.
5. There is no difference between a v3 transaction having "explicit" and "inherited" replaceability signaling.
6. The miner score of a transaction is equal to the minimum between its ancestor feerate and individual feerate.
7. When the descendant of a v3 transaction is being replaced, its descendant count does not change, and its descendant size changes by the difference between the replacement and to-be-replaced transactions.
8. Given an unconfirmed v3 transaction of size `s` paying fees `f`, a maximum-size child paying the same feerate pays  `f/s * 1000` in fees.

### v3 Fixes This

Descendant Count Overestimation: due to [property](#v3-Properties) #7, RBF carve out is not needed.
Since no two v3 transactions can share a descendant, `GetEntriesForConflict` also will not
overestimate.

Below-Min-Relay-Fee Dependencies: due to [property](#v3-Properties) #4, it is feasible to calculate
fee dependencies ahead of time and/or remove them afterwards, with reasonable limits. As such, 0-fee
v3 transactions can be allowed.

Incentive Compatibility Checks: due to [property](#v3-Properties) #6, it is feasible to add a RBF
rule comparing the incentive compatibility / "miner" scores of replacement and to-be-replaced
transactions.

Pinning Through Absolute Fee Rules: [properties](#v3-Properties) #1 and #8 make the cost to replace
a v3 transaction much less variable. An attacker can attempt to raise the cost of replacement by
attaching a descendant, but can only do so by a small amount without CPFPing it.

### v3 Allows for New Stuff

Here are some exciting possibilities with v3:

- 0-fee transactions
	- [Ephemeral Outputs](https://github.com/bitcoin/bitcoin/pull/26403) Proposal by instagibbs
- Package RBF
- Potential elimination of double anchor outputs and, subsequently, [CPFP Carve
  Out](https://github.com/bitcoin/bitcoin/blob/master/doc/policy/mempool-limits.md#cpfp-carve-out)

## V3 Disadvantages

### General Limitations

V3 disallows some previous patterns of usage, such as batched fee-bumping (ariard: batched bumping
would be [unsafe anyway](https://github.com/bitcoin/bitcoin/pull/22674#issuecomment-900352202)) or
creating long chains of unconfirmed transactions, multiple anchor outputs, etc. This means some
wallets and users might not want to use v3.

V3 is an easily-identifiable property of a transaction which could be used to fingerprint users and
software that use it.

It can be argued that, since the restricted package limits are not needed for DoS reasons, they are
not more incentive compatible for a miner to adopt. For example, instead of using these rules, they
could just allow all v3 transactions under the same policy as v2 and accept a hypothetical 3rd
descendant which pays very high fees. However, since aforementioned [v3 properties](#V3-Properties)
allow miner/mempool policy to determine incentive compatibility more accurately, a miner who wants
to earn more money could be *more* interested in using these v3 rules.

V3 does not address ["pinning through opt out"](#Pinning-Through-Opt-Out), though I consider this out of scope.

## Alternatives Considered

... and why they don't work (unless you can help figure out how to fix the problems!).

### Multi-Parent V3

The v3 proposal at some point allowed v3 transactions to have multiple ancestors, which would allow
for batched fee-bumping. There are 2 major problems:

1. It doesn't solve the [second variant](#Pinning-Through-Absolute-Fee-Rules) of pinning through
   absolute fee using a high-fee descendant with an additional large, low-feerate ancestor,
described [above](#Pinning-Through-Absolute-Fee-Rules).

2. Difficulty in handling [fee dependencies](); allowing just 1 parent means `n` replacements can
   only have `n` fee dependencies, while allowing 24 parents could mean `24 * n` fee dependencies.

### Non-Absolute-Fee-Based RBF Policy

Given that the "Rule 3 and 4 Pinning" problems are so bad, there have been many ideas for a new
replacement policy that allows replacements to *not* pay more in absolute fees (i.e. get rid of Rule
3 and/or Rule 4). See [this
section](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#replace-by-feerate-only) of
last year's doc, as well as the discussions on
[these](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-January/019817.html)
[two](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-March/020095.html) mailing list
posts and end of the
[gist](https://gist.github.com/glozow/25d9662c52453bd08b4b4b1d3783b9ff#replace-by-feerate-only).

The main concern is DoS: we have priced network bandwidth for transaction relay at 1sat/vB. We'll
consider it a DoS vulnerability if someone can get the node (and network) to relay transaction data
at a cost less than that.

Consider a rule where the fee can stay the same (get rid of Rule 4) but the feerate must double. The
user can start out with 100KvB transaction, paying 1sat/vB. A user can reduce its size over and over
again, doubling the feerate each time until it gets too small, and end up paying 100Ksat for
100KvB(1 + 1/2 + 1/4 + ... log2(mintxsize)) -> approaches 200KvB. Basically we can relay
transactions for 0.5sat/vB.

If the fee is allowed to decrease (get rid of Rule 3 and 4), a 1sat/vB, 100KvB transaction can be
replaced by a 100vB transaction paying 200 sats. That's 200 sats to relay 100,200vB of transaction
data, which is less than 0.002sat/vB. It becomes quite cheap to replace large portions of the
mempool, decreasing both its average feerate and total absolute fees.


## Comments, Notes, etc.

- [instagibbs/policy.md](https://gist.github.com/instagibbs/b3095752d6289ab52166c04df55c1c19)
