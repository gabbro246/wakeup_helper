"""Number entities for Wakeup Helper."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
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
    """Set up routine number entities."""
    controller = entry.runtime_data
    if entry.data["routine_type"] == ROUTINE_NAP:
        async_add_entities([NapDurationNumber(entry, controller)])
    else:
        async_add_entities(
            [
                FadeDurationNumber(entry, controller),
                EndBrightnessNumber(entry, controller),
            ]
        )


class NapDurationNumber(WakeupHelperEntity, NumberEntity):
    """Configure a nap's duration."""

    _attr_translation_key = "nap_duration"
    _attr_icon = "mdi:timer-sand"
    _attr_device_class = NumberDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = 15
    _attr_native_max_value = 90
    _attr_native_step = 5
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "duration")
        self.controller = controller

    @property
    def native_value(self) -> float:
        return self.controller.duration

    async def async_set_native_value(self, value: float) -> None:
        await self.controller.async_set_duration(value)


class FadeDurationNumber(WakeupHelperEntity, NumberEntity):
    """Configure a wake-up light's fade duration."""

    _attr_translation_key = "fade_duration"
    _attr_icon = "mdi:weather-sunset-up"
    _attr_device_class = NumberDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = 0
    _attr_native_max_value = 120
    _attr_native_step = 5
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "fade_duration")
        self.controller = controller

    @property
    def native_value(self) -> float:
        return self.controller.fade_duration

    async def async_set_native_value(self, value: float) -> None:
        await self.controller.async_set_fade_duration(value)


class EndBrightnessNumber(WakeupHelperEntity, NumberEntity):
    """Configure the brightness reached at alarm time."""

    _attr_translation_key = "end_brightness"
    _attr_icon = "mdi:brightness-7"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_mode = NumberMode.SLIDER
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "end_brightness")
        self.controller = controller

    @property
    def native_value(self) -> float:
        return self.controller.brightness

    async def async_set_native_value(self, value: float) -> None:
        await self.controller.async_set_brightness(value)
