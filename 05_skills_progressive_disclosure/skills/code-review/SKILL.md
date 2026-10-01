---
name: code-review
description: Review Python API code for correctness, input handling, and security defects. Use when asked to review code or an API implementation.
---

# Code review

Read the supplied code before suggesting changes. Identify concrete defects,
explain the failing input or behavior, and propose a minimal correction.

For SQL queries, check whether untrusted input is bound as a parameter rather
than interpolated into the query. Do not assume the database driver's placeholder
syntax. State the driver assumption when showing a corrected snippet.

Return the highest-impact findings first, followed by a corrected example and
one regression test suggestion. Do not modify files unless explicitly requested.
