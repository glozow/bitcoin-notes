# PR Review Workshop

## Table of Contents

- [Prerequisites](#Prerequisites)
	- [Build Bitcoin Core From Source](#Build-Bitcoin-Core-From-Source)
	- [Set up your Dev Environment](#Dev-Environment)
- [How to review a PR](#PR-Review)
	- [Concept](#Concept)
	- [Approach](#Approach-and-Implementation)
	- [Learning the Codebase](#Learning-the-Codebase)
	- [Learning C++](#Learning-C)
- [Resources](#Resources)

## Prerequisites

### Build Bitcoin Core From Source

1. Fork the [bitcoin/bitcoin repo][1].

2. Clone your fork locally. Add both bitcoin/bitcoin and youruser/bitcoin as remotes and name them
   something non-confusing for yourself.
There are multiple ways to do this. Here is the way through https. I've named my remote "origin"
and the bitcoin/bitcoin remote "upstream."

```
git clone bitcoin https://github.com/<user>/bitcoin.git
cd bitcoin
git remote add upstream https://github.com/bitcoin/bitcoin.git
git remote add origin https://github.com/<user>/bitcoin.git
```

3. Download the dependencies and build the source code. See [docs][2] for building instructions and
   options for your computer. Here is what I'd do on my macbook. For the sake of our time-limited
workshop, you may want to not build the wallet and gui.
```
./autogen.sh
./configure --without-gui --disable-wallet
make -j $(nproc + 1)
```

4. See that you now have a bitcoind executable. You can run your own bitcoin node! If you built the
   gui, you can also run that.
```
./src/bitcoind
```

5. Run some tests. I'd start with the unit and functional tests:
```
make check
test/functional/test_runner.py
```

### Dev Environment

(Optional)

See the Bitcoin Core [productivity tips][3]. Top tips: install ccache and multi-thread builds.

Bitcoin Core is a large codebase. Make it easy for yourself to find things in the code. Install a
good grepper, use ctags, or use an IDE with search functionality built in.

Get familiar with github, [collaborating using pull requests][4] and using git in an open source project.

A diff viewer can go a long way in helping you review PRs.

There are various Bitcoin Core-specific resources on general practices, review culture, first-hand
accounts, etc. You don't need to read everything before you get started, but they might help.

Find an IRC client you like and [join the #bitcoin-core-dev channel][5] on the libera.chat server
to attend meetings, ask questions, and/or ask for CI restarts.

## PR Review

### Decide on a PR to review

- [High Priority PR Board][23]
- [Marco's Code Coverage Graphs][24]
- [good first issues][25]

### Setup

This is what I normally do to review a PR.

Check out the PR locally. There are multiple ways to do this, e.g., fetching through the repo,
adding the author as a remote, or setting git config to automatically [create branches for pull
requests][6] (I like this a lot because it also means I get PR numbers whenever I use `git log`).

For today, we can do the simplest method:
```
git fetch upstream pull/xyz/head:reviewxyz
git checkout reviewxyz
```
Rebase on master to detect silent merge conflicts. Build and run the unit + functional test suite
for a smoke check. This should tell us if there is something obvious wrong. By no means should you
consider "all tests passed" to mean this PR is good to go.
```
git rebase master
make check -j12 && test/functional/test_runner.py -j12
```

If there are multiple commits, run this smoke check on each one to make sure the commits compile and
"work" individually. Where `n` is the number of commits to be merged from the branch:
```
git rebase -i --exec "make check && test/functional/test_runner.py" HEAD~n
```

These steps above might take a while, so now is a good time to pull up the PR on github, look at the
PR description if we haven't already, read other reviewers' comments, and gather background
information on the concept. Usually I've already done this before I checked it out locally, but
getting building and running as early as possible (especially if people are doing this for the first
time) makes sense for our shorter time window.

For example, was there a [PR Review Club][7] on this PR?

### Concept

All PRs must be sufficiently motivated, even if it's a "minor" change that wouldn't affect users.
Before looking at the details of the C++ code, let's [ask ourselves][9] whether this PR is a good
idea.

Is this a bug fix?  These questions should follow:

- Is this actually a bug? Is it a real bug or a misuse of the software, something impossible to
  hit realistically? Can the issue be solved simply with better documentation?
- "How bad" is the bug? What users are affected?
- Is there a test that can be run before to reproduce the issue, and after to verify the fix?
- Is there a description of how to reproduce the bug manually? Can we reproduce the bug ourselves?

If the PR includes a test (which it should, if it's a bug fix), let's first make sure the test passes with the changes in this PR
and fails without it. Since this is a test that only sometimes fails, we can run it multiple times:

Once you've determined whether this PR is a good idea, you might be comfortable leaving a "Concept
ACK" review on the PR.

### Approach and Implementation

So we've determined this is a good idea. Now we want to look at the code. This part is much
less structured. We'll probably just walk through the code, try to understand it, test things out,
and ask outselves questions like:

- Are there any alternative approaches? How does this approach compare?
- Are space and time complexity acceptable for the use case?
- Could this implementation easily be swapped for an STL algorithm or container?

We'll also look at the test and ask ourselves questions like:

- Is there good test coverage? Can we think of any untested edge-cases? If we change a line, do any
  tests fail?
- Is the type of test appropriate?
- Is the test well-written? Is it unacceptably slow, thread-safe, or unmaintainably complex?

Once you've decided this approach is more appropriate than any alternatives, you might be
comfortable leaving an "Approach ACK" review on the PR.

#### Learning the codebase

[Doxygen][11] is quite helpful in looking at the caller/callee graphs of functions in the codebase.
For example, in this PR, we can look up the path for
[`CWallet::ResendWalletTransactions`](https://doxygen.bitcoincore.org/group__map_wallet.html#ga6e7601aa3a97a089c49601067f1de83c).

Bitcoin Core is a large and old(ish) software project, but its development culture is very unique in
that everything must be strongly motivated and almost all decisions are publicly documented in
the commit messages and discussions. At times, it may seem tedious to have paragraphs of
justification in commit messages, but if you're ever wondering "when and why was this implemented
this way?" you can always find the answer through a few [`git blame`][12], [`git log`][13], and/or github
searches. This is incredibly powerful!

If you want to see the history of changes to a function, even if things were renamed or moved to
different files, you can use `git log` to see the history. For example, using `git log` on the
`ReacceptWalletTransactions()` can show us when `SubmitMemoryPoolAndRelay` was introduced:
```
$ git log -s -L 1837,1852:src/wallet/wallet.cpp

commit 9a556564e9dc64ae0ad723c78da33d0c982f006f
Author: Andrew Chow <achow101-github@achow101.com>
Date:   Mon Aug 1 20:10:37 2022 -0400

    wallet: Sort txs in ResendWalletTransactions

    ReacceptWalletTransactions sorts txs by insertion order,
    ResendWalletTransactions should as well.

    Includes a minor refactor of ResendWalletTranactions in order to share
    tx sorting code.

commit b11a195ef450bd138aa03204a5e74fdd3ddced26 (upstream/pr/22100)
Author: Russell Yanofsky <russ@yanofsky.org>
Date:   Fri Feb 12 18:01:22 2021 -0500

    refactor: Detach wallet transaction methods (followup for move-only)

    Followup to commit "MOVEONLY: CWallet transaction code out of
    wallet.cpp/.h" that detaches and renames some CWalletTx methods, making
    into them into standalone functions or CWallet methods instead.

    There are no changes in behavior and no code changes that aren't purely
    mechanical. It just gives spend and receive functions more consistent
    names and removes the circular dependencies added by the earlier
    MOVEONLY commit.

    There are also no comment or documentation changes. Removed comments
    from transaction.h are just migrated to spend.h, receive.h, and
    wallet.h.

commit b66c429c56c85fa16c309be0b2bca9c25fdd3e1a
Author: Antoine Riard <ariard@student.42.fr>
Date:   Mon Apr 29 09:52:01 2019 -0400

    Remove locked_chain from GetDepthInMainChain and its callers

    We don't remove yet Chain locks as we need to preserve lock
    order with CWallet one until swapping at once to avoid
    deadlock failures (spotted by --enable-debug)

commit c8b53c3beafa289dcdbd8c2ee9f957bdeca79cbc (upstream/pr/16557)
Author: John Newbery <john@johnnewbery.com>
Date:   Fri Aug 9 11:07:30 2019 -0400

    [wallet] Restore confirmed/conflicted tx check in SubmitMemoryPoolAndRelay()

    Restores the confirmed/conflicted tx check removed in
    8753f5652b4710e66b50ce87788bf6f33619b75a. There should be no external
    behaviour change (these txs would not get accepted to the mempool
    anyway), but not having the check in the wallet causes log spam.

    Also adds a comment to ResentWalletTransactions() that
    confirmed/conflicted tx check is done in SubmitMemoryPoolAndRelay().

commit 8753f5652b4710e66b50ce87788bf6f33619b75a
Author: Antoine Riard <ariard@student.42.fr>
Date:   Thu Apr 11 16:01:58 2019 +0000

    Remove duplicate checks in SubmitMemoryPoolAndRelay

    IsCoinBase check is already performed early by
    AcceptToMemoryPoolWorker
    GetDepthInMainChain check is already perfomed by
    BroadcastTransaction

    To avoid deadlock we MUST keep lock order in
    ResendWalletTransactions and CommitTransaction,
    even if we lock cs_main again further.
    in BroadcastTransaction. Lock order will need
    to be clean at once in a future refactoring

commit 611291c198eb2be9bf1aea1bf9b2187b18bdb3aa
Author: Antoine Riard <ariard@student.42.fr>
Date:   Thu Apr 11 15:58:53 2019 +0000

    Introduce CWalletTx::SubmitMemoryPoolAndRelay

    Higher wallet-tx method combining RelayWalletTransactions and
    AcceptToMemoryPool, using new Chain::broadcastTransaction
```

#### Learning C++

Bitcoin Core is written in C++, which is usually a new language to people. But don't worry,
the need to learn more C++ will never stop! Sometimes syntax is new to
C++14 or C++17, some annotations are used with specific compilers and/or options. For example, this
PR uses [structured binding](https://en.cppreference.com/w/cpp/language/structured_binding) and [clang
thready safety analysis](https://clang.llvm.org/docs/ThreadSafetyAnalysis.html), and the test's
nondeterminism is due to how [STL unordered
maps](https://en.cppreference.com/w/cpp/container/unordered_map) work.

If you're coming from higher-level programming languages, something like [A Tour of C++][14] can
give you a nice tutorial overview to the C++ memory model, usage of STL containers and algorithms,
and an introduction to some C++17 and C++20 niceities. I've also found [Effective Modern C++][15] to
be a good "recipe book" for C++14.

## Next Steps

Now that you've reviewed your first PR, what's next?

[Leave a review on the
PR](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md#peer-review). Here's a
[writeup](https://github.com/glozow/bitcoin-notes/blob/master/review-checklist.md#bad-reviews) on
what makes a "good" or "bad" review. Some more resources on "how to contribute" to Bitcoin Core:

- [Dev wiki][28]
- [Contributing guidelines][29]

Attend a [PR review club meeting][7]! I personally learned about Bitcoin Core by attending these
review clubs weekly. I reviewed the PR ahead of time on Tuesdays (initially, it would take me a
whole day to get through the notes), asked questions at the meeting on Wednesdays, and usually left
a review on Thursdays.

"How do I know what PRs or issues to work on?"

- [High Priority PR Board][23]
- [Marco's Code Coverage Graphs][24]
- [good first issues][25]
- [Jonatack's Blog Post On Review][26]

## Resources

- [Bitcoin Core Github Repository][1]
- [Documentation][2]
- [Productivity Tips][3]
- [Github Documentation on Collaborating using PRs][4]
- [Automatically fetch PRs and create branches][5]
- [#bitcoin-core-dev IRC channel from a web browser][6]

- [Bitcoin Core PR Review Club][7]
- [Bitcoin Stack Exchange][30]
- [Bitcoin Optech Topics List][31]

- [Doxygen][11]

- [fanquake's review tools][16]
- [FJahr's Debugging Guide][17]
- [My "checklist"][27]

- [C++ Reference][18]
- [C++ Books List][19]
- [Effective Modern C++][15]
- [Godbolt Interactive C++ Compiler][20]

- [Chaincode Protocol Development Seminar][21]
- [Chaincode Residency Curriculum][22]


[1]: https://github.com/bitcoin/bitcoin
[2]: https://github.com/bitcoin/bitcoin/tree/master/doc
[3]: https://github.com/bitcoin/bitcoin/blob/master/doc/productivity.md
[4]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests
[5]: https://kiwiirc.com/nextclient/irc.libera.chat?channel=#bitcoin-core-dev
[6]: https://gist.github.com/karlhorky/88b3c8c258796cd3eb97615da36e07be
[7]: https://bitcoincore.reviews
[9]: https://github.com/glozow/bitcoin-notes/blob/master/review-checklist.md#conceptual
[11]: https://doxygen.bitcoincore.org
[12]: https://git-scm.com/docs/git-blame
[13]: https://git-scm.com/docs/git-log

[14]: https://www.stroustrup.com/tour2.html
[15]: https://www.amazon.com/dp/1491903996

[16]: https://github.com/fanquake/core-review
[17]: https://github.com/fjahr/debugging_bitcoin

[18]: https://en.cppreference.com/w/
[19]: https://stackoverflow.com/questions/388242/the-definitive-c-book-guide-and-list
[20]: https://godbolt.org/

[21]: https://chaincode.gitbook.io/seminars/bitcoin-protocol-development
[22]: https://github.com/chaincodelabs/bitcoin-curriculum

[23]: https://github.com/orgs/bitcoin/projects/1
[24]: https://marcofalke.github.io/btc_cov/total.coverage/index.html 
[25]: https://github.com/bitcoin/bitcoin/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22
[26]: https://jonatack.github.io/articles/on-reviewing-and-helping-those-who-do-it
[27]: https://github.com/glozow/bitcoin-notes/blob/master/review-checklist.md
[28]: https://github.com/bitcoin-core/bitcoin-devwiki/wiki
[29]: https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md
[30]: https://bitcoin.stackexchange.com/
[31]: https://bitcoinops.org/en/topics/
