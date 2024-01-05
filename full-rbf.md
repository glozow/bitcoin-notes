# Full RBF

This was last updated in October 2022. It is still on my todo list to update for the last year's
worth of discussions.

Disclaimer: this is my personal understanding from reading everything I can and speaking to as many
people as possible. I'll indicate when I'm giving my own opinion. Otherwise, I've tried to be
open-minded and fair but there may be unintentional biases.

## Background

### RBF and Full RBF

[Replace-by-Fee](https://bitcoinops.org/en/topics/replace-by-fee/) is a mempool policy that allows
nodes to decide between conflicting unconfirmed transactions based on feerate. Prior to this policy,
the mempool accepted whichever transaction it saw first.

- [Bitcoin Core #6871](https://github.com/bitcoin/bitcoin/pull/6871)
- [BIP 125](https://github.com/bitcoin/bips/blob/master/bip-0125.mediawiki)
- Bitcoin Core has used opt-in (BIP 125) RBF since 0.12.0

The definition of **Full RBF** has [changed over
time](https://bitcoinops.org/en/newsletters/2022/10/19/#fn:full-rbf). In this document, it means a
policy of accepting transaction replacements even if the original transactions did not signal BIP125
replaceability.

### Recently

June 2021: Antoine Riard posted about a plan to add a -mempoolfullrbf option in v24.0 (scheduled for
September/October 2022), soliciting opinions and concerns.
- [optech
  summary](https://bitcoinops.org/en/newsletters/2021/06/23/#allowing-transaction-replacement-by-default)
- [ml post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2021-June/019074.html)

June 2022: Antoine Riard opened [#25353](https://github.com/bitcoin/bitcoin/issues/25353) to add
-mempoolfullrbf option
- [optech summary](https://bitcoinops.org/en/newsletters/2022/06/22/#full-replace-by-fee)

July 2022: Bitcoin Core merged [#25353](https://github.com/bitcoin/bitcoin/issues/25353)
- [optech summary](https://bitcoinops.org/en/newsletters/2022/07/13/#bitcoin-core-25353)

October 2022: Dario Sneidermanis posted concerns about full RBF and the -mempoolfullrbf option in
Bitcoin Core creating problems for businesses accepting unconfirmed transactions as final. He
requested removal of the -mempoolfullrbf option from v24.0 to give Muun and other applications more
time to prepare.
- [optech summary](https://bitcoinops.org/en/newsletters/2022/10/19/#transaction-replacement-option)
- [ml post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/020980.html)

This post led to various discusssions and mailing list posts, mainly about full RBF in general:

- [Many](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/020981.html)
[responded](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021006.html)
emphasizing that the default Bitcoin Core RBF policy had not changed.
- Anthony Towns
  [posted](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021017.html) in
agreement with the idea that network-wide deployment of full RBF, not just the individual node
option, is on the table. He suggested, as a way to give protocols time to test and businesses time
to adapt, temporarily restricting the option to testnet-only and creating a timeline for deployment
of default true full RBF on mainnet.
- Sergej Kotliar
  [posted](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021056.html) about
issues with full RBF, disagreeing with the idea that double spend risk is already high and that LN
can replace on-chain "zeroconf" payments. He provided some data from Bitrefill's experiences. He
says that, in practice, "fewer than 1 in a million" double spend attempts succeed. He notes only 15%
of their payments use LN and a past experiment defaulting to bech32 simply drove users away. He
expects that, if Bitrefill stopped accepting unconfirmed payments, "the majority of the current 85%
of bitcoin users that pay onchain would just not use bitcoin anymore."
- John Carvalho
  [posted](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021011.html) about
general issues with RBF, believing it to make zeroconf payment risks less manageable. In the same
[post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021056.html) mentioned
above, Sergej Kotliar also described the free option problem as one of the issues with replacements
in general. See American call option section below.

Several full-RBF-related pull requests have been opened to Bitcoin Core.
-  [#26287](https://github.com/bitcoin/bitcoin/pull/26287) implemented the request to remove the
   option on mainnet. It was closed after opposition from several reviewers.
- [#26323](https://github.com/bitcoin/bitcoin/pull/26323) is a PR to enable full RBF by default, but
  at a predetermined time (May 1, 2023). If users set the  `-mempoolfullrbf=1` option, it does not
go into effect until then. Users can also set the `-mempoolfullrbf=0` option to continue requiring
signaling past that day.
- [#26305](https://github.com/bitcoin/bitcoin/pull/26305) is a PR to enable full RBF by default,
  implementing the second part of what Antoine had posted to the mailing list. It is not intended
for v24.0. Most reviewers are indicating concept ACK for v25.0 or some other later time.

## Summaries

This is my understanding of the situation after reading and speaking with people 1:1. There are
still people I haven't managed to get ahold of and there could be some biases here, but I've tried
my best and apologize if I've unfairly represented anyone's arguments.

### Full RBF in general

There seems to be 3 groups of thought:

1. we should actively move towards Full RBF

2. we should try to prevent Full RBF for now, but end up there later

3. we should try to prevent Full RBF from *ever* happening

The first position is largely held by protocol developers, and the second by some businesses. The
last position seems to be very rare.

#### Why we should actively move towards Full RBF

1. Full RBF is the natural state of the network. The point of Bitcoin blocks, PoW, etc. is to solve
   double-spending; there was never any guarantee of finality for unconfirmed transactions. When a
miner receives two conflicting transactions, the incentive-compatible policy is to take the one
giving them higher fees. Using an RBF policy helps nodes have a more accurate picture of which
transaction is likely to confirm. A security assumption of "miners will be nice" when a
non-signaling tx has a higher-feerate conflict, that is significantly weaker than "miners will do
the rational thing."

2. Full RBF is already observable, so we should be prepared to update our mempool policy to give us
   a more accurate view of what will be mined. If full RBF becomes widespread and my node is still
assuming opt-in to be honored, it will reject transactions that are likely to be mined and
potentially blind me to double-spend attempts.

3. Enabling full RBF closes various signaling-based DoS/pinning
   [attacks](https://lists.linuxfoundation.org/pipermail/lightning-dev/2021-May/003033.html).

Common counterarguments:
- Accepting unconfirmed transactions as final is actually safe in practice.
- LN attacks are also uncommon in practice.

#### Why we should try to prevent Full RBF for now

1. Full RBF will create a higher risk of double-spends for businesses accepting unconfirmed
   transactions as final. Accepting non-signaling unconfirmed transactions is unsafe in theory, but
currently quite safe in practice, and a common way for Bitcoin users to send fast payments. LN
exists, but the ecosystem is still building the technological and UX layers to make that option
accessible to many users, and adoption is still low. Removing the option of using on-chain
unconfirmed transactions might not actually encourage LN adoption, but drive users away instead.
[Dario Sneidermanis
post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/020980.html)


Common counterarguments:
- Zeroconf really isn't safe; double spends are possible today.
- If zeroconf is safe in practice, it's not really due to full RBF not happening, but because
  businesses are using precautions such as requiring high feerates and
[waiting](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021112.html) to
detect raced conflicting transactions in [other (sometimes many)
mempools](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021084.html).
Businesses are also typically protected
[legally](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021087.html) from
users double-spending them.

#### Why we should try to prevent Full RBF from ever happening

1. RBF in general creates a higher risk of double-spends for businesses accepting unconfirmed
   transactions as final. The current risk is close to zero. These businesses should be able to
continue making these assumptions because it enables "fast" on-chain payments.

2. [American call
   option](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021056.html): if the
exchange rate changes between transaction creation and confirmation, the user can replace the
transaction to "cancel" it and create a new one.

Common counterarguments:
- Full RBF is inevitable, especially when fees become a more significant part of block rewards.
  Trying to force people to do incentive-incompatible things is nonsensical and impractical in a
decentralized network. [Russell O'Connor
post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021037.html),[Antoine
Riard post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021067.html)
- The free call option [already exists today](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021056.html) with
opt-in RBF and may have [other
solutions](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021108.html).

### The -mempoolfullrbf option

#### Why we should remove the -mempoolfullrbf option for now

1. Existence of the option cannot be distinguished from Bitcoin Core endorsing it. Bitcoin Core has
   not turned it on by default, but by adding the option, has signaled that it's safe for users to
have this option.

2. Adding the option makes it easier to run full RBF, so miners *will* turn it on, increasing the
   chances of non-signaling replacements propagating in practice. Only a minority is enough for
non-signaled replacements to happen. [Dario Sneidermanis
post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/020984.html)

3. If this leads to full RBF before businesses are ready, they may be attacked and/or be forced to
   narrow the options for their (many) users. That could be bad for Bitcoin.

#### Why we should keep the -mempoolfullrbf

1. One user of a software product should not be able to take options away from other users. We have
   some users saying "I want the option to configure my personal node to do this" and other users
saying "I don't want other users to have this option because \_." It seems unreasonable to say
"yeah, sorry, you can't have this feature, not because we can't support it, but because another user
said so."

2. This is holding Bitcoin Core responsible for the decisions of individual node operators. It
   hasn't changed the default behavior. It added an option. Having this option doesn't mean full RBF
happens; full RBF could still happen if we removed it. [Pieter Wuille
post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021006.html)

Common counterarguments:
- If adding the option doesn't matter, then removing it shouldn't matter either. [Anthony Towns
   post](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021001.html)

### Questions and Factual Disagreements

I think it's worth having a section on these fundamental disagreements, as they cause people to talk
past one another in many discussions.

- The prevalence of full RBF on the network
	- Peter Todd [reports](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021012.html) that he has observed replacements of non-signaling transactions
	  using opentimestamps. He notes that they are rare, and it's possible that these
replacements are due to other factors.
	- He also
	  [posted](https://np.reddit.com/r/Bitcoin/comments/40ejy8/peter_todd_with_my_doublespendpy_tool_with/cytlhh0/)
about this in 2016. That thread reads similarly to this year's discussion.
- The current risk of double-spends by accepting "zeroconf"
- The level of support for RBF and LN in the Bitcoin ecosystem
- How much "notice" Bitcoin Core has given
	- Murch and others (particularly during the [irc meeting](https://www.erisian.com.au/bitcoin-core-dev/log-2022-10-20.html))
	  [say](https://github.com/bitcoin/bitcoin/pull/26287#issuecomment-1276444078) that "we have been talking about full-rbf for seven years."
	- Antoine Riard [posted](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2021-June/019074.html) to the mailing list in June 2021, more than 1 year before the option was merged.
	- David Harding
	  [notes](https://github.com/bitcoin/bitcoin/pull/26287#issuecomment-1289901007) that the
	post perhaps doesn't fully capture the potential impacts and *risks* of adding the option.
Many people believe it can directly cause full RBF to be common on the network, so it should have
been communicated that businesses must be ready for full RBF by then.

I have a few open questions, and would really appreciate being able to ask miners them:

- If v24.0 contains the `-mempoolfullrbf` option, will any miners turn it on? If so, how soon?
- If we removed the -mempoolfullrbf option, would any miners still end up doing full RBF (e.g.
  running with a patch)?

## Moving Forward

### Detecting Full RBF on the network

We should try to monitor how prevalent full RBF is on the network because, if it becomes very normal
to see non-signaling replacements, it should be our firm recommendation to turn `-mempoolfullrbf=1`
on. A few things to keep an eye on:

- Peter Todd's [opentimestamps](https://alice.btc.calendar.opentimestamps.org/). Each transaction
  has its fees listed; anything higher than 182sat is a non-signaled replacement.
- Individual experiments of non-signaled replacements.
- Double-spend attempts on Muun, Bitrefill, and businesses that accept unconfirmed transactions as
  final.
- Full RBF in other pieces of software. For example, implementing full RBF or adding behavior to
  assume replacements can happen without signaling.

### Bitcoin Core v24.0

Bitcoin Core v24.0 was [scheduled](https://github.com/bitcoin/bitcoin/issues/24987) for release 19th
of October 2022. Bug fixes also delayed the release, but I think this is the last blocker. I don't
think "we're too close to change anything" is a good argument, but the urgency exists.

Full RBF was [discussed](https://www.erisian.com.au/bitcoin-core-dev/log-2022-10-20.html) in the
weekly bitcoin-core-dev irc meeting. No decision was made to merge or move forward with any of
PRs #26323 or #26287. Many supported #26305, but for a longer time period (1-2 releases or 1-2 years
from now). Many disliked the idea of removing an option from users, especially if the option is
desired and a safe practice for the individual node operator.

The biggest question to me is "will adding this option cause miners to switch to full RBF?" and I
think it needs to be answered by miners and not through speculation. Just like full RBF proponents
cannot definitively say "miners will do it because it's rational," I don't think people can say
"miners will do it because it's easy to flip a config."

Dario posted an [analysis](https://gist.github.com/esneider/4eb16fcd959cb8c6b657c314442801ee) of the
available PRs from Muun's perspective. It is decidedly pro-full RBF but is interested in some
predictability. For example, if it is expected that everyone will switch to full RBF at a
predetermined time ~6 months from now, Muun has time to implement and deploy their solutions.

### Rollout Timeline

Multiple people have suggested a timeline for coordinated deployment of full RBF:

- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021026.html
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021017.html
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021099.html
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2022-October/021101.html

I personally also believe the safest way to deploy full RBF is in a coordinated fashion aligning
with when people agree the ecosystem would be ready. While this is not a consensus change, it is
much safer for everyone on the network to switch over at the same time.

As mentioned earlier, if full RBF is starts happening on the network and most Bitcoin Core users
don't have a way to configure their node to accept non-signaled replacements, their mempools become
inaccurate. Even if we monitor the network closely and miners actively communicate that they are
accepting non-signaling replacements, it is much safer to have nodes switch automatically than to
try to tell everyone to restart with `-mempoolfullrbf=1`.

A timeline would put pressure on businesses to figure technical and UX things out, but something
like 2 years would be very reasonable in my view. Similarly, if miners had been planning on
switching to full RBF after the 2024 halving (i.e. because fees matter more as the subsidy
decreases), this would line up with their plans so (I think) they probably wouldn't feel the need to
do it through a patch.

However, I also think that merging some kind of lockin-on-timeout activation can cause an onslaught of
accusations that Bitcoin Core is trying to force Full RBF. Trying to ask businesses who would be
affected by full RBF "when might you be ready for full RBF?" seems to always be met with "never!"
Though I think it's still worth trying.

### Businesses that need help dealing with full RBF

#### Payment Replacement Detection

#### Payment Replacement Prevention

