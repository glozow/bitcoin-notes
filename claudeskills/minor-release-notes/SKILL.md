---
name: bitcoin-minor-release-skill
description: Automatically generate minor release notes based on the PRs merged into this branch since the last version.
---

<!-- Requires you to already have bumped the version. -->
<!-- Note that this doesn't handle partially backported PRs or copy text release notes for significant changes like
mempool policy or activation params. You should definitely write more extensive release notes. -->


# Bitcoin Core minor release notes

Extract GitHub Pull Request numbers from backport commits and format them for release notes.

## Identify Current Release Version

Check `CMakeLists.txt` to determine what release is being prepared and what BASE_VERSION tag to use.

```bash
grep -E "CLIENT_VERSION_(MAJOR|MINOR|BUILD|RC)" CMakeLists.txt | head -4
```

Example output:
```
set(CLIENT_VERSION_MAJOR 29)
set(CLIENT_VERSION_MINOR 3)
set(CLIENT_VERSION_BUILD 0)
set(CLIENT_VERSION_RC 1)
```

This means we're preparing `v29.3rc1`. The previous release tag to diff from is `v29.2`.

### Determining the BASE_VERSION tag

Find the most recent non-release-candidate tag on the `X.x` branch:

```bash
git tag --list 'vX.*' --sort=-v:refname | grep -v "rc" | head -1
```

Example for v29.3:
```bash
git tag --list 'v29.*' --sort=-v:refname | grep -v "rc" | head -1
```

This handles cases like:
- Preparing v29.3 → finds v29.2 (or v29.2.1 if a patch release exists)
- Preparing v30.1 → finds v30.0.1 if it exists, otherwise v30.0
- Release candidates use the same BASE_VERSION tag as the final release (e.g. v29.3rc2 and v29.3rc1 should both use v29.2)

## Extract PR Numbers

The `Github-Pull` field in commit messages can use inconsistent formats, so handle all three:
- `Github-Pull: #XXXXX`
- `Github-Pull: XXXXX` (no `#`)
- `Github-Pull: bitcoin/bitcoin#XXXXX`

### Get all unique PR numbers between a tag and HEAD

```bash
git log <tag>..HEAD --pretty=format:"%b" | grep -i "github-pull" | sed 's/.*#//' | sed 's/Github-Pull: //' | sort -n | uniq
```

Example:
```bash
git log v29.2..HEAD --pretty=format:"%b" | grep -i "github-pull" | sed 's/.*#//' | sed 's/Github-Pull: //' | sort -n | uniq
```

### View all Github-Pull lines (to debug format issues)

```bash
git log <tag>..HEAD --pretty=format:"%b" | grep -i "github-pull" | sort | uniq
```

### Find PRs merged directly to the release branch (not backported from master)

In rare cases, a PR may be merged directly into the X.x branch rather than being backported from master. These appear as merge commits in the subject line and usually don't mention "backport".

```bash
git log <tag>..HEAD --oneline | grep "Merge bitcoin/bitcoin#" | grep -iv "backport"
```

Example:
```bash
git log v29.2..HEAD --oneline | grep "Merge bitcoin/bitcoin#" | grep -iv "backport"
```

## Look Up PR Titles from Master

This is much faster than looking them up through github.
Merge commits in master use the format: `Merge bitcoin/bitcoin#XXXXX: <title>`

### Search for specific PR numbers

```bash
git log master --oneline | grep -E "bitcoin/bitcoin#(PR1|PR2|PR3|...)"
```

Example:
```bash
git log master --oneline | grep -E "bitcoin/bitcoin#(31423|32473|33050|33105)"
```

## Formatting for Release Notes

### 1. Generate the PR list with titles

Combine the above commands to get a formatted list:

```bash
# First, get the PR numbers
prs=$(git log <tag>..HEAD --pretty=format:"%b" | grep -i "github-pull" | sed 's/.*#//' | sed 's/Github-Pull: //' | sort -n | uniq | tr '\n' '|' | sed 's/|$//')

# Then look up titles
git log master --oneline | grep -E "bitcoin/bitcoin#($prs)"
```

### 2. Format as markdown table

The output from the merge commit search can be transformed into a markdown table:

| PR Number | Title | Backport? |
|-----------|-------|-----------|
| #XXXXX | Description of the change | Yes/No |

### 3. Categorize for release notes

Group PRs by type based on their title prefixes. Default to Misc:
- **Validation**: `validation`, `consensus`
- **P2P Network**: `net`, `p2p`
- **Mempool**: `mempool`, `tx relay policy`, `policy`, `fee est`
- **Wallet**: `wallet`, `wallettool`
- **Mining**: `miner`, `mining`
- **Build**: `build`, `guix`, `depends`
- **Tests**: `test`, `qa`
- **Docs**: `doc`, `docs`
- **Misc**: `ci`, `contrib`


### 4. Get contributors for credits section

```bash
git log --format='- %aN' <tag>..HEAD | grep -v 'merge-script' | sort -fiu
```

### 5. Get supported systems

Find the supported systems string from the BASE_VERSION's historical release notes:

```bash
grep -A2 "is supported and" doc/release-notes/release-notes-<BASE_VERSION>.md | tail -2 | tr '\n' ' '
```

Example for v29.3rc1 (BASE_VERSION is v29.2):
```bash
grep -A2 "is supported and" doc/release-notes/release-notes-29.2.md | tail -2 | tr '\n' ' '
```

This extracts the line like `Linux Kernel 3.17+, macOS 13+, and Windows 10+`.

## Release notes format

See `release-notes-template.md` for the full template structure. Copy it to `doc/release-notes.md` and fill in:
- Replace `<VERSION>` with the version number (e.g., `30.1` or `29.3rc1`)
- Replace `<DIRNAME>` with the download directory path:
  - Final releases: `bitcoin-core-X.Y/`
    - Example: v28.3 → `bitcoin-core-28.3/`
  - Release candidates: `bitcoin-core-X.Y/test.rcN/`
    - Example: v29.1rc2 → `bitcoin-core-29.1/test.rc2/`
- Replace `<SUPPORTED_SYSTEMS>` with the appropriate string
- Add PR entries under the appropriate category sections
- Fill in the credits section with contributor names
