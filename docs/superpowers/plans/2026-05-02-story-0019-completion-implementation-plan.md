# Story 0019 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete story `0019` and child tasks `0020`-`0023` by making bootstrap lifecycle, Telegram readiness, health, logging, storage readiness probing, tests, and planning statuses align.

**Architecture:** Keep `ServiceRuntime` as the bootstrap owner, but add narrow test seams for shutdown, probe timing, and health binding. Storage readiness is a non-fatal continuously updated signal; Telegram bootstrap is gated until storage first becomes ready and remains connected if storage later degrades.

**Tech Stack:** Python 3.12, asyncio, aiohttp, python-json-logger 4.1.0, pytest, pytest-asyncio.

---

## File Structure

- Modify `src/telegram_aggregator/bootstrap/service.py`: runtime lifecycle, readiness probing, Telegram gating, shutdown cleanup, JSON logging contract, and test seams.
- Modify `tests/unit/bootstrap/test_service.py`: replace stale run-until-disconnected expectations with contract tests for storage gating, Telegram bootstrap, health, logging, periodic readiness, and shutdown.
- Modify planning docs after tests pass:
  - `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md`
  - `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/01_0020_runtime_lifecycle_queue_boundaries.md`
  - `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/02_0021_telegram_client_bootstrap.md`
  - `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/03_0022_observability_health_surface.md`
  - `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/04_0023_bootstrap_verification_harness.md`

Do not touch `docs_ua/` or any `brief.uk.md` file because `.codexignore` excludes them.

---

### Task 1: Add Deterministic Runtime Seams and Storage Readiness Helpers

**Files:**
- Modify: `src/telegram_aggregator/bootstrap/service.py`
- Test: `tests/unit/bootstrap/test_service.py`

- [ ] **Step 1: Write failing tests for readiness helper behavior**

Add these imports near the top of `tests/unit/bootstrap/test_service.py`:

```python
import asyncio
import json
import logging

import pytest

from telegram_aggregator.bootstrap.service import ServiceRuntime, run_service
from telegram_aggregator.config import load_app_config
from telegram_aggregator.storage import ReadinessResult, StorageConfigError
```

Replace the old import block if needed so `run_service` is still imported and `ServiceRuntime`, `load_app_config`, and `ReadinessResult` are available.

Replace `_FakeStorage` with this sequence-aware fake:

```python
class _FakeStorage:
    def __init__(
        self,
        events: list[object],
        *,
        readiness_results: list[ReadinessResult | Exception] | None = None,
    ) -> None:
        self._events = events
        self._readiness_results = readiness_results or [
            ReadinessResult(db_reachable=True, migrations_current=True)
        ]
        self._readiness_index = 0
        self.closed = False

    async def check_readiness(self) -> ReadinessResult:
        self._events.append("storage-check")
        result = self._readiness_results[
            min(self._readiness_index, len(self._readiness_results) - 1)
        ]
        self._readiness_index += 1

        if isinstance(result, Exception):
            raise result

        return result

    async def close(self) -> None:
        self.closed = True
        self._events.append("storage-close")
```

Replace `_install_fake_storage()` with:

```python
def _install_fake_storage(
    monkeypatch: pytest.MonkeyPatch,
    events: list[object],
    *,
    readiness_results: list[ReadinessResult | Exception] | None = None,
) -> _FakeStorage:
    storage = _FakeStorage(events, readiness_results=readiness_results)

    def _build_storage(database_url: str) -> _FakeStorage:
        events.append(("storage-build", database_url))
        return storage

    monkeypatch.setattr(
        "telegram_aggregator.bootstrap.service.build_storage",
        _build_storage,
    )
    return storage
```

Add this test:

