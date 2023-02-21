"""Constants for the TFL Live Arrivals integration."""

DOMAIN = "tfl_livearrivals"
DOMAIN_DATA = f"{DOMAIN}_data"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

ENDPOINT = "https://api.tfl.gov.uk/Line/{lines}/Arrivals/{bus_stop_id}?direction=all"
ENDPOINT_WITH_TOKEN = "https://api.tfl.gov.uk/Line/{lines}/Arrivals/{bus_stop_id}?direction=all&app_key={api_token}"


CONF_TOKEN = "api_token"
CONF_LINES = "lines"
CONF_BUS_STOP_ID = "bus_stop_id"

REFRESH = 2
