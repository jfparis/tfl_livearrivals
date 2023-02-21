"""Config flow for TFL Live Arrival integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_BUS_STOP_ID, CONF_LINES, CONF_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_TOKEN): str,
        vol.Required(CONF_LINES): str,
        vol.Required(CONF_BUS_STOP_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": f'TFL departure {data["bus_stop_id"]} lines {data["lines"]}'}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for National Rail UK."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # user_input[CONF_STATION] = user_input[CONF_STATION].strip()
        # user_input[CONF_DESTINATIONS] = (
        #    user_input[CONF_DESTINATIONS].strip().replace(" ", "").upper()
        # )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except InvalidToken:
            errors["base"] = "invalid_token"
        except InvalidInput:
            errors["base"] = "invalid_station_input"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidToken(HomeAssistantError):
    """Error to indicate the Token is invalid."""


class InvalidInput(HomeAssistantError):
    """Error to indicate there is invalid user input."""
