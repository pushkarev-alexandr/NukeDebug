import tkinter as tk
import os
import nuke

tcl = tk.Tcl()

def value(knob_path: str) -> str:
    spl = knob_path.split(".")
    return nuke.toNode(spl[0]).knob(spl[1]).value()

tcl.createcommand('getenv', os.getenv)
tcl.createcommand('value', value)
