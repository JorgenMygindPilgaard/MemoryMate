import sys
from ui_widgets import *
from PyQt6.QtWidgets import QWidget,QMainWindow,QApplication
from exiftool_wrapper import ExifTool
from file_metadata_util import QueueHost, QueueStatusMonitor, FileReadQueue
from ui_status import UiStatusManager
from ui_main import FilePanel, FileList, SettingsWheeel
from PyQt6.QtGui import QIcon
from file_metadata_util import FileMetadata, FilePreview


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Get UI-status from last run from UI-status file
        self.ui_status = UiStatusManager.getInstance(os.path.join(settings.app_data_location, "ui_status.json"))

        self.setWindowTitle("Memory Mate "+settings.version)
        self.setWindowIcon(QIcon('memory_mate.ico'))

        current_file = self.ui_status.getStatusParameter('current_file')
        if not current_file:
            current_file = "Memory Mate Sample Photo.jpg"       # Show sample-photo at first launch
            FileMetadata.getInstance(current_file).readLogicalTagValues()
            FilePreview.getInstance(current_file).readImage()
        else:
          # Start loading files in current folder
            try:
               FileMetadata.getInstance(current_file).readLogicalTagValues()
               FilePreview.getInstance(current_file).readImage()
               FileReadQueue.appendQueue(current_file)    # Triggers other files in folder to be read
            except Exception as e:
               current_file = ''
#

        #-------------------------------------------------------------------------------------------------------------
        # Prepare widgets for MainWindow
        #-------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        self.file_panel = FilePanel.getInstance(current_file)

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

    def closeEvent(self, event):
        self.file_panel.saveMetadata()      # Saves metadata if changed
        self.ui_status.setUiStatusParameters({'current_file':   self.file_panel.file_name,
                                              'open_folders':   self.file_list.getOpenFolders(),
                                              'selected_items': self.file_list.getSelectedItems(),
                                              'vertical_scroll_position': self.file_list.getVerticalScrollPosition(),
                                              'is_maximized': self.isMaximized()})
#                                              'geometry': self.geometry().saveToVariant()})
        self.ui_status.save()
        QueueHost.get_instance().stop_queue_worker()
        ExifTool.closeProcess()              # Close exiftool processes
        super().closeEvent(event)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
QueueHost.get_instance().start_queue_worker()    #Start Queue-processing
app.exec()

