---
name: git-smart-fixup
description: Split staged changes or HEAD commit into `fixup!` commits that target the appropriate previous commits in the current branch.
---
# Git Smart Fixup

## Trigger

User invokes `/smart-fixup` or asks to split changes into fixup commits.

## Arguments

- `--from-head`: Use the HEAD commit instead of staged changes (will reset HEAD and recreate as fixups)
- `--dry-run`: Show what fixup commits would be created without actually creating them
- `--base <ref>`: Specify the base branch (default: auto-detect master/main)

## Instructions

### Step 1: Determine the Base Branch and Commit Range

1. Find the merge base between current branch and main/master:
   ```bash
   git merge-base HEAD master
   ```

2. Get the list of commits from merge base to HEAD (these are candidates for fixup targets):
   ```bash
   git log --oneline --reverse <merge-base>..HEAD
   ```

3. Store commit hashes and their messages for later matching.

### Step 2: Get the Changes to Split

**If using staged changes (default):**
```bash
git diff --cached --unified=0
```

**If using `--from-head`:**
```bash
# Get the diff from HEAD commit
git show HEAD --unified=0 --format=""

# Store HEAD message for potential fallback
git log -1 --format="%s" HEAD

# Soft reset to unstage HEAD's changes
git reset --soft HEAD~1
```

### Step 3: Analyze Each Hunk and Find Target Commits

For each changed file and hunk:

1. Parse the diff to extract file paths and line ranges.

2. For each modified/deleted line range, use git blame to find which commit last touched those lines:
   ```bash
   # For the version before our changes, blame the lines being modified
   git blame -l -L <start>,<end> <merge-base>..HEAD~1 -- <file> 2>/dev/null
   ```

   If blaming the range fails (new lines), check the surrounding context:
   ```bash
   git blame -l -L <start-3>,<start> HEAD~1 -- <file> 2>/dev/null
   ```

3. For each hunk, determine the target commit:
   - Extract commit hashes from blame output
   - Check if any blamed commit is within our branch's commits (between merge-base and HEAD)
   - If multiple commits touched the lines, prefer the most recent one in our branch
   - If no branch commit is found, this hunk will go into a "new" commit

### Step 4: Group Changes by Target Commit

Create a mapping of target commits to their associated hunks:

```
{
  "<commit-hash-1>": [hunk1, hunk2, ...],
  "<commit-hash-2>": [hunk3, ...],
  "NEW": [hunk4, hunk5, ...]  // Changes not attributable to any branch commit
}
```

### Step 5: Create Fixup Commits

For each target commit with associated hunks:

1. Stage only the relevant hunks using `git add -p` or by creating patch files:
   ```bash
   # Create a patch for this group of hunks
   # Apply with: git apply --cached <patch-file>
   ```

2. Create the fixup commit:
   ```bash
   git commit --fixup=<target-commit-hash>
   ```

3. For changes marked as "NEW" (not attributable to branch commits):
   - If `--from-head` was used, use the original HEAD commit message
   - Otherwise, prompt the user for a commit message or create with a descriptive message

### Step 6: Report Results

Display a summary:
```
Original commit: <original-head>

Created X fixup commits:
  fixup! <original-commit-message-1> (N files, M lines)
  fixup! <original-commit-message-2> (N files, M lines)

Remaining changes (not matched to branch commits):
  <new-commit-message> (N files, M lines)

To confirm that these commits match the original state, run:
  git diff <original-head>..<new-head>

To squash these fixups, run:
  git rebase -i --autosquash <merge-base>
```

## Edge Cases

1. **No staged changes and no `--from-head`**: Error with helpful message.

2. **New files**: These typically become a new commit unless the user added them alongside modifications to existing code.

3. **Binary files**: Skip blame analysis, treat as new changes.

4. **Renamed files**: Use `git log --follow` to track through renames.

## Implementation Notes

- Use `git diff --cached -U0` for minimal context when parsing hunks
- Parse unified diff format: `@@ -start,count +start,count @@`
- Handle the case where blame returns commits outside the branch range
- Consider using `git log -S` or `git log -G` as fallback for finding related commits
- Preserve the order of fixup commits to match the original commit order for cleaner rebases
