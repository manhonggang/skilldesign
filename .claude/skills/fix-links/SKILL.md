---
name: fix-links
description: >-
  Audit and repair all broken Obsidian wikilinks across the vault.
  Extracts every [[wikilink#heading]] reference, verifies the target
  file exists and the heading text matches exactly, then fixes any
  mismatches. Use this skill when links create new empty notes instead
  of navigating to existing documents, or whenever you want to run a
  vault-wide link health check.
tags:
  - obsidian
  - maintenance
  - links
  - audit
---

# Fix Obsidian Wikilinks

## Overview

This skill performs a vault-wide audit of all wikilinks that contain
heading references (`[[file#heading]]` or `[[file#heading|alias]]`).
It verifies that every such link can resolve correctly in Obsidian,
then repairs any broken links it finds.

## When to Use

- Clicking a wikilink opens a **new empty note** instead of an existing
  document → the filename in the link does not match any file on disk.
- Clicking a wikilink opens the **correct file but does not scroll to
  the heading** → the heading text in the link does not match any
  heading in the target file.
- After a batch rename or refactoring session.
- As a periodic vault health check.

## The Process (Step by Step)

### Phase 1 — Extract all heading-referenced wikilinks

Run this across every `.md` file in the vault root (and sub-folders
if they exist):

```bash
grep -oh '\[\[[^]]*#[^]]*' *.md | sort -u
```

This gives a deduplicated list of every `[[file#heading...]]` pattern.

For each entry, split it into:
- **Filename** — the part before `#`
- **Heading reference** — the part after `#` and before `|` or `]]`
- **Alias** — the part after `|` (if present)

### Phase 2 — Verify the target file exists

For each unique filename in the extracted links:

1. Check that a file with that **exact name** exists on disk.
   Use `ls` with a pattern, not glob, to catch invisible character
   differences (Unicode normalization, fullwidth vs halfwidth, etc.):

   ```bash
   ls *.md | grep -F "exact filename from link"
   ```

2. If no match is found, the filename in the link is wrong. Common causes:
   - **Truncated filename** — e.g. `[[三系统正交定位分析#...]]` when the
     actual file is `三系统正交定位分析：奥义、技能与遗物.md`. The link is
     missing `：奥义、技能与遗物`.
   - **Fullwidth vs halfwidth characters** — the colon `:` (U+003A) and
     the fullwidth colon `：` (U+FF1A) are different characters. Verify
     with `xxd` if needed.
   - **Unicode normalization** — NFC vs NFD forms of the same character.
     Use `xxd` to compare raw bytes.

3. Fix any filename mismatches first — a wrong filename is a hard break;
   Obsidian will create a new empty note.

### Phase 3 — Verify the heading reference matches

For each link whose target file exists, check every heading reference:

1. Extract all headings from the target file:

   ```bash
   grep -n '^#\+ ' "target-file.md"
   ```

2. For each heading reference in the links, verify an **exact text match**
   exists (ignoring the `#` markers — `## My Heading` is referenced as
   `#My Heading`).

3. Common heading mismatches and their causes:

| Link says | Actual heading | Root cause |
|-----------|---------------|------------|
| `#1. 多维博弈的克制闭环` | `## 1. 多维博弈的克制闭环 (Combat & Counters)` | **Missing parenthetical suffix** — heading has an English parenthetical that was omitted from the link. |
| `#4. 资源动力学与元素锚定` | `## 4. 资源动力学与元素锚定 (Resource & Elemental Anchoring)` | Same as above. |
| `#5. 1+1 双轨道构筑` | `## 5. 1+1双轨道构筑` | **Space mismatch** — the heading has no space between `1+1` and `双轨道`, but the link inserts one. |
| `#3.3 技能的转换器本质（充能属性作为定位根）` | `### 3.3 技能的转换器本质（充能属性作为定位根）` | Looks correct but may still fail due to fullwidth parentheses or other invisible Unicode differences. |

4. **If the heading text appears to match but the link still fails** in
   Obsidian, the safest fix is to use a **block ID** instead (see below).

5. Fix each mismatch by editing the link text to match the actual heading
   exactly.

### Phase 4 — Handle table wikilinks with pipe aliases

Wikilinks inside Markdown tables are a special case. Obsidian handles
`|` inside `[[...]]` correctly (it parses wikilinks before tables), but
excessive whitespace can confuse parsers.

**Pattern to fix:**

```
| [[some-file#heading                                 | alias]]                               |
```

Remove the extra whitespace before the alias `|`:

```
| [[some-file#heading|alias]]                               |
```

If the table cell is narrow, consider using `\|` to escape the pipe:

```
| [[some-file#heading\|alias]]                               |
```

Both forms work in Obsidian; the key is to remove the trailing
whitespace inside the wikilink.

### Phase 5 — For CJK-heavy headings: prefer block IDs

Headings with Chinese characters, fullwidth punctuation, and special
symbols can fail to match across different Obsidian versions or
encodings, even when the text appears identical.

**The block ID approach is immune to these issues.**

Instead of:
```
[[文件#3.3 某个中文标题（含括号）|显示文字]]
```

1. Add a block ID to the target heading:

   ```markdown
   ### 3.3 某个中文标题（含括号） ^meaningful-id
   ```

2. Reference the block ID:

   ```markdown
   [[文件#^meaningful-id|显示文字]]
   ```

**Block ID naming conventions:**
- Use kebab-case English identifiers: `^converter-root`, `^two-resource-types`
- Make them semantically meaningful so readers understand the target
- Place a space before the `^` in the heading line
- The block ID must be unique within the file

### Phase 6 — Cross-file sweep

After fixing the file the user is looking at, always run a sweep
across the **entire vault** for the same broken patterns. A wrong
heading reference in one file is almost always wrong in other files
that reference the same heading.

```bash
# Find all files that reference a specific broken heading pattern
grep -rn "broken heading pattern" --include="*.md" .
```

Fix every occurrence. The `replace_all` option in the Edit tool is
useful here, but always verify the context of each match first — a
string might appear in non-link text where it should not be changed.

## Common Failure Patterns (Quick Reference)

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Heading missing ` (English Suffix)` | File opens, heading not found | Add the suffix to the link |
| Space difference (`1+1双` vs `1+1 双`) | File opens, heading not found | Match the actual heading exactly |
| Truncated filename (missing `：子标题`) | Creates new empty note | Restore the full filename |
| Fullwidth vs halfwidth colon/parens | Creates new empty note | Verify with `xxd`, use correct Unicode |
| CJK heading works in preview but not editor | Intermittent | Switch to block IDs |
| Table wikilink with trailing spaces | Link renders oddly | Remove excess whitespace |

## Tools Used

- `Glob` — find all `.md` files in the vault
- `Grep` / `Bash: grep` — extract wikilinks, find heading patterns
- `Read` — read target files to verify headings
- `Bash: xxd` — hex-dump characters when Unicode is suspected
- `Edit` — fix broken links in place
- `Write` — add block IDs to target files when necessary

## Safety Rules

1. **Never change the target file's heading text** to match a broken
   link — other links may already reference the correct heading text.
   Always fix the link to match the heading, not the other way around.
2. When adding block IDs to a target file, place them on the same line
   as the heading, after the heading text: `### Heading ^block-id`.
3. Always read a file before editing it — the Edit tool enforces this.
4. When using `replace_all`, ensure the search string is unique enough
   that it won't match non-link text.
5. Verify every fix by re-running the grep to confirm no broken
   references remain.
