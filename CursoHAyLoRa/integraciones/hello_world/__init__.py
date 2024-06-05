DOMAIN = "hello_world"

#Selecciona uno de los dos métodos y comenta el que no uses
def setup(hass, config):
    hass.states.async_set("hello_state.world", "all")
    return True 

#async def async_setup(hass, config):
#    hass.states.async_set("hello_state.world", "all")
#    return True
