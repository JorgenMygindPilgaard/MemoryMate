from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFileDialog


class FileSelector(QWidget):
    def __init__(self, placeholder_text=None, file_path=None, selector_title='Select File'):
        super().__init__()
        layout = QVBoxLayout()
        self.file_path_entry = self.ClickableLineEdit(self, placeholder_text=placeholder_text, text=file_path,
                                                      selector_title=selector_title)
        layout.addWidget(self.file_path_entry)
        self.setLayout(layout)

    def getFilePath(self):
        return self.file_path_entry.text()

    class ClickableLineEdit(QLineEdit):
        def __init__(self, parent=None, placeholder_text=None, text=None, selector_title='Select File'):
            super().__init__(parent)
            if placeholder_text:
                self.setPlaceholderText(placeholder_text)
            if text:
                self.setText(text)
            self.selector_title = selector_title

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                dialog = QFileDialog(self)
                dialog.setWindowTitle(self.selector_title)
                dialog.setFileMode(QFileDialog.FileMode.Directory)  # Allow selecting only folders
                dialog.setOption(
                    QFileDialog.Option.DontUseNativeDialog)  # Allows showing files but not selecting them
                dialog.setDirectory(self.text())  # Start at current text if available

                if dialog.exec():
                    selected_folders = dialog.selectedFiles()
                    if selected_folders:
                        self.setText(selected_folders[0])
            else:
                super().mousePressEvent(event)  # Keep default behavior for other mouse actions
