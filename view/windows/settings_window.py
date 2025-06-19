import sys

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QCheckBox, QPushButton, QApplication

from configuration.language import Texts
from configuration.settings import Settings
from view.windows.file_selector import FileSelector
import subprocess


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Prepare window
        window_title = Texts.get("settings_window_title")
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 400, 200)
        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)

        # Add language selection box
        self.language_combobox = QComboBox(self)
        for index, (key, value) in enumerate(Settings.get('languages').items()):
            self.language_combobox.addItem(key+" - "+value)
            if key == Settings.get('language'):
                self.language_combobox.setCurrentIndex(index)
        language_label = QLabel(Texts.get("settings_labels_application_language"), self)
        language_layout = QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        settings_layout.addLayout(language_layout)

        # Add ui_mode-selection
        self.ui_mode_combobox = QComboBox(self)
        for index, ui_mode in enumerate(Settings.get('ui_modes')):
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

        # Add Lightroom integration fields
        lr_integration_headline = QLabel(Texts.get('settings_lr_integration_headline'))
        settings_layout.addWidget(lr_integration_headline)
        self.lr_integration_active_checkbox = QCheckBox(Texts.get('settings_labels_lr_integration_active'))
        self.lr_integration_active_checkbox.setChecked(Settings.get('lr_integration_active'))
        settings_layout.addWidget(self.lr_integration_active_checkbox)
        lr_integration_disclaimer_label = QLabel(Texts.get('settings_lr_integration_disclaimer'))
        lr_integration_disclaimer_label.setStyleSheet("color: #868686;")
        settings_layout.addWidget(lr_integration_disclaimer_label)
        self.lr_cat_file_selector = FileSelector(Texts.get('settings_lr_file_selector_placeholder_text'),
                                                           Settings.get('lr_db_path'),
                                                           Texts.get('settings_lr_file_selector_title'))
        lr_cat_file_selector_label = QLabel(Texts.get('settings_labels_lr_db_file'))
        lr_cat_file_selector_layout = QHBoxLayout()
        lr_cat_file_selector_layout.addWidget(lr_cat_file_selector_label)
        lr_cat_file_selector_layout.addWidget(self.lr_cat_file_selector)
        settings_layout.addLayout(lr_cat_file_selector_layout)


        settings_layout.addSpacing(20)
        self.ok_button = QPushButton("OK")
        settings_layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.saveSettings)

    def saveSettings(self):
        Settings.set("language",self.language_combobox.currentText()[:2])
        ui_mode = Settings.get('ui_modes').get(self.ui_mode_combobox.currentIndex())
        Settings.set('ui_mode',ui_mode)
        Settings.set('lr_integration_active',self.lr_integration_active_checkbox.isChecked())
        Settings.set('lr_db_path',self.lr_cat_file_selector.getFilePath())
        Settings.writeSettingsFile()
        python = sys.executable  # Get Python executable path
        script = sys.argv[0]  # Get the current script file
        subprocess.Popen([python, script])  # Start a new instance
        QApplication.quit()  # Close current instance
        self.accept()
