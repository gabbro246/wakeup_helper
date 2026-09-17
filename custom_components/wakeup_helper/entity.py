"""Shared entity support for Wakeup Helper."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from . import WakeupHelperConfigEntry
from .const import DOMAIN, ROUTINE_NAP
from .routine import RoutineController


class WakeupHelperEntity(Entity):
    """Base class for entities belonging to a routine device."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        entry: WakeupHelperConfigEntry,
        controller: RoutineController,
        key: str,
    ) -> None:
        self._entry = entry
        self.controller = controller
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        routine_type = entry.data["routine_type"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Wakeup Helper",
            model="Nap mode" if routine_type == ROUTINE_NAP else "Wake-up light",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime state changes."""
        self.async_on_remove(
            self.controller.async_add_listener(self.async_write_ha_state)
        )
