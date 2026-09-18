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
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TimeSelector,
)

from .const import (
    CONF_ALARM_SCRIPT,
    CONF_ALARM_TIME,
    CONF_BRIGHTNESS,
    CONF_COVERS,
    CONF_DURATION,
    CONF_FADE_DURATION,
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


def _lights_selector() -> EntitySelector:
    return EntitySelector(EntitySelectorConfig(domain="light", multiple=True))


def _covers_selector() -> EntitySelector:
    return EntitySelector(EntitySelectorConfig(domain="cover", multiple=True))


def _script_selector() -> EntitySelector:
    return EntitySelector(EntitySelectorConfig(domain="script"))


def _nap_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME, default=values.get(CONF_NAME, "Bedroom nap")
            ): TextSelector(),
            vol.Required(
                CONF_LIGHTS, default=values.get(CONF_LIGHTS, [])
            ): _lights_selector(),
            vol.Required(
                CONF_COVERS, default=values.get(CONF_COVERS, [])
            ): _covers_selector(),
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
        vol.Required(
            CONF_LIGHTS, default=values.get(CONF_LIGHTS, [])
        ): _lights_selector(),
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
        if user_input is not None:
            if user_input[CONF_ROUTINE_TYPE] == ROUTINE_NAP:
                return await self.async_step_nap()
            return await self.async_step_wakeup()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROUTINE_TYPE): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"value": ROUTINE_NAP, "label": "Nap mode"},
                                {
                                    "value": ROUTINE_WAKEUP,
                                    "label": "Wake-up light",
                                },
                            ],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
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
            return self.async_create_entry(title="", data=user_input)

        if routine_type == ROUTINE_NAP:
            schema = vol.Schema(
                {
                    vol.Required(
                        CONF_LIGHTS, default=current.get(CONF_LIGHTS, [])
                    ): _lights_selector(),
                    vol.Required(
                        CONF_COVERS, default=current.get(CONF_COVERS, [])
                    ): _covers_selector(),
                }
            )
        else:
            fields: dict[Any, Any] = {
                vol.Required(
                    CONF_LIGHTS, default=current.get(CONF_LIGHTS, [])
                ): _lights_selector()
            }
            if script := current.get(CONF_ALARM_SCRIPT):
                fields[vol.Optional(CONF_ALARM_SCRIPT, default=script)] = (
                    _script_selector()
                )
            else:
                fields[vol.Optional(CONF_ALARM_SCRIPT)] = _script_selector()
            schema = vol.Schema(fields)

        return self.async_show_form(step_id="init", data_schema=schema)