```python
@pytest.mark.asyncio
async def test_storage_readiness_refresh_sets_ready_state(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
            ReadinessResult(db_reachable=True, migrations_current=False),
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )

    config = load_app_config()
    runtime = ServiceRuntime(config, storage_probe_interval=0.01)

    assert await runtime._refresh_storage_readiness() is True
    assert runtime._readiness.storage_ready is True

    assert await runtime._refresh_storage_readiness() is False
    assert runtime._readiness.storage_ready is False

    assert await runtime._refresh_storage_readiness() is False
    assert runtime._readiness.storage_ready is False
```

- [ ] **Step 2: Run the focused test and confirm it fails**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_storage_readiness_refresh_sets_ready_state -q
```

Expected: FAIL because `ServiceRuntime.__init__()` does not accept `storage_probe_interval` and `_refresh_storage_readiness()` does not exist.

- [ ] **Step 3: Implement runtime seams and readiness helper**

In `src/telegram_aggregator/bootstrap/service.py`, adjust imports:

```python
import contextlib
from collections.abc import Awaitable, Callable

from pythonjsonlogger.json import JsonFormatter
```

Remove:

```python
from pythonjsonlogger.jsonlogger import JsonFormatter
```

Change `ServiceRuntime.__init__()` to:

```python
    def __init__(
        self,
        config: AppConfig,
        *,
        storage_probe_interval: float = _STORAGE_PROBE_INTERVAL,
        shutdown_waiter: Callable[[], Awaitable[None]] | None = None,
        health_host: str = _HEALTH_HOST,
        health_port: int = _HEALTH_PORT,
    ) -> None:
        from telegram_aggregator.processing.message_queue import MessageQueue
        from telegram_aggregator.telegram import TelegramClient

        self._config = config
        self._storage = build_storage(config.database_url)
        self._client = TelegramClient(config)
        self._message_queue = MessageQueue()
        self._readiness = RuntimeReadiness()
        self._health_runner: web.AppRunner | None = None
        self._health_site: web.TCPSite | None = None
        self._tasks: list[asyncio.Task] = []
        self._storage_probe_interval = storage_probe_interval
        self._shutdown_waiter = shutdown_waiter or self._wait_for_shutdown_signal
        self._health_host = health_host
        self._health_port = health_port
```

Add this method inside `ServiceRuntime`:

```python
    async def _refresh_storage_readiness(self) -> bool:
        try:
            result = await self._storage.check_readiness()
        except StorageError as exc:
            logger.warning("Storage readiness probe failed: %s", exc)
            self._readiness.storage_ready = False
            return False

        ready = result.db_reachable and result.migrations_current
        self._readiness.storage_ready = ready
        return ready
```

Change `_storage_probe_loop()` to accept an event and probe immediately:

```python
    async def _storage_probe_loop(self, storage_ready_event: asyncio.Event) -> None:
        while True:
            ready = await self._refresh_storage_readiness()
            if ready:
                storage_ready_event.set()
            else:
                storage_ready_event.clear()
            await asyncio.sleep(self._storage_probe_interval)
```

Update `_start_health_server()` to use the injectable host and port while
preserving the runtime defaults:

```python
    async def _start_health_server(self) -> None:
        app = web.Application()
        app.router.add_get("/health", self._handle_health)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host=self._health_host, port=self._health_port)
        await site.start()

        self._health_runner = runner
        self._health_site = site
        logger.info(
            "Health endpoint listening on http://%s:%d/health",
            self._health_host,
            self._health_port,
        )
```

Update `_stop_health_server()` so the stored site reference is cleared:

```python
    async def _stop_health_server(self) -> None:
        if self._health_runner is not None:
            await self._health_runner.cleanup()
            self._health_runner = None
            self._health_site = None
```

Change `_stop_all_tasks()` to async cleanup:

```python
    async def _stop_all_tasks(self) -> None:
        tasks = list(self._tasks)
        self._tasks = []

        for task in tasks:
            task.cancel()

        if tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(*tasks, return_exceptions=True)
```

- [ ] **Step 4: Run the focused test and confirm it passes**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_storage_readiness_refresh_sets_ready_state -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "test: cover bootstrap storage readiness refresh"
```

