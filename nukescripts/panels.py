import sys
import nuke
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QVBoxLayout, QDialogButtonBox, QFormLayout, QCheckBox

app = QApplication(sys.argv)

class PythonPanel(QDialog):
    def __init__(self, title="", id="", scrollable=True):
        super().__init__()
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
        if knob.__class__.__name__ == "String_Knob":
            self.form_layout.addRow(knob.label(), QLineEdit())
        elif knob.__class__.__name__ == "Boolean_Knob":
            self.form_layout.addRow("", QCheckBox(knob.label()))

    def showModalDialog(self, defaultKnobText=""):
        return self.exec()
