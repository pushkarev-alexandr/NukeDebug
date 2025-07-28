import nuke
from typing import Dict
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout

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
