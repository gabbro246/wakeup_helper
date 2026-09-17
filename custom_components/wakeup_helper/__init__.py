"""The Wakeup Helper integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, PLATFORMS, ROUTINE_NAP, STORAGE_VERSION
from .routine import NapController, RoutineController, WakeupController

type WakeupHelperConfigEntry = ConfigEntry[RoutineController]


async def async_setup_entry(
    hass: HomeAssistant, entry: WakeupHelperConfigEntry
) -> bool:
    """Set up Wakeup Helper from a config entry."""
    if entry.data["routine_type"] == ROUTINE_NAP:
        controller: RoutineController = NapController(hass, entry)
    else:
        controller = WakeupController(hass, entry)

    await controller.async_initialize()
    entry.runtime_data = controller
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: WakeupHelperConfigEntry
) -> bool:
    """Unload a Wakeup Helper config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    await entry.runtime_data.async_shutdown()
    return True


async def async_remove_entry(
    hass: HomeAssistant, entry: WakeupHelperConfigEntry
) -> None:
    """Remove persistent state when a routine is deleted."""
    store = Store[dict](hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    await store.async_remove()


async def _async_update_listener(
    hass: HomeAssistant, entry: WakeupHelperConfigEntry
) -> None:
    """Reload an entry after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
