"""Switch entities for Wakeup Helper."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WakeupHelperConfigEntry
from .const import DOMAIN, ROUTINE_NAP
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
        entities: list[SwitchEntity] = [NapSwitch(entry, controller)]
        active_action_keys: set[str] = set()
        if controller.light_target:
            entities.append(NapTurnOffLightsSwitch(entry, controller))
            active_action_keys.add("turn_off_lights_at_start")
        if controller.cover_target:
            entities.extend(
                [
                    NapCloseCoversSwitch(entry, controller),
                    NapOpenCoversSwitch(entry, controller),
                ]
            )
            active_action_keys.update(
                {"close_covers_at_start", "open_covers_at_end"}
            )
        if controller.end_light_target:
            entities.append(NapEndLightsSwitch(entry, controller))
            active_action_keys.add("turn_on_lights_at_end")

        registry = er.async_get(hass)
        for key in {
            "turn_off_lights_at_start",
            "close_covers_at_start",
            "open_covers_at_end",
            "turn_on_lights_at_end",
        } - active_action_keys:
            if entity_id := registry.async_get_entity_id(
                "switch", DOMAIN, f"{entry.entry_id}_{key}"
            ):
                registry.async_remove(entity_id)
        async_add_entities(entities)
    else:
        async_add_entities([WakeupSwitch(entry, controller)])


class NapSwitch(WakeupHelperEntity, SwitchEntity):
    """Start or end a nap."""

    _attr_translation_key = "nap_control"
    _attr_icon = "mdi:sleep"

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "switch")
        self.controller = controller

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose this routine's entities and device to its dashboard card."""
        attributes: dict[str, Any] = {
            "wakeup_helper_entities": dict(self.controller.entity_ids),
            "wakeup_helper_name": self._entry.title,
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

    _attr_translation_key = "wakeup_control"
    _attr_icon = "mdi:weather-sunset-up"

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "switch")
        self.controller = controller

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose this routine's entities and device to its dashboard card."""
        attributes: dict[str, Any] = {
            "wakeup_helper_entities": dict(self.controller.entity_ids),
            "wakeup_helper_name": self._entry.title,
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


class NapTurnOffLightsSwitch(WakeupHelperEntity, SwitchEntity):
    """Choose whether lights turn off when a nap starts."""

    _attr_translation_key = "turn_off_lights_at_start"
    _attr_icon = "mdi:lightbulb-off-outline"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "turn_off_lights_at_start")
        self.controller = controller

    @property
    def is_on(self) -> bool:
        return self.controller.turn_off_lights_at_start

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_set_turn_off_lights_at_start(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_set_turn_off_lights_at_start(False)


class NapCloseCoversSwitch(WakeupHelperEntity, SwitchEntity):
    """Choose whether covers close when a nap starts."""

    _attr_translation_key = "close_covers_at_start"
    _attr_icon = "mdi:window-shutter"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "close_covers_at_start")
        self.controller = controller

    @property
    def is_on(self) -> bool:
        return self.controller.close_covers_at_start

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.controller.async_set_close_covers_at_start(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.controller.async_set_close_covers_at_start(False)


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
