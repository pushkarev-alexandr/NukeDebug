from variables import *
from typing import overload, Any, Union, List, Dict, Callable, Literal, Type, Optional
import os, re, sys, tempfile
from ocio_aces12_colorspaces import colorspaces_list

from PySide2.QtWidgets import QApplication, QLineEdit, QCheckBox, QComboBox, QPlainTextEdit, QLabel, QWidget, QWidgetItem, QPushButton
from PySide2.QtGui import QIntValidator

os.environ["NUKE_TEMP_DIR"] = os.path.join(tempfile.gettempdir(), "nuke").replace("\\", "/")

app = QApplication(sys.argv)

_pluginPath: List[str] = [os.path.expanduser("~/.nuke").replace("\\", "/")]

class MenuItem:
    def __init__(self):
        self._name: str = ""
        self._icon: str = ""
        self._script: str = ""
        self._enabled: bool = True
        self._shortcut: str = ""

    def icon(self) -> str:
        """Returns the name of the icon on this menu item as path of the icon."""
        return self._icon

    def invoke(self):
        """Perform the action associated with this menu item."""
        pass

    def name(self) -> str:
        """Returns the name of the menu item."""
        return self._name

    def script(self) -> str:
        """Returns the script that gets executed for this menu item."""
        return self._script

    def setEnabled(self, enabled: bool) -> None:
        """
        Enable or disable the item.
        Args:
            enabled (bool): True to enable the object; False to disable it.
        """
        self._enabled = enabled

    def setIcon(self, icon: str) -> None:
        """
        Set the icon on this menu item
        Args:
            icon (str): the new icon as a path
        """
        self._icon = icon

    def setScript(self, script: str) -> None:
        """
        Set the script to be executed for this menu item.
        Note: To call a python script file, you can use the execfile() function. i.e: menu.setScript("execfile('script.py')")
        """
        self._script = script

    def setShortcut(self, keySequence: str) -> None:
        """
        Set the keyboard shortcut on this menu item.
        Args:
            keySequence (str): the new shortcut in PortableText format, e.g. "Ctrl+Shift+P"
        """
        self._shortcut = keySequence

    def shortcut(self) -> str:
        """
        Returns the keyboard shortcut on this menu item. The format of this is the PortableText format. It will return a string such as "Ctrl+Shift+P".
        Note that on Mac OS X the Command key is equivalent to Ctrl.
        """
        return self._shortcut

class Menu(MenuItem):
    def __init__(self):
        super().__init__()
    
    def addCommand(self, name: str, command: Union[str, Callable] = None, shortcut: str = "", icon: str = "", tooltip: str = "", index: int = -1, readonly: bool = False, shortcutContext: int = None) -> MenuItem:
        """
        Add a new command to this menu/toolbar. Note that when invoked, the command is automatically enclosed in an undo group, so that undo/redo functionality works. Optional arguments can be specified by name. Note that if the command argument is not specified, then the command will be auto-created as a "nuke.createNode()" using the name argument as the node to create.
        Example: menubar = nuke.menu('Nuke') fileMenu = menubar.findItem('File') fileMenu.addCommand('NewCommand', 'print 10', shortcut='t')
        Args:
            name (str): The name for the menu/toolbar item. The name may contain submenu names delimited by '/' or '', and submenus are created as needed.
            command (Union[str, Callable]): Optional. The command to add to the menu/toolbar. This can be a string to evaluate or a Python Callable (function, method, etc) to run.
            shortcut (str): Optional. The keyboard shortcut for the command, such as 'R', 'F5' or 'Ctrl-H'. Note that this overrides pre-existing other uses for the shortcut.
            icon (str): Optional. An icon for the command. This should be a path to an icon in the nuke.pluginPath() directory. If the icon is not specified, Nuke will automatically try to find an icon with the name argument and .png appended to it.
            tooltip (str): Optional. The tooltip text, displayed on mouseover for toolbar buttons.
            index (int): Optional. The position to insert the new item in, in the menu/toolbar. This defaults to last in the menu/toolbar.
            readonly (bool): Optional. True/False for whether the item should be available when the menu is invoked in a read-only context.
        Returns:
            MenuItem: The menu/toolbar item that was added to hold the command.
        """
        pass

    def addMenu(self, name: str, icon: str = "", tooltip: str = "", index: int = -1) -> "Menu":
        """
        Add a new submenu.
        Args:
            **kwargs: The, following, keyword, arguments, are, accepted - `name` The name for the menu/toolbar item `icon` An icon for the menu. Loaded from the nuke search path.
                      `tooltip` The tooltip text. `index` The position to insert the menu in. Use -1 to add to the end of the menu.
        Returns:
            Menu: The submenu that was added.
        """
        return Menu()
    
    def addSeparator(self, **kwargs) -> MenuItem:
        """
        Add a separator to this menu/toolbar.
        Args:
            **kwargs: The, following, keyword, arguments, are, accepted - `index` The position to insert the new separator in, in the menu/toolbar.
        Returns:
            MenuItem: The separator that was created.
        """
        pass

    def clearMenu(self, **kwargs) -> bool:
        """
        Clears a menu.
        Args:
            **kwargs: The, following, keyword, arguments, are, accepted - `name` The name for the menu/toolbar item
        Returns:
            bool: true if cleared, false if menu not found
        """
        pass
    
    def findItem(self, name: str) -> "Menu":
        """
        Finds a submenu or command with a particular name.
        Args:
            name (str): The name to search for.
        Returns:
            Menu: The submenu or command we found, or None if we could not find anything.
        """
        pass

    def items(self) -> list:
        """
        Returns a list of sub menu items.
        Returns:
            list: A list of all sub menu items.
        """
        return []

    def menu(self, name: str) -> "Menu":
        """
        Finds a submenu or command with a particular name.
        Args:
            name (str): The name to search for.
        Returns:
            Menu: The submenu or command we found, or None if we could not find anything.
        """

    def name(self) -> str:
        """Returns the name of the menu item."""
        return self._name
    
    def removeItem(self, name) -> bool:
        """
        Removes a submenu or command with a particular name. If the containing menu becomes empty, it will be removed too.
        Args:
            name (str): The name to remove for.
        Returns:
            bool: True if removed, False if menu not found
        """
        return False

