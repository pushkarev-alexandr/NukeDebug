from typing import List
import os, re

_all_nodes = {}

class MenuItem:
    def __init__(self):
        pass

class Menu(MenuItem):
    def __init__(self):
        super().__init__()

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
    
    def setValue(self, value):
        self._value = value
    
    def value(self):
        return self._value

    def name(self):
        return self._name
    
    def label(self):
        return self._label

    def node(self):
        return self._node

class Array_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = 0.0

class Int_Knob(Array_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = 0

class Boolean_Knob(Array_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self._value = False

class String_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class EvalString_Knob(String_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Multiline_Eval_String_Knob(EvalString_Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

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
            if matches and isinstance(first_frame, str) and first_frame.isdigit():
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
    def __init__(self, name, label=None):
        super().__init__(name, label)
        self.value = None

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
        capital_disk_letter = __file__[0].upper() + __file__[1:] if __file__ else __file__
        self.addKnob(File_Knob("name", ""))
        self._data["name"].setValue(capital_disk_letter)
    
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
        self.addKnob(Enumeration_Knob("colorspace", "Input Transform"))

        self._channels = ['rgba.red', 'rgba.green', 'rgba.blue', 'rgba.alpha']

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
        "Dot": Dot
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
    pass

def getFilename(message, pattern=None, default=None, favorites=None, type=None, multiple=False):
    return input("Enter path: ").replace('\\', '/').strip('"')

def menu(name: str):
    return _menus.get(name)

def message(prompt):
    print(prompt)
