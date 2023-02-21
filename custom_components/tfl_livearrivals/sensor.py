"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import time

import async_timeout

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .client import TFLClient
from .const import CONF_BUS_STOP_ID, CONF_LINES, CONF_TOKEN, DOMAIN, REFRESH

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""

    api_token = entry.data.get(CONF_TOKEN)
    lines = entry.data.get(CONF_LINES)
    bus_stop_id = entry.data.get(CONF_BUS_STOP_ID)

    _LOGGER.debug(f"Setting up sensor for bus {lines} at stop {bus_stop_id}")

    coordinator = TFLScheduleCoordinator(hass, lines, bus_stop_id, api_token)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([TFLSchedule(coordinator)])


class TFLScheduleCoordinator(DataUpdateCoordinator):
    description: str = None
    friendly_name: str = None
    sensor_name: str = None

    def __init__(self, hass, lines, bus_stop_id, api_token):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=REFRESH),
        )
        self.lines = lines
        self.bus_stop_id = bus_stop_id
        self.my_api = TFLClient(lines, bus_stop_id, api_token)

        self.last_data_refresh = None

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # chek whether we should refresh the data of not
        if (
            self.last_data_refresh is None
            or (
                self.last_data_refresh is not None
                and (time.time() - self.last_data_refresh) > 5 * 60
            )
            or (
                self.data["next_bus_expected"] is not None
                and datetime.now(self.data["next_bus_expected"].tzinfo)
                >= self.data["next_bus_expected"] - timedelta(minutes=1)
            )
        ):
            # try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(30):
                data = await self.my_api.async_get_data()
                self.last_data_refresh = time.time()
            # except aiohttp.ClientError as err:
            #    raise UpdateFailed(f"Error communicating with API: {err}") from err

            if self.sensor_name is None:
                self.sensor_name = (
                    f"bus_schedule_{self.bus_stop_id}_{'_'.join(self.lines.split(','))}"
                )

            if self.description is None:
                self.description = (
                    f"Bus schedule at {data['station']} for lines {self.lines}"
                )

            if self.friendly_name is None:
                self.friendly_name = (
                    f"Bus schedule at {data['station']} for lines {self.lines}"
                )

            data["name"] = self.sensor_name
            data["description"] = self.description
            data["friendly_name"] = self.friendly_name

            if len(data["departures"]) > 0:
                data["next_bus_expected"] = data["departures"][0]["expected_time"]
                data["destination"] = data["departures"][0]["destination"]
                data["line"] = data["departures"][0]["line"]
            else:
                data["next_bus_expected"] = None
                data["destination"] = None
                data["line"] = None

        else:
            data = self.data

        return data


class TFLSchedule(CoordinatorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    attribution = "This uses National Rail Darwin Data Feeds"

    def __init__(self, coordinator):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.entity_id = f"sensor.{coordinator.data['name'].lower()}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.data

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self.coordinator.data["name"]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["next_bus_expected"]
