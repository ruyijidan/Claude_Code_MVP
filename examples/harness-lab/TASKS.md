# Harness Lab Tasks / Harness 练习任务

## Task 1 / 任务一

Fix the divide-by-zero behavior in `labapp/calculator.py`.

Success looks like:

- `divide(10, 0)` raises `ValueError`
- existing non-zero division still works
- tests pass

## Task 2 / 任务二

Add `safe_divide(left, right, default=None)`.

Success looks like:

- non-zero division returns the quotient
- divide-by-zero returns `default`
- tests cover both cases

## Task 3 / 任务三

Write a short run summary after the change.

Success looks like:

- changed files are listed
- verification command is listed
- final outcome is explicit
