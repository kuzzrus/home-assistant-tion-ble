"""Tests for selecting one BlueZ path when multiple adapters see a device."""

from types import SimpleNamespace

import pytest

from custom_components.tion_ble import bluez_pairing


class _Message:
    """Keep the D-Bus message fields used by the fake bus."""

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


class _ObjectManagerBus:
    """Return a fixed BlueZ object tree."""

    def __init__(self, managed_objects: dict) -> None:
        self.managed_objects = managed_objects

    async def call(self, _message):
        return SimpleNamespace(message_type="return", body=[self.managed_objects])


@pytest.fixture(autouse=True)
def fake_dbus_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permit the selection helper to run on non-Linux test hosts."""
    monkeypatch.setattr(bluez_pairing, "Message", _Message)
    monkeypatch.setattr(
        bluez_pairing,
        "MessageType",
        SimpleNamespace(ERROR="error"),
    )


def _device(address: str) -> dict:
    """Build the relevant subset of a BlueZ Device1 object."""
    return {
        "org.bluez.Device1": {
            "Address": address,
        }
    }


async def test_selected_hci1_path_wins_when_hci0_has_same_address() -> None:
    """Do not pair through the first adapter merely because it appears first."""
    address = "AA:BB:CC:DD:EE:FF"
    hci0_path = "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"
    hci1_path = "/org/bluez/hci1/dev_AA_BB_CC_DD_EE_FF"
    bus = _ObjectManagerBus(
        {
            hci0_path: _device(address),
            hci1_path: _device(address),
        }
    )

    result = await bluez_pairing._find_device_path(bus, address, hci1_path)

    assert result == hci1_path


async def test_missing_selected_path_does_not_fall_back_to_other_hci() -> None:
    """Avoid silently pairing through a different local adapter."""
    address = "AA:BB:CC:DD:EE:FF"
    hci0_path = "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"
    missing_hci1_path = "/org/bluez/hci1/dev_AA_BB_CC_DD_EE_FF"
    bus = _ObjectManagerBus({hci0_path: _device(address)})

    result = await bluez_pairing._find_device_path(
        bus,
        address,
        missing_hci1_path,
    )

    assert result is None
