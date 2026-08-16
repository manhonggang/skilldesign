---
name: rich-text-replace
description: >-
  Replace game terms in text with rich text tags (from 富文本表)
  and bold formatting for terms not in the table. Every rich text
  tag MUST be wrapped in backticks to prevent Obsidian from parsing
  them as HTML. This skill only handles formatting replacement —
  it does NOT rewrite descriptions or change prose style. Use this
  skill when the user asks to "replace with rich text", "apply
  rich text formatting", or similar requests.
tags:
  - game-design
  - rich-text
  - formatting
  - obsidian
---

# Rich Text Replacement

## Overview

This skill replaces game-specific terms in text with two types of
formatting. It does **not** rewrite descriptions or change prose style.

1. **Rich text** — for terms in [[富文本表]]: wrap with game engine
   `<color=#...><href=...>term</href></color>` tags, then wrap the
   whole tag in Markdown backticks (for Obsidian safety).
2. **Bold** (`**term**`) — for named game mechanics (buffs, debuffs,
   special effects) that are NOT in the rich text table.
3. **Dynamic placeholders** (`{PerValue1}`, `{FixedValue1}`, etc.)
   are never modified.

## When to Use

- User asks to "replace with rich text" or "apply 富文本"
- User asks to format game text with colors and links
- User references [[富文本表]] in a formatting request

## Critical Rule: Always Wrap Rich Text in Backticks

**Every rich text tag must be wrapped in Markdown backticks** when used
in any document:

```
施加3层`<color=#f02b2b><href=game://buff/42>燃烧</href></color>`
```

**Why**: The `<color=#...>` and `<href=...>` tags use angle brackets
(`<` and `>`). Obsidian's Markdown renderer interprets these as HTML
tags and tries to parse them. Since `<color>` is not a valid HTML
element, the renderer either:
- Strips the tag entirely (content disappears)
- Breaks the surrounding table/sentence structure
- Produces incomplete text when copied

Wrapping in backticks forces Obsidian to treat the tag as inline code,
preserving all characters intact.

**When using outside Obsidian**: Remove the surrounding backticks
before pasting into game configuration.

## The Process (Step by Step)

### Phase 1 — Load the rich text mapping

Read [[富文本表]] to extract all known term → rich text mappings.
Build a lookup table in memory:

| Term | Rich Text (raw, no backticks) |
|------|------------------------------|
| 燃烧 | `<color=#f02b2b><href=game://buff/42>燃烧</href></color>` |
| 寒冷 | `<color=#229da4><href=game://buff/21>寒冷</href></color>` |
| 中毒 | `<color=#24a422><href=game://buff/3>中毒</href></color>` |
| ... | ... |

Also note the color conventions for reference:

| Color | Hex | Purpose |
|-------|-----|---------|
| Red | `#f02b2b` | Damage/Attack (燃烧, 天雷, 反击, 撕裂, 暴击率, etc.) |
| Orange | `#f07b2b` | Secondary/Special (闪电, 追击, 感电, etc.) |
| Green | `#24a422` | Buff/Recovery/Poison (中毒, 抵御, 恢复, etc.) |
| Cyan | `#229da4` | Ice/Agility (寒冷, 闪避, 灵敏, 脱力, etc.) |
| Purple | `#6e22a4` | Special items/Crystals (连接石, 升级水晶, 天堂水晶) |

### Phase 2 — Read the target file

Read the file containing skill/item descriptions. Identify:
- The structure (is it a table? bullet list? plain text?)
- Where descriptions begin and end
- Line count — this must be preserved exactly

### Phase 3 — Identify terms to replace

For each description line, scan for terms that match the rich text
table. **Use exact substring matching** — a term like `恢复` should
only match the exact characters `恢复`, not similar terms like `回复`.

Terms that appear in the rich text table → replace with rich text
(wrapped in backticks).

### Phase 4 — Identify terms to bold

For each description line, identify named game mechanics that are
NOT in the rich text table:
- Named status effects (冰冻, 压制, 死亡预兆, 雷殛)
- Named shields/buffs (烈阳护盾, 蝎后护盾, 狂怒, 怒噬)
- Named special attacks (嗜血蝠, 毒翼飓风)
- Core mechanics (暴击 — note: 暴击率 is in the table, but 暴击 alone is not)
- Named weather/field effects (雷暴)
- Armor/debuff mechanics (破甲, 弱化效果)

**Do NOT bold** common RPG terms: 伤害, 攻击, 生命, 护盾, 回合, 目标,
敌人, 角色, 玩家. These are too generic.

### Phase 5 — Write the result with exact line matching

Write the modified file back, ensuring:
- Every line number matches the original file exactly
- Frontmatter and header rows are unchanged
- Blank lines are preserved
- The user can copy a specific line range and paste it back into the
  original source without offset

## Example

**Before:**
```
造成{PerValue1}力量+{FixedValue1}伤害并施加 3 层燃烧和死亡预兆
```

**After** (燃烧 in rich text + backticks, 死亡预兆 bolded):
```
造成{PerValue1}力量+{FixedValue1}伤害并施加 3 层`<color=#f02b2b><href=game://buff/42>燃烧</href></color>`和**死亡预兆**
```

## Tools Used

- `Read` — load 富文本表 and target file
- `Edit` or `Write` — apply changes (Write is preferred for bulk
  replacements to avoid partial-edit errors)
- `Bash: wc -l` — verify line count matches

## Safety Rules

1. **Always read 富文本表 first** — never guess or hardcode rich text
   mappings. The table may be updated.
2. **Exact line count preservation** — the output must have the same
   number of lines as the input. This is critical for the user's
   copy-paste workflow.
3. **Exact term matching only** — `恢复` ≠ `回复`. Only replace when
   the substring is an exact match.
4. **Backticks on every rich text tag** — no exceptions. Missing
   backticks = broken Obsidian rendering = user can't copy.
5. **Never modify dynamic placeholders** — `{PerValue1}`, `{FixedValue1}`,
   etc. must pass through unchanged.
6. **Verify line count** after writing — run `wc -l` to confirm.
