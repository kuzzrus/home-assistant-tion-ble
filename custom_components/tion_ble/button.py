"""Button platform for Tion Lite."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import TionBleConfigEntry
from .const import DEFAULT_MAX_FAN_SPEED
from .entity import TionBleEntity


@dataclass(frozen=True, kw_only=True)
class TionSpeedButtonDescription(ButtonEntityDescription):
    """Describe a Tion Lite speed button."""

    speed: int


SPEED_BUTTONS = tuple(
    TionSpeedButtonDescription(
        key=f"fan_speed_{speed}",
        translation_key=f"fan_speed_{speed}",
        icon=f"mdi:numeric-{speed}-circle",
        speed=speed,
    )
    for speed in range(1, DEFAULT_MAX_FAN_SPEED + 1)
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TionBleConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ventilation speed buttons."""
    max_speed = entry.runtime_data.coordinator.data.max_fan_speed
    if max_speed <= 0:
        max_speed = DEFAULT_MAX_FAN_SPEED
    async_add_entities(
        TionFanSpeedButton(entry, description)
        for description in SPEED_BUTTONS
        if description.speed <= max_speed
    )


class TionFanSpeedButton(TionBleEntity, ButtonEntity):
    """Set one exact Tion Lite ventilation speed."""

    entity_description: TionSpeedButtonDescription

    def __init__(
        self,
        entry: TionBleConfigEntry,
        description: TionSpeedButtonDescription,
    ) -> None:
        """Initialize the speed button."""
        super().__init__(entry, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Turn on the breezer at this speed."""
        await self.coordinator.async_set_state(
            power=True,
            fan_speed=self.entity_description.speed,
        )
