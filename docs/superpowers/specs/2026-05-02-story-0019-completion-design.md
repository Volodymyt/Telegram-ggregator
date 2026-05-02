# Story 0019 Completion Design

## Context

Story `0019` covers bootstrap, observability, Telegram bootstrap readiness, queue
boundaries, and the verification harness. Its child tasks `0020`, `0021`,
`0022`, and `0023` must all be complete before the story can move to `Done`.

The current branch added JSON logging, an HTTP health endpoint, runtime
readiness flags, and a periodic storage probe, but the existing bootstrap tests
still target the older `client.run_until_disconnected()` lifecycle and do not
cover the new health/readiness contract.

## Chosen Approach

Complete story `0019` through contract-focused bootstrap tests plus minimal
production fixes. The tests should define the expected bootstrap behavior across
the story and its child tasks. Production changes should stay limited to defects
or small seams required to make that behavior deterministic and testable.

This avoids a broad bootstrap refactor while still making the story verifiable.

## Runtime Contract

The health server starts early so operators can see readiness while dependencies
are still unavailable.

Storage readiness is checked periodically through `Storage.check_readiness()`.
Storage errors never crash the process. They set `storage_ready=false`, are
logged correctly, and make the health endpoint return `503`.

Telegram bootstrap is part of story `0019`, but it is gated by storage readiness.
The service must not connect to Telegram while storage is not ready. Once storage
first becomes ready, the service validates and opens the configured Telegram
session through the existing session/login contract. A successful Telegram
context sets `telegram_ready=true`.

If storage later becomes unavailable after Telegram bootstrap, the service keeps
the Telegram connection open and continues running. Queue behavior is out of
scope for this story; no new queue semantics should be introduced here.

Worker readiness is a high-level bootstrap boundary signal. It may become ready
after Telegram bootstrap and queue boundary startup, without implementing
business intake, processing, aggregation, or publishing workers.

Shutdown is explicit and owned by bootstrap. It clears readiness flags, stops
background tasks, cleans up the health server, exits the Telegram context if it
was entered, and closes storage.

## Minimal Production Fixes

- Import `JsonFormatter` from `pythonjsonlogger.json`, not the deprecated
  `pythonjsonlogger.jsonlogger` compatibility module.
- Emit the logging field contract expected by review: `asctime`, `level`, `name`,
  `lineno`, `message`, and `exc_info`.
- Fix storage readiness log calls so exceptions are formatted safely.
- Add a narrow test seam for deterministic shutdown instead of relying on real
  OS signals in unit tests.
- Add a narrow test seam for readiness probe timing and health binding, while
  preserving runtime defaults.
- Gate Telegram bootstrap on storage readiness without crashing when storage is
  initially unavailable.

## Test Contract

`tests/unit/bootstrap/test_service.py` should be updated around the current story
contract rather than the old `run_until_disconnected()` lifecycle.

Fake storage returns real `ReadinessResult` values and can provide a sequence of
ready, not-ready, and exception states. This tests readiness aggregation without
retesting storage internals.

Fake Telegram clients record `__aenter__`, `__aexit__`, session failures, and the
minimal bootstrap calls needed by the current service flow. They do not model
Telethon internals.

Tests should cover:

- initial storage not ready keeps the service alive, reports health `503`, and
  does not enter the Telegram context;
- storage becoming ready later triggers Telegram bootstrap and then worker
  readiness;
- storage failing after Telegram bootstrap changes health to `503` without
  disconnecting Telegram;
- Telegram missing, unusable, or unauthorized session failures remain distinct
  operator-facing failures once storage is ready;
- graceful shutdown cleans up health, storage, and Telegram context when entered;
- health responses aggregate `storage`, `telegram`, `workers`, and `ok`;
- JSON logging emits valid JSON with the required fields;
- periodic storage readiness failures are logged without logging formatter
  errors.

Queue tests stay limited to the bootstrap boundary: queue construction and
`run()` after Telegram readiness. No business queue behavior is added.

## Planning Status

After production and test verification pass, update story `0019` and child tasks
`0020`, `0021`, `0022`, and `0023` from `Status: Ready` to `Status: Done`.

## Verification

Run:

```bash
pytest tests/unit/bootstrap/test_service.py -q
python -m pytest
```

If sandbox socket restrictions prevent aiohttp health checks from binding, run
the same pytest commands outside the sandbox using the approved `pytest` command.
