## Release Checklist

(\*) = with perms. All other tasks can be done by other people.

### Minor

For each release candidate:
- [ ] translations
	- [ ] pull translations, PR
	- [ ] review
	- [ ] merge\*
- [ ] Backports
	- [ ] find/suggest things to backport
	- [ ] decide what to backport\*
	- [ ] backports PR
	- [ ] review
	- [ ] merge\*
- [ ] Final Changes
	- [ ] build changes in configure.ac
	- [ ] generate manpages
	- [ ] (maybe) update bips.md
	- [ ] (maybe) update example bitcoin.conf
	- [ ] create/update release notes
	- [ ] review
	- [ ] merge\*
- [ ] create and push tag\*
- [ ] guix attestations
	- [ ] build
	- [ ] attest noncodesigned
	- [ ] codesign\*
	- [ ] attest codesigned
- [ ] upload bins to website\*
	- [ ] verify everyone's attestations
	- [ ] create SHA256SUMS.asc file
- [ ] post announcements
	- [ ] bitcoin-core-dev mailing list
	- [ ] bitcoin-dev group

Final version:
- [ ] Final Changes
    - [ ] build changes in configure.ac
	- [ ] generate manpages
	- [ ] (maybe) update bips.md
	- [ ] (maybe) update example bitcoin.conf
	- [ ] create/update release notes
	- [ ] review
	- [ ] merge\*
- [ ] create and push tag\*
- [ ] website announcement PR
	- [ ] review
	- [ ] merge\*
- [ ] guix attestations
	- [ ] build
	- [ ] attest noncodesigned
	- [ ] codesign\*
	- [ ] attest codesigned
- [ ] upload bins to website
	- [ ] verify everyone's attestations
	- [ ] create SHA256SUMS.asc file
	- [ ] create torrent (need magnet for announcements)
- [ ] add release notes to master doc/release-notes/ directory (need link for announcements)
	- [ ] review
	- [ ] merge\*
- [ ] post announcements
	- [ ] bitcoin-core-dev mailing list
	- [ ] bitcoin-dev group
	- [ ] twitter\*
- [ ] create github release\*
- [ ] harass package managers (repology.org)

### Major
Additional for major releases:
- [ ] DNS fixed seeds
	- [ ] review
	- [ ] merge\*
- [ ] chainparams
	- [ ] review
	- [ ] merge\*
- [ ] headers sync params
	- [ ] review
	- [ ] merge\*
- [ ] write the release notes
	- [ ] archive previous
	- [ ] clear all the release notes in tree
	- [ ] write draft
	- [ ] get everyone to write their release notes in mediawiki
- [ ] branch off
- [ ] create issue for testing
- [ ] release candidate testing guide
	- [ ] make guide
	- [ ] create issue for testing guide feedback
	- [ ] review club meeting
- [ ] website: RPC docs
	- [ ] create them
	- [ ] review
	- [ ] merge\*
- [ ] eol github: delete milestones, labels, branches, tag final\*
- [ ] eol website: maintenance table, archive
	- [ ] review
	- [ ] merge\*

#### Timelines / Coordination

(?) = I think this is a good idea for coordination purposes

- `T - 6m` (?) Branch off of previous release: Talk about big-size rocks to accomplish in this milestone
- `T - 3m`: (?) Talk about medium-size Pebbles to add to Milestone (this is separate from bug fixes etc. that should go in). Imo at this point all big features for the release should already have been discussed.
- `T - 8w`: Translations freeze
- `T - 7w`: (?) Kill-Shill-Merge for remaining PRs on the milestone / what should go in next one
- `T - 6w`: Feature Freeze
- `T - 4w`: Create release notes, find somebody to create RC Testing Guide
- `T - 4w`: Branch off, tag first RC
- `T - 4w`: Review Club for RC testing
- `T`: Target Release date

