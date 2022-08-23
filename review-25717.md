# Review n25717

## p2p changes

See Anti DoS Headers Sync notes in notes-private

### Quick Links

For block download background

- Headers First Sync https://github.com/bitcoin/bitcoin/pull/4468
- BIP 130 SendHeaders https://github.com/bitcoin/bitcoin/pull/7129
- BIP 152 https://github.com/bitcoin/bitcoin/pull/8068

- block relay only peers https://github.com/bitcoin/bitcoin/pull/19858
- additional headers sync peers https://github.com/bitcoin/bitcoin/pull/25720
- rate limit getheaders https://github.com/bitcoin/bitcoin/pull/25454
- download from inbound if needed https://github.com/bitcoin/bitcoin/pull/24171

### Work

Q: What is "sufficient" work?
- `nMinimumChainWork` for new nodes
- since 23.0
0x00000000000000000000000000000000000000002927cdceccbd5209e81e80db
- we will disconnect / won't try to IBD from nodes with chain not meeting
this amount of work
- e.g. try `bitcoind
-minimumchainwork=0x0000000000000000000000000000000000000fff2927cdceccbd5209e81e80db`,
get a bunch of `Disconnecting outbound peer i for old chain, best known block = <none>`
- `max(nMinimumChainWork, tip()->nChainWork)` for synced nodes

