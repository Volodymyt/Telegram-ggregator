"""Smoke tests for the canonical unit-test contract."""

from __future__ import annotations

import asyncio
import importlib

import pytest
import pytest_asyncio


@pytest.mark.parametrize(
    "module_name",
    [
        "telegram_aggregator",
        "telegram_aggregator.__main__",
        "telegram_aggregator.login",
        "telegram_aggregator.telegram",
    ],
)
def test_canonical_modules_import(module_name: str) -> None:
    """The canonical package and entry modules stay importable from src layout."""

    module = importlib.import_module(module_name)

    assert module is not None


@pytest_asyncio.fixture
async def async_contract_fixture() -> str:
    """Exercise the strict pytest-asyncio fixture contract."""

    await asyncio.sleep(0)
    return "ready"


@pytest.mark.asyncio
async def test_asyncio_contract_smoke(async_contract_fixture: str) -> None:
    """The canonical runner executes explicitly marked async unit tests."""

    await asyncio.sleep(0)

    assert async_contract_fixture == "ready"
