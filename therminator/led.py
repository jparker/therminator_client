#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from RPi import GPIO

class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self.state = 'off'

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = 'on'

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = 'off'


if __name__ == '__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--pin',
        type=int,
        required=True,
        help='GPIO pin connected to LED'
    )
    args = parser.parse_args()

    try:
        GPIO.setmode(GPIO.BCM)
        led = LED(pin=args.pin)
        print('Blinking LED 5 times')
        for _ in range(5):
            led.on()
            time.sleep(0.75)
            led.off()
            time.sleep(0.25)
    finally:
        GPIO.cleanup()
