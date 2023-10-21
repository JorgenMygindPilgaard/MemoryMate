import sys
from PyQt6.QtWidgets import QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QWidget
import settings


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Prepare window
        window_title = settings.text_keys.get("settings_window_title").get(settings.language)
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 400, 200)
        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)

        # Add language selection box
        self.language_combobox = QComboBox(self)
        for index, (key, value) in enumerate(settings.languages.items()):
            self.language_combobox.addItem(key+" - "+value)
            if key == settings.language:
                self.language_combobox.setCurrentIndex(index)
        language_label = QLabel(settings.text_keys.get("settings_labels_application_language").get(settings.language), self)
        language_layout = QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        settings_layout.addLayout(language_layout)

        # Connect the ComboBox's item selection to a slot
        self.language_combobox.currentIndexChanged.connect(self.onLanguageSelected)

    def onLanguageSelected(self, index):
        settings.settings["language"] = self.language_combobox.currentText()[:2]
        settings.write_settings_file()
