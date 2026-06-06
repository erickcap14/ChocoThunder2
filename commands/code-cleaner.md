---
description: Code Cleaner — audit Python files for readability violations (read-only report) or apply the coding standard to rewrite files
allowed-tools: Task
---

Task: Use the code-cleaner subagent to route this request to the correct specialist (code-cleaner-audit or code-cleaner-format) and return the final result.

## Examples
- `/code-cleaner audit src/` — scan all Python files in src/ and report violations
- `/code-cleaner audit utils/helpers.py` — audit a single file
- `/code-cleaner format src/` — apply the coding standard to all files in src/
- `/code-cleaner format utils/helpers.py` — clean a single file
- `/code-cleaner` — dispatcher will ask: audit or format?

User request:
$ARGUMENTS
