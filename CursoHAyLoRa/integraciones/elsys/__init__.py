import voluptuous as vol
import json
import base64

from homeassistant.components import mqtt
from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.helpers.discovery import async_load_platform


from .const import (
    DOMAIN,
    RECEIVE_DATA_TOPIC,
    DATA_EVENT,
)
import logging

_LOGGER = logging.getLogger(__name__)

class ChirpBridge:

    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
        _LOGGER.debug('__init__')
        _LOGGER.debug(f"config en __init__.py: {self.config}")

    async def async_start(self):

        async def on_data_received(msg):
            try:
                data = json.loads(msg.payload)            

                event_data = dict(
                    {"devEUI": data["devEUI"], "data": data['data']}
                )
                _LOGGER.debug(event_data)
                self.hass.bus.fire(DATA_EVENT, event_data)
            except Exception as err:
                print(err)

        await mqtt.async_subscribe(self.hass, RECEIVE_DATA_TOPIC, on_data_received, 0, None)


async def async_setup(hass, config: dict):
    """Set up the lorawan component."""

    _LOGGER.debug("ELSYS ERSCO2 LoRaWAN setup")

    bridge = ChirpBridge(hass=hass, config=config[DOMAIN])

    '''
    hass.data[const.DOMAIN] = {
        "config": config[const.DOMAIN], 
        "bridge": bridge, 
        "devices": {}
    }
    '''

    hass.async_create_task(
        async_load_platform(hass, SENSOR, DOMAIN, None, config)
    )

    await bridge.async_start()

    return True