---

### Task 2: Gate Telegram Bootstrap on Storage Readiness

**Files:**
- Modify: `src/telegram_aggregator/bootstrap/service.py`
- Test: `tests/unit/bootstrap/test_service.py`

- [ ] **Step 1: Add deterministic fakes for runtime lifecycle tests**

Add these helper classes to `tests/unit/bootstrap/test_service.py` after `_install_fake_storage()`:

```python
class _ShutdownController:
    def __init__(self) -> None:
        self._event = asyncio.Event()

    async def wait(self) -> None:
        await self._event.wait()

    def trigger(self) -> None:
        self._event.set()


class _FakeQueue:
    def __init__(self, events: list[object]) -> None:
        self._events = events

    def run(self) -> None:
        self._events.append("queue-run")

    def push(self, message) -> None:
        self._events.append(("queue-push", message))

    def stop(self) -> None:
        self._events.append("queue-stop")


class _FakeClient:
    events: list[object] = []
    enter_event: asyncio.Event | None = None
    exit_event: asyncio.Event | None = None

    def __init__(self, config) -> None:
        self.events = type(self).events
        self.events.append(("client-init", config.dry_run, config.telegram.session_path))

    async def __aenter__(self):
        self.events.append("client-enter")
        if self.enter_event is not None:
            self.enter_event.set()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.events.append("client-exit")
        if self.exit_event is not None:
            self.exit_event.set()
        return False

    def subscribe_to_new_messages(self, callback) -> None:
        self.events.append("subscribe")

    async def get_user_channels(self) -> list[object]:
        self.events.append("get-user-channels")
        return []
```

Add this installer:

```python
def _install_fake_runtime_components(
    monkeypatch: pytest.MonkeyPatch,
    events: list[object],
) -> None:
    _FakeClient.events = events
    _FakeClient.enter_event = None
    _FakeClient.exit_event = None

    def _queue_factory() -> _FakeQueue:
        events.append("queue-init")
        return _FakeQueue(events)

    monkeypatch.setattr(
        "telegram_aggregator.processing.message_queue.MessageQueue",
        _queue_factory,
    )
    monkeypatch.setattr("telegram_aggregator.telegram.TelegramClient", _FakeClient)
```

- [ ] **Step 2: Add failing test for initial storage not ready**

Add:

```python
@pytest.mark.asyncio
async def test_runtime_waits_for_storage_before_telegram_bootstrap(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.sleep(0.05)

    assert "client-enter" not in events
    assert "queue-run" not in events
    assert runtime._readiness.storage_ready is False
    assert runtime._readiness.telegram_ready is False
    assert runtime._readiness.workers_ready is False

    shutdown.trigger()
    await task
    assert "storage-close" in events
```

Add `_async_noop` near helpers:

```python
async def _async_noop() -> None:
    return None
```

