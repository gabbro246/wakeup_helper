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
CONF_LIGHT_AREAS: Final = "light_areas"
CONF_COVERS: Final = "covers"
CONF_COVER_AREAS: Final = "cover_areas"
CONF_END_LIGHTS: Final = "end_lights"
CONF_END_LIGHT_AREAS: Final = "end_light_areas"
CONF_ALARM_SCRIPT: Final = "alarm_script"
CONF_DURATION: Final = "duration"
CONF_ALARM_TIME: Final = "alarm_time"
CONF_FADE_DURATION: Final = "fade_duration"
CONF_BRIGHTNESS: Final = "brightness"
CONF_TURN_ON_LIGHTS_AT_END: Final = "turn_on_lights_at_end"
CONF_OPEN_COVERS_AT_END: Final = "open_covers_at_end"
CONF_OPEN_COVERS_AT_ALARM: Final = "open_covers_at_alarm"
CONF_TURN_OFF_LIGHTS_AT_START: Final = "turn_off_lights_at_start"
CONF_CLOSE_COVERS_AT_START: Final = "close_covers_at_start"

DEFAULT_NAP_DURATION: Final = 30
DEFAULT_ALARM_TIME: Final = "07:00:00"
DEFAULT_FADE_DURATION: Final = 25
DEFAULT_BRIGHTNESS: Final = 100
DEFAULT_TURN_ON_LIGHTS_AT_END: Final = False
DEFAULT_OPEN_COVERS_AT_END: Final = True
DEFAULT_OPEN_COVERS_AT_ALARM: Final = True
DEFAULT_TURN_OFF_LIGHTS_AT_START: Final = True
DEFAULT_CLOSE_COVERS_AT_START: Final = True

EVENT_WAKEUP: Final = "wakeup_helper_wakeup"

CARD_URL: Final = "/wakeup_helper/wakeup-helper-card.js?v=0.4.3"
STATIC_URL: Final = "/wakeup_helper"

STORAGE_VERSION: Final = 1

PLATFORMS: Final[list[Platform]] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.TIME,
]
