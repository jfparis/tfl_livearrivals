# tfl_livearrivals

Provides live bus timings from Transport for London for London buses.

## Installation
You can install this through [HACS](https://github.com/custom-components/hacs).

Otherwise, you can install it manually.

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called tfl_livearrivals.
4. Download all the files from the custom_components/tfl_livearrivals/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Inside the new directory, run 'pip install -r requirements.txt'
7. Restart Home Assistant

## Configuration

You will configure one integration per bus stop.

You may specify one or more buses to monitor per stop.

### Get your bus stop ID

Go to the following URL:

```https://api.tfl.gov.uk/Line/[buses you want to monitor]/Arrivals```

```[buses you want to monitor]``` is a comma-separated list of buses you are interseted in. For example, the following URL will pull all arrivals for the 2, 68, and 196:

```https://api.tfl.gov.uk/Line/2,68,196/Arrivals```

Next, search the API response for the name of your specific station (retrieve it from Google Maps or similar). The stop ID you want is the ```naptanId``` associated with the stop. Most stops will have two different ```naptanId``` values, one for each direction of travel. Use the ```destinationName``` field to differentiate between the two.

### Add the integration

You can add the integration in the usual way using its config-flow, using your comma-separated list of values and the ```naptanId``` as required. 

## Examples

The following example will create a simple table of bus departures, suitable to add to a Markdown card.

```yaml
### West Norwood
{% set departures = state_attr('sensor.bus_schedule_490001331w_2_68_196', 'departures') %}
| Bus | Destination | min |
| --- | ----------- | --- |{% for departure in departures -%}{% set minutes = ((as_timestamp(departure.expected_time) - as_timestamp(now())) / 60) | round(0) %}
| **{{ departure.line }}** | {{ departure.destination }} | {% if minutes == 0 %}due {% else %}{{ minutes }} {% endif -%}|
{%- endfor %}
```
