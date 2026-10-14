"""Config flow for Wakeup Helper."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TargetSelector,
    TargetSelectorConfig,
    TextSelector,
    TimeSelector,
)

from .const import (
    CONF_ALARM_SCRIPT,
    CONF_ALARM_TIME,
    CONF_BRIGHTNESS,
    CONF_COVER_AREAS,
    CONF_COVERS,
    CONF_DURATION,
    CONF_END_LIGHT_AREAS,
    CONF_END_LIGHTS,
    CONF_FADE_DURATION,
    CONF_LIGHT_AREAS,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_ROUTINE_TYPE,
    DEFAULT_ALARM_TIME,
    DEFAULT_BRIGHTNESS,
    DEFAULT_FADE_DURATION,
    DEFAULT_NAP_DURATION,
    DOMAIN,
    ROUTINE_NAP,
    ROUTINE_WAKEUP,
)


def _target_selector(domain: str) -> TargetSelector:
    return TargetSelector(
        TargetSelectorConfig(entity=EntitySelectorConfig(domain=domain))
    )


def _target_value(
    values: dict[str, Any],
    key: str,
    legacy_area_key: str | None = None,
) -> dict[str, list[str]]:
    """Return a native target while accepting pre-0.4.1 stored selections."""
    stored = values.get(key)
    target: dict[str, list[str]] = {}
    if isinstance(stored, dict):
        for target_key in ("entity_id", "device_id", "area_id"):
            selected = stored.get(target_key)
            if isinstance(selected, str):
                target[target_key] = [selected]
            elif selected:
                target[target_key] = list(selected)
    elif isinstance(stored, str):
        target["entity_id"] = [stored]
    elif stored:
        target["entity_id"] = list(stored)

    if (
        not isinstance(stored, dict)
        and legacy_area_key
        and (legacy_areas := values.get(legacy_area_key))
    ):
        area_ids = target.setdefault("area_id", [])
        for area_id in (
            [legacy_areas] if isinstance(legacy_areas, str) else legacy_areas
        ):
            if area_id not in area_ids:
                area_ids.append(area_id)
    return target


def _optional_target(
    key: str,
    values: dict[str, Any],
    legacy_area_key: str | None = None,
) -> Any:
    """Return an optional field with the stored selection shown as a suggestion."""
    target = _target_value(values, key, legacy_area_key)
    if target:
        return vol.Optional(key, description={"suggested_value": target})
    return vol.Optional(key)


def _script_selector() -> EntitySelector:
    return EntitySelector(EntitySelectorConfig(domain="script"))


def _nap_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME, default=values.get(CONF_NAME, "Bedroom nap")
            ): TextSelector(),
            _optional_target(
                CONF_LIGHTS, values, CONF_LIGHT_AREAS
            ): _target_selector("light"),
            _optional_target(
                CONF_COVERS, values, CONF_COVER_AREAS
            ): _target_selector("cover"),
            vol.Required(
                CONF_DURATION,
                default=values.get(CONF_DURATION, DEFAULT_NAP_DURATION),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=15,
                    max=90,
                    step=5,
                    unit_of_measurement="min",
                    mode=NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _wakeup_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_NAME, default=values.get(CONF_NAME, "Bedroom wake-up light")
        ): TextSelector(),
        _optional_target(
            CONF_LIGHTS, values, CONF_LIGHT_AREAS
        ): _target_selector("light"),
        vol.Required(
            CONF_ALARM_TIME,
            default=values.get(CONF_ALARM_TIME, DEFAULT_ALARM_TIME),
        ): TimeSelector(),
        vol.Required(
            CONF_FADE_DURATION,
            default=values.get(CONF_FADE_DURATION, DEFAULT_FADE_DURATION),
        ): NumberSelector(
            NumberSelectorConfig(
                min=0,
                max=120,
                step=5,
                unit_of_measurement="min",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_BRIGHTNESS,
            default=values.get(CONF_BRIGHTNESS, DEFAULT_BRIGHTNESS),
        ): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=100,
                step=5,
                unit_of_measurement="%",
                mode=NumberSelectorMode.SLIDER,
            )
        ),
    }
    script_default = values.get(CONF_ALARM_SCRIPT)
    if script_default:
        schema[vol.Optional(CONF_ALARM_SCRIPT, default=script_default)] = (
            _script_selector()
        )
    else:
        schema[vol.Optional(CONF_ALARM_SCRIPT)] = _script_selector()
    return vol.Schema(schema)


class WakeupHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wakeup Helper."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Choose which type of routine to create."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["nap", "wakeup"],
        )

    async def async_step_nap(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Configure a nap mode."""
        if user_input is not None:
            name = user_input.pop(CONF_NAME)
            return self.async_create_entry(
                title=name,
                data={CONF_ROUTINE_TYPE: ROUTINE_NAP, CONF_NAME: name, **user_input},
            )
        return self.async_show_form(
            step_id="nap", data_schema=_nap_schema(), last_step=True
        )

    async def async_step_wakeup(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Configure a wake-up light."""
        if user_input is not None:
            name = user_input.pop(CONF_NAME)
            return self.async_create_entry(
                title=name,
                data={
                    CONF_ROUTINE_TYPE: ROUTINE_WAKEUP,
                    CONF_NAME: name,
                    **user_input,
                },
            )
        return self.async_show_form(
            step_id="wakeup", data_schema=_wakeup_schema(), last_step=True
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> WakeupHelperOptionsFlow:
        """Return the options flow."""
        return WakeupHelperOptionsFlow(config_entry)


class WakeupHelperOptionsFlow(config_entries.OptionsFlow):
    """Edit the target entities for a routine."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Show editable routine targets."""
        routine_type = self._entry.data[CONF_ROUTINE_TYPE]
        current = {**self._entry.data, **self._entry.options}

        if user_input is not None:
            target_keys = [CONF_LIGHTS]
            if routine_type == ROUTINE_NAP:
                target_keys.extend([CONF_COVERS, CONF_END_LIGHTS])
            for key in target_keys:
                user_input.setdefault(key, {})
            return self.async_create_entry(title="", data=user_input)

        if routine_type == ROUTINE_NAP:
            schema = vol.Schema(
                {
                    _optional_target(
                        CONF_LIGHTS, current, CONF_LIGHT_AREAS
                    ): _target_selector("light"),
                    _optional_target(
                        CONF_COVERS, current, CONF_COVER_AREAS
                    ): _target_selector("cover"),
                    _optional_target(
                        CONF_END_LIGHTS,
                        current,
                        CONF_END_LIGHT_AREAS,
                    ): _target_selector("light"),
                }
            )
        else:
            fields: dict[Any, Any] = {
                _optional_target(
                    CONF_LIGHTS, current, CONF_LIGHT_AREAS
                ): _target_selector("light"),
            }
            if script := current.get(CONF_ALARM_SCRIPT):
                fields[vol.Optional(CONF_ALARM_SCRIPT, default=script)] = (
                    _script_selector()
                )
            else:
                fields[vol.Optional(CONF_ALARM_SCRIPT)] = _script_selector()
            schema = vol.Schema(fields)

        return self.async_show_form(step_id="init", data_schema=schema)
