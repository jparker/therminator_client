# Therminator Client

The therminator project is a client/server application I'm developing to log
data about my home. See
[therminator\_server](https://github.com/jparker/therminator_server) for the
server component.

This repository houses the client component. The therminator module interfaces
with a therminator device attached to a
[Raspberry Pi](https://www.raspberrypi.org) to measure temperature, humidity,
and ambient light levels. The measurements are logged and sent to the
therminator server API.

The therminator device includes a temperature sensor and a photoresistor. If
using a DHT22 temperature sensor, the temperature and humidity will be
measured. If a DS18B20 is used, only the temperature will be measured.

## Installation

I'm still fleshing out this process.

The client depends on RPi.GPIO, Adafruit\_DHT, PyYAML, and requests.

## Usage

```bash
$ python3 -m therminator -h
usage: __main__.py [-h] -c FILE [-d] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        Path to YAML config file
  -d, --debug           Enable debugging output
  -v, --version         Display version information and exit
$ python3 -m therminator --config path/to/config.yml
```

## Configuration

The details of how the device is wired up to the Raspberry Pi should be placed
in a YAML file and passed to the client with the `--config` option. See the
file sample\_config.yml for an example configuration.

### DHT22

In order to read from a DHT22 sensor, the
[Adafruit\_DHT22](https://github.com/adafruit/Adafruit_Python_DHT) needs to be
installed on the Raspberry Pi, and the config file should provide the GPIO pin
to which the DHT22's data pin as connected.

Adafruit has a
[great tutorial](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging)
on working with DHTxx sensors. The expected circuit design and code for
interfacing with it is derived from this tutorial.

### DS18B20

In order to read from a DS18B20 sensor, 1-wire support needs to into the
kernel. This can be enabled by running `raspi-config` or by adding the
following line to /boot/config.txt:

```
dtoverlay=w1-gpio
```

In addition, the `w1_therm` kernel module needs to be loaded. (I am new to
Raspberry Pis. In practice, this module just seems to be available once 1-wire
is enabled and a DS18B20 is attached. I may be forgetting something.)

Adafruit also has a
[great tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20?view=all)
for working with the DS18B20 from a Raspberry Pi.

### Photoresistor

The photoresistor is used by measuring the amount of time it takes to charge a
capacitor through the photoresistor. The config file should provide the
capacticance of the capacitor (in μF), the resistance of the regular resistor
through which current is flowing (in Ω), and the GPIO pins used to charge and
discharge the capacitor.

Multiple measurements of the resistance of the photoresistor will be taken, and
the average of those readings will be returned. By default, 20 readings and
taken. In extremely dark conditions, this may take a very long time. It may be
necessary to use a smaller capacitor or take fewer readings if you are unable
to get a reading within a reasonable amount of time. (By default, the client
will timeout if it hasn't completed 20 readings within 5 minutes.)

The expected design of this portion of the circuit and the code for working
with it is derived from the "Analog Inputs" section of "Chapter 9: Interfacing
Hardware" of _Programming the Raspberry Pi (2nd Ed.)_.
