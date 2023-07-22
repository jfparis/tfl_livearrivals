"""Client for the TFL live bus arrival APU"""
import logging
from datetime import datetime

import aiohttp

from .const import ENDPOINT, ENDPOINT_WITH_TOKEN

_LOGGER = logging.getLogger(__name__)


class TFLClientException(Exception):
    """Base exception class."""


class TFLClient:
    """Client for the TFL Live Bus Arrival"""

    def __init__(self, lines, bus_stop_id, api_token) -> None:
        self.lines = lines
        self.bus_stop_id = bus_stop_id
        self.api_token = api_token

        if self.api_token is None:
            self.endpoint = ENDPOINT
        else:
            self.endpoint = ENDPOINT_WITH_TOKEN

        self.url = self.endpoint.format(
            lines=self.lines, bus_stop_id=self.bus_stop_id, api_token=self.api_token
        )

    async def get_raw_departures(self):
        """Get the raw data from the api"""

        _LOGGER.debug("Request: %s" % self.url)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                json_response = await resp.json()
                return json_response

    def process_data(self, json_message):
        """Unpack the data return by the api in a usable format for hass"""

        status = {}
        status["departures"] = []
        station_name = None
        for each in json_message:
            departure = {}
            departure["line"] = each["lineId"]
            if station_name is None:
                station_name = each["stationName"]
            departure["destination"] = each["destinationName"]
            departure["expected_time"] = datetime.fromisoformat(
                each["timeToLive"].replace("Z", "+00:00")
            )

            status["departures"].append(departure)

        status["station"] = station_name
        status["departures"] = sorted(
            status["departures"],
            key=lambda d: d["expected_time"]
            # if isinstance(d["expected"], datetime)
            # else d["scheduled"],
        )

        return status

    async def async_get_data(self):
        """Data resfresh function called by the coordinator"""
        try:
            _LOGGER.debug("Requesting depearture data for %s", self.bus_stop_id)
            raw_data = await self.get_raw_departures()
        except aiohttp.ClientError as err:
            _LOGGER.exception("Exception whilst fetching data: ")
            raise TFLClientException("Error whilst Fetching Data") from err

        try:
            _LOGGER.debug("Procession station schedule for %s", self.bus_stop_id)
            data = self.process_data(raw_data)
        except Exception as err:
            _LOGGER.exception("Exception whilst processing data: ")
            raise TFLClientException("unexpected data from api") from err
        return data
