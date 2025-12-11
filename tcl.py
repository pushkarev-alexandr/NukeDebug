import tkinter as tk
import os
import nuke

_tcl = tk.Tcl()

def value(knob_path: str) -> str:
    spl = knob_path.split(".")
    return nuke.toNode(spl[0]).knob(spl[1]).value()

_tcl.createcommand('getenv', os.getenv)
_tcl.createcommand('value', value)
_tcl.createcommand('firstof', lambda *args: next((arg for arg in args if arg), ''))

def tcl(s: str, *args) -> str:
    """
    Run a tcl command. The arguments must be strings and passed to the command.
    If no arguments are given and the command has whitespace in it then it is instead interpreted as a tcl program (this is deprecated).
    Args:
        s (str): TCL code.
        *args: The arguments to pass in to the TCL code.
    Returns:
        str: Result of TCL command as string.
    """
    if args:
        return _tcl.call(s, *args)
    else:
        return _tcl.eval(s)
