from typing import Union, List, Callable
import os, re, sys

from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QCheckBox, QComboBox, QPlainTextEdit, QLabel, QWidget, QWidgetItem 
from PySide6.QtGui import QIntValidator

STARTLINE = 1

app = QApplication(sys.argv)

_all_nodes = {}
_pluginPath: List[str] = [os.path.expanduser("~/.nuke").replace("\\", "/")]

class MenuItem:
    def __init__(self):
        pass

class Menu(MenuItem):
    def __init__(self):
        super().__init__()
    
    def addCommand(self, name: str, command: Union[str, Callable] = None, shortcut: str = "", icon: str = "", tooltip: str = "", index: int = -1, readonly: bool = False) -> MenuItem:
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

class Format:
    def __init__(self, name, width, height, pixelAspect=1.0):  # TODO takes at least 6 arguments
        self._name = name
        self._width = width
        self._height = height
        self._pixelAspect = pixelAspect

    def name(self):
        return self._name

    def width(self):
        return self._width
    
    def height(self):
        return self._height
    
    def pixelAspect(self):
        return self._pixelAspect
    
    def setName(self, name):
        self._name = name

class Knob:
    def __init__(self, name, label=None):
        self._name = name
        self._label = label if label else name
        self._value = None
        self._node = None
        self._flag = 0
        self._tooltip: str = ""
        self._visible = True
        self._pyside_object: QWidget = QWidget()
        self._pyside_object_label_item: QWidgetItem = None
        self._panel = None

    def setValue(self, val, chan=None) -> bool:
        """Sets the value `val` at channel `chan`."""
        self._value = val
        return True
    
    def value(self):
        return self._value.split("\t\t\t")[0] if isinstance(self._value, str) else self._value

    def name(self):
        return self._name
    
    def label(self):
        return self._label

    def node(self):
        return self._node

    def clearFlag(self, f):
        self._flag = 0

    def flag(self, f) -> bool:
        """Returns whether the input flag is set.
        TODO Reimplement to return bool value"""
        return self._flag

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
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value: bool = False
        self._pyside_object: QCheckBox = QCheckBox(self._label)
    
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
        super()._setPanel(panel)
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

class Node:
    def __init__(self, cls):
        self.cls = cls
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
        self.setName(cls)
    
    def __getitem__(self, key):
        return self._data[key]

    def Class(self):
        return self.cls

    def knob(self, name):
        return self._data.get(name)
    
    def addKnob(self, k: Knob):
        """Add knob k to this node or panel."""
        self._data[k.name()] = k
        k._node = self

    def setName(self, name, uncollide=True, updateExpressions=False):
        name = name.rstrip("0123456789")
        class_node_names = [node.name() for node in _all_nodes.get(self.cls, [])]
        index = 1
        while f"{name}{index}" in class_node_names:
            index += 1
        self._data["name"].setValue(f"{name}{index}")
    
    def name(self):
        return self._data["name"].value()

    def channels(self) -> List[str]:
        """List channels output by this node."""
        # TODO Сделать чтобы нода спрашивала у нод сверху какие каналы есть
        return self._channels

    def setInput(self, i, node):
        """Connect input i to node if canSetInput() returns true."""
        # TODO
        pass

    def setSelected(self, selected):
        """Set the selection state of the node. This is the same as changing the 'selected' knob."""
        self._data["selected"].setValue(selected)

    def setXYpos(self, x, y):
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

class Group(Node):
    def __init__(self):
        super().__init__("Group")

class Root(Node):
    def __init__(self):
        super().__init__("Root")
        self._data["name"].setValue(__file__)
        kn = Enumeration_Knob("colorManagement", "color management")
        kn.setValues(["Nuke", "OCIO"])
        self.addKnob(kn)
        kn = Enumeration_Knob("OCIO_config", "OCIO config")
        kn.setValues(['aces_1.2\tACES/aces_1.2\t\t', 'fn-nuke_cg-config-v1.0.0_aces-v1.3_ocio-v2.1\tACES/fn-nuke_cg-config-v1.0.0_aces-v1.3_ocio-v2.1\t\tcg-config-v1.0.0_aces-v1.3_ocio-v2.1', 'fn-nuke_studio-config-v1.0.0_aces-v1.3_ocio-v2.1\tACES/fn-nuke_studio-config-v1.0.0_aces-v1.3_ocio-v2.1\t\tstudio-config-v1.0.0_aces-v1.3_ocio-v2.1', 'nuke-default', 'custom'])
        self.addKnob(kn)

    def name(self):
        val = self._data["name"].value()
        return val if val else "Root"

