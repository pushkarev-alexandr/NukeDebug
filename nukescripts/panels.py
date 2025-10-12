import nuke
from typing import Dict
from PySide2.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout

class PythonPanel(QDialog):
    def __init__(self, title="", id="", scrollable=True):
        super().__init__()
        self._knobs: Dict[str, nuke.Knob] = {}

        self.setWindowTitle(title)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)
    
    def addKnob(self, knob: nuke.Knob):
        row_index = self.form_layout.rowCount()
        if isinstance(knob, nuke.Boolean_Knob):
            self.form_layout.addRow("", knob._pyside_object)
        else:
            self.form_layout.addRow(knob.label(), knob._pyside_object)
        label_item = self.form_layout.itemAt(row_index, QFormLayout.LabelRole)
        knob._pyside_object_label_item = label_item
        knob._setPanel(self)
        self._knobs[knob.name()] = knob

    def knobs(self) -> Dict[str, nuke.Knob]:
        return self._knobs

    def showModalDialog(self, defaultKnobText=""):
        return self.exec()
    
    def knobChanged(self, knob: nuke.Knob):
        pass

def registerWidgetAsPanel ( widget, name, id, create = False ):
    """registerWidgetAsPanel(widget, name, id, create) -> PythonPanel

        Wraps and registers a widget to be used in a Nuke panel.

        widget - should be a string of the class for the widget
        name - is is the name as it will appear on the Pane menu
        id - should the the unique ID for this widget panel
        create - if this is set to true a new NukePanel will be returned that wraps this widget

        Example ( using PySide2 )

        import nuke
        from PySide2 import QtCore, QtWidgets
        from nukescripts import panels

        class NukeTestWindow( QtWidgets.QWidget ):
            def __init__(self, parent=None):
                QtWidgets.QWidget.__init__(self, parent)
                self.setLayout( QtWidgets.QVBoxLayout() )
                
                self.myTable = QtWidgets.QTableWidget()
                headers = ['Date', 'Files', 'Size', 'Path' ]
                self.myTable.setColumnCount( len( headers ) )
                self.myTable.setHorizontalHeaderLabels( headers )
                self.layout().addWidget( self.myTable )

        nukescripts.registerWidgetAsPanel('NukeTestWindow', 'NukeTestWindow', 'uk.co.thefoundry.NukeTestWindow' )
    """
    
    # class Panel( PythonPanel ):

    #     def __init__(self, widget, name, id):
    #         PythonPanel.__init__(self, name, id )
    #         self.customKnob = nuke.PyCustom_Knob( name, "", "__import__('nukescripts').panels.WidgetKnob(" + widget + ")" )
    #         self.addKnob( self.customKnob  )

    # def addPanel():
    #     return Panel( widget, name, id ).addToPane()

    # menu = nuke.menu('Pane')
    # menu.addCommand( name, addPanel)
    # registerPanel( id, addPanel )

    # if ( create ):
    #     return Panel( widget, name, id )
    # else:
    #     return None
