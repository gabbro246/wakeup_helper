"""Constants for Wakeup Helper."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "wakeup_helper"

ROUTINE_NAP: Final = "nap"
ROUTINE_WAKEUP: Final = "wakeup"

CONF_ROUTINE_TYPE: Final = "routine_type"
CONF_NAME: Final = "name"
CONF_LIGHTS: Final = "lights"
CONF_COVERS: Final = "covers"
CONF_ALARM_SCRIPT: Final = "alarm_script"
CONF_DURATION: Final = "duration"
CONF_ALARM_TIME: Final = "alarm_time"
CONF_FADE_DURATION: Final = "fade_duration"
CONF_BRIGHTNESS: Final = "brightness"

DEFAULT_NAP_DURATION: Final = 30
DEFAULT_ALARM_TIME: Final = "07:00:00"
DEFAULT_FADE_DURATION: Final = 25
DEFAULT_BRIGHTNESS: Final = 100

EVENT_WAKEUP: Final = "wakeup_helper_wakeup"

CARD_URL: Final = "/wakeup_helper/wakeup-helper-card.js?v=0.3.0"
STATIC_URL: Final = "/wakeup_helper"

STORAGE_VERSION: Final = 1

PLATFORMS: Final[list[Platform]] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.TIME,
]
