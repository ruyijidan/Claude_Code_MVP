# Harness Lab / Harness 练习靶子

## Purpose / 目的

This directory is a tiny practice target for learners who want to build or test a first harness.

It is intentionally small.

The goal is not product realism.

The goal is to create a safe training target for:

- context assembly
- task planning
- bugfix verification
- small feature delivery

## What Is Inside / 里面有什么

- `app/calculator.py`: a tiny module with one known bug and one missing capability
- `labapp/calculator.py`: a tiny module with one known bug and one missing capability
- `tests/test_calculator.py`: a small test suite with one failing expectation
- `TASKS.md`: suggested harness exercises

## Suggested Exercises / 建议练习

1. Run the tests and inspect the current failure.
2. Ask your harness to fix the failing behavior without broad refactoring.
3. Add the missing `safe_divide` behavior with tests.
4. Record a replay artifact for the run.

## Current State / 当前状态

The sample intentionally starts with one failing test.

That failure is the first exercise target, not a broken example.

## Why This Exists / 为什么有这个例子

Reading `Claude_Code_MVP` directly is great for learning architecture.

Practicing on a tiny target is better for learning execution discipline.
