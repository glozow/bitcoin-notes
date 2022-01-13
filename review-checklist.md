# Common PR Review Questions

People often ask "how do I get better at reviewing PRs?" and I'm not sure how to answer that other
than "review a lot of PRs" and "look at a lot of PR reviews that others have done."

### "Bad" Reviews

A "bad" review would be something like:

* I checked out the PR and ran all the automated tests. ACK.

* Not sure what this does, but it's trying to change wallet behavior. NACK.

* ACK (no explanation)

* NACK (no explanation)

### Great Reviews

A "good" review doesn't necessarily find a bug, or contain a ton of comments, or picks with a
fine-toothed comb. I think it just needs to have enough information so that maintainer or author can
determine how much weight to put on it. For example, any monkey can create 10 github accounts and
sybil att-ACK PR reviews.

- Commit-by-Commit thoroughness: https://github.com/bitcoin/bitcoin/pull/17331#pullrequestreview-663562523,
  https://github.com/bitcoin/bitcoin/pull/17331#pullrequestreview-665781489

- Testing/Benchmarking: https://github.com/bitcoin/bitcoin/pull/20827#issuecomment-1023108273

- A reACK that lists what happened in between:
  https://github.com/bitcoin/bitcoin/pull/20749#pullrequestreview-578845627

- Helpful notes for other reviewers: https://github.com/bitcoin/bitcoin/pull/20962#pullrequestreview-780869719

- https://github.com/bitcoin/bitcoin/pull/21061#issuecomment-851563105

- https://github.com/bitcoin/bitcoin/pull/23121#pullrequestreview-842354501

- https://github.com/bitcoin/bitcoin/pull/15169#pullrequestreview-262526428

- https://github.com/bitcoin/bitcoin/pull/19988#discussion_r499511223

- https://github.com/bitcoin/bitcoin/pull/19988#discussion_r498781706

You can leave a helpful review without being an expert:

- Clarifying what the review doesn't cover: https://github.com/bitcoin/bitcoin/pull/20749#pullrequestreview-570434073

- Summarizing what you think the PR does:
  https://github.com/bitcoin/bitcoin/pull/23443#pullrequestreview-823339788

- Asking questions: https://github.com/bitcoin/bitcoin/pull/19988#pullrequestreview-500252767

- NACK including personal and summary of others' reasons:
  https://github.com/bitcoin/bitcoin/pull/22871#pullrequestreview-763016994

- Describing exactly what you did to review:
  https://github.com/bitcoin/bitcoin/pull/20749#pullrequestreview-576608102

Lots more examples below as well.

### What is this?

I personally think a good review is one where I've asked myself a lot of pointed questions about the
PR and been satisfied with the answers to them. Sometimes, the same question applies to many PRs, so
I've made an effort to write them down here.

This is a list of questions I might ask myself while reviewing a Bitcoin Core PR.
It is not a list of *all* the questions I would ask while reviewing a PR. In fact, I don't think any
list of 100 questions could be sufficient for any specific PR.

**I do NOT recommend treating this as a checklist with which you review PRs.**

I think it's a good idea to create your own list of common PR review questions, and perhaps use
these examples as inspiration for generating those questions.

On the organization of these questions:

This list is approximately organized by the order in which I'd ask those questions. For me, the
nature of the question usually depends on what stage the PR is at and the extent of my own review.
Naturally, I start with conceptual questions, then approach-related questions, and then
implementation questions. Generally, I personally think it's useless to leave C++ syntax-related
comments on a draft PR, and would feel rude going back to "does this make sense" after the author
has addressed 20+ of my code organization suggestions.

## Conceptual

Before considering anything implementation-related:

- What type of PR is this? New feature, bug fix, performance, refactor, documentation, testing, etc.  Does it contain more than one of those categories?

- Does the PR take into account other work in the project (eg does it conflict unnecessarily with other PRs, or go in a different direction from other people’s work, etc).

- Could this PR be re-organized to make review easier?

- Could this PR be split up?

