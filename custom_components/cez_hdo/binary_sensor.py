import logging
from datetime import datetime, time
import holidays

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers.event import async_track_time_change

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Nízký Tarif"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

CZ_HOLIDAYS = holidays.CZ()

WEEKDAY_TIMES = [
    (time(3, 20), time(7, 10)),
    (time(14, 45), time(17, 10)),
    (time(22, 10), time(23, 55)),
]

WEEKEND_TIMES = [
    (time(3, 20), time(7, 10)),
    (time(15, 10), time(17, 20)),
    (time(21, 55), time(23, 55)),
]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    async_add_entities([NizkyTarifBinarySensor(name)], True)

class NizkyTarifBinarySensor(BinarySensorEntity):
    def __init__(self, name):
        self._name = name
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_added_to_hass(self):
        async_track_time_change(self.hass, self.update, second=0)
        await self.async_update()

    async def update(self, now=None):
        today = datetime.now().date()
        current_time = datetime.now().time()
        is_holiday = today in CZ_HOLIDAYS
        is_weekend = datetime.now().weekday() >= 5

        if is_holiday or is_weekend:
            active_times = WEEKEND_TIMES
        else:
            active_times = WEEKDAY_TIMES

        self._state = any(start <= current_time <= end for start, end in active_times)
        self.async_write_ha_state()
