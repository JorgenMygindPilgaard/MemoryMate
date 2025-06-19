from PyQt6.QtWidgets import QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QDialog, QPushButton
from configuration.settings import Settings
from configuration.language import Texts

class InitialSettingsWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Prepare window
        self.setWindowTitle(Texts.get("settings_window_title"))
        self.setGeometry(400, 300, 300, 150)
        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)
        self.headline = QLabel('Please select Language - Vælg Sprog')
        settings_layout.addWidget(self.headline)

        # Add language selection box
        self.language_combobox = QComboBox()
        for index, (key, value) in enumerate(Settings.get('languages').items()):
            self.language_combobox.addItem(key+" - "+value)
            if key == 'EN':
                self.language_combobox.setCurrentIndex(index)
        language_label = QLabel('Language - Sprog')
        language_layout = QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        settings_layout.addLayout(language_layout)

        # Add ui_mode-selection
        self.ui_mode_combobox = QComboBox(self)
        for index, ui_mode in enumerate(Settings.get('ui_modes')):
            language = Settings.get('language')
            if language is None:
                language = 'EN'
            self.ui_mode_combobox.addItem(Texts.get("settings_ui_mode."+ui_mode))
            if ui_mode == Settings.get('ui_mode'):
                self.ui_mode_combobox.setCurrentIndex(index)
        if self.ui_mode_combobox.currentIndex() is None:
            self.ui_mode_combobox.setCurrentIndex(0)
        ui_mode_label = QLabel(Texts.get("settings_labels_ui_mode"), self)
        ui_mode_layout = QHBoxLayout()
        ui_mode_layout.addWidget(ui_mode_label)
        ui_mode_layout.addWidget(self.ui_mode_combobox)
        settings_layout.addLayout(ui_mode_layout)


        settings_layout.addSpacing(20)
        self.ok_button = QPushButton("OK")
        settings_layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.saveSettings)

    def saveSettings(self, index):
        Settings.set('language',self.language_combobox.currentText()[:2])

        ui_mode = Settings.get('ui_modes')[self.ui_mode_combobox.currentIndex()]
        Settings.set('ui_mode',ui_mode)

        Settings.writeSettingsFile()
        self.accept()
