# OP_RETURN PR Merge Notes

This is a copy of my [comment](https://github.com/bitcoin/bitcoin/pull/32406#issuecomment-2955614286) on PR #32406 prior to merging it. Mirroring because it has been buried under other comments.

After weighing the technical arguments for/against this change and considering the objections [0], I believe this is ready for merge. Below is my handwritten summary outlining why I think so. I’m including (non-exhaustive list of) links where possible, so if you’d like to analyze the same sources without my personal bias, please do.

The concept was discussed here, #32359, #28130, #32381, the mailing list / google group [1], delving [2][3][4], stacker news [5], twitter, etc.

The primary motivation for this PR is to correct a mismatch between the harmfulness and standardness of data storage techniques. It makes the (prunable) OP_RETURN option available so that data is not stuffed into unprunable outputs. While proponents of the PR aren’t enthusiastic about data storage as a use case, the existing standard methods (e.g. bare pubkeys) involve bloating the UTXO set, representing a long term cost to the network. This concern is not merely theoretical, as there are examples of designs and transaction utilize the more harmful techniques [1].

Another motivation is to support Bitcoin’s public, decentralized market for blockspace, by not making transaction relay policy stricter than what is reliably mined [14]. The OP_RETURN limits are among very few policy rules that exist solely to discourage use. These restrictions push people - e.g. ones who don’t want to bloat the UTXO set - towards direct-to-miner submission, which harms mempool utility and creates centralization pressure. This is consistent with the rationale to change the default value of `-mempoolfullrbf` to 1.

To elaborate, the PR helps avoid a world in which an economically relevant volume of transactions is sent using direct submission. We move closer to that world when large economic actors (L2s, exchanges, etc.) choose to build direct relationships with large miners in order to get nonstandard transactions mined. If widely used, central submission services undermine the permissionless design of PoW-based consensus, hurt the censorship rtance and privacy of transaction broadcast, and destroy the fast block propagation our network has enjoyed for many years… all while not preventing the nonstandard transactions we dislike. Such services exist and are in use today; it is worth trying to reduce reasons to use them. [6][7]

These are strong motivations to change the default. I also believe all of the objections have been adequately addressed [0]. Summarized below:

(1) Some users want options to control what kinds of data-carrying transactions they allow on their nodes.

This PR, replacing #32359, doesn’t remove the `-datacarrier` or `-datacarriersize` options. Contrary to what many are saying, the PR does not force the user to accept larger datacarrier transactions in transaction relay. Setting `-datacarrier=0` still turns it off, and `-datacarriersize=83` gives you the original default (the same amount of data but across 1 or more outputs).

Some developers still believe the option should be removed, but there is consensus for waiting atst 1 release like we did for `-mempoolfullrbf`. No timeline is set for removal.

The options are deprecated in this PR, meaning they remain usable without any extra steps, but are discouraged through a warning message. This discouragement comes from the development philosophy that all user options should either come with clear recommendations for how to use them or, if no recommendation can be made, they should not exist or be discouraged. In essence, “don’t offer users footguns”. It seems that not all frequent contributors agree with this philosophy, but I think the conversation can be deferred until there is a proposal for removal of the option.

(2) Disapproval of the “arbitrary data storage use case” on the Bitcoin network (there are many many tweets that I am not linking here, but yes I did see them) [11][12][13]

(2a) Belief that Bitcoin Core default policy should be used to prevent certain kinds of use cases.

It is not possible for Bitcoin Core to prevent certain kinds of transactions fromed. It is software run only voluntarily by users (which may include miners). Demanding that Bitcoin Core prevent certain transactions from being mined reflects a misunderstanding of the relationship between open source software users and developers.

In earlier years, mempool policy helped shape wallet behavior *proactively* when miner and user software was more homogeneous. Once transactions are regularly mined, restrictive policy has the effect of blinding nodes to transactions that are later included in blocks. This rationale was used to change the default of `-mempoolfullrbf` in #30493.

(2b) Even if Bitcoin Core cannot prevent certain use cases, it should still not relay transactions that are not in service of its monetary purpose to discourage them.

First, there is nontrivial harm in blinding a node to transactions that are likely to be mined, as described above.

Other Bitcoin clients consider filtering non-monetary uses of Bitcoin in transaction relay as one of their development priorities, which is their prerogative. Some people have also opened pull requests to “fix the filters” within Bitcoin Core (e.g. #28408, #29520, #29187).

The reactions to these pull requests *did* show that, in general, using mempool policy to “filter” transactions is controversial amongst contributors.

Briefly summarized: these kinds of policy rules are impossible to implement comprehensively, are not appropriate for protocol-level code, and cannot compete with economic demand. The “spam” applications operate on hype cycles and can change storage methods instantly; policy changes take at least 6 months to be deployed and even longer to be widely adopted (if they are at all). Ultimately, people who work on Bitcoin to enable censorship resistant payments likely don’t want to work on code that judges transactions based on their use case.

While Bitcoin Core aims to have no central authority directing it, the project’s direction is decided by its contributors, and the vast majority of them don’t seem to hold4].

Similarly, another Bitcoin client could focus on hyper-optimizing for performance on specific hardware and drop support for others; Bitcoin Core’s contributors might not pursue that due to their priority of making node running highly accessible. Another project might prioritize rapid response to security vulnerabilities and build in auto-updates; Bitcoin Core’s contributors would likely reject this kind of developer-user relationship. (There aren’t collective statements about these beliefs, I’m just giving examples that I personally think are plausible).

(2c) Concerns that this encourages more arbitrary data storage, either because it is made cheandardness represents what is “kosher,” or there is an ulterior motive to purposefully enable it. “The filters work, so don’t remo”

The purpose of this PR is not to encourage people to flood blocks with OP_RETURNs, just as changing the default of `-mempoolfullrbf` to 1 was not a signal that people should try to cheat zeroconf merchants. The commentary across all platforms is overwhelmingly in favor of Bitcoin’s monetary use case, even amongst those who think that arbitrary data storage is useful. Software users should look for projects whose developers demonstrate commitment to the monetary use case through their work, not through social media virtue signaling.

The on-chain cost has not changed. OP_RETURNs are more expensive than non-Bitcoin perpetual storage methods. Within Bitcoin, OP_RETURNs cost proportionally more than typical payments that benefit from the witness discount. While it is true that the (small) additional cost of using private mempool services may be saved, as summarized above, it is imant that miners don’t make significant extra money from mining these transactions.

(3) Belief that large OP_RETURNs are spam, harmful, abusive, or dangerous to the network and should be discouraged in transaction relay on those grounds [15].

There are categories of transactions that policies should discourage: upgradeable fields, security and DoS problems, and transactions that make it too difficult to assess incentive compatibility [16][17]. OP_RETURN isn’t expensive to validate, doe impact incentive compatibility assessment, has no potential for UTXO set pollution, etc. which is why it does not meet these criteria. Instead, people seem to use the term “spam” as an inaccurate name for undesirable transactions [18].

The introduction of the limits was indeed intended to protect network resources at a timen these outputs were not prunable, blocks were mostly empty, and 1sat/vB was almost free [19]. Contrast that with today’s environment, where prunable outputs represent a relatively low cost to the network and there ests a substantial economic deterrent to filling blocks with OP_RETURNs.

One significant cost to Bitcoin is reputational (many of us dislike the association with popular uses of OP_RETURN). But this is far outweighed by other goals like compact block reconstruction and mempool utility.

(4) Consideration for the approach of only raising the limit slightly, for example to the threshold at which OP_RETURN becomes more expensive than inscriptions [20][21].

Going back to the primary principle of not restricting policy further than what miners are confirming (unless there is another reason like DoS), a small increase would not achieve this PR’s intended purpose [22].

[0] https://datatracker.ietf.org/doc/html/rfc7282#page-7 
[1] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/mJyek28lDAAJ
[2] https://delvingbitcoin.org/t/addressing-community-concerns-and-objections-regarding-my-recent-proposal-to-relax-bitcoin-cores-standardness-limits-on-op-return-outputs/1697
[3] https://delvingbitcoin.org/t/op-return-limits-pros-and-cons/1645/
[4] https://delvingbitcoin.org/t/a-comprehensive-op-return-limits-q-a-resource-to-combat-misinformation/1689 
[5] https://stacker.news/items/971277 
[6] https://x.com/mononautical/status/1920221641948246081 
[7] https://x.com/oomahq/status/1930401993341776173 
[8] https://stacker.news/items/971277?commentId=971285
[9] https://delvingbitcoin.org/t/addressing-community-concerns-and-objections-regarding-my-recent-proposal-to-relax-bitcoin-cores-standardness-limits-on-op-return-outputs/1697#p-5007-the-datacarrier-option-should-be-kept-on-bitcoin-core-regardless-of-whether-the-default-is-changed-26
[10] https://x.com/GrassFedBitcoin/status/1921219038430015758 
[11] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/-QPhqSMwEQAJ
[12] https://x.com/wk057/status/1917235710781690171 
[13] https://x.com/GrassFedBitcoin/status/1921219038430015758 
[14] https://bitcoincore.org/en/2025/06/06/relay-statement/ 
[15] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/yoSAe-aaDgAJ 
[16] https://bitcoinops.org/en/blog/waiting-for-confirmation/#policy-for-protection-of-node-resources 
[17] https://bitcoinops.org/en/blog/waiting-for-confirmation/#network-resources 
[18] https://delvingbitcoin.org/t/the-spam-problem-of-bitcoin-and-unpermissioned-broadcast-networks-in-general/1692/2
[19] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/GRKe8kq-EgAJ 
[20] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/6PYyNG6UAQAJ 
[21] https://bitcoin.stackexchange.com/questions/122321/when-is-op-return-cheaper-than-op-false-op-if
[22] https://groups.google.com/g/bitcoindev/c/d6ZO7gXGYbQ/m/lP69f0KaAQAJ

Thank you to sipa for helping review this.