class Dot(Node):
    def __init__(self):
        super().__init__("Dot")

class Read(Node):
    def __init__(self):
        super().__init__("Read")
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
        super().__init__("Write")
        self.addKnob(File_Knob("file", ""))
        kn = Enumeration_Knob("file_type", "file type")
        kn.setValues([" ", "cin", "dpx", "exr", "hdr", "jpeg", "mov\t\t\tffmpeg", "mxf", "null", "pic", "png", "sgi", "targa", "tiff", "xpm", "yuv"])
        self.addKnob(kn)
        kn = Enumeration_Knob("mov64_codec", "Codec")
        kn.setValues(['', '', '', 'ap4x\t\x07', 'ap4h\t\x07', 'apch\t\x07', 'apcn\t\x07', 'apcs\t\x07', 'apco\t\x07', 'mp1v\t\x07', 'rle \tAnimation', 'appr\tApple ProRes', 'AVdn\tAvid DNxHD', 'AVdh\tAvid DNxHR', 'h264\tH.264', 'mjpa\tMotion JPEG A', 'mjpb\tMotion JPEG B', 'mp4v\tMPEG-4', 'jpeg\tPhoto - JPEG', 'png \tPNG', 'v210\tUncompressed'])
        self.addKnob(kn)
        self.addKnob(Enumeration_Knob("colorspace", "Output Transform"))

class Copy(Node):
    def __init__(self):
        super().__init__("Copy")
        for i in range(4):
            self.addKnob(Channel_Knob(f"from{i}", "Copy channel"))
            self.addKnob(Channel_Knob(f"to{i}", ""))
        self.addKnob(ChannelMask_Knob("channels", "Layer Copy"))
        self.addKnob(Enumeration_Knob("metainput", "metadata from"))

class Unpremult(Node):
    def __init__(self):
        super().__init__("Copy")
        self.addKnob(ChannelMask_Knob("channels", "divide"))
        self.addKnob(Channel_Knob("alpha", "by"))
        self.addKnob(Boolean_Knob("invert", ""))

class Shuffle2(Node):
    def __init__(self):
        super().__init__("Shuffle2")
        self.addKnob(Channel_Knob("in1", ""))

class Remove(Node):
    def __init__(self):
        super().__init__("Remove")
        self.addKnob(Enumeration_Knob("operation", ""))
        self.addKnob(ChannelMask_Knob("channels", ""))

class Merge2(Node):
    def __init__(self):
        super().__init__("Merge2")
        self.addKnob(Enumeration_Knob("operation", ""))
        self.addKnob(Channel_Knob("output", ""))

class MergeExpression(Node):
    def __init__(self):
        super().__init__("MergeExpression")
        for i in range(4):
            self.addKnob(EvalString_Knob(f"expr{i}", "="))

class Reformat(Node):
    def __init__(self):
        super().__init__("Reformat")
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
        super().__init__("TimeClip")
        self.addKnob(Int_Knob("first", "frame range"))
        self.addKnob(Int_Knob("last", ""))

class FrameRange(Node):
    def __init__(self):
        super().__init__("FrameRange")
        self.addKnob(Array_Knob("first_frame", "frame range"))
        self.addKnob(Array_Knob("last_frame", ""))

class AppendClip(Node):
    def __init__(self):
        super().__init__("AppendClip")
        self.addKnob(Array_Knob("firstFrame", "First Frame"))
        self.addKnob(Array_Knob("lastFrame", "Last Frame"))

_root = Root()
_menus = {'Nuke': Menu(), 'Nodes': Menu()}

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
        "Write": Write
    }

    if nodeClass in node_types:
        node = node_types[nodeClass]()
        _all_nodes.setdefault(nodeClass, []).append(node)
        return node
    
    return Node(nodeClass)

def root():
    return _root

def allNodes(filter=None):
    if filter:
        return _all_nodes.get(filter, [])
    return [i for lst in _all_nodes.values() for i in lst]

def toNode(s: str) -> Node:
    """Search for a node in the DAG by name and return it as a Python object."""
    for node in allNodes():
        if node.name() == s:
            return node
    return None

def getFileNameList(dir, splitSequences= False, extraInformation= False, returnDirs=True, returnHidden=False):
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

def getFilename(message, pattern=None, default=None, favorites=None, type=None, multiple=False):
    return input("Enter path: ").replace('\\', '/').strip('"')

def menu(name: str):
    return _menus.get(name)

def message(prompt):
    print(prompt)

def execute(nameOrNode, start, end, incr, views, continueOnError=False):
    pass

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