- could potentially ramp down the work requirement by gaming timestamps
- permitted difficulty transition is 4. where is that rule?
  [code](https://github.com/bitcoin/bitcoin/blob/1a369f006fd0bec373b95001ed84b480e852f191/src/pow.cpp#L55-L59).
Q: sanity check? add an assert that this works in `ContextualCheckHeader` and sync on mainnet,
should pass on every header. yep

- max commitments: Amount we allocate for storing commitments to the headers. Maximum number of
headers we might download divided by header commitment frequency. `m_max_commitments =
6*(GetAdjustedTime() - chain_start->GetMedianTimePast() + MAX_FUTURE_BLOCK_TIME) /
HEADER_COMMITMENT_FREQUENCY;`
	- "timewarp chain" = chain with blocks at the fastest possible rate, 6blocks/second. [MTP
  rule](https://github.com/bitcoin/bitcoin/blob/2bd9aa5a44b88c866c4d98f8a7bf7154049cba31/src/validation.cpp#L3467-L3469). 12 years * 6 blocks per second is like 2 billion headers.

	- If the peer exceeds this amount, we just disconnect and give up.  important to not underestimate or
we might never sync (Q: can hit the "exceeded max commitments at height" error?). Overestimating should be ok because small amount of space used.
	- past version also had + 1 week just in case it takes that long to sync
	  headers(?). don't think that's possible.

Q: what's the longest amount of time we'll stay connected to download headers from them?
[headers sync
timeout](https://github.com/bitcoin/bitcoin/blob/2bd9aa5a44b88c866c4d98f8a7bf7154049cba31/src/net_processing.cpp#L4933-L4936)
`HEADERS_DOWNLOAD_TIMEOUT_BASE`, `HEADERS_DOWNLOAD_TIMEOUT_PER_HEADER`
Additional non-fsync?

Memory usage = size of commitment bits + size of redownload buffer. Security/mem usage tradeoff.
Store more commitments or require more commitments to match = need to store more

### HeadersSyncState

Presync-only members
```c
// set at the beginning 6blocks/sec * time since m_chain_start when we start. never changes.
m_max_commitments;

// these correspond to the same header. last one received. starts at m_chain_start
m_last_header_received;
m_current_height;
m_current_chain_work;
```

Redownload-only members
```c
// both deques: push to back, pop from front
std::deque<CompressedHeader> m_redownloaded_headers;
// last header *stored* in the deque
// initialized to m_chain_start when we get to redownload phase
int64_t m_redownload_buffer_last_height;
uint256 m_redownload_buffer_last_hash;

// CompressedHeaders can omit prev block hash because they're stored in order
// just store this to reconstruct headers
uint256 m_redownload_buffer_first_prev_hash;

arith_uint256 m_redownload_chain_work;
// happens when total redownload work exceeds minimum chain work
// Afterwards, don't need the commitment bits anymore
bool m_process_all_remaining_headers;
```

state for both
```c
m_download_state; // {PRESYNC, REDOWNLOAD, FINAL}
bitdeque m_header_commitments; // store in the presync phase, check in the post-sync phase
```

params for both, these don't change throughout the life
```c
m_id; // ONLY used for logging. dependency on net.h
m_consensus_params; // use for PermittedDifficultyTransition
m_minimum_required_work; // from AntiDoSWorkThreshold()
m_hasher; // salted
m_commit_offset; // randomized at the beginning, peer can't guess
```

check VASRH and VASHC are using the same headers for commitments (member function instead
of using offset?)


Q: dealing with peers, just abort sync/disconnect?

- `!PermittedDifficultyTransition()` in presync and redownload (in redownload, this would be the
  equivalent of commitment not matching)
- exceeded max commitments
- doesn't connect

#### net processing

`ProcessHeadersMessage` and `IsContinuationOfLowWorkHeadersSync`: track these are used correctly
- result `pow_validated_headers`
- param `headers`
- temp `previously_downloaded_headers`


### headerssync param optimization script

1. first pick max number of headers an attacker may cause us to accept, as a fraction of the real
   amount of headers in true chain (1.2)

2. for each hfreq (num headers for each bit committed) in range, find minimum buffer size
   s.t. it's impossible to trick us into accepting a low-difficulty chain in redownload phase

try everything in a range(lower, upper) bound. How are these bounds decided? some magic, ok
just try a bunch of values print out the pairs, range makes sense

3. pick the (hfreq, rfsize) with lowest memory usage.  memory usage is maximum of: (1) size of
   commitment bitdeque of the mainchain + size of compressed header buffer and (2) size of
commitment bitdeque of a timewarp chain

Maintenance: probably run this "every few years." Ideally just need to update `TIME` and
`MINCHAINWORK_HEADERS`. Q: Other params?

- `ATTACK_BANDWIDTH` is based on hashing power of a currently powerful CPU. Conservative, since we
  want this to work for a not-so-powerful computer.

- `ATTACK_FRACTION` is 1.2 headers per block interval. Conservative.

- Need to update the script if compressed header size changes (ah that's why
`static_assert(sizeof(CompressedHeader) == 48);`), header batch (2000), header size on network (81).

### Delay sendheaders until after minimumchainwork

BIP130 sendheaders i.e. don't send me inv(block). getting a header throws us off
we'll get inv(block) while in IBD for [new blocks](https://bitcoincore.reviews/25720#l-30)

Check we won't send it multiple times now that it's in `SendMessages` instead of in response to
verack. `PeerManagerImpl::m_sent_sendheaders`.

Q: why is it strictly greater than `nMinimumChainWork` instead of reaching it which is what we do
for the other pieces of logic?

## non-p2p changes

### bitdeque

Why use a deque instead of, for example, a vector?
[comments](https://github.com/bitcoin/bitcoin/pull/25717#issuecomment-1212412201)
- use less memory by deleting the commitment bits of headers we've re-downloaded
- bookkeeping is perhaps simpler by popping as we go
- we want to pop from the front and push from the back as we go

This is meant to behave exactly like a `std::deque<bool>` but with bit packing, i.e. each element
only uses 1 bit.
- a `std::deque<T>` expects to allocate more than 1 bit per element `T`
- access, insertion, and removal from the front and back should be O(1)
- doing so in the middle of the data structure is O(n)

Implementation has 3 things: a `std::deque` and 2 `int`s for tracking the padding at the front and back
- Utilizes a `std::deque`, but instead of storing 1 bit per element, it stores multiple
- the `std::deque` stores words or "blobs" instead of bits
- there are `BITS_PER_WORD` or `BlobSize`  bits per element of the deque
```
using word_type = std::bitset<BlobSize>;
using deque_type = std::deque<word_type>;
static_assert(BlobSize > 0);
static constexpr int BITS_PER_WORD = BlobSize;
deque_type m_deque;
```
- A custom `Iterator` is defined, which points to an element (bool) within the `m_deque` . Has 2
  values: `m_deque` iterator and bit position within the bitset
- It keeps track of padding at the front and back because the number of elements might not be a
  multiple of `BITS_PER_WORD`
- Implements container interface: {move, copy} {ctors,assignment}. {iterator, const\_iterator}
  {c,r,}{begin, end}. size(), empty(), max\_size(), clear(), resize(), erase(), insert(),
{push,pop,emplace}\_{back,front,at}, etc.
- no surprises in the implementations

The fuzzer compares the behavior of bitdeque with a `std::deque<bool>`. It calls the same function
on both data structures and asserts that they behave the same way. Want to go through the bitdeque
methods -- especially those called in the code -- and see they're all fuzzed.

The fuzzer uses lower BlobSize than what `HeadersSyncState` uses
[because](https://github.com/bitcoin/bitcoin/pull/25717#discussion_r934923131) we want to test
interactions with many allocations, and that happens more easily when blobs are smaller.

### RPC

Test `bitcoin-cli getpeerinfo | grep presync` during sync.
This is mirroring exactly what we do with `CNodeStateStats::nSyncHeight`.

### Logging and GUI

commit "Track headers presync and log it"

Want to log presync because the time it takes can be noticeable to a user. Don't want to just have
silence for a few minutes before any IBD progress is shown.  Don't want unconditional logging,
because that can also be a DoS to fill disk space.

Usually headers processing is reported by validation, but since we purposefully *don't* feed headers
to validation yet at this stage, need to have net\_processing handle. It may or may not call in to
`ChainstateManager::ReportHeadersPresync` after calling `PeerManagerImpl::ProcessHeadersMessage()`.

Sanity check limits on reporting?

- Peer stats updated at the end of each `IsContinuationOfLowWorkHeadersSync`. Only kept for peers
  with a `HeadersSyncState` that's in `PRESYNC` or `REDOWNLOAD`.

- Keep map of `HeadersPresyncStats` for each presyncing per but only potentially report for updates
  to the "best" one. Can trigger if this peer was already the best one, or just became the best one.
So for example, if we have multiple peers we're syncing headers from, one has given us more
work headers, and we won't report progress on the presync of the less-work peer.

- Don't report if `m_best_header` already surpassed `minimumChainWork`

- Only allow once per 0.25sec. `ChainstateManager::m_last_presync_update` updated every time
  `uiInterface.NotifyHeaderTip()` called.

- Log, but only if in IBD.

- GUI throttles in `TipChanged` (not changed here)

Progress calculated using the number of blocks expected based
on current time - block time with consensus params `nPowTargetSpacing`.
Percentage progress = `100 * num_synced \ total` where `total = num_synced +
calculated_blocks_left`.
Q: Is progress consistent everywhere i.e. gui progress is same as log? ya

Is `peer_best` in `m_headers_presync_stats` calculated correctly?

- `HeadersPresyncStats` is a [pair](https://en.cppreference.com/w/cpp/utility/pair/operator_cmp).
  First = total work. Second = presync stats if in presync state, otherwise nullopt if in redownload
state Comparing stat `a` and stat `b`:
- `a` is better than `b` if the total verified work is higher
- if total verified work is the same, and `a` and `b` are both in presync, `a` is better if it has
  higher height
- if total verified work is the same, but `a` is in presync and `b` is in redownload, `a` is better.
  Because if `b.second == std::nullopt` and `a.second.has_value()` then `a > b`.

bitcoin-qt uses a "signal framework," i.e. slots receive signals emitted from the node and may or
may not change some visual element of the gui. Not all of it operates this way; lots of information
is queried through the node interface.

Q: `TryLowWorkHeadersSync` in a batch of `MAX_HEADERS_RESULTS` 2000, but doesn't look for the first
"new" header.
Does this affect the `ReportHeadersPresync` rate limiting, i.e. do we ever use something that could
include old headers? no, based on work, not number of headers passed in

Validation interface notifies clients when there's a new header tip.

`NotifyHeaderTip`  is called in these places:
- in `ProcessNewBlockHeaders` after calling `AcceptBlockHeader` on one or more headers
- in `ProcessNewBlock` after `AcceptBlock` but before ABC
- in `LoadExternalBlockFile`  while loading blocks
- this PR, in `ReportHeadersPresync`

The `BitcoinGUI::progressBarLabel` displays text about the node's IBD progress.

- status bar has a
  [widget](https://github.com/bitcoin/bitcoin/blob/2bd9aa5a44b88c866c4d98f8a7bf7154049cba31/src/qt/bitcoingui.cpp#L203) for `progressBarLabel`. That displays the status in the lower left corner
  of the gui window.

- various functions change the text displayed by this label. `updateHeadersSyncProgressLabel` and
  `updateHeadersPresyncProgressLabel` both set it

Pass a `presync` value and, instead of `CBlockIndex`, height and timestamp. That's sufficient
info, block index not available during presync.

Previously, a `header` boolean parameter told us whether something was `=0` new header (in initial
headers sync) or `=1` new block. This is now changed to essentially an enum with 3 possibilities.
`0` still means block. `2` now means (redownloaded) header, and `1` means pre-synced header.

## Tests

HeadersSyncState unit tests

- Some helper functions to help construct headers chains
- Test cases:
    - presync chain != redownloaded chain -> should final, failed, don't request more
    - same chain twice -> successful
    - chain with insufficient work, full -> keep requesting
    - chain with insufficient work, non-full -> exit, nothing accepted for validation
- Should look at members of struct returned from `HeadersSynceState::ProcessNextHeaders`: `success`,
  `request_more`, `pow_validated_headers`

functional test p2p_headers_sync_with_minchainwork

- minchainwork is respected. 3 nodes: miner, small minchainwork, large minchainwork
    - `generate()` has `sync_fun=self.no_op`, i.e. don't sync blocks, otherwise hang
    - topology: node0(manual)->(inbound)node1, node0(manual)->(inbound)node2
- commit #9: rpc reports presync status for peers. note need to use batches of 2000. try another
  batch, should update to 4000. everyone else is -1.
- commit #11: large reorgs succeed. try a few different `BLOCKS_TO_MINE` values
    - Q: why do we need to add `-checkblockindex=0` to the args?
