"""Switch entities for Wakeup Helper."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WakeupHelperConfigEntry
from .const import ROUTINE_NAP
from .entity import WakeupHelperEntity
from .routine import NapController, WakeupController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WakeupHelperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a routine switch."""
    controller = entry.runtime_data
    if entry.data["routine_type"] == ROUTINE_NAP:
        async_add_entities(
            [
                NapSwitch(entry, controller),
                NapEndLightsSwitch(entry, controller),
                NapOpenCoversSwitch(entry, controller),
            ]
        )
    else:
        async_add_entities([WakeupSwitch(entry, controller)])


class NapSwitch(WakeupHelperEntity, SwitchEntity):
    """Start or end a nap."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:sleep"

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "switch")
        self.controller = controller
        self._attr_name = entry.title

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose this routine's entities and device to its dashboard card."""
        attributes: dict[str, Any] = {
            "wakeup_helper_entities": dict(self.controller.entity_ids)
        }
        if device_id := self.device_registry_id:
            attributes["wakeup_helper_device_id"] = device_id
        return attributes

    @property
    def is_on(self) -> bool:
        return self.controller.active

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_turn_on()

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_turn_off()


class WakeupSwitch(WakeupHelperEntity, SwitchEntity):
    """Enable or disable a wake-up light."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:weather-sunset-up"

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "switch")
        self.controller = controller
        self._attr_name = entry.title

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose this routine's entities and device to its dashboard card."""
        attributes: dict[str, Any] = {
            "wakeup_helper_entities": dict(self.controller.entity_ids)
        }
        if device_id := self.device_registry_id:
            attributes["wakeup_helper_device_id"] = device_id
        return attributes

    @property
    def is_on(self) -> bool:
        return self.controller.enabled

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_set_enabled(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_set_enabled(False)


class NapEndLightsSwitch(WakeupHelperEntity, SwitchEntity):
    """Choose whether lights turn on when a nap ends."""

    _attr_translation_key = "turn_on_lights_at_end"
    _attr_icon = "mdi:lightbulb-on-outline"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "turn_on_lights_at_end")
        self.controller = controller

    @property
    def is_on(self) -> bool:
        return self.controller.turn_on_lights_at_end

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_set_turn_on_lights_at_end(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_set_turn_on_lights_at_end(False)


class NapOpenCoversSwitch(WakeupHelperEntity, SwitchEntity):
    """Choose whether covers open when a nap ends."""

    _attr_translation_key = "open_covers_at_end"
    _attr_icon = "mdi:window-shutter-open"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "open_covers_at_end")
        self.controller = controller

    @property
    def is_on(self) -> bool:
        return self.controller.open_covers_at_end

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_set_open_covers_at_end(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_set_open_covers_at_end(False)
