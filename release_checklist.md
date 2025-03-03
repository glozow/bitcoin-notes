## Release Checklist

This is an extension to the [doc](https://github.com/bitcoin/bitcoin/blob/master/doc/release-process.md) on the main repo, but with all tasks listed in sequential order and divided into things that individual people can do.

(\*) = with perms. All other tasks can be done by other people.
As an idea, you could have 3 people tasked with each release: (A), (B), (C), where (C) is the "captain" and (A) and (B) are volunteers who may or may not be maintainers but agree to be highly responsive during this release cycle. (C*) indicates "C or someone with the right permissions" which can be helpful if (C) doesn't want to merge their own PR or doesn't have access to something in particular.
Other roles include "guix builders," "codesigners," and "testing guide creator." I've assigned this so that (B) is the person who does website PRs.

### Minor

For each release candidate:
- [ ] translations
	- [ ] pull translations, PR (A)
	- [ ] review (B) (C*)
	- [ ] merge\* (C*)
- [ ] Backports
	- [ ] find/suggest things to backport (C) (everyone)
	- [ ] decide what to backport\* (C)
	- [ ] backports PR (C)
	- [ ] review (A) (B)
	- [ ] merge\* (C*)
- [ ] Final Changes PR (A)
	- [ ] build changes in configure.ac (A)
	- [ ] generate manpages (A)
	- [ ] (maybe) update bips.md (A)
	- [ ] (maybe) update example bitcoin.conf (A)
	- [ ] create/update release notes (A)
	- [ ] review (B) (C)
	- [ ] merge\* (C*)
- [ ] create and push tag\* (C)
- [ ] guix attestations
	- [ ] build (guix builders)
	- [ ] attest noncodesigned (guix builders)
	- [ ] codesign\* (codesigners)
	- [ ] attest codesigned (guix builders)
- [ ] upload bins to website\* (C*)
	- [ ] verify everyone's attestations (C)
	- [ ] create SHA256SUMS.asc file (C)
- [ ] post announcements
	- [ ] bitcoin-core-dev mailing list (C*)
	- [ ] bitcoin-dev group (C*)

Final version:
- [ ] Final Changes (C*)
    - [ ] build changes in configure.ac (A)
	- [ ] generate manpages (A)
	- [ ] (maybe) update bips.md (A)
	- [ ] (maybe) update example bitcoin.conf (A)
	- [ ] create/update release notes (A)
	- [ ] review (B) (C)
	- [ ] merge\* (C*)
- [ ] create and push tag\* (C*)
- [ ] website announcement PR (A)
	- [ ] review (A) (C)
	- [ ] merge\* (C*)
- [ ] guix attestations (guix builders)
	- [ ] build (guix builders)
	- [ ] attest noncodesigned (guix builders)
	- [ ] codesign\* (codesigners)
	- [ ] attest codesigned (guix builders)
- [ ] upload bins to website (C*)
	- [ ] verify everyone's attestations (C)
	- [ ] create SHA256SUMS.asc file (C)
	- [ ] create torrent (need magnet for announcements) (C)
- [ ] add release notes to master doc/release-notes/ directory (need link for announcements) (C)
	- [ ] review (A) (B) (C)
	- [ ] merge\* (C*)
- [ ] post announcements (C)
	- [ ] bitcoin-core-dev mailing list
	- [ ] bitcoin-dev group
	- [ ] twitter\* (C*)
- [ ] create github release\* (C)
- [ ] harass package managers (repology.org) (C*)

### Major
Additional for major releases:
- [ ] DNS fixed seeds (A or somebody who owns this)
	- [ ] review (B) (C) (or somebody who owns this)
	- [ ] merge\* (C*)
- [ ] chainparams (B)
	- [ ] review (A) (C)
	- [ ] merge\* (C*)
- [ ] headers sync params (B)
	- [ ] review (A) (C)
	- [ ] merge\* (C*)
- [ ] write the release notes (everyone)
	- [ ] archive previous (B)
	- [ ] clear all the release notes in tree (B)
	- [ ] write draft (B)
	- [ ] get everyone to write their release notes in mediawiki (B)
- [ ] branch off (C)
- [ ] create issue for testing (A)
- [ ] release candidate testing guide (A)
	- [ ] make guide (testing guide creator)
	- [ ] create issue for testing guide feedback (A)
	- [ ] review club meeting (testing guide creator)
- [ ] website: RPC docs (B)
	- [ ] create them (B)
	- [ ] review (A), (C)
	- [ ] merge\* (C*)
- [ ] eol github: delete milestones, labels, branches, tag final\* (C)
- [ ] eol website: maintenance table, archive (B)
	- [ ] review (A) (C)
	- [ ] merge\* (C*)

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

