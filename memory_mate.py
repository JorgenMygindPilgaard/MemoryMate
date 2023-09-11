import sys
from ui_widgets import *
from PyQt6.QtWidgets import QWidget,QMainWindow,QApplication
from exiftool_wrapper import ExifTool
from file_metadata_util import QueueHost, QueueStatusMonitor
from ui_status import UiStatusManager
from ui_main import FilePanel, FileList


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Mate")

        # Get UI-status from last run from UI-status file
        self.ui_status = UiStatusManager(os.path.join(settings.app_data_location, "ui_status.json"))

        #-------------------------------------------------------------------------------------------------------------
        # Prepare widgets for MainWindow
        #-------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        self.file_panel = FilePanel.getInstance(self.ui_status.getStatusParameter('current_file'))
#        self.file_panel = FilePanel.getInstance('')

        # File (Right part of MainWindow)
        self.queue_status_monitor = QueueStatusMonitor()

        # File list (Left part of MainWindow)
        self.file_list = FileList(dir_path='', file_panel=self.file_panel)
        self.file_list.setOpenFolders(self.ui_status.getStatusParameter('open_folders'))
        self.file_list.setSelectedItems(self.ui_status.getStatusParameter('selected_items'))
#        self.file_list.setFixedWidth(1200)


        # Main-widget (Central widget of MainWindow)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        #-------------------------------------------------------------------------------------------------------------
        # Place Widgets in laqyout
        #-------------------------------------------------------------------------------------------------------------
        main_layout = QHBoxLayout()
        file_panel_layout = QVBoxLayout()

        # main_layout.addWidget(folder_tree)         #Out
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(file_panel_layout)
        file_panel_layout.addLayout(self.queue_status_monitor)
        file_panel_layout.addWidget(self.file_panel)
#        main_layout.addWidget(self.file_panel)   #file manages its own layout

        main_widget.setLayout(main_layout)

    def closeEvent(self, event):
        self.file_panel.saveMetadata()      # Saves metadata if changed
        self.ui_status.setUiStatusParameters({'current_file':   self.file_panel.file_name,
                                              'open_folders':   self.file_list.getOpenFolders(),
                                              'selected_items': self.file_list.getSelectedItems()})
        ExifTool.close()              # Close exiftool process
        super().closeEvent(event)

app = QApplication(sys.argv)
window = MainWindow()
QueueHost.get_instance().start_queue_worker()    #Start Queue-processing
window.setGeometry(100, 100, 2000, 1000)
window.show()
app.exec()

