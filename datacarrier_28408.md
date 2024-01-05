# PR 28408 Review

This is about https://github.com/bitcoin/bitcoin/pull/28408, "datacarriersize: Match more datacarrying"

## Contents
- [Background](#Background)
  - [`-datacarriersize` history](#datacarriersize-History)
- [ACKs by reason](#ACKs-by-reason)
- [NACKs by reason](#NACKs-by-reason)

## Background

By default, Bitcoin Core restricts the number of `OP_RETURN` outputs and amount of data embedded
using an `OP_RETURN` output for unconfirmed transaction. The default value is 80 bytes, and the
`-datacarriersize` configuration can be used to change limit on the amount of data. Since the
`-datacarriersize` option was introduced, it has only applied to `OP_RETURN`.

This PR updates mempool policy to restrict the amount of data that can be embedded in witnesses.
Accordingly, users that configure `-datacarriersize` would see the limit used to restrict
inscriptions as well as opreturns.

It does not implement a blanket way of identifying "arbitrary" embedded data in witnesses (as there
is no way to do so). It does check `OP_FALSE OP_IF ... OP_ENDIF` which targets inscriptions.

### datacarriersize History

Links of the history of `-datacarriersize` in chronological order:
- 20214-06-26: PR adding `-datacarrier` [merged](https://github.com/bitcoin/bitcoin/pull/3715)
- 2014-10-31: PR adding `-datacarriersize` [merged](https://github.com/bitcoin/bitcoin/pull/5077)
  - The default is set to `MAX_OP_RETURN_RELAY`. [link](https://github.com/bitcoin/bitcoin/pull/5077/files#diff-a1732fc4dc1526b294a41db3f2d3d5e863ec76e68ee3f73449618551f7a469ebR18)
  - The helptext is written as "Maximum size of data in data carrier transactions we relay and mine" [link](https://github.com/bitcoin/bitcoin/pull/5077/files#diff-b1e19192258d83199d8adaa5ac31f067af98f63554bfdd679bd8e8073815e69dR349)
- 2015-02: v0.10.0 is released. Its [release notes explicitly define](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.10.0.md#mining-and-relay-policy-enhancements) the term "data carrier" as pertaining to OP_RETURN transactions when describing `-datacarrier` and `-datacarriersize`.
- 2017-08-16: PR adding documentation for "datacarrier" is [opened](https://github.com/bitcoin/bitcoin/pull/11058)
  - "I was confused about what 'data carrier' meant, so I wanted to comment the `fAcceptDatacarrier` and `nMaxDatacarrierBytes` fields specifically"
  - The PR adds: "A data carrying output is an unspendable output containing data. The script type is designated as TX_NULL_DATA." [link](https://github.com/bitcoin/bitcoin/pull/11058/files#diff-4c44c096ea0d1ded9679ea69831cdd3879cb50c5cb829b20c740d96e17f53c8eR37-R38)
- 2023-06-06: PR to clarify helptext of `-datacarriersize` is [opened](https://github.com/bitcoin/bitcoin/pull/27832)
  - The helptext is changed to "Relay and mine transactions whose data-carrying raw scriptPubKey is of this size or less". [link](https://github.com/bitcoin/bitcoin/pull/27832/files#diff-b1e19192258d83199d8adaa5ac31f067af98f63554bfdd679bd8e8073815e69dR591)
- 2023-08-03: PR to clarify docstring of `-datacarriersize` is [merged](https://github.com/bitcoin/bitcoin/pull/27832)
- 2023-09-05: PR to change the code to apply `-datacarriersize` to `OP_FALSE OP_IF` and other patterns of data embedding is [opened](https://github.com/bitcoin/bitcoin/pull/28408)
- 2023-09-12: luke-jr files CVE-2023-50428, "datacarrier size limits can be bypassed by obfuscating data as code (e.g., with OP_FALSE OP_IF)"

## Summary of Comments

This is a summary of the arguments on the PRs, mailing list posts, and some twitter threads about #28408.

### ACKs by reason

If you feel I have misrepresented/omitted something you said, feel free to let me know.

#### "Stop inscriptions, which are spam"

These types of transactions are used for ordinals, NFTs, data-carrying, or some use case that is not
financial transactions. The traffic is "spam" and undermines the usage of Bitcoin for
payments due to high transaction traffic and fees.
- "these spam transactions make the real usefulness of Bitcoin more and more difficult to use."
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1813986420
- "inserting data [is] a trick and abuse of the taproot script."
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1849244134
- being able to embed random bytes is an "exploit"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1852422627
- "If Bitcoin is MONEY (it is!)... then non-monetary Txs should be reduced as much as possible"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1872925369
- "the cheerleaders for [ordinals] is the Ethereum, anti Bitcoin maximalists, 'we need to change
  Bitcoin culture' time wasting trolls."
https://github.com/bitcoin/bips/pull/1408#issuecomment-1430240866
- This is a "misuse of the network, which was meant for _financial transactions_ (the whitepaper,
  name and code point to this)... data storage... was not an intended use case"
https://github.com/bitcoin/bips/pull/1408#issuecomment-1430883728
- This is causing "network congestion" and "higher fees or slower processing times" and this is a
  "DDoS attack" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1857098045
- "issue is not with the inscriptions but with the astronomical fees in general"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1866837996
- "Bitcoin - the network - needs to be protected from spam RIGHT NOW"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1878334784

#### "Inscriptions and embedded data harm the network"

These types of transactions are costly for node operators and are harming the network in some way.
- "The transactions targeted by this pull-req. are a very significant source of prohibitive cost for
  regular node operators"
[https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735381194](https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735381194)
- "These transactions affect the decentralization of the network by increasing the cost of operating
  the nodes"
[https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735111336](https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735111336)
- "disproportionate and excessive storage of large data directly on the blockchain"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1857098045

#### "People want this"

Clearly there is user desire and a specific use case, so Bitcoin Core should offer this option. The
alternative is that people write and run patches, which can be unsafe.
- "Node runners need a builtin option to ignore all modern forms of datacarrying so they don't have
  to resort to manually patching their nodes."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1792205732
- "if developers do not help node runners defend themselves against this attack, they may have to
  resort to misappropriate means to strengthen their defense."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1793719771
- "I want to be in charge of my mempool policy and I want to decide what is spam and what is not"
  https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1816059282
- miners would want this "if they believed Bitcoin to be money and not just a permisionless,
  immutable blockchain, they would indeed filter the spam to make the MONETARY network usable"
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1872925369

#### "This just fixes datacarriersize to work as intended"
We limit data-carrying in OP_RETURNs. This should be applied to all methods of embedding arbitrary data in transactions.
This was always the "intent" of `-datacarriersize` and so this is a "bug fix."
**Note**: see [datacarriersize history](#datacarriersize-History).
- luke-jr considers it a bug that  `-datacarriersize` was not updated with other types of
  data-carrying, when segwit and taproot were introduced, and filed this as a bug/vulnerability
https://github.com/advisories/GHSA-9x7v-86jh-jjch
- "Bitcoin Core already standardizes the insertion of arbitrary data above 83 bytes and inscriptions
  are a diverted way to bypass this limit so it is a bug fix."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1849100398
- "Spam is already filtered at various levels in the code, and has been for over a decade. All this
  PR does is apply an existing limit on datacarriersize to data carrying of a different form of data
carrying that is clearly an unintended exploit."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1873573115
- "What is the purpose of the datacarrier limit if not to impose a limit on arbitrary data stored in
  transactions?" https://x.com/cguida6/status/1742723175543124294?s=20
- PR #29173, "The purpose of this standardization rule is not to target only the data contained in
  the raw scriptPubKey, but all forms of arbitrary data."
https://github.com/bitcoin/bitcoin/pull/29173

### NACKs by reason

Here is a summary of the arguments against this PR.

#### "This will not prevent inscriptions"

This will not stop inscriptions. It is unlikely (because it's incentive-incompatible) that miners
(and users of inscriptions of course) would employ this policy, which means it would have little effect
in stopping those transactions.
- "If only Ocean pool uses this and it remains a relatively small pool, it will have no effect. If
  it is widely deployed, it's trivial to circumvent."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1844981799
- "Beyond the immediate loss of inscription reveal transaction fee revenue, this  
would appear to be long-term incentive-incompatible for miners."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1833205912
- "It is very unlikely that minres will give up that source of revenue. Censoring those transactions
  would simply encourage the development of private mempools"
[https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735079576](https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1735079576)
- "The ordinals transactions will end up in the blockchain anyway, bypassing the mempool, so this PR
  does nothing to solve/mitigate the problem"
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1849289963
- "To the extent that this is an attempt to not just not _see_ certain transactions, but also to
  _discourage_ their use, this will at best cause those transactions to be routed around nodes
implementing this, or at worst result in a practice of transactions submitted directly to miners,
which has serious risks for the centralization of mining."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1877812112
- "inscription enthusiasts could maintain relay of inscriptions on the network by ensuring that a small fraction of the nodes on the network does not filter inscriptions" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1878746998
- "it is obvious that a block template built from a filtered mempool must result in a lower total block reward than one built from all unconfirmed transactions. This means that any miners filtering inscriptions reduce their own revenue to the benefit of non-filtering miners." https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1878746998

#### "We cannot write code to detect all embedded data"

In general, we cannot stop transactions that have arbitrary data embedded in them. Inscriptions exist amongst numerous ways to
embed data (which we cannot ever fully encompass). It may be best to leave the methods that are most
efficient wrt network resource costs.
- "There's no universal way to filter all present and future datacarrying styles. This invites an
  endless cat and mouse game inside very critical code paths."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1842754101
- trying to stop all types of data embedding "will cause this code to grow in complexity. And every time that
  happens there'll be a lot of pressure on maintainers to push it through quickly 'to stop the
spam'" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1844981799
- "as near as I can tell there is no sensible way to prevent people from storing arbitrary data in
  witnesses without incentivizing even worse behavior and/or breaking legitimate use cases."
https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2023-January/021372.html
- Some links related to why witness data is a more cost-effective way to embed data, and why witness
  data is discounted (not putting as much effort into summarizing)

#### "This change is potentially harmful"

This PR, which changes the default mempool policy, is potentially harmful to the individual node
operator and to the network.
- Excluding transactions that will be mined is harmful to a node. "The point of participating in
  transaction relay and having a mempool is being able to make a prediction about what the next
blocks will look like. Intentionally excluding transactions for which a very clear (however stupid)
economic demand exists breaks that ability" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1877812112
- "In the end, users running this patch still process blocks including inscriptions. They only harm their own feerate estimation, slow down their block validation, and are less useful peers to other nodes." https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1878746998
- Changing default policy is generally dangerous. Making previously-standard transactions
  nonstandard means that some people may now find it much more difficult to access their funds. "By
changing the default, instead of being opt in, it represents a potentially disruptive and unwelcome
change in behavior for miners relying on Bitcoin Core to construct block templates... this would
represent a mild form of confiscation, and should be avoided."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1833205912

#### Other points against the PR

- Generally, using mempool policy to discourage usage is now ineffective, even though it has been
  used that way in the past. "While non-standardness has historically been used to discourage
burdensome practices, I believe this is (a) far less relevant these days where full blocks are the
norm so it won't reduce node operation costs anyway and (b) powerless to stop transactions for which
an existing market _already exists_ - one which pays dozens of BTC in fee per day."
https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1877812112
- This attempt to "censor" transactions on the basis of use case is inappropriate. The free market
decides what Bitcoin's usage is.
  - "It's not up to us to tell how people should use bitcoin. If you think your design is more 'elegant'
then do it and let the free market decide which one is better." https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1850275514
  - "Bitcoin is a decentralized permissionless network... anyone can use their bitcoin in whichever manner they desire, regardless
how distasteful (for any reason) the use case" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1850654602
- This changes what `-datacarriersize` does out from underneath users, in addition to changing default policy. "it couples the policy on OP_RETURN output size and the new limits on data embedded in redundant script code, so that it's impossible to configure your node in a way that matches the default policy for 26.0 and earlier releases" https://github.com/bitcoin/bitcoin/pull/28408#issuecomment-1878831217
