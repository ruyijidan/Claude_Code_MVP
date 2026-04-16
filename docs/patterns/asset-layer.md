---
last_updated: 2026-04-15
status: active
owner: core
---

# Asset Layer / 资产层

## Purpose / 目的

The asset layer is where repeatable execution knowledge becomes explicit repository material instead of staying trapped inside prompt wording or loop code.

## What Counts As An Asset / 什么算资产

In `Claude_Code_MVP`, the first useful asset categories are:

- workflows
- templates
- rules

These are stored under:

- `specs/workflows/`
- `specs/templates/`
- `specs/rules/`

## Why This Layer Matters / 为什么这层重要

Without an asset layer, every adjustment tends to fall into one of two bad buckets:

- change the loop code for a small behavioral tweak
- rely on agent behavior to remember more and more conventions

An explicit asset layer gives the project a middle option:

- keep the harness core stable
- move reusable execution meaning into versioned repo assets

## Current Repository Direction / 当前仓库方向

The repository now uses this layer in a lightweight but real way:

- workflow assets shape plan construction
- workflow verification helps shape gates and completion checks
- workflow stop conditions are accepted by the repair policy interface
- rule assets can influence critic behavior

This is still an early version, but it already changes the project’s adjustment surface.

## What Should Stay Out Of This Layer / 什么不该放进这一层

The asset layer should not replace the harness core.

It should not own:

- command execution primitives
- runtime adapters
- permission enforcement
- replay storage
- test execution

Those remain code-level control systems.

The asset layer should instead describe:

- repeatable task structures
- reusable expectations
- reusable behavior boundaries

## Design Principle / 设计原则

Keep the asset layer:

- explicit
- small
- reviewable
- easy to evolve without rewriting the loop

That is the real value of this layer.
