from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton

from configuration.language import Texts


class InputFileNamePattern(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Texts.get("standardize_dialog_title"))
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add labels and input fields
        prefix_label = QLabel(Texts.get("standardize_dialog_prefix_label"))

        self.prefix = QLineEdit()
        layout.addWidget(prefix_label)
        layout.addWidget(self.prefix)

        num_pattern_label = QLabel(Texts.get("standardize_dialog_number_pattern_label"))
        self.num_pattern = QLineEdit()
        layout.addWidget(num_pattern_label)
        layout.addWidget(self.num_pattern)

        suffix_label = QLabel(Texts.get("standardize_dialog_postfix_label"))
        self.suffix = QLineEdit()
        layout.addWidget(suffix_label)
        layout.addWidget(self.suffix)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton(Texts.get("general_ok"))
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton(Texts.get("general_cancel"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

    def getInput(self):
        # Return the input values as a tuple
        return (self.prefix.text(), self.num_pattern.text(), self.suffix.text())
