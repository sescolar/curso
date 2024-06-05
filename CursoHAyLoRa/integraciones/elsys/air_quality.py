import logging
import base64
from typing import Any, Dict
import voluptuous as vol

from homeassistant.components.sensor import DOMAIN as CO2
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_ID,
    CONF_NAME,
)

from .const import (
    DOMAIN,
    DATA_EVENT
)
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensors from configuration.yaml."""
    _LOGGER.debug("ERSCO2: setup_platform 1")
    _LOGGER.debug(config)
    #if discovery_info == {}:
    #    return

    id = config[CONF_ID] #discovery_info[0][CONF_ID]
    name = config[CONF_NAME]
    _LOGGER.debug(id)
    _LOGGER.debug(name)

    air_quality = AirQuality(hass, name, id)
    add_entities([air_quality])
    _LOGGER.debug("ERSCO2: setup_platform 2")

class AirQuality(SensorEntity):
    def __init__(self, hass, name, id):
        self.hass = hass
        self._id = id
        self._name = name
        self._attributes = {}
        self._state = 0
        self._state_class = "measurement"
        self.schedule_update_ha_state()

        try:
            hass.bus.listen(DATA_EVENT, self._handle_event)
        except Exception as e:
            _LOGGER.debug(e)

    def _update_state(self, data):
        #data = base64.b64decode(data)
        _LOGGER.debug("Data={}".format(data))
        self._state = data[11] * 256 + data[12]
        self._attributes['Temperature'] = (data[1] * 256 + (data[2]))/10
        self._attributes['Humidity'] = data[4]
        self._attributes['Light'] = data[6] *256 + data[7]
        self._attributes['Motion'] = data[9]
        self._attributes['CO2'] = data[11] * 256 + data[12]
        self._attributes['Vdd'] = data[14] * 256 + data[15]
        self.schedule_update_ha_state()

    def _handle_event(self, event):
        if "devEUI" not in event.data or "data" not in event.data:
            return

        if self._id == event.data["devEUI"]:
            event_data = event.data["data"]
            _LOGGER.debug("ERSCO2-1 event_data={}".format(event_data))
            decoded = base64.b64decode(event_data)
            _LOGGER.debug("ERSCO2-2 event_data={}".format(decoded))
            self._update_state(decoded)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return self._attributes

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return str(self._id)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
       return self._state

    @property
    def state_class(self):
       return self._state_class
