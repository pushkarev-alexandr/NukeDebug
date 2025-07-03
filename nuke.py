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
    
    def setValue(self, value):
        self._value = value
    
    def value(self):
        return self._value

    def name(self):
        return self._name
    
    def label(self):
        return self._label

class File_Knob(Knob):
    def __init__(self, name, label=None):
        super().__init__(name, label)

class Node:
    def __init__(self, cls):
        self.cls = cls
        self._data = {"name": Knob("name", "")}
        self.setName(cls)
    
    def __getitem__(self, key):
        return self._data[key]

    def Class(self):
        return self.cls

    def knob(self, name):
        return self._data.get(name)
    
    def setName(self, name, uncollide=True, updateExpressions=False):
        self._data["name"].setValue(name)
    
    def name(self):
        return self._data["name"].value()

class Group(Node):
    def __init__(self):
        super().__init__("Group")

class Root(Node):
    def __init__(self):
        super().__init__("Root")
        capital_disk_letter = __file__[0].upper() + __file__[1:] if __file__ else __file__
        self._data["name"].setValue(capital_disk_letter)
    
    def name(self):
        val = self._data["name"].value()
        return val if val else "Root"

class Read(Node):
    def __init__(self):
        super().__init__("Read")
        self._data["file"] = Knob("file", "File")
        self._data["first"] = Knob("first", "Frame Range")
        self._data["last"] = Knob("last", "")
        self._data["origfirst"] = Knob("origfirst", "Original Range")
        self._data["origlast"] = Knob("origlast", "")
        self._data["colorspace"] = Knob("colorspace", "Input Transform")

_all_nodes = {}
_root = Root()
_menus = {'Nuke': Menu(), 'Nodes': Menu()}

def createNode(nodeClass: str, inpanel: bool = True) -> Node:
    if nodeClass == "Read":
        node = Read()
        _all_nodes.setdefault("Read", []).append(node)
        return node
    return Node(nodeClass)

def root():
    return _root

def allNodes(filter=None):
    if filter:
        return _all_nodes.get(filter, [])
    return [i for lst in _all_nodes.values() for i in lst]

def getFileNameList(dir, splitSequences= False, extraInformation= False, returnDirs=True, returnHidden=False):
    pass

def menu(name: str):
    return _menus.get(name)
