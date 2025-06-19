import os
from configuration.paths import Paths

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton, QMainWindow, QWidget, \
    QApplication

from configuration.settings import Settings
from view.ui_components.file_preview import FilePreview
from services.metadata_services.exiftool_wrapper import ExifTool
from services.metadata_services.metadata import FileMetadata
from services.queue_services.queue import Queue
from view.ui_components.file_metadata_update_queue_status import QueueStatusMonitor
from view.windows.file_list import FileList
from view.windows.file_panel import FilePanel
from view.ui_components.settings_wheel import SettingsWheeel
from services.utility_services.parameter_manager import ParameterManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Get UI-status from last run from UI-status file
        self.ui_status = ParameterManager.getInstance(Paths.get('ui_status'))

        self.setWindowTitle("Memory Mate " + Settings.get('version'))
        self.setWindowIcon(QIcon(os.path.join(Paths.get('resources'), 'memory_mate.ico')))

        current_file = self.ui_status.getParameter('current_file')
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
            current_file = os.path.join(Paths.get('resources'),
                                        "Memory Mate Sample Photo.jpg")  # Show sample-photo at first launch
            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FilePreview.getInstance(current_file).readImage()
        else:
            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FilePreview.getInstance(current_file).readImage()
        # CurrentFileChangedEmitter.getInstance().emit(current_file)
        # FileMetadata.getInstance(current_file).readLogicalTagValues()
        # FilePreview.getInstance(current_file).readImage()
        # Stack.getInstance('metadata.read',FileMetadata,'processReadStackEntry').push(current_file)    # Triggers other files in folder to be read

        # -------------------------------------------------------------------------------------------------------------
        # Chose settings at first launch
        # -------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        self.file_panel = FilePanel.getInstance(current_file)

        # Prepare metadata write queue
        self.metadata_write_queue = Queue.getInstance('metadata.write', FileMetadata, 'processWriteQueueEntry',
                                                      Paths.get('queue'))  # Instanciate Queue for updating metadata
        if self.ui_status.getParameter('is_paused'):
            self.metadata_write_queue.pause()
        self.metadata_write_queue.start()  # Måske ikke nødvendigt

        # Status of file-processing (Top line of main-window)
        self.metadata_write_queue_status_monitor = QueueStatusMonitor(self.metadata_write_queue)

        # Clickable settings-wheel in top line of main window
        self.settings_wheel = SettingsWheeel()

        # File list (Left part of MainWindow)
        self.file_list = FileList(dir_path='')
        self.file_list.setOpenFolders(self.ui_status.getParameter('open_folders'))
        self.file_list.setSelectedItems(self.ui_status.getParameter('selected_items'))
        self.file_list.setCurrentItem(self.ui_status.getParameter('current_file'))

        # Main-widget (Central widget of MainWindow)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # -------------------------------------------------------------------------------------------------------------
        # Place Widgets in laqyout
        # -------------------------------------------------------------------------------------------------------------
        main_layout = QVBoxLayout()
        controll_line_layout = QHBoxLayout()
        main_layout.addLayout(controll_line_layout)
        file_section_layout = QHBoxLayout()
        main_layout.addLayout(file_section_layout)
        file_panel_layout = QVBoxLayout()
        file_section_layout.addWidget(self.file_list)
        file_section_layout.addLayout(file_panel_layout)
        file_panel_layout.addWidget(self.file_panel)
        controll_line_layout.addLayout(self.metadata_write_queue_status_monitor)
        controll_line_layout.addWidget(self.settings_wheel)
        main_widget.setLayout(main_layout)
        self.setGeometry(100, 100, 1600, 800)
        is_maximized = self.ui_status.getParameter('is_maximized')
        if is_maximized == None:
            is_maximized = True
        if is_maximized:
            self.showMaximized()

        self.file_list.setVerticalScrollPosition(self.ui_status.getParameter('vertical_scroll_position'))
        # if self.ui_status.getParameter('geometry'):
        #     self.setGeometry(self.ui_status.getParameter('geometry').toVariang())

        self.file_panel.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.file_panel and event.type() == QEvent.Type.KeyPress:
            if event.key() in (
            Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_PageDown, Qt.Key.Key_PageUp):
                # Forward the event to FileList
                QApplication.sendEvent(self.file_list, event)
                return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        self.file_panel.saveMetadata()  # Saves metadata if changed
        self.ui_status.setParameters({'current_file': self.file_panel.file_name,
                                      'open_folders': self.file_list.getOpenFolders(),
                                      'selected_items': self.file_list.getSelectedItems(),
                                      'vertical_scroll_position': self.file_list.getVerticalScrollPosition(),
                                      'is_maximized': self.isMaximized(),
                                      'is_paused': self.metadata_write_queue.queue_worker_paused})
        self.ui_status.save()
        ExifTool.closeProcess()  # Close exiftool processes
        super().closeEvent(event)