- Could the PR-splitting leave us in a weird intermediary state? examples: [sending sendrecon before
  you can do recon](https://github.com/bitcoin/bitcoin/pull/23443#pullrequestreview-823455718),
[a commit fails tests](https://github.com/bitcoin/bitcoin/pull/23075#pullrequestreview-827662306)

- Are all commits atomic? If a commit
  [fails](https://github.com/bitcoin/bitcoin/pull/23075#pullrequestreview-827662306), it's harder to
revert and breaks `git bisect`

- Could this just be a scripted-diff?

### Motivation

Is this PR sufficiently motivated?

Does the PR add a new feature?

- Is the feature useful for a significant number of users, or very few?

- Would this feature only benefit an extremely advanced user who should probably write a custom patch instead?

- Has anyone actually requested this? examples: [nonexistent future soft fork](https://github.com/bitcoin/bitcoin/pull/22871#issuecomment-915689161)

- Are there other features that would be enabled by this PR?

- If this PR is an improvement, how is it demonstrated?

	- Is there a bench? A simulation?

	- Is there a description of how to reproduce something manually?
[example race](https://github.com/bitcoin/bitcoin/pull/22577#issue-955282835)

	- Has it been tested within the context of the full network? How does it interact with other protocol features (e.g. compact block relay) or proposed improvements?

	- Did you verify the results yourself? example
	  [bench](https://github.com/bitcoin/bitcoin/pull/23157#pullrequestreview-775676379)

	- Did you evaluate the method used to gather measurements?

Does the PR solve a problem? Does it fix a bug?

- Is it a real bug or misuse of the software?

- Can the issue be solved simply with better documentation?
  [example](https://github.com/bitcoin/bitcoin/pull/22867#pullrequestreview-822532341)

### Downsides

What are the downsides of this PR, conceptually?

- What are the maintenance costs of this PR?

	- Does it require someone to update it at every release?

	- Is this PR introducing a bunch of hard-to-understand new code?

	- Is this PR introducing any new dependencies?

- Is it incompatible with another existing/proposed improvement?

- Is this compatible with all of the {operating systems, architectures, platforms, dependency
  versions} we want to support?  [example](https://github.com/bitcoin/bitcoin/pull/23585#issuecomment-983259221)

### For users

- Does this introduce a footgun?

- Should this be the new default for users?

- Should this be optional/configurable? Should it be opt in or opt out?

- Are the changes backwards-compatible?


## Approach

This PR is a good idea. That doesn't mean it should be merged.

- Does this belong in protocol or should it be at the application level?

- Is there a BIP/specification? Is it well-specified?

- Would this cause our behavior to deviate from a protocol/specification that we are supposed to support?

- Are there any alternative approaches? How does this approach compare?

	- improved/worsened technical debt

	- Performance

	- User Interface, examples: [sweepwallet](https://github.com/bitcoin/bitcoin/pull/23534#issuecomment-1005891404)

	- safety wrt activation

	- global vs local maximum, examples: [packages in fee estimation](https://github.com/bitcoin/bitcoin/pull/17331#pullrequestreview-665781489)

	- kill another bird with the same stone, examples: [background fee estimator](https://github.com/bitcoin/bitcoin/pull/17786#issuecomment-1005017943)

	- code organization and architecture, examples: [CCoinsViewPackage](https://github.com/bitcoin/bitcoin/pull/20833#discussion_r563152582), [ReconciliationState](https://github.com/bitcoin/bitcoin/pull/23443#discussion_r763854039)

- Are the magic numbers (constants, percentages, feerates, sizes, etc.) well-researched? examples: [consolidation feerate](https://github.com/bitcoin/bitcoin/pull/22009#discussion_r691956992)


### Security, Privacy, DoS

- What threat model? Does this change the way we handle something from a p2p node, or can this code path only be hit by a (privileged) RPC/GUI/REST client?

- Could a bug here cause inflation or a deviation from consensus?

- Are we introducing a new social engineering security risk? E.g. a new command/file that scammers can use to easily steal from a wallet

#### Are we introducing new DoS vectors?

- Is it possible for a peer to exhaust CPU resources? How much stuff can a peer make us do? e.g.
  [number of calls](https://github.com/bitcoin/bitcoin/pull/19988#discussion_r499511223)

- Could a peer cause us to loop infinitely or for a long period of time?

- Could a peer cause an OOM?

- What are the bounds on memory usage? examples: [maprelay memory
  blowout](https://github.com/bitcoin/bitcoin/pull/14220#issuecomment-428486018 )

- If this is deployed to a whole network of nodes, will it cause periodic spikes in bandwidth usage?

- Is there an assert() statement we could potentially hit due to peer input, causing a whole network of nodes to crash?

- How does this affect the performance of our UTXOset cache? examples:
  [thrashing and faster lookups](https://github.com/bitcoin/bitcoin/blob/807169e10b4a18324356ed6ee4d69587b96a7c70/src/validation.cpp#L1234-L1251)

- Would this give a peer the ability to make us write an unbounded amount of data to our debug.log?

#### Privacy

- Could this make it easier to deanonymize transaction origin?

- Could an attacker take advantage of this behavior to more easily analyze network topology?
  examples: [addr relay
cache](https://github.com/bitcoin/bitcoin/commit/acd6135b43941fa51d52f5fcdb2ce944280ad01e)

- Are we creating a behavior that can be used to fingerprint this node?

- Is privacy specifically worsened by this PR, or does it have a neutral effect within the context of an existing privacy leak?

#### Security By Component

- p2p

	- Could this make it easier for a peer to eclipse us/ Monopolize our addrman?

	- Does this change eviction logic in a way that may allow attackers to trigger us to disconnect from an honest peer?

	- Is it possible for an attacker to censor somebody’s transaction by taking advantage of some behavior we have here?

	- Are we opening a new pinning vector?

	- Could it cause us to add transactions to our mempool that aren’t incentive-compatible, thereby causing it to deviate from miners’ mempools?

	- Does this leak information about when a transaction enters/leaves our mempool?

- Wallet

	- Could a bug here cause someone to lose money?

	- Could this link transactions, UTXOs, addresses, etc. together?


## Implementation

At first glance, this PR looks like a good improvement and the approach seems to make sense. Here is
the Big danger now; it can have some nasty bugs in it.
Don't "no behavior changes," sometimes a bug is hiding in a refactor: [example
bug](https://github.com/bitcoin/bitcoin/pull/21160#discussion_r623305322).

- Is there a BIP/specification? Does this implementation match the specification? example: [recon
  version](https://github.com/bitcoin/bitcoin/pull/23443#discussion_r763874524)

### Common Bitcoin-Specific Bugs and Attacks

- Are we using the txid when you should be using wtxid, and vice versa?

- Are we using virtual bytes when we should be using bytes, and vice versa?

- If this uses virtual bytes, is it compatible with something else that uses weight units, and vice
versa?

- Are we using fee when we should be using feerate, and vice versa?

- Is this code safe when the transaction’s txid != wtxid?

- Can this have any impact on block propagation speed?

- Does this break the guix build?

- What impacts might this have on LN transactions or other L2 projects? example: [would ban LN
  in tx relay](https://github.com/bitcoin/bitcoin/pull/22871#pullrequestreview-760633448)

### Performance

- Are space and time complexity acceptable for the use case?

- Are the data structures appropriate for this purpose?

- Does it make use of the tools we have for parallelization?

- If adding optional functionality, how does it impact the performance of a user’s node if they don’t opt in to it? E.g. USDT

### Code Architecture

(this is a big topic, and isn’t unique to Bitcoin)
### Thread safety, concurrency

- Is it thread-safe?

- Would it be thread-safe in the future if/when x and y were to be multi-threaded?


### C++

- Are we making copies of variables when we should be passing a reference?
  [example](https://github.com/bitcoin/bitcoin/pull/22677#discussion_r760400537)

- Are we casting variables unnecessarily? Should we be using auto instead?

- Const things should be const

- RAII

- Free your memory, or just use smart pointers

- Could this implementation easily be swapped for an STL algorithm or container?

- Are you using boost when you should be using stdlib?

Examples:

- default syntax https://github.com/bitcoin/bitcoin/pull/19988#discussion_r494257310

- friend https://github.com/bitcoin/bitcoin/pull/19988#discussion_r498699913

- performance discussion https://github.com/bitcoin/bitcoin/pull/19988#discussion_r498781706

- compiler help you https://github.com/bitcoin/bitcoin/pull/19988#discussion_r498644419

- arrays vs std::arays https://github.com/bitcoin/bitcoin/pull/19988#discussion_r500887683


## Other

### Testing

Are there enough tests?

- Is there good test coverage? Is there any code that isn’t tested? example
  [sendrecon](https://github.com/bitcoin/bitcoin/pull/23443#discussion_r763865574)

- Are there normal-usage or edge cases that aren’t tested?

- Is the type of test appropriate? (unit, fuzz, functional, bench)

	- Is it an isolated, low-level piece of code -> unit

	- Is it just an implementation detail -> unit

	- Are there two implementations that you need to ensure are identical -> differential fuzz,
	  [example](https://github.com/bitcoin/bitcoin/pull/19988/commits/5b03121d60527a193a84c339151481f9c9c1962b)

	- Is it trying to demonstrate a low-level performance boost -> bench

	- Does it have an affect on observable behavior -> functional

- Is it actually testing what it should be testing?

	- If you’re asserting that something doesn’t happen, is it because of a delay? e.g.
[tx announcement delay](https://github.com/bitcoin/bitcoin/pull/21327#discussion_r585782939)

	- If you’re asserting that something doesn’t happen, is it because it’s handled asynchronously?

	- Are you sure that you’re testing this code in isolation or is it buried under 999 other things that
could be causing some behavior?

	- If you mutate the implementation, does the test fail?

Are the tests well-written?

- Is it using the functional test framework to test a very low-level detail?

- Are the tests unacceptably slow? examples: [LegacyScriptPubKeyMan in selector tests](https://github.com/bitcoin/bitcoin/pull/23288)

- Do the tests rely on timing that may be delayed when they are run in parallel with other tests?
  Are the tests racy? [example](https://github.com/bitcoin/bitcoin/pull/11740#issuecomment-350817586)

- Are the tests themselves maintainable? example: [script verification flags must be updated](https://github.com/bitcoin/bitcoin/pull/21280#discussion_r603986455)

- In functional tests: does the test have a wallet dependency when it’s not testing wallet behavior?

- In functional tests: is it thread-safe?

- Are the tests repeating stuff when they should be using utils?

- Is the test adding helper code that should be added to test utils?

- Is manual testing required and/or appropriate? Are any methods suggested?

### Documentation

- Is this well-documented enough?

	- Is the code easy to follow? Are the comments misleading, incorrect, obvious?

	- Are release notes needed?

	- Are potential footguns and user errors plastered with warnings? e.g.
[mentioning bytes when you want weight](https://github.com/bitcoin/bitcoin/pull/23201#discussion_r783933728)

	- Are future TODOs documented well enough so that maintenance doesn’t require the author to personally remember to do something? E.g. deprecations

	- Are newly introduced functions, members, classes, etc. accompanied with a doxygen header comment?

- If a future developer traced the history back to a particular commit, would they be able to understand why a change was made? Does the description match what the code does (will be in the merge commit log) - [if not, it should be updated](https://github.com/bitcoin/bitcoin/pull/22009#issuecomment-901766747)

- If a future developer were to change this, might they make a mistake if they don't understand it
  fully? Can this be guarded - e.g. with static assertions, sanity checks, etc?

- Does this implementation break any pre-existing API expectations? e.g. we might now call a
  function with different arguments that breaks its preconditions.

### Meta

- Who might need to be notified about this change?

- Does this PR add new dependencies or increase usage of a dependency we’re trying to get rid of?

