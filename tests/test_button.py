"""Tests for the Tion Lite speed buttons."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("homeassistant.components.button")

from custom_components.tion_ble.button import (
    SPEED_BUTTONS,
    TionFanSpeedButton,
)


@pytest.fixture
def entry() -> MagicMock:
    """Create a config entry backed by a minimal coordinator."""
    coordinator = MagicMock()
    coordinator.data = SimpleNamespace(max_fan_speed=6, fan_speed=2)
    coordinator.async_set_state = AsyncMock()
    config_entry = MagicMock()
    config_entry.title = "Tion Lite"
    config_entry.runtime_data.coordinator = coordinator
    config_entry.runtime_data.client.address = "AA:BB:CC:DD:EE:FF"
    return config_entry


def test_six_speed_buttons_are_available() -> None:
    """Expose one action for every hardware speed."""
    assert [description.speed for description in SPEED_BUTTONS] == [1, 2, 3, 4, 5, 6]


async def test_speed_button_turns_on_breezer(entry: MagicMock) -> None:
    """Pressing a speed button should enable airflow at that exact speed."""
    button = TionFanSpeedButton(entry, SPEED_BUTTONS[4])

    await button.async_press()

    button.coordinator.async_set_state.assert_awaited_once_with(
        power=True,
        fan_speed=5,
    )
