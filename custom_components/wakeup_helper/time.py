"""Time entities for Wakeup Helper."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WakeupHelperConfigEntry
from .const import ROUTINE_WAKEUP
from .entity import WakeupHelperEntity
from .routine import WakeupController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WakeupHelperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a wake-up alarm time entity."""
    if entry.data["routine_type"] == ROUTINE_WAKEUP:
        async_add_entities([AlarmTimeEntity(entry, entry.runtime_data)])


class AlarmTimeEntity(WakeupHelperEntity, TimeEntity):
    """Configure a wake-up light's alarm time."""

    _attr_translation_key = "alarm_time"
    _attr_icon = "mdi:alarm"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "alarm_time")
        self.controller = controller

    @property
    def native_value(self) -> time:
        return self.controller.alarm_time

    async def async_set_value(self, value: time) -> None:
        await self.controller.async_set_alarm_time(value)
