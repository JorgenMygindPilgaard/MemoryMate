import sys
from ui_widgets import *
from PyQt5.QtWidgets import QWidget,QMainWindow,QApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Mate")
        #-------------------------------------------------------------------------------------------------------------
        # Prepare widgets for MainWindow
        #-------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        file_panel = FilePanel.getInstance('')

        # File list (Middle part of MainWindow)
        file_list = FileList(dir_path='', current_file=file_panel)
        file_list.setFixedWidth(600)


        # Folder-tree (Left part of MainWindow)
        folder_tree = FolderTree('',file_list)
        folder_tree.setFixedWidth(700)

        # Main-widget (Central widget of MainWindow)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        #-------------------------------------------------------------------------------------------------------------
        # Place Widgets in laqyout
        #-------------------------------------------------------------------------------------------------------------
        main_layout = QHBoxLayout()

        main_layout.addWidget(folder_tree)
        main_layout.addWidget(file_list)
        main_layout.addWidget(file_panel)   #file manages its own layout

        #        main_layout.addLayout(file.layout)   #file manages its own layout

        main_widget.setLayout(main_layout)

    def closeEvent(self, event):
        FilePanel.saveMetadata()      # Saves metadata if changed
        super().closeEvent(event)

app = QApplication(sys.argv)
# Set stylesheet for entire app
font=app.font()   #font from system
font_family = font.family()
font_size = str(font.pointSize())+"pt"
font_weight = str(font.weight())
app.setStyleSheet(f"* {{ font-family: {font_family}; font-size: {font_size}; font-weight: {font_weight};}}")
window = MainWindow()
window.setGeometry(100, 100, 2000, 1000)
window.show()
app.exec()