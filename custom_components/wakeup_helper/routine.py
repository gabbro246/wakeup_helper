"""Runtime logic for Wakeup Helper."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ALARM_SCRIPT,
    CONF_ALARM_TIME,
    CONF_BRIGHTNESS,
    CONF_COVERS,
    CONF_DURATION,
    CONF_FADE_DURATION,
    CONF_LIGHTS,
    DEFAULT_ALARM_TIME,
    DEFAULT_BRIGHTNESS,
    DEFAULT_FADE_DURATION,
    DEFAULT_NAP_DURATION,
    DOMAIN,
    EVENT_WAKEUP,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[], None]


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Turn a stored value into a bounded integer."""
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


class RoutineController:
    """Base class for a virtual sleep routine device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize a routine."""
        self.hass = hass
        self.entry = entry
        self._listeners: set[Listener] = set()
        self._stored: dict[str, Any] = {}
        self._store = Store[dict[str, Any]](
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._cancel_schedule: Callable[[], None] | None = None

    @property
    def config(self) -> dict[str, Any]:
        """Return entry data with user options applied."""
        return {**self.entry.data, **self.entry.options}

    @property
    def lights(self) -> list[str]:
        """Return configured light entity IDs."""
        return list(self.config.get(CONF_LIGHTS, []))

    async def async_initialize(self) -> None:
        """Load persistent state."""
        self._stored = await self._store.async_load() or {}

    async def async_shutdown(self) -> None:
        """Stop callbacks and save persistent state."""
        self._cancel_timer()
        await self._store.async_save(self._storage_data())

    @callback
    def async_add_listener(self, listener: Listener) -> Callable[[], None]:
        """Subscribe an entity to controller changes."""
        self._listeners.add(listener)

        @callback
        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    @callback
    def _notify(self) -> None:
        """Notify subscribed entities."""
        for listener in tuple(self._listeners):
            listener()

    @callback
    def _save_later(self) -> None:
        """Persist state after closely grouped changes settle."""
        self._store.async_delay_save(self._storage_data, 1)

    def _storage_data(self) -> dict[str, Any]:
        """Return state that should survive restarts."""
        raise NotImplementedError

    @callback
    def _cancel_timer(self) -> None:
        """Cancel the current scheduled callback."""
        if self._cancel_schedule is not None:
            self._cancel_schedule()
            self._cancel_schedule = None

    async def _async_call_target(
        self,
        domain: str,
        service: str,
        entity_ids: list[str],
        data: dict[str, Any] | None = None,
    ) -> None:
        """Call a Home Assistant service for configured targets."""
        if not entity_ids:
            return
        try:
            await self.hass.services.async_call(
                domain,
                service,
                data or {},
                target={"entity_id": entity_ids},
                blocking=True,
            )
        except HomeAssistantError as err:
            _LOGGER.warning(
                "Could not call %s.%s for %s: %s",
                domain,
                service,
                self.entry.title,
                err,
            )


class NapController(RoutineController):
    """Control one nap mode device."""

    duration: int
    active: bool
    end_at: datetime | None

    @property
    def covers(self) -> list[str]:
        """Return configured cover entity IDs."""
        return list(self.config.get(CONF_COVERS, []))

    async def async_initialize(self) -> None:
        """Restore the nap state and timer."""
        await super().async_initialize()
        self.duration = _bounded_int(
            self._stored.get(CONF_DURATION, self.config.get(CONF_DURATION)),
            DEFAULT_NAP_DURATION,
            5,
            180,
        )
        self.active = bool(self._stored.get("active", False))
        self.end_at = None
        if stored_end := self._stored.get("end_at"):
            self.end_at = dt_util.parse_datetime(stored_end)

        if not self.active or self.end_at is None:
            self.active = False
            self.end_at = None
            return

        if self.end_at <= dt_util.now():
            await self.async_turn_off()
        else:
            self._schedule_end()

    def _storage_data(self) -> dict[str, Any]:
        return {
            CONF_DURATION: self.duration,
            "active": self.active,
            "end_at": self.end_at.isoformat() if self.end_at else None,
        }

    async def async_set_duration(self, value: float) -> None:
        """Set the duration for future naps."""
        self.duration = _bounded_int(value, DEFAULT_NAP_DURATION, 5, 180)
        self._save_later()
        self._notify()

    async def async_turn_on(self) -> None:
        """Start a nap."""
        if self.active:
            return
        self.active = True
        self.end_at = dt_util.now() + timedelta(minutes=self.duration)
        self._schedule_end()
        self._save_later()
        self._notify()
        await self._async_call_target("cover", "close_cover", self.covers)
        await self._async_call_target("light", "turn_off", self.lights)

    async def async_turn_off(self) -> None:
        """End a nap early or after its duration."""
        if not self.active:
            return
        self._cancel_timer()
        self.active = False
        self.end_at = None
        self._save_later()
        self._notify()
        await self._async_call_target("cover", "open_cover", self.covers)

    @callback
    def _schedule_end(self) -> None:
        """Schedule the end of the active nap."""
        self._cancel_timer()
        if self.end_at is not None:
            self._cancel_schedule = async_track_point_in_time(
                self.hass, self._handle_end, self.end_at
            )

    @callback
    def _handle_end(self, _now: datetime) -> None:
        self._cancel_schedule = None
        self.hass.async_create_task(self.async_turn_off())


class WakeupController(RoutineController):
    """Control one daily wake-up light device."""

    enabled: bool
    alarm_time: time
    fade_duration: int
    brightness: int
    status: str
    next_alarm: datetime | None

    async def async_initialize(self) -> None:
        """Restore settings and schedule the next alarm."""
        await super().async_initialize()
        raw_time = str(
            self._stored.get(CONF_ALARM_TIME, self.config.get(CONF_ALARM_TIME))
            or DEFAULT_ALARM_TIME
        )
        try:
            self.alarm_time = time.fromisoformat(raw_time)
        except ValueError:
            self.alarm_time = time.fromisoformat(DEFAULT_ALARM_TIME)
        self.fade_duration = _bounded_int(
            self._stored.get(CONF_FADE_DURATION, self.config.get(CONF_FADE_DURATION)),
            DEFAULT_FADE_DURATION,
            0,
            120,
        )
        self.brightness = _bounded_int(
            self._stored.get(CONF_BRIGHTNESS, self.config.get(CONF_BRIGHTNESS)),
            DEFAULT_BRIGHTNESS,
            1,
            100,
        )
        self.enabled = bool(self._stored.get("enabled", False))
        self.status = "off"
        self.next_alarm = None
        self._schedule_next()

    def _storage_data(self) -> dict[str, Any]:
        return {
            CONF_ALARM_TIME: self.alarm_time.isoformat(),
            CONF_FADE_DURATION: self.fade_duration,
            CONF_BRIGHTNESS: self.brightness,
            "enabled": self.enabled,
        }

    async def async_set_enabled(self, enabled: bool) -> None:
        """Enable or disable the daily alarm."""
        if self.enabled == enabled:
            return
        self.enabled = enabled
        self._save_later()
        self._schedule_next()

    async def async_set_alarm_time(self, value: time) -> None:
        """Set the daily alarm time."""
        self.alarm_time = value.replace(tzinfo=None)
        self._save_later()
        self._schedule_next()

    async def async_set_fade_duration(self, value: float) -> None:
        """Set the sunrise duration."""
        self.fade_duration = _bounded_int(value, DEFAULT_FADE_DURATION, 0, 120)
        self._save_later()
        self._schedule_next()

    async def async_set_brightness(self, value: float) -> None:
        """Set the brightness reached at alarm time."""
        self.brightness = _bounded_int(value, DEFAULT_BRIGHTNESS, 1, 100)
        self._save_later()
        self._notify()

    def _find_next_alarm(self, now: datetime) -> datetime:
        candidate = datetime.combine(now.date(), self.alarm_time, now.tzinfo)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    @callback
    def _schedule_next(self) -> None:
        """Schedule the next fade step or alarm."""
        self._cancel_timer()
        if not self.enabled:
            self.status = "off"
            self.next_alarm = None
            self._notify()
            return

        now = dt_util.now()
        self.next_alarm = self._find_next_alarm(now)
        fade_start = self.next_alarm - timedelta(minutes=self.fade_duration)
        if now < fade_start:
            self.status = "waiting"
            run_at = fade_start
        else:
            self.status = "waking"
            run_at = now
        self._notify()
        self._cancel_schedule = async_track_point_in_time(
            self.hass, self._handle_tick, run_at
        )

    @callback
    def _handle_tick(self, _now: datetime) -> None:
        self._cancel_schedule = None
        self.hass.async_create_task(self._async_tick())

    async def _async_tick(self) -> None:
        """Advance the simulated sunrise."""
        if not self.enabled or self.next_alarm is None:
            return

        now = dt_util.now()
        if now >= self.next_alarm - timedelta(seconds=1):
            await self._async_alarm()
            return

        fade_start = self.next_alarm - timedelta(minutes=self.fade_duration)
        fade_seconds = max(1.0, (self.next_alarm - fade_start).total_seconds())
        progress = max(0.0, min(1.0, (now - fade_start).total_seconds() / fade_seconds))
        brightness = max(1, round(self.brightness * progress))
        transition = max(1, min(60, round((self.next_alarm - now).total_seconds())))
        await self._async_call_target(
            "light",
            "turn_on",
            self.lights,
            {"brightness_pct": brightness, "transition": transition},
        )
        self.status = "waking"
        self._notify()
        run_at = min(now + timedelta(minutes=1), self.next_alarm)
        self._cancel_schedule = async_track_point_in_time(
            self.hass, self._handle_tick, run_at
        )

    async def _async_alarm(self) -> None:
        """Finish the sunrise and run alarm actions."""
        await self._async_call_target(
            "light",
            "turn_on",
            self.lights,
            {"brightness_pct": self.brightness, "transition": 30},
        )
        self.status = "alarm"
        self._notify()
        self.hass.bus.async_fire(
            EVENT_WAKEUP,
            {
                "config_entry_id": self.entry.entry_id,
                "name": self.entry.title,
                "lights": self.lights,
            },
        )
        if script := self.config.get(CONF_ALARM_SCRIPT):
            await self._async_call_target("script", "turn_on", [script])

        self._cancel_schedule = async_track_point_in_time(
            self.hass,
            self._handle_alarm_finished,
            dt_util.now() + timedelta(minutes=1),
        )

    @callback
    def _handle_alarm_finished(self, _now: datetime) -> None:
        self._cancel_schedule = None
        self._schedule_next()