- [ ] **Step 3: Run the focused test and confirm it fails**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_runtime_waits_for_storage_before_telegram_bootstrap -q
```

Expected: FAIL because current `run()` enters Telegram even when storage readiness is false.

- [ ] **Step 4: Implement wait-for-storage gate**

Add this helper method inside `ServiceRuntime`:

```python
    async def _wait_for_storage_ready_or_shutdown(
        self,
        storage_ready_event: asyncio.Event,
        shutdown_task: asyncio.Task,
    ) -> bool:
        while not storage_ready_event.is_set():
            wait_task = asyncio.create_task(storage_ready_event.wait())
            done, pending = await asyncio.wait(
                {wait_task, shutdown_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if shutdown_task in done:
                return False

        return True
```

Replace `ServiceRuntime.run()` with:

```python
    async def run(self) -> None:
        storage_ready_event = asyncio.Event()

        try:
            await self._start_health_server()

            probe_task = asyncio.create_task(
                self._storage_probe_loop(storage_ready_event)
            )
            self._tasks.append(probe_task)

            shutdown_task = asyncio.create_task(self._shutdown_waiter())
            self._tasks.append(shutdown_task)

            if not await self._wait_for_storage_ready_or_shutdown(
                storage_ready_event,
                shutdown_task,
            ):
                await shutdown_task
                return

            async with self._client as client:
                self._readiness.telegram_ready = True
                client.subscribe_to_new_messages(self.on_new_message)

                logger.info("Listening for new messages")
                logger.info("Load channels...")
                channels = await client.get_user_channels()

                for channel in channels:
                    logger.info("  channel • [%s] %s", channel.tg_id, channel.title)

                logger.info("Load history...")

                if channels:
                    messages = await client.fetch_channel_history(
                        channels[0].tg_id,
                        limit=50,
                    )

                    for message in messages:
                        self._message_queue.push(message)

                self._readiness.workers_ready = True
                self._message_queue.run()

                await shutdown_task

        finally:
            self._readiness.workers_ready = False
            self._readiness.telegram_ready = False
            self._readiness.storage_ready = False
            await self._stop_all_tasks()
            await self._stop_health_server()
            await self._storage.close()
```

- [ ] **Step 5: Run the focused test and confirm it passes**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_runtime_waits_for_storage_before_telegram_bootstrap -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "feat: gate telegram bootstrap on storage readiness"
```

---

### Task 3: Cover Storage Recovery and Degradation Without Telegram Disconnect

**Files:**
- Modify: `tests/unit/bootstrap/test_service.py`
- Modify only if needed: `src/telegram_aggregator/bootstrap/service.py`

- [ ] **Step 1: Add failing test for storage becoming ready**

Add:

```python
@pytest.mark.asyncio
async def test_storage_recovery_starts_telegram_and_workers(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
            ReadinessResult(db_reachable=True, migrations_current=True),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    _FakeClient.enter_event = asyncio.Event()
    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.wait_for(_FakeClient.enter_event.wait(), timeout=1)

    assert "client-enter" in events
    assert "subscribe" in events
    assert "queue-run" in events
    assert runtime._readiness.storage_ready is True
    assert runtime._readiness.telegram_ready is True
    assert runtime._readiness.workers_ready is True

    shutdown.trigger()
    await task
    _FakeClient.enter_event = None
```

- [ ] **Step 2: Run the focused test and confirm it fails if Task 2 did not fully implement recovery**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_storage_recovery_starts_telegram_and_workers -q
```

Expected: PASS after Task 2. If it fails, the failure should show that the storage-ready event is not being set from the probe loop.

- [ ] **Step 3: Add failing test for storage degradation after Telegram bootstrap**

Add:

```python
@pytest.mark.asyncio
async def test_storage_degradation_keeps_telegram_connected(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=True, migrations_current=True),
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    _FakeClient.enter_event = asyncio.Event()
    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.wait_for(_FakeClient.enter_event.wait(), timeout=1)
    await asyncio.sleep(0.05)

    assert "client-enter" in events
    assert "client-exit" not in events
    assert runtime._readiness.storage_ready is False
    assert runtime._readiness.telegram_ready is True
    assert runtime._readiness.workers_ready is True

    shutdown.trigger()
    await task
    assert "client-exit" in events
    _FakeClient.enter_event = None
```

- [ ] **Step 4: Run both storage lifecycle tests**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_storage_recovery_starts_telegram_and_workers tests/unit/bootstrap/test_service.py::test_storage_degradation_keeps_telegram_connected -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "test: cover bootstrap storage recovery and degradation"
```

---

### Task 4: Update Telegram Bootstrap Failure Tests

**Files:**
- Modify: `tests/unit/bootstrap/test_service.py`
- Modify only if needed: `src/telegram_aggregator/bootstrap/service.py`

- [ ] **Step 1: Update fake storage defaults and remove stale successful run expectations**

Delete or rewrite these old tests because they assert the removed `run_until_disconnected()` contract:

```python
test_run_service_dry_run_skips_telegram_runtime
test_run_service_uses_telegram_runtime_when_not_dry_run
test_run_service_surfaces_storage_readiness_errors_cleanly
```

Keep the config validation tests:

```python
test_run_service_exits_cleanly_on_missing_database_url
test_run_service_exits_cleanly_on_invalid_log_level
test_run_service_exits_cleanly_on_invalid_yaml_shape
test_run_service_exits_cleanly_on_invalid_identifier
```

- [ ] **Step 2: Add helper to make `run_service()` fail after storage ready without real health binding**

Add:

```python
def _disable_health_server(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _start(self) -> None:
        return None

    async def _stop(self) -> None:
        return None

    monkeypatch.setattr(ServiceRuntime, "_start_health_server", _start)
    monkeypatch.setattr(ServiceRuntime, "_stop_health_server", _stop)
```

- [ ] **Step 3: Update Telegram failure tests to pass readiness results**

In each existing Telegram failure test, change `_install_fake_storage(monkeypatch, [])` to:

```python
events: list[object] = []
_install_fake_storage(
    monkeypatch,
    events,
    readiness_results=[
        ReadinessResult(db_reachable=True, migrations_current=True),
    ],
)
_disable_health_server(monkeypatch)
```

Apply this to:

```python
test_run_service_rejects_missing_session_file
test_run_service_surfaces_unauthorized_session
test_run_service_surfaces_session_path_errors_from_post_connect_runtime
test_run_service_surfaces_unexpected_errors_as_clean_exit
```

- [ ] **Step 4: Run Telegram failure tests**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_run_service_rejects_missing_session_file tests/unit/bootstrap/test_service.py::test_run_service_surfaces_unauthorized_session tests/unit/bootstrap/test_service.py::test_run_service_surfaces_session_path_errors_from_post_connect_runtime tests/unit/bootstrap/test_service.py::test_run_service_surfaces_unexpected_errors_as_clean_exit -q
```

Expected: PASS. These tests prove Telegram bootstrap remains in scope and surfaces session failures distinctly after storage is ready.

- [ ] **Step 5: Commit**

```bash
git add tests/unit/bootstrap/test_service.py
git commit -m "test: align telegram bootstrap failure coverage"
```

---

### Task 5: Cover Health Responses and JSON Logging Contract

**Files:**
- Modify: `src/telegram_aggregator/bootstrap/service.py`
- Modify: `tests/unit/bootstrap/test_service.py`

- [ ] **Step 1: Add health handler tests**

Add:

```python
@pytest.mark.asyncio
async def test_health_response_reports_not_ready_components(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(monkeypatch, events)

    config = load_app_config()
    runtime = ServiceRuntime(config)
    runtime._readiness.storage_ready = True
    runtime._readiness.telegram_ready = False
    runtime._readiness.workers_ready = False

    response = await runtime._handle_health(None)  # type: ignore[arg-type]
    payload = json.loads(response.text)

    assert response.status == 503
    assert payload == {
        "ok": False,
        "storage": True,
        "telegram": False,
        "workers": False,
    }


@pytest.mark.asyncio
async def test_health_response_reports_ready_runtime(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(monkeypatch, events)

    config = load_app_config()
    runtime = ServiceRuntime(config)
    runtime._readiness.storage_ready = True
    runtime._readiness.telegram_ready = True
    runtime._readiness.workers_ready = True

    response = await runtime._handle_health(None)  # type: ignore[arg-type]
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload == {
        "ok": True,
        "storage": True,
        "telegram": True,
        "workers": True,
    }
```

- [ ] **Step 2: Add JSON logging contract test**

Update imports:

```python
from telegram_aggregator.bootstrap.service import (
    ServiceRuntime,
    _configure_json_logging,
    run_service,
)
```

Add:

```python
def test_configure_json_logging_emits_required_fields(capsys) -> None:
    _configure_json_logging(logging.INFO)
    logger = logging.getLogger("telegram_aggregator.tests")

    logger.info("hello")
    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert payload["level"] == "INFO"
    assert payload["name"] == "telegram_aggregator.tests"
    assert payload["message"] == "hello"
    assert "asctime" in payload
    assert "lineno" in payload
    assert "exc_info" in payload
```

- [ ] **Step 3: Run tests and confirm JSON logging test fails before formatter fix**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_health_response_reports_not_ready_components tests/unit/bootstrap/test_service.py::test_health_response_reports_ready_runtime tests/unit/bootstrap/test_service.py::test_configure_json_logging_emits_required_fields -q
```

Expected: health tests PASS; logging test FAIL because current payload uses `levelname` and imports the deprecated compatibility module.

- [ ] **Step 4: Fix JSON logger import and field contract**

In `src/telegram_aggregator/bootstrap/service.py`, make sure the import is:

```python
from pythonjsonlogger.json import JsonFormatter
```

Change `_configure_json_logging()` formatter setup to:

```python
    formatter = JsonFormatter(
        ["asctime", "levelname", "name", "lineno", "message", "exc_info"],
        rename_fields={"levelname": "level"},
    )
    handler.setFormatter(formatter)
```

- [ ] **Step 5: Run health and logging tests again**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_health_response_reports_not_ready_components tests/unit/bootstrap/test_service.py::test_health_response_reports_ready_runtime tests/unit/bootstrap/test_service.py::test_configure_json_logging_emits_required_fields -q
```

Expected: PASS with no `pythonjsonlogger.jsonlogger` deprecation warning.

- [ ] **Step 6: Commit**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "test: cover bootstrap health and json logging"
```

---

### Task 6: Verify Logging Errors Are Gone and Cleanup Is Graceful

**Files:**
- Modify: `tests/unit/bootstrap/test_service.py`
- Modify only if needed: `src/telegram_aggregator/bootstrap/service.py`

- [ ] **Step 1: Add test for storage exception logging**

Add:

```python
@pytest.mark.asyncio
async def test_storage_probe_failure_logs_without_formatter_error(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            StorageConfigError("DB unreachable: connection refused"),
        ],
    )

    config = load_app_config()
    runtime = ServiceRuntime(config)

    with caplog.at_level(logging.WARNING):
        assert await runtime._refresh_storage_readiness() is False

    assert "Storage readiness probe failed: DB unreachable: connection refused" in caplog.text
```

- [ ] **Step 2: Add test for shutdown cleanup before Telegram bootstrap**

Add:

```python
@pytest.mark.asyncio
async def test_shutdown_before_storage_ready_cleans_up_without_telegram(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    events: list[object] = []
    _install_fake_storage(
        monkeypatch,
        events,
        readiness_results=[
            ReadinessResult(db_reachable=False, migrations_current=False),
        ],
    )
    _install_fake_runtime_components(monkeypatch, events)

    shutdown = _ShutdownController()
    config = load_app_config()
    runtime = ServiceRuntime(
        config,
        storage_probe_interval=0.01,
        shutdown_waiter=shutdown.wait,
    )
    monkeypatch.setattr(runtime, "_start_health_server", _async_noop)
    monkeypatch.setattr(runtime, "_stop_health_server", _async_noop)

    task = asyncio.create_task(runtime.run())
    await asyncio.sleep(0.02)
    shutdown.trigger()
    await task

    assert "client-enter" not in events
    assert "storage-close" in events
    assert runtime._readiness.storage_ready is False
    assert runtime._readiness.telegram_ready is False
    assert runtime._readiness.workers_ready is False
```

- [ ] **Step 3: Run cleanup and logging tests**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py::test_storage_probe_failure_logs_without_formatter_error tests/unit/bootstrap/test_service.py::test_shutdown_before_storage_ready_cleans_up_without_telegram -q
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "test: cover bootstrap readiness logging and cleanup"
```

---

### Task 7: Run Bootstrap Suite and Full Unit Suite

**Files:**
- Modify only if test failures require scoped fixes:
  - `src/telegram_aggregator/bootstrap/service.py`
  - `tests/unit/bootstrap/test_service.py`

- [ ] **Step 1: Run bootstrap tests**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py -q
```

Expected: all tests in `tests/unit/bootstrap/test_service.py` PASS.

If sandbox local socket restrictions cause `PermissionError` or aiohttp bind failures, rerun the same command outside the sandbox with:

```bash
pytest tests/unit/bootstrap/test_service.py -q
```

The `pytest` command prefix is already approved for escalation.

- [ ] **Step 2: Fix only failures directly related to story 0019 contract**

If tests fail, inspect the failure and adjust only:

```python
src/telegram_aggregator/bootstrap/service.py
tests/unit/bootstrap/test_service.py
```

Do not refactor queue internals, storage internals, Telegram adapter internals, or planning docs in this step.

- [ ] **Step 3: Run full test suite**

Run:

```bash
python -m pytest
```

Expected: full suite PASS.

- [ ] **Step 4: Commit final code/test fixes if any were needed**

```bash
git add src/telegram_aggregator/bootstrap/service.py tests/unit/bootstrap/test_service.py
git commit -m "fix: complete story 0019 bootstrap verification"
```

If Task 7 required no new edits after earlier commits, skip this commit.

---

### Task 8: Update Planning Statuses

**Files:**
- Modify: `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md`
- Modify: `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/01_0020_runtime_lifecycle_queue_boundaries.md`
- Modify: `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/02_0021_telegram_client_bootstrap.md`
- Modify: `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/03_0022_observability_health_surface.md`
- Modify: `docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/04_0023_bootstrap_verification_harness.md`

- [ ] **Step 1: Confirm tests are green before status edits**

Confirm the latest completed commands include:

```text
pytest tests/unit/bootstrap/test_service.py -q
python -m pytest
```

Both must have exit code `0`.

- [ ] **Step 2: Update story and task statuses**

In all five planning files listed above, change:

```markdown
Status: Ready
```

to:

```markdown
Status: Done
```

Change:

```markdown
Last updated: 2026-03-15
```

or:

```markdown
Last updated: 2026-03-16
```

to:

```markdown
Last updated: 2026-05-02
```

- [ ] **Step 3: Verify no ignored docs were touched**

Run:

```bash
git status --short
```

Expected changed planning paths are under `docs/planning/active/.../05_0019_bootstrap_observability_test_harness/` and no path includes `docs_ua/` or `brief.uk.md`.

- [ ] **Step 4: Commit planning status updates**

```bash
git add docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/01_0020_runtime_lifecycle_queue_boundaries.md docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/02_0021_telegram_client_bootstrap.md docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/03_0022_observability_health_surface.md docs/planning/active/01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/tasks/04_0023_bootstrap_verification_harness.md
git commit -m "docs: mark story 0019 complete"
```

---

### Task 9: Final Verification and Review Summary

**Files:**
- No planned edits.

- [ ] **Step 1: Run final verification**

Run:

```bash
pytest tests/unit/bootstrap/test_service.py -q
python -m pytest
git status --short
```

Expected:

```text
tests/unit/bootstrap/test_service.py: all pass
full pytest suite: all pass
git status --short: clean or only intentional uncommitted plan artifacts
```

- [ ] **Step 2: Prepare final review summary**

Summarize:

```text
- Storage readiness is non-fatal and periodically updates health.
- Telegram bootstrap is gated until storage is ready and stays connected if storage later degrades.
- Health responses cover storage/telegram/workers/ok.
- JSON logging uses pythonjsonlogger.json.JsonFormatter and emits level.
- Story 0019 and tasks 0020-0023 are marked Done after verification.
- Verification commands and pass/fail results.
```

Do not claim completion unless both verification commands passed in the current run.
