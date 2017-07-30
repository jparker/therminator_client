#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import Tk
from . import app as _app

root = Tk()
root.wm_title('Therminator')
app = _app.App(root)
root.mainloop()
