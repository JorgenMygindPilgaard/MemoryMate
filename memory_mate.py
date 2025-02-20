import sys
import os
from ui_widgets import *
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QDialog, QComboBox
from exiftool_wrapper import ExifTool
from file_metadata_util import QueueHost, QueueStatusMonitor, FileReadQueue
from ui_status import UiStatusManager
from ui_main import FilePanel, FileList, SettingsWheeel,SettingsWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QEvent
from file_metadata_util import FileMetadata, FilePreview
import settings
import qdarkstyle
from language import getText
from lightroom_integration import processLightroomQueue

class WelcomeWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Prepare window
        self.setWindowTitle('Welcome - Velkommen')
        self.setGeometry(400, 300, 300, 150)
        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)
        self.headline = QLabel('Please select Language - Vælg Sprog')
        settings_layout.addWidget(self.headline)

        # Add language selection box
        self.language_combobox = QComboBox()
        for index, (key, value) in enumerate(settings.languages.items()):
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
        for index, ui_mode in enumerate(settings.ui_modes):
            language = settings.language
            if language is None:
                language = 'EN'
            self.ui_mode_combobox.addItem(getText("settings_ui_mode."+ui_mode))
            if ui_mode == settings.ui_mode:
                self.ui_mode_combobox.setCurrentIndex(index)
        if self.ui_mode_combobox.currentIndex() is None:
            self.ui_mode_combobox.setCurrentIndex(0)
        ui_mode_label = QLabel(getText("settings_labels_ui_mode"), self)
        ui_mode_layout = QHBoxLayout()
        ui_mode_layout.addWidget(ui_mode_label)
        ui_mode_layout.addWidget(self.ui_mode_combobox)
        settings_layout.addLayout(ui_mode_layout)


        settings_layout.addSpacing(20)
        self.ok_button = QPushButton("OK")
        settings_layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.saveLanguage)

    def saveLanguage(self, index):
        settings.settings["language"] = self.language_combobox.currentText()[:2]
        settings.language = self.language_combobox.currentText()[:2]

        ui_mode = settings.ui_modes[self.ui_mode_combobox.currentIndex()]
        settings.settings["ui_mode"] = ui_mode
        settings.ui_mode = ui_mode

        settings.writeSettingsFile()
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Get UI-status from last run from UI-status file
        self.ui_status = UiStatusManager.getInstance(os.path.join(settings.app_data_location, "ui_status.json"))

        self.setWindowTitle("Memory Mate "+settings.version)
        self.setWindowIcon(QIcon(os.path.join(settings.resource_path,'memory_mate.ico')))

        current_file = self.ui_status.getStatusParameter('current_file')
        show_sample_photo = False

        file_exist = False
        if not current_file:
            show_sample_photo = True
        else:
            if isinstance(current_file, str):
                file_exist = os.path.isfile(current_file)

        if not file_exist:
            show_sample_photo = True

        if show_sample_photo:
            current_file = os.path.join(settings.resource_path, "Memory Mate Sample Photo.jpg")       # Show sample-photo at first launch
            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FilePreview.getInstance(current_file).readImage()
        else:
            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FilePreview.getInstance(current_file).readImage()
#            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FileReadQueue.appendQueue(current_file)    # Triggers other files in folder to be read

        #-------------------------------------------------------------------------------------------------------------
        # Chose settings at first launch
        #-------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        self.file_panel = FilePanel.getInstance(current_file)

        # Set Queue to paused/running from uu-status
        if self.ui_status.getStatusParameter('is_paused'):
            QueueHost.get_instance().pause_queue_worker()

        # Status of file-processing (Top line of main-window)
        self.queue_status_monitor = QueueStatusMonitor()

        # Clickable settings-wheel in top line of main window
        self.settings_wheel = SettingsWheeel()

        # File list (Left part of MainWindow)
        self.file_list = FileList(dir_path='')
        self.file_list.setOpenFolders(self.ui_status.getStatusParameter('open_folders'))
        self.file_list.setSelectedItems(self.ui_status.getStatusParameter('selected_items'))
        self.file_list.setCurrentItem(self.ui_status.getStatusParameter('current_file'))

        # Main-widget (Central widget of MainWindow)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        #-------------------------------------------------------------------------------------------------------------
        # Place Widgets in laqyout
        #-------------------------------------------------------------------------------------------------------------
        main_layout = QVBoxLayout()
        controll_line_layout = QHBoxLayout()
        main_layout.addLayout(controll_line_layout)
        file_section_layout = QHBoxLayout()
        main_layout.addLayout(file_section_layout)
        file_panel_layout = QVBoxLayout()
        file_section_layout.addWidget(self.file_list)
        file_section_layout.addLayout(file_panel_layout)
        file_panel_layout.addWidget(self.file_panel)
        controll_line_layout.addLayout(self.queue_status_monitor)
        controll_line_layout.addWidget(self.settings_wheel)
        main_widget.setLayout(main_layout)
        self.setGeometry(100, 100, 1600, 800)
        is_maximized = self.ui_status.getStatusParameter('is_maximized')
        if is_maximized == None:
            is_maximized = True
        if is_maximized:
            self.showMaximized()

        self.file_list.setVerticalScrollPosition(self.ui_status.getStatusParameter('vertical_scroll_position'))
        # if self.ui_status.getStatusParameter('geometry'):
        #     self.setGeometry(self.ui_status.getStatusParameter('geometry').toVariang())

        self.file_panel.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.file_panel and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_PageDown, Qt.Key.Key_PageUp):
                # Forward the event to FileList
                QApplication.sendEvent(self.file_list, event)
                return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        self.file_panel.saveMetadata()      # Saves metadata if changed
        self.ui_status.setUiStatusParameters({'current_file':   self.file_panel.file_name,
                                              'open_folders':   self.file_list.getOpenFolders(),
                                              'selected_items': self.file_list.getSelectedItems(),
                                              'vertical_scroll_position': self.file_list.getVerticalScrollPosition(),
                                              'is_maximized': self.isMaximized(),
                                              'is_paused': QueueHost.get_instance().queue_worker_paused})
        self.ui_status.save()
        QueueHost.get_instance().stop_queue_worker()
        ExifTool.closeProcess()              # Close exiftool processes
        super().closeEvent(event)

app = QApplication(sys.argv)
app.setStyle("Fusion")

# Check if language is set, if not, show the selection dialog
if settings.language is None:
    dialog = WelcomeWindow()
    if dialog.exec() == QDialog.DialogCode.Rejected:  # If user closes the dialog, exit app
        sys.exit()

# Rename files in Lightroom if anything in queue
if settings.lr_integration_active:
    processLightroomQueue(settings.lr_db_path,settings.lr_queue_file_path,True)


# Set UI-mode
if settings.ui_mode == 'LIGHT':
    app.setStyle("Fusion")
elif settings.ui_mode == 'DARK':
    app.setStyleSheet(qdarkstyle.load_stylesheet())
else:
    app.setStyle("Fusion")

window = MainWindow()
window.show()
QueueHost.get_instance().start_queue_worker()    #Start Queue-processing
app.exec()

