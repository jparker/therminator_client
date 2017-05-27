__version__ = '0.0.1'

from .sensors import pi, dht22, ds18b20, photoresistor

SENSORS = {
    'pi': sensors.pi,
    'dht22': sensors.dht22,
    'ds18b20': sensors.ds18b20,
    'photoresistor': sensors.photoresistor,
}
