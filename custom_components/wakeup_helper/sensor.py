"""Sensor entities for Wakeup Helper."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
    """Set up status and event time sensors."""
    controller = entry.runtime_data
    if entry.data["routine_type"] == ROUTINE_NAP:
        async_add_entities(
            [NapStatusSensor(entry, controller), NapEndsSensor(entry, controller)]
        )
    else:
        async_add_entities(
            [
                WakeupStatusSensor(entry, controller),
                NextAlarmSensor(entry, controller),
            ]
        )


class NapStatusSensor(WakeupHelperEntity, SensorEntity):
    """Report whether a nap is active."""

    _attr_translation_key = "nap_status"
    _attr_icon = "mdi:sleep"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options: ClassVar[list[str]] = ["off", "napping"]

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "status")
        self.controller = controller

    @property
    def native_value(self) -> str:
        return "napping" if self.controller.active else "off"


class NapEndsSensor(WakeupHelperEntity, SensorEntity):
    """Report when the active nap ends."""

    _attr_translation_key = "nap_ends"
    _attr_icon = "mdi:timer-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: NapController
    ) -> None:
        super().__init__(entry, controller, "ends")
        self.controller = controller

    @property
    def native_value(self) -> datetime | None:
        return self.controller.end_at


class WakeupStatusSensor(WakeupHelperEntity, SensorEntity):
    """Report the current wake-up light stage."""

    _attr_translation_key = "wakeup_status"
    _attr_icon = "mdi:weather-sunset-up"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options: ClassVar[list[str]] = ["off", "waiting", "waking", "alarm"]

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "status")
        self.controller = controller

    @property
    def native_value(self) -> str:
        return self.controller.status


class NextAlarmSensor(WakeupHelperEntity, SensorEntity):
    """Report the next alarm date and time."""

    _attr_translation_key = "next_alarm"
    _attr_icon = "mdi:alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self, entry: WakeupHelperConfigEntry, controller: WakeupController
    ) -> None:
        super().__init__(entry, controller, "next_alarm")
        self.controller = controller

    @property
    def native_value(self) -> datetime | None:
        return self.controller.next_alarm
