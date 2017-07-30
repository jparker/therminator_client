#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from tkinter import *
from .. import utils
from ..sensors import *


class App:
    FIELDS = ['Int Temp', 'Ext Temp', 'Humidity']

    def __init__(self, master, config, logger):
        self.config = config
        self.logger = logger
        self.frame = Frame(master)
        self.frame.pack()
        for i, text in enumerate(self.FIELDS):
            label = Label(self.frame, text=text)
            label.grid(row=0, column=i)
            label.config(font=('Ubuntu', 18), width=10)

        self.__int_temp(row=1, column=0)
        self.__ext_temp(row=1, column=1)
        self.__humidity(row=1, column=2)

        self.__refresh(row=2, column=0)
        self.__close(row=2, column=2)

    def refresh(self):
        try:
            utils.lock(logger=self.logger)

            sensor = self.config['internal']['sensor']
            kwargs = self.config['internal']['options']
            int_temp = utils.lookup_sensor(sensor).read(**kwargs)
            self.int_temp.set('{:.1f}°F'.format(int_temp * 9/5 + 32))

            sensor = self.config['temperature']['sensor']
            kwargs = self.config['temperature']['options']
            ext_temp, humidity = utils.lookup_sensor(sensor).read(**kwargs)
            self.ext_temp.set('{:.1f}°F'.format(ext_temp * 9/5 + 32))
            self.humidity.set('{:.1f}%'.format(humidity))
        finally:
            utils.unlock(self.logger)

    def close(self):
        exit(0)

    def __int_temp(self, **kwargs):
        self.int_temp = StringVar()
        label = Label(self.frame, textvariable=self.int_temp)
        label.grid(**kwargs)
        label.config(font=('Ubuntu', 32))

    def __ext_temp(self, **kwargs):
        self.ext_temp = StringVar()
        label = Label(self.frame, textvariable=self.ext_temp)
        label.grid(**kwargs)
        label.config(font=('Ubuntu', 32))

    def __humidity(self, **kwargs):
        self.humidity = StringVar()
        label = Label(self.frame, textvariable=self.humidity)
        label.grid(**kwargs)
        label.config(font=('Ubuntu', 32))

    def __refresh(self, **kwargs):
        button = Button(self.frame, text='Refresh', command=self.refresh)
        button.grid(**kwargs)
        button.config(font=('Ubuntu', 24))

    def __close(self, **kwargs):
        button = Button(self.frame, text='Exit', command=self.close)
        button.grid(**kwargs)
        button.config(font=('Ubuntu', 24))


def main():
    args = utils.parse_args()
    config = utils.load_config(args.config)
    logger = utils.setup_logger(config['logging'], debug=args.debug)

    root = Tk()
    root.wm_title('Therminator')
    app = App(root, config=config, logger=logger)
    root.mainloop()


if __name__ == '__main__':
    main()