class Format:
    def __init__(self, width: int, height: int, x: int, y: int, r: int, t: int, pixelAspect: float = 1.0):
        self._name: str = ""
        for i in [width, height, x, y, r, t]:
            if not isinstance(i, int):
                raise TypeError(f"'{type(i).__name__}' object cannot be interpreted as an integer")
        self._width: int = width
        self._height: int = height
        self._x: int = x
        self._y: int = y
        self._r: int = r
        self._t: int = t
        self._pixelAspect: float = pixelAspect

    def add(self, name) -> None:
        """Add this instance to a list of 'named' formats."""
        pass

    def height(self) -> int:
        """Return the height of image file in pixels."""
        return self._height
    
    def name(self) -> str:
        """Returns the user-visible name of the format."""
        return self._name
    
    def pixelAspect(self) -> float:
        """Returns the pixel aspect ratio (pixel width divided by pixel height) for this format."""
        return self._pixelAspect

    def r(self) -> int:
        """Return the right edge of image file in pixels."""
        return self._r
    
    def setName(self, name) -> None:
        """Set name of this format. The name parameter is the new name for the format."""
        self._name = name
    
    def width(self) -> int:
        """Return the width of image file in pixels."""
        return self._width

    def t(self) -> int:
        """Return the top edge of image file in pixels."""
        return self._t

    def x(self) -> int:
        """Return the left edge of image file in pixels."""
        return self._x
    
    def y(self) -> int:
        """Return the bottom edge of image file in pixels."""
        return self._y

class Knob:
    def __init__(self, name, label=None):
        self._name = name
        self._label = label if label else name
        self._value = None
        self._node = None
        self._flag = 0
        self._tooltip: str = ""
        self._visible = True
        self._enabled = True
        self._pyside_object: QWidget = QWidget()
        self._pyside_object_label_item: QWidgetItem = None
        self._panel = None

    def setValue(self, val, chan=None) -> bool:
        """Sets the value `val` at channel `chan`."""
        self._value = val
        return True
    
    def value(self):
        return self._value.split("\t\t\t")[0] if isinstance(self._value, str) else self._value

    def getValue(self):
        return self.value()

    def name(self):
        return self._name
    
    def label(self):
        return self._label

    def node(self):
        return self._node

    def clearAnimated(self) -> bool:
        """Clear animation for channel 'c'. Return True if successful."""
        return True

    def clearFlag(self, f):
        self._flag = 0

    def flag(self, f) -> bool:
        """Returns whether the input flag is set.
        TODO Reimplement to return bool value"""
        return self._flag

    def setEnabled(self, enabled) -> None:
        """
        Enable or disable the knob.
        Args:
            enabled (bool): True to enable the knob, False to disable it.
        """
        self._enabled = enabled

    def setFlag(self, f):
        self._flag = f

    def setTooltip(self, s: str) -> None:
        self._tooltip = s
        self._pyside_object.setToolTip(s)

    def setVisible(self, visible: bool) -> None:
        """Show or hide the knob."""
        self._visible = visible
        self._pyside_object.setVisible(visible)
        if self._pyside_object_label_item and self._pyside_object_label_item.widget():
            self._pyside_object_label_item.widget().setVisible(visible)

    def tooltip(self) -> str:
        return self._tooltip

    def visible(self) -> bool:
        """
        Returns:
            bool: True if the knob is visible, False if it's hidden.
        """
        return self._visible

    def _setPanel(self, panel):
        self._panel = panel

class Format_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value: Format = None

class Array_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = 0.0

