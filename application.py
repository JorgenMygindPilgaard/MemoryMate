import sys
from ui_widgets import *
from PyQt5.QtWidgets import QWidget,QMainWindow,QApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata Editor")
        #-------------------------------------------------------------------------------------------------------------
        # Prepare widgets for MainWindow
        #-------------------------------------------------------------------------------------------------------------
        # File (Right part of MainWindow)
        file = File.get_instance('')

        # File list (Middle part of MainWindow)
        file_list = FileList(dir_path='', current_file=file)

        # Folder-tree (Left part of MainWindow)
        folder_tree = FolderTree('',file_list)

        # Main-widget (Central widget of MainWindow)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        #-------------------------------------------------------------------------------------------------------------
        # Place Widgets in laqyout
        #-------------------------------------------------------------------------------------------------------------
        main_layout = QHBoxLayout()

        main_layout.addWidget(folder_tree)
        main_layout.addWidget(file_list)
        main_layout.addLayout(file.layout)   #file manages its own layout

        main_widget.setLayout(main_layout)


app = QApplication(sys.argv)
# Set stylesheet for entire app
font=app.font()   #font from system
font_family = font.family()
font_size = str(font.pointSize())+"pt"
font_weight = str(font.weight())
app.setStyleSheet(f"* {{ font-family: {font_family}; font-size: {font_size}; font-weight: {font_weight};}}")
window = MainWindow()
window.show()
app.exec()