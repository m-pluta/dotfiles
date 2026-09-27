---
name: commit-style
description: Write git commit messages in the user's preferred style. Use whenever drafting or writing a commit message with `git commit`. Auto-detects kernel-tree style (Linux-kernel-style conventions: Fixes:/Signed-off-by, symptom-first prose) vs. normal-repo style (Conventional Commits v1.0.0). Covers subject format, body prose rules, trailers, and scope discovery.
---

# Commit message style

Two modes, auto-detected per repo. If detection is ambiguous, ask the user which mode applies before writing the message.

**Kernel-tree mode** if the repo root has `MAINTAINERS` and `COPYING` files, or recent `git log` output already uses `Signed-off-by:` trailers as a matter of course.

**Normal-repo mode** otherwise.

## Rules that apply in both modes

- **Never use a semicolon (`;`)** anywhere in the subject or body. Rephrase as two sentences, or use a comma/dash/"and" instead.
- **Never include specific measurement values, benchmark numbers, timings, or one-off results** (e.g. "took 4.2s on my machine", "reduced latency by 30%", "tested with 10k iterations"). This is especially important for the kernel, which runs on an enormous range of hardware and workloads — a specific number from one run doesn't generalize and reads as sloppy. If a change has a performance motivation, describe it qualitatively (e.g. "avoids quadratic work for large inputs", "removes a redundant syscall on the hot path") rather than citing a measured figure.
- **Never fabricate or assume author identity.** Before writing `Signed-off-by:` or any trailer that names the author, get the identity from the repo itself:
  ```
  git config user.name
  git config user.email
  ```
  Use exactly what git reports for *this* repo/worktree — never the assistant's own identity, a value remembered from another project, or a guess. If `git config` returns nothing, ask the user.
- **Never add a `Co-Authored-By: Claude` or any Claude/Anthropic attribution trailer.** The only acceptable AI-attribution trailer is `Assisted-by: LLM`, and only in kernel-tree mode, and only when an LLM genuinely helped draft/analyze that specific commit — it is not added automatically to every commit.
- Write in imperative mood ("Fix", "Add", "Move" — not "Fixes", "Added", "Moves").
- No emojis.

## Kernel-tree mode

### Subject

```
<area path>: <Imperative capitalized sentence>
```

- No trailing period.
- Keep the whole subject line short — aim for ≤75 columns.
- The `<area path>` prefix must match the convention already established for the files being touched. Find it before writing the subject:
  ```
  git log --oneline -- <changed-path> | head -20
  ```
  Reuse the existing prefix (e.g. `mm:`, `net: tcp:`, `fs: ext4:`) rather than inventing a new one.

### Body

- Freeform prose paragraphs, wrapped at ~75 columns. No bullet points, no markdown — even when covering multiple small related fixes, fold each into its own short paragraph.
- Never refer to "this commit" / "this patch" / "I" — describe the code and its behavior directly.
- Structure, in order:
  1. **Symptom first.** Describe the user-visible problem. If there's a concrete repro, show the invocation and the broken output, indented by two spaces, verbatim.
  2. **Root cause.** Explain the mechanism, naming the exact functions/variables involved (with `()` on function names).
  3. **The fix.** State what changes, and show the corrected output (indented, two spaces) if a before/after contrast helps.
- Precise and technical — no hedging, no vague language.

### Trailers

Blank line before the trailer block, then exactly this order:

1. `Fixes: <12-hex-sha> ("<original commit's own subject>")` — one line per distinct prior commit responsible for the bug. Omit entirely for pure enhancements/cleanups that aren't tied to a specific regression.
2. `Assisted-by: LLM` — only when true for this commit
3. `Signed-off-by: <Name> <<email>>` — always last, identity from `git config`

### Worked example (invented, illustrative only)

```
mm: page_alloc: Fix off-by-one in zone boundary check

When the requested order pushes the candidate page past the last valid
page frame in a zone, the boundary check still accepts it, because it
compares against the wrong end value. This lets the allocator hand out
a page just past the end of a zone.

Compare against the zone's actual last pfn instead.

Fixes: 0123456789ab ("mm: page_alloc: introduce per-zone boundary check")
Signed-off-by: <Name> <<email>>
```

## Normal-repo mode: Conventional Commits v1.0.0

Full spec: https://www.conventionalcommits.org/en/v1.0.0/

### Format

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

### Types

Required by the spec:
- `feat` — a new feature (SemVer MINOR)
- `fix` — a bug fix (SemVer PATCH)

Additional types this project uses (Angular convention, widely adopted, must be picked from this explicit list — do not invent others):
- `build` — changes to the build system or external dependencies
- `chore` — routine maintenance with no production code change (tooling, config)
- `ci` — CI configuration/scripts
- `docs` — documentation only
- `style` — formatting/whitespace, no code meaning change
- `refactor` — code change that neither fixes a bug nor adds a feature
- `perf` — a code change that improves performance
- `test` — adding or correcting tests
- `revert` — reverts a previous commit

### Scope — must be discovered, never invented on the spot

A scope is a parenthesized noun after the type: `feat(parser): add ability to parse arrays`.

Before choosing a scope, discover the project's established scope vocabulary:
```
git log --oneline | grep -oP '(?<=\()[\w./-]+(?=\)!?:)' | sort -u
```
- If the change fits one of the scopes that comes back, use it exactly as spelled.
- If nothing fits and this looks like a genuinely new area, **ask the user to confirm the new scope name** before using it — don't invent one silently. Once confirmed, treat it as now part of this project's explicit scope list for future commits.
- Omit the scope entirely if the change is cross-cutting and no single scope fits.

### Description

- Immediately follows `type[(scope)][!]: `.
- Imperative, no capital letter required, no trailing period.

### Body

- One blank line after the description.
- Freeform prose, may be multiple paragraphs. Explain motivation and contrast with previous behavior where useful.

### Footers

- One blank line after the body.
- `Token: value` or `Token #value`. Multi-word tokens use hyphens (`Reviewed-by`, `Refs`), except the literal token `BREAKING CHANGE`, which stays as two words in capitals.
- A footer's value may span multiple lines, until the next footer token starts.
- Common footers: `Refs: #123`, `Reviewed-by: <name>`, `Closes: #123`.

### Breaking changes

Either:
- `!` immediately after the type/scope and before the colon: `feat(api)!: remove deprecated endpoint`, or
- A footer: `BREAKING CHANGE: <description of the break>` (`BREAKING-CHANGE:` is a synonym).

A breaking change can be flagged on any type, not just `feat`.

### Worked example

```
fix(parser): handle trailing comma in array literals

Trailing commas were previously rejected outright, which diverges from
what most JSON5-like inputs allow.

Refs: #482
```