class Int_Knob(Array_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value: int = 0
        self._pyside_object: QLineEdit = QLineEdit()
        self._pyside_object.setValidator(QIntValidator())
    
    def setValue(self, val: int) -> bool:
        self._value = val
        self._pyside_object.setText(str(val))
        return True
    
    def _setPanel(self, panel):
        super()._setPanel(panel)
        def handle_text_changed():
            self._value = int(self._pyside_object.text())
            self._panel.knobChanged(self)
        self._pyside_object.textChanged.connect(handle_text_changed)

class Boolean_Knob(Array_Knob):
    def __init__(self, name, label=None, value=False):
        super().__init__(name, label)
        self._pyside_object: QCheckBox = QCheckBox(self._label)
        self.setValue(value)
    
    def setValue(self, b: bool) -> bool:
        """Set the boolean value of this knob."""
        self._value = b
        self._pyside_object.setChecked(b)
        return True

    def _setPanel(self, panel):
        super()._setPanel(panel)
        def handle_toggled():
            self._value = self._pyside_object.isChecked()
            self._panel.knobChanged(self)
        self._pyside_object.toggled.connect(handle_toggled)

class String_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value: str = ""
        self._pyside_object: QLineEdit = QLineEdit()
    
    def setValue(self, val, view='default'):
        self._value = val
        self._pyside_object.setText(val)

    def _setPanel(self, panel):
        super()._setPanel(panel)
        def handle_text_changed():
            self._value = self._pyside_object.text()
            self._panel.knobChanged(self)
        self._pyside_object.textChanged.connect(handle_text_changed)

class EvalString_Knob(String_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Multiline_Eval_String_Knob(EvalString_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._pyside_object: QPlainTextEdit = QPlainTextEdit()
    
    def setValue(self, val, view='default'):
        self._value = val
        self._pyside_object.setPlainText(val)
    
    def _setPanel(self, panel):
        Knob._setPanel(self, panel)
        def handle_text_changed():
            self._value = self._pyside_object.toPlainText()
            self._panel.knobChanged(self)
        self._pyside_object.textChanged.connect(handle_text_changed)

class Text_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value: str = ""
        self._pyside_object: QLabel = QLabel()
    
    def setValue(self, val, chan=None) -> bool:
        """Sets the value `val` at channel `chan`."""
        self._value = val
        self._pyside_object.setText(val)
        return True

class File_Knob(EvalString_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
    
    def fromUserText(self, s):
        """Assign string to knob, parses frame range off the end and opens file to get set the format."""

        def get_exr_channels(file_path: str) -> list:
            try:
                import OpenEXR
            except ImportError:
                print("Install OpenEXR library to access loading channels information for EXR files")
                return []

            ch_map = {"r": "red", "g": "green", "b": "blue", "a": "alpha"}
            channels = []
            with OpenEXR.File(file_path) as exr_file:
                for part in exr_file.parts:
                    part_channels = []
                    spl = []
                    for channel in part.header.get("channels"):
                        spl = channel.name.split(".")
                        if len(spl)==1 and spl[0].lower() in ch_map:
                            spl = ["rgba", spl[0]]
                        if len(spl)==2:
                            spl[1] = ch_map.get(spl[1].lower(), spl[1])
                        part_channels.append(".".join(spl))
                    if spl and spl[0] == "rgba":
                        part_channels.reverse()
                    channels += part_channels

            return channels

        spl = s.split(" ")
        file_path = spl[0]
        self.setValue(file_path)
        first_frame = None
        if len(spl)>1:
            spl = spl[1].split("-")
            first_frame = spl[0]
            last_frame = spl[1] if len(spl)>1 else first_frame
            if first_frame.isdigit() and last_frame.isdigit():
                pass  # TODO выставить первый и последний кадр
        #  TODO выставить формат

        # get channels
        if os.path.splitext(file_path)[1].lower() == ".exr" and self.node():
            matches = list(re.finditer(r"#+|%\d+d", file_path))
            if matches and isinstance(first_frame, str) and first_frame and first_frame.isdigit():
                last_match = matches[-1]
                match_str = last_match.group()
                padding = len(match_str) if match_str.startswith('#') else int(re.search(r'\d+', match_str).group())
                start, end = last_match.start(), last_match.end()
                file_path = file_path[:start] + first_frame.zfill(padding) + file_path[end:]
            if os.path.isfile(file_path):
                self.node()._channels = get_exr_channels(file_path)

    def getEvaluatedValue(self, oc = None) -> str:
        """Returns the string on this knob, will be normalized to technical notation if sequence (%4d). Will also evaluate the string for any tcl expressions"""
        return self.value()

class Unsigned_Knob(Array_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Enumeration_Knob(Unsigned_Knob):
    def __init__(self, name, label = None, values: List[str] = []):
        super().__init__(name, label)
        self._values: List[str] = []
        self._pyside_object: QComboBox = QComboBox()
        self.setValues(values)
        self._value = values[0] if values else None
    
    def setValues(self, items: List[str]):
        self._values = items
        self._pyside_object.clear()
        self._pyside_object.addItems(items)

    def setValue(self, item):
        """Set the current value. If item is of an Integer type it will treat it as an index to the enum, otherwise as a value."""
        if isinstance(item, int) and item < len(self._values):
            self._value = self._values[item]
            return True
        else:
            for v in self._values:
                if v.split("\t")[0] == item:
                    self._value = item
                    return True
        return False

    def values(self):
        return self._values

    def _setPanel(self, panel):
        super()._setPanel(panel)
        self._pyside_object.currentIndexChanged.connect(lambda: self._panel.knobChanged(self))

class Channel_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = "none"

class ChannelMask_Knob(Channel_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = "none"

class Script_Knob(String_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._pyside_object: QPushButton = QPushButton(self._label)
    
    def _setPanel(self, panel):
        Knob._setPanel(self, panel)
        self._pyside_object.clicked.connect(lambda: self._panel.knobChanged(self))

class PyScript_Knob(Script_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Node:
    def __init__(self):
        self._data = {}
        self.addKnob(String_Knob("name", ""))
        self.addKnob(Boolean_Knob("selected", ""))
        self.addKnob(Array_Knob("xpos", "INVISIBLE"))
        self.addKnob(Array_Knob("ypos", "INVISIBLE"))
        self.addKnob(Boolean_Knob("postage_stamp", "Postage Stamp"))
        self.addKnob(Multiline_Eval_String_Knob("label", "Label"))

        self._screenWidth = 80
        self._screenHeight = 18
        self._channels = []
        self.setName(self.__class__.__name__)

        self._inputs: Dict[Node] = {}
        self._metadata = {}

    @overload
    def __getitem__(self, key: Literal["name"]) -> String_Knob: ...
    
    @overload
    def __getitem__(self, key: Literal["file"]) -> File_Knob: ...

    @overload
    def __getitem__(self, key: Literal["also_merge"]) -> ChannelMask_Knob: ...

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def Class(self):
        return self.__class__.__name__

    def autoplace(self) -> None:
        """Automatically place nodes, so they do not overlap."""
        pass

    def knob(self, name):
        return self._data.get(name)
    
    def addKnob(self, k: Knob):
        """Add knob k to this node or panel."""
        self._data[k.name()] = k
        k._node = self

    def setName(self, name, uncollide=True, updateExpressions=False):
        name = name.rstrip("0123456789")
        node_names = [node.name() for node in allNodes()]
        index = 1
        while f"{name}{index}" in node_names:
            index += 1
        self._data["name"].setValue(f"{name}{index}")
    
    def name(self):
        return self._data["name"].value()

    def channels(self) -> List[str]:
        """List channels output by this node."""
        # TODO Сделать чтобы нода спрашивала у нод сверху какие каналы есть
        return self._channels

    def metadata(self, key: str=None, time: float=1001, view=None) -> Union[dict, str, None]:
        """
        Return the metadata item for key on this node at current output context, or at optional time and view.
        If key is not specified a dictionary containing all key/value pairs is returned. None is returned if key does not exist on this node.
        Args:
            key (str): Optional name of the metadata key to retrieve.
            time (str): Optional time to evaluate at (default is taken from node's current output context).
            view: Optional view to evaluate at (default is taken from node's current output context).
        Returns:
            Union[dict, str, None]: The requested metadata value, a dictionary containing all keys if a key name is not provided, or None if the specified key is not matched.
        """
        if key is None:
            return self._metadata
        return self._metadata.get(key)

    def setInput(self, i: int, node: Type["Node"]) -> bool:
        """Connect input i to node if canSetInput() returns true."""
        self._inputs[i] = node
        return True

    def input(self, i: int) -> Union[Type["Node"], None]:
        """Returns the i'th input"""
        return self._inputs.get(i)

    def inputs(self) -> int:
        """Gets the maximum number of connected inputs. Number of the highest connected input + 1. If inputs 0, 1, and 3 are connected, this will return 4."""
        return len(self._inputs)

    def isSelected(self) -> bool:
        """Returns the current selection state of the node. This is the same as checking the 'selected' knob."""
        return self._data["selected"].value()

    def setSelected(self, selected: bool) -> None:
        """
        Set the selection state of the node. This is the same as changing the 'selected' knob.
        Args:
            selected (bool): New selection state - True or False.
        """
        self._data["selected"].setValue(selected)

    def setXYpos(self, x: int, y: int) -> None:
        """Set the (x, y) position of node in node graph."""
        self._data["xpos"].setValue(x)
        self._data["ypos"].setValue(y)

    def setXpos(self, x):
        """Set the x position of node in node graph."""
        self._data["xpos"].setValue(x)

    def setYpos(self, y):
        """Set the y position of node in node graph."""
        self._data["ypos"].setValue(y)

    def xpos(self):
        return self._data["xpos"].value()

    def ypos(self):
        return self._data["ypos"].value()

    def screenWidth(self) -> int:
        """Width of the node when displayed on screen in the DAG, at 1:1 zoom, in pixels."""
        return self._screenWidth

    def screenHeight(self) -> int:
        """Height of the node when displayed on screen in the DAG, at 1:1 zoom, in pixels."""
        return self._screenHeight

    def dependencies(self, what: int) -> List[Type["Node"]]:
        """
        List all nodes referred to by this node. 'what' is an optional integer (see below).
        You can use the following constants or'ed together to select what types of dependencies are looked for:
                `nuke.EXPRESSIONS` = expressions
                `nuke.INPUTS` = visible input pipes
                `nuke.HIDDEN_INPUTS` = hidden input pipes.
        The default is to look for all types of connections.
        Args:
            what (int): Or'ed constant of `nuke.EXPRESSIONS`, `nuke.INPUTS` and `nuke.HIDDEN_INPUTS` to select the types of dependencies. The default is to look for all types of connections.
        Returns:
            List[Node]: List of nodes.
        Example:
            >>> nuke.toNode('Blur1').dependencies( nuke.INPUTS | nuke.EXPRESSIONS )
        """
        return []
    
    def dependent(self, what: int, forceEvaluate: bool = True) -> List[Type["Node"]]:
        """
        List all nodes that read information from this node. 'what' is an optional integer:
                You can use any combination of the following constants or'ed together to select what types of dependent nodes to look for:
                        `nuke.EXPRESSIONS` = expressions
                        `nuke.INPUTS` = visible input pipes
                        `nuke.HIDDEN_INPUTS` = hidden input pipes.
        The default is to look for all types of connections.
        `forceEvaluate` is an optional boolean defaulting to True. When this parameter is true, it forces a re-evaluation of the entire tree. 
        This can be expensive, but otherwise could give incorrect results if nodes are expression-linked. 
        Args:
            what (int): Or'ed constant of `nuke.EXPRESSIONS`, `nuke.INPUTS` and `nuke.HIDDEN_INPUTS` to select the types of dependent nodes. The default is to look for all types of connections.
            forceEvaluate (bool): Specifies whether a full tree evaluation will take place. Defaults to True.
        Returns:
            List[Node]: List of nodes.
        Example:
            >>> nuke.toNode('Blur1').dependent( nuke.INPUTS | nuke.EXPRESSIONS )
        """
        return []

class Group(Node):
    def __init__(self):
        super().__init__()
        self._nodes: List[Node] = []
    
    def nodes(self) -> List[Node]:
        """List of nodes in group."""
        return self._nodes

    def selectedNodes(self) -> list:
        """Selected nodes."""
        res = []
        for n in self._nodes:
            selected = n.isSelected()
            if selected:
                res.append(n)
        return res

class Root(Group):
    def __init__(self):
        super().__init__()
        kn = Enumeration_Knob("colorManagement", "color management")
        kn.setValues(["Nuke", "OCIO"])
        kn.setValue("OCIO")
        self.addKnob(kn)
        kn = Enumeration_Knob("OCIO_config", "OCIO config")
        kn.setValues(["aces_1.2\tACES/aces_1.2\t\t", "fn-nuke_cg-config-v1.0.0_aces-v1.3_ocio-v2.1\tACES/fn-nuke_cg-config-v1.0.0_aces-v1.3_ocio-v2.1\t\tcg-config-v1.0.0_aces-v1.3_ocio-v2.1", "fn-nuke_studio-config-v1.0.0_aces-v1.3_ocio-v2.1\tACES/fn-nuke_studio-config-v1.0.0_aces-v1.3_ocio-v2.1\t\tstudio-config-v1.0.0_aces-v1.3_ocio-v2.1", "nuke-default", "custom"])
        kn.setValue("aces_1.2")
        self.addKnob(kn)
        kn = Array_Knob("fps")
        kn.setValue(24)
        self.addKnob(kn)
        kn = Enumeration_Knob("proxy_type", "")
        kn.setValues(["format", "scale"])
        kn.setValue("scale")
        self.addKnob(kn)
        kn = Format_Knob("format", "full size format")
        format = Format(1920, 1080, 0, 0, 1920, 1080)
        format.setName("HD_1080")
        kn.setValue(format)
        self.addKnob(kn)
        kn = Array_Knob("first_frame", "frame range")
        kn.setValue(1)
        self.addKnob(kn)
        kn = Array_Knob("last_frame", "")
        kn.setValue(100)
        self.addKnob(kn)
        self.addKnob(Boolean_Knob("lock_range"))

    def name(self):
        val = self._data["name"].value()
        return val if val else "Root"
    
    def setName(self, name):
        self._data["name"].setValue(name.replace("\\", "/"))

class Dot(Node):
    def __init__(self):
        super().__init__()

class Read(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(File_Knob("file", "File"))
        self.addKnob(Int_Knob("first", "Frame Range"))
        self.addKnob(Int_Knob("last", ""))
        self.addKnob(Int_Knob("origfirst", "Original Range"))
        self.addKnob(Int_Knob("origlast", ""))
        kn = Enumeration_Knob("frame_mode", "Frame")
        kn.setValues(['expression', 'start at', 'offset'])
        self.addKnob(kn)
        self.addKnob(String_Knob("frame", ""))
        self.addKnob(Enumeration_Knob("colorspace", "Input Transform"))

        self._channels = ['rgba.red', 'rgba.green', 'rgba.blue', 'rgba.alpha']

class Write(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(ChannelMask_Knob("channels"))
        self.addKnob(File_Knob("file", ""))
        kn = Enumeration_Knob("file_type", "file type")
        kn.setValues([" ", "cin", "dpx", "exr", "hdr", "jpeg", "mov\t\t\tffmpeg", "mxf", "null", "pic", "png", "sgi", "targa", "tiff", "xpm", "yuv"])
        self.addKnob(kn)
        kn = Enumeration_Knob("mov64_codec", "Codec")
        kn.setValues(['', '', '', 'ap4x\t\x07', 'ap4h\t\x07', 'apch\t\x07', 'apcn\t\x07', 'apcs\t\x07', 'apco\t\x07', 'mp1v\t\x07', 'rle \tAnimation', 'appr\tApple ProRes', 'AVdn\tAvid DNxHD', 'AVdh\tAvid DNxHR', 'h264\tH.264', 'mjpa\tMotion JPEG A', 'mjpb\tMotion JPEG B', 'mp4v\tMPEG-4', 'jpeg\tPhoto - JPEG', 'png \tPNG', 'v210\tUncompressed'])
        self.addKnob(kn)
        kn = Enumeration_Knob("colorspace", "Output Transform")
        kn.setValues(colorspaces_list)
        self.addKnob(kn)

class Copy(Node):
    def __init__(self):
        super().__init__()
        for i in range(4):
            self.addKnob(Channel_Knob(f"from{i}", "Copy channel"))
            self.addKnob(Channel_Knob(f"to{i}", ""))
        self.addKnob(ChannelMask_Knob("channels", "Layer Copy"))
        self.addKnob(Enumeration_Knob("metainput", "metadata from"))

class Unpremult(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(ChannelMask_Knob("channels", "divide"))
        self.addKnob(Channel_Knob("alpha", "by"))
        self.addKnob(Boolean_Knob("invert", ""))

class Shuffle2(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Channel_Knob("in1", ""))
        self.addKnob(Channel_Knob("out1", ""))

class Remove(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Enumeration_Knob("operation", ""))
        self.addKnob(ChannelMask_Knob("channels", ""))

class Merge2(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Enumeration_Knob("operation", ""))
        self.addKnob(Channel_Knob("output", ""))
        self.addKnob(ChannelMask_Knob("also_merge", "also merge"))
        kn = Enumeration_Knob("bbox", "set bbox to ")
        kn.setValues(["union", "intersection", "A", "B"])
        self.addKnob(Enumeration_Knob("bbox", "set bbox to "))

class MergeExpression(Node):
    def __init__(self):
        super().__init__()
        for i in range(4):
            self.addKnob(EvalString_Knob(f"expr{i}", "="))

class Reformat(Node):
    def __init__(self):
        super().__init__()
        type_kn = Enumeration_Knob("type", "")
        type_kn.setValues(["to format", "to box", "scale"])
        self.addKnob(type_kn)
        self.addKnob(Array_Knob("box_width", "width/height"))
        self.addKnob(Array_Knob("box_height", ""))
        self.addKnob(Boolean_Knob("box_fixed", "force this shape"))
        resize_kn = Enumeration_Knob("resize", "resize type")
        resize_kn.setValues(["none", "width", "height", "fit", "fill", "distort"])
        self.addKnob(resize_kn)
        self.addKnob(Boolean_Knob("black_outside", "black outside"))

class TimeClip(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Int_Knob("first", "frame range"))
        self.addKnob(Int_Knob("last", ""))

class FrameRange(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Array_Knob("first_frame", "frame range"))
        self.addKnob(Array_Knob("last_frame", ""))

class AppendClip(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Array_Knob("firstFrame", "First Frame"))
        self.addKnob(Array_Knob("lastFrame", "Last Frame"))

class Viewer(Node):
    def __init__(self):
        super().__init__()
        self.addKnob(Enumeration_Knob("viewerProcess", "view transform", ["sRGB (ACES)", "DCDM (ACES)", "DCDM P3D60 Limited (ACES)", "DCDM P3D65 Limited (ACES)", "P3-D60 (ACES)", "P3-D65 ST2084 1000 nits (ACES)", "P3-D65 ST2084 2000 nits (ACES)", "P3-D65 ST2084 4000 nits (ACES)", "P3-DCI D60 simulation (ACES)", "P3-DCI D65 simulation (ACES)", "P3D65 (ACES)", "P3D65 D60 simulation (ACES)", "P3D65 Rec.709 Limited (ACES)", "P3D65 ST2084 108 nits (ACES)", "Rec.2020 (ACES)", "Rec.2020 P3D65 Limited (ACES)", "Rec.2020 Rec.709 Limited (ACES)", "Rec.2020 HLG 1000 nits (ACES)", "Rec.2020 ST2084 1000 nits (ACES)", "Rec.2020 ST2084 2000 nits (ACES)", "Rec.2020 ST2084 4000 nits (ACES)", "Rec.709 (ACES)", "Rec.709 D60 sim. (ACES)", "sRGB D60 sim. (ACES)", "Raw (ACES)", "Log (ACES)"]))
    
    def setInput(self, i, node):
        res = super().setInput(i, node)
        for v in _viewerWindows:
            if v._node == self:
                v._active_input = i
        return res

def createNode(nodeClass: str, inpanel: bool = True) -> Node:
    node_types = {
        "Read": Read,
        "Copy": Copy,
        "Unpremult": Unpremult,
        "Shuffle2": Shuffle2,
        "Remove": Remove,
        "Merge2": Merge2,
        "Group": Group,
        "MergeExpression": MergeExpression,
        "Dot": Dot,
        "Reformat": Reformat,
        "TimeClip": TimeClip,
        "FrameRange": FrameRange,
        "AppendClip": AppendClip,
        "Write": Write,
        "Viewer": Viewer
    }

    if nodeClass in node_types:
        node = node_types[nodeClass]()
        root()._nodes.append(node)
        if nodeClass == "Viewer":
            for v in _viewerWindows:
                v._active = False
            _viewerWindows.append(ViewerWindow(node))
        return node
    
    return Node()

def root() -> Root:
    """
    Get the DAG's root node. Always succeeds.
    Returns:
        Root: The root node. This will never be None.
    """
    return _root

def script_directory() -> str:
    return os.path.dirname(root().name()) if root().name() != "Root" else ""

def allNodes(filter: str = None, group = None, recurseGroups : bool = False) -> List[Node]:
    """
    List of all nodes in a group. If you need to get all the nodes in the script from a context which has no child nodes, for instance a control panel, use nuke.root().nodes().
    Args:
        filter (str): Optional. Only return nodes of the specified class.
        group (): Optional. If the group is omitted the current group (ie the group the user picked a menu item from the toolbar of) is used.
        recurseGroups (bool): Optional. If True, will also return all child nodes within any group nodes. This is done recursively and defaults to False.
    """
    if filter:
        return [n for n in root().nodes() if n.Class() == filter]
    return root().nodes()

def selectedNode() -> Node:
    """Returns the 'node the user is thinking about'. If several nodes are selected, this returns one of them. The one returned will be an 'output' node in that no other selected nodes use that node as an input.
    If no nodes are selected, then if the last thing typed was a hotkey this returns the node the cursor is pointing at. If none, or the last event was not a hotkey, this produces a 'No node selected' error."""
    nodes = root().selectedNodes()
    if nodes:
        return nodes[0]
    raise ValueError("no node selected")

def selectedNodes(filter: str = None) -> List[Node]:
    """
    Returns a list of all selected nodes in the current group. An attempt is made to return them in 'useful' order where inputs are done before the final node, so commands applied to this list go from top-down.
    Args:
        filter (str): Optional class of Node. Instructs the algorithm to apply only to a specific class of nodes.
    """
    nodes = root().selectedNodes()
    if filter:
        return [n for n in nodes if n.Class() == filter]
    return nodes

def toNode(s: str) -> Node:
    """Search for a node in the DAG by name and return it as a Python object."""
    for node in allNodes():
        if node.name() == s:
            return node
    return None

def getFileNameList(dir: str, splitSequences: bool = False, extraInformation: bool = False, returnDirs: bool = True, returnHidden: bool = False) -> List[str]:
    """
    Args:
        dir (str): The directory to get sequences from.
        splitSequences (bool): Whether to split sequences or not.
        extraInformation (bool): Whether or not there should be extra sequence information on the sequence name.
        returnDirs (bool): Whether to return a list of directories as well as sequences.
        returnHidden (bool): Whether to return hidden files and directories.
    Returns:
        List[str]: Retrieves the filename list.
    """
    if not os.path.isdir(dir):
        return []

    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    seq_dict = {}
    singles = []

    seq_re = re.compile(r"^(.*?)(\d+)(\.[^.]+)$")

    for f in files:
        m = seq_re.match(f)
        if m:
            prefix, frame, ext = m.groups()
            pattern = f"{prefix}#{ext}"
            if pattern not in seq_dict:
                seq_dict[pattern] = []
            seq_dict[pattern].append(int(frame))
        else:
            singles.append(f)

    result = []
    for pattern, frames in seq_dict.items():
        if frames:
            frames.sort()
            result.append(f"{pattern} {frames[0]}-{frames[-1]}")
    result.extend(singles)
    return result

def getFilename(message: str, pattern: str = None, default: str = None, favorites: str = None, type: str = None, multiple: bool = False) -> Union[List[str], str, None]:
    """
    Pops up a file chooser dialog box. You can use the pattern to restrict the displayed choices to matching filenames, normal Unix glob rules are used here.
    Args:
        message (str): Present the user with this message.
        pattern (str): Optional file selection pattern.
        default (str): Optional default filename and path.
        favorites (str): Optional. Restrict favorites to this set. Must be one of 'image', 'script', or 'font'.
        type (str): Optional the type of browser, to define task-specific behaviors; currently only 'save' is recognised.
        multiple (bool): Optional boolean convertible object to allow for multiple selection. If this is True, the return value will be a list of strings; if not, it will be a single string. The default is False.
    Returns:
        Union[List[str], str, None]: If multiple is True, the user input is returned as a list of strings, otherwise as a single string. If the dialog was cancelled, the return value will be None.
    """
    return input("Enter path: ").replace("\\", "/").strip('"')

def addFormat(s: str) -> Union[Format, None]:
    """
    Create a new image format, which will show up on the pull-down menus for image formats. You must give a width and height and name.
    The xyrt rectangle describes the image area, if it is smaller than the width and height (for Academy aperture, for example).
    The pixel aspect is the ratio of the width of a pixel to the height.
    Args:
        s (str): String in TCL format `w h ?x y r t? ?pa? name`.
    """
    spl = s.split()
    if len(spl) > 1:
        width = int(spl[0])
        height = int(spl[1])
        format = Format(width, height, 0, 0, width, height)
        if len(spl) == 3:
            try:
                pa = float(spl[2])
                format.setPixelAspect(pa)
            except ValueError:
                format.setName(spl[2])
        elif len(spl) == 4:
            format.setPixelAspect(spl[2])
            format.setName(spl[3])
        return format
    return None

def formats() -> list:
    """
    Returns:
        list: List of all available formats.
    """
    return [root()["format"].value()]

def menu(name: str):
    return _menus.get(name)

def message(prompt: str) -> None:
    """
    Show an info dialog box. Pops up an info box (with a 'i' and the text message) and waits for the user to hit the OK button.
    Args:
        prompt (str): Present user with this message.
    """
    print(prompt)

def getInput(prompt: str, default: str = "") -> str:
    """
    Pops up a dialog box with a text field for an arbitrary string.
    Args:
        prompt (str): Present the user with this message.
        default (str): Optional. Default value for the input text field.
    Returns:
        str: String from text field or None if dialog is cancelled.
    """
    return input(prompt)

def execute(nameOrNode, start, end, incr, views, continueOnError=False):
    pass

def delete(n: Node) -> None:
    """The named node is deleted. It can be recovered with an undo."""
    root()._nodes.remove(n)

def ask(prompt: str) -> bool:
    return input(prompt).lower() in ['yes', 'y'] 

def pluginAddPath(args: Union[str, List[str]], addToSysPath: bool = True):
    """Adds all the paths to the beginning of the Nuke plugin path. If the path already exists in the list of plugin paths, it is moved to the start. If this command is executed inside an init.py then the init.py in the path will be executed. It also adds the paths to the sys.path, if addToSysPath is True."""
    if isinstance(args, str):
        args = [args]
    for arg in args:
        if arg in _pluginPath:
            _pluginPath.remove(arg)
        _pluginPath.insert(0, arg)
        if addToSysPath:
            sys.path.insert(0, arg)

def pluginAppendPath(args, addToSysPath: bool = True):
    """Add a filepath to the end of the Nuke plugin path. If the path already exists in the list of plugin paths, it will remain at its current position. It also appends the paths to the sys.path, if addToSysPath is True."""
    for arg in args:
        if arg not in _pluginPath:
            _pluginPath.append(arg)
        if addToSysPath:
            sys.path.append(arg)

def pluginPath() -> List[str]:
    """List all the directories Nuke will search in for plugins.
    The built-in default is `~/.nuke` and the 'plugins' directory from the same location the NUKE executable file is in. Setting the environment variable `$NUKE_PATH` to a colon-separated list of directories will replace the `~/.nuke` with your own set of directories, but the plugins directory is always on the end."""
    return _pluginPath

def scriptNew():
    """Start a new script. Returns True if successful."""
    return True

def scriptOpen(file: str):
    """Opens a new script containing the contents of the named file."""
    root().setName(file)
    for callback_info in _onScriptLoadCallbacks:
        callback_info["call"](*callback_info["args"], **callback_info["kwargs"])

def scriptReadFile(file: str):
    """Read nodes from a file."""
    pass

def scriptReadText(s: str):
    """Read nodes from a string."""
    pass

def scriptSave(filename: str = None) -> bool:
    """
    Saves the current script to the current file name. If there is no current file name and Nuke is running in GUI mode, the user is asked for a name using the file chooser.
    Args:
        filename (str): Save to this file name without changing the script name in the project (use scriptSaveAs() if you want it to change).
    Returns:
            bool: True if the file was saved, otherwise an exception is thrown.
    """
    pass

def scriptSaveAs(filename: str = None, overwrite: int = -1) -> None:
    """
    Saves the current script with the given file name if supplied, or (in GUI mode) asks the user for one using the file chooser. If Nuke is not running in GUI mode, you must supply a filename.
    Args:
        filename (str): Saves the current script with the given file name if supplied, or (in GUI mode) asks the user for one using the file chooser.
        overwrite (int): If 1 (true) always overwrite; if 0 (false) never overwrite; otherwise, in GUI mode ask the user, in terminal do same as False. Default is -1, meaning 'ask the user'.    
    """
    root().setName(filename)

def addOnCreate(call, args=(), kwargs={}, nodeClass="*"):
    """Add code to execute when a node is created or undeleted"""
    pass

def addOnDestroy(call, args=(), kwargs={}, nodeClass="*"):
    """Add code to execute when a node is destroyed"""
    pass

def addOnScriptClose(call, args=(), kwargs={}, nodeClass="Root"):
    """Add code to execute before a script is closed"""
    pass

def addOnScriptLoad(call, args=(), kwargs={}, nodeClass="Root"):
    """Add code to execute when a script is loaded"""
    _onScriptLoadCallbacks.append({"call": call, "args": args, "kwargs": kwargs})

def addOnScriptSave(call, args=(), kwargs={}, nodeClass="Root"):
    """Add code to execute before a script is saved"""
    pass

def addOnUserCreate(call, args=(), kwargs={}, nodeClass="*"):
    """Add code to execute when user creates a node"""
    pass

def thisClass() -> str:
    """Get the class name of the current node. This equivalent to calling nuke.thisNode().Class(), only faster."""
    return root().Class()

def thisGroup() -> Group:
    """Returns the current context Group node."""
    return root()

def thisKnob() -> Knob:
    """Returns the current context knob if any."""
    return None

def thisNode() -> Node:
    """Return the current context node."""
    return root()

def thisPane():
    """Returns the active pane. This is only valid during a pane menu callback or window layout restoration."""
    # TODO
    return None

def thisParent() -> Node:
    """Returns the current context Node parent."""
    return None

def thisView() -> str:
    """Get the name of the current view."""
    return "main"

class ViewerWindow:
    def __init__(self, node: Viewer):
        self._active = True
        self._active_input = None
        self._node = node

    def activeInput(self, secondary: bool = False) -> Union[int, None]:
        """
        Returns the currently active input of the viewer - i. e. the one with its image in the output window.
        Args:
            secondary (bool):  True to return the index of the active secondary (wipe) input, or False (the default) to return the primary input.
        Returns:
            int: The currently active input of the viewer, starting with 0 for the first, or None if no input is active.
        """
        return self._active_input

    def node(self) -> Viewer:
        """Returns the Viewer node currently associated with this window."""
        return self._node

def activeViewer() -> Union[ViewerWindow, None]:
    """Return an object representing the active Viewer panel. This is not the same as the Viewer node, this is the viewer UI element."""
    for viewer in _viewerWindows:
        if viewer._active:
            return viewer
    return None

class AnimationKey:
    """
    Attributes:
        extrapolation (int): Controls how to set the left slope of the first point and the right slope of the last point
        interpolation (int): Used to calculate all the slopes except for the left slope of the first key and the right slope of the last key
        la (float): The left 'bicubic' value
        lslope (float): The derivative to the left of the point
        ra (float): The right 'bicubic' value
        rslope (float): The derivative to the right of the point
        selected (bool): True if the point is selected in the curve editor
        x (float): The horizontal position of the point
        y (float): The vertical position of the point
    """
    def __init__(self, x: float, y: float):
        self.extrapolation: int = 1
        self.interpolation: int = 0
        self.la: float = 0.0
        self.lslope: float = 0.0 
        self.ra: float = 0.0
        self.rslope: float = 0.0
        self.selected: bool = False
        self.x: float = x
        self.y: float = y

class AnimationCurve:
    def __init__(self):
        pass

    def addKey(self, keys: List[AnimationKey]) -> None:
        """
        Insert a sequence of keys.
        Args:
            keys (List[AnimationKey]): Sequence of AnimationKey.
        """
        pass

    def changeInterpolation(self, keys, type) -> None:
        """
        Change interpolation (and extrapolation) type for the keys.
        Args:
            keys: Sequence of keys.
            type: Interpolation type. One of nuke.HORIZONTAL, nuke.BREAK, nuke.BEFORE_CONST, nuke.BEFORE_LINEAR, nuke.AFTER_CONST or nuke.AFTER_LINEAR.
        """
        pass

    def clear(self) -> None:
        """Delete all keys."""
        pass

    def constant(self) -> bool:
        """
        Returns:
            bool: True if the animation appears to be a horizontal line, is a simple number, or it is the default and all the points are at the same y value and have 0 slopes. False otherwise.
        """
        pass

    def derivative(self, t: float, n=1) -> float:
        """
        The n'th derivative at time 't'. If n is less than 1 it returns evaluate(t).
        Args:
            t (float): Time.
            n (int): Optional. Default is 1.
        Returns:
            float: The value of the derivative.
        """
        pass

    def evaluate(self, t: float) -> float:
        """
        Value at time 't'.
        Args:
            t (float): Time.
        Returns:
            float: The value of the animation at time 't'.
        """
        pass

    def fixSlopes(self) -> None:
        pass

    def fromScript(self, s: str) -> None:
        pass

    def identity(self) -> bool:
        """
        Returns:
            bool: True if the animation appears to be such that y == x everywhere. This is True only for an expression of 'x' or the default expression and all points having y == x and slope == 1. Extrapolation is ignored.
        """
        pass

    def integrate(self, t1, t2) -> float:
        """
        Calculate the area underneath the curve from t1 to t2. @param t1 The start of the integration range. @param t2 The end of the integration range.
        Returns:
            float: The result of the integration.
        """
        pass

    def inverse(self, y) -> float:
        """
        The inverse function at value y. This is the value of x such that evaluate(x) returns y. This is designed to invert color lookup tables. It only works if the derivative is zero or positive everywhere.
        Args:
            y: The value of the function to get the inverse for.
        """
        pass

    def keys(self) -> List[AnimationKey]:
        """List of keys."""
        pass

    def knobAndFieldName(self) -> str:
        """Knob and field name combined (e.g. 'translate.x')."""
        pass

    def noExpression(self) -> bool:
        """
        Returns:
            bool: True if the expression is the default expression (i.e. the keys control the curve), False otherwise.
        """
        pass
    
    def removeKey(self, keys) -> None:
        """
        Remove some keys from the curve.
        Args:
            keys: The sequence of keys to be removed.
        """
        pass
    
    def selected(self) -> bool:
        """
        Returns:
            bool: True if selected, False otherwise.
        """
        pass
    
    def setExpression(self, s: str) -> None:
        """
        Set expression.
        Args:
            s (str): A string containing the expression.
        """
        pass
    
    def setKey(self, t: float, y: float) -> AnimationKey:
        """
        Set a key at time t and value y. If there is no key there one is created. If there is a key there it is moved vertically to be at y.
        If a new key is inserted the interpolation and extrapolation are copied from a neighboring key, if there were no keys then it is set to nuke.SMOOTH interpolation and nuke.CONSTANT extrapolation.
        Args:
            t (float): The time to set the key at.
            y (float): The value for the key.
        Returns:
            AnimationKey: The new key.
        """
        pass
    
    def size(self) -> int:
        """
        Returns:
            int: Number of keys.
        """
        pass

    def toScript(self, selected: bool) -> str:
        """
        Args:
            selected (bool): Optional parameter. If this is given and is True, then only process the selected curves; otherwise convert all.
        Returns:
            str: A string containing the curves.
        """
        pass

    def view(self) -> str:
        """The view this AnimationCurve object is associated with."""
        return "main"

class Panel:
    """
    Panel class for creating custom dialog panels in Nuke.
    
    This class provides methods to add various UI controls (knobs) to a panel
    and display them to the user. The panel can contain different types of
    input controls like text fields, buttons, checkboxes, color choosers, etc.
    """
    
    def __init__(self, title: str):
        """
        Initialize a new Panel.
        
        Args:
            title: The title of the panel window
        """
        self._title = title
        self._width = 300
        self._knobs = {}
        self._values = {}
    
    def __new__(cls, *args, **kwargs):
        """
        Create a new Panel instance.
        
        Returns:
            A new Panel object
        """
        return super().__new__(cls)
    
    def addBooleanCheckBox(self, name: str, value: bool = False) -> bool:
        """
        Add a boolean check box knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'boolean_checkbox'
        self._values[name] = value
        return True
    
    def addButton(self, name: str, value: str = "") -> bool:
        """
        Add a button to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'button'
        self._values[name] = value
        return True
    
    def addClipnameSearch(self, name: str, value: str = "") -> bool:
        """
        Add a clipname search knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'clipname_search'
        self._values[name] = value
        return True
    
    def addEnumerationPulldown(self, name: str, value: str = "") -> bool:
        """
        Add a pulldown menu to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'enumeration_pulldown'
        self._values[name] = value
        return True
    
    def addExpressionInput(self, name: str, value: str = "") -> bool:
        """
        Add an expression evaluator to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'expression_input'
        self._values[name] = value
        return True
    
    def addFilenameSearch(self, name: str, value: str = "") -> bool:
        """
        Add a filename search knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'filename_search'
        self._values[name] = value
        return True
    
    def addMultilineTextInput(self, name: str, value: str = "") -> bool:
        """
        Add a multi-line text knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'multiline_text_input'
        self._values[name] = value
        return True
    
    def addNotepad(self, name: str, value: str = "") -> bool:
        """
        Add a text edit widget to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'notepad'
        self._values[name] = value
        return True
    
    def addPasswordInput(self, name: str, value: str = "") -> bool:
        """
        Add a password input knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'password_input'
        self._values[name] = value
        return True
    
    def addRGBColorChip(self, name: str, value: Union[int, tuple, list] = 0) -> bool:
        """
        Add a color chooser to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob (color value)
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'rgb_color_chip'
        self._values[name] = value
        return True
    
    def addScriptCommand(self, name: str, value: str = "") -> bool:
        """
        Add a script command evaluator to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'script_command'
        self._values[name] = value
        return True
    
    def addSingleLineInput(self, name: str, value: str = "") -> bool:
        """
        Add a single-line input knob to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'single_line_input'
        self._values[name] = value
        return True
    
    def addTextFontPulldown(self, name: str, value: str = "") -> bool:
        """
        Add a font chooser to the panel.
        
        Args:
            name: The name for the new knob
            value: The initial value for the new knob
            
        Returns:
            True if successful
        """
        self._knobs[name] = 'text_font_pulldown'
        self._values[name] = value
        return True
    
    def clear(self) -> None:
        """
        Clear all panel attributes.
        """
        self._knobs.clear()
        self._values.clear()
    
    def execute(self, name: str) -> Optional[str]:
        """
        Execute the script command associated with a particular label and return the
        result as a string.
        
        Args:
            name: The name of the script field to execute
            
        Returns:
            The result of the script as a string, or None if it fails
        """
        if name in self._knobs and self._knobs[name] == 'script_command':
            # In a real implementation, this would execute the script
            # For now, just return the stored value
            return str(self._values.get(name, ""))
        return None
    
    def setTitle(self, val: str) -> bool:
        """
        Set the current title for the panel.
        
        Args:
            val: The title as a string
            
        Returns:
            True if successful
        """
        self._title = val
        return True
    
    def setWidth(self, val: int) -> bool:
        """
        Set the width of the panel.
        
        Args:
            val: The width as an int
            
        Returns:
            True if successful
        """
        self._width = val
        return True
    
    def show(self) -> int:
        """
        Display the panel.
        
        Returns:
            An int value indicating how the dialog was closed (normally, or cancelled)
        """
        # In a real implementation, this would show the actual dialog
        # For now, simulate showing and return 1 (OK)
        print(f"Showing panel: {self._title}")
        print(f"Panel width: {self._width}")
        print("Panel contents:")
        for name, knob_type in self._knobs.items():
            value = self._values[name]
            print(f"  {name} ({knob_type}): {value}")
        return 1  # 1 typically means OK, 0 means cancelled
    
    def title(self) -> str:
        """
        Get the current title for the panel.
        
        Returns:
            The title as a string
        """
        return self._title
    
    def value(self, name: str) -> Any:
        """
        Get the value of a particular control in the panel.
        
        Args:
            name: The name of the knob to get a value from
            
        Returns:
            The value for the field if any, otherwise None
        """
        return self._values.get(name, None)
    
    def width(self) -> int:
        """
        Get the width of the panel.
        
        Returns:
            The width as an int
        """
        return self._width

class ProgressTask:
    def __init__(self, title: str):
        self._title = title
        self._progress = 0
        self._message = ""
        self._is_cancelled = False

    def isCancelled(self) -> bool:
        """
        Check if the progress task has been cancelled.
        
        Returns:
            True if cancelled, False otherwise
        """
        return self._is_cancelled

    def setMessage(self, message: str) -> None:
        """
        Set the message for the progress task.
        
        Args:
            message: The message to set
        """
        self._message = message

    def setProgress(self, progress: int) -> None:
        """
        Set the progress for the progress task.

        Args:
            progress: The progress value to set (0-100)
        """
        if progress < 101:
            self._progress = max(0, progress)

_root = Root()
_menus = {"Nuke": Menu(), "Nodes": Menu()}
_viewerWindows: List[ViewerWindow] = []
_viewerWindows.append(ViewerWindow(createNode("Viewer")))
_onScriptLoadCallbacks = []
