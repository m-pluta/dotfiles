---
name: squash-commit-msg
description: Write the commit message a pull request will be squash-merged as, and add it to the PR body in a collapsed block. Use only when the user asks for a squash commit message for a PR. Not for kernel trees.
---

# Squash commit message

The body of the commit the PR will be squash-merged as. Body only: leave out the subject line, since the PR title becomes it.

## 1. Write it

Follow the `commit-style` skill's normal-repo rules. Plain prose wrapped at ~72 columns, describing what the change does and why, based on the PR as a whole rather than any single commit.

Write it in ASD-STE100 Simplified Technical English. Use the `asd-ste100` skill to check the wording. Code identifiers stay as they are.

## 2. Add it to the PR body

Append it to the end of the body, after everything else:

````
<details>
<summary>Squash commit message</summary>

```
<What the change does and why, as plain prose wrapped at about 72
columns. No subject line.>
```

</details>
````

For a PR being created, include it in the body passed to `fj pr create` / `gh pr create`. For an existing PR, show the new body in chat first, then replace it with `fj pr edit <n> body "<body>"` or `gh pr edit <n> --body "<body>"`, keeping the existing purpose and changes.
