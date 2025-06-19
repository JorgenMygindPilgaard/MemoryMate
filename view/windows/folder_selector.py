from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFileDialog, QDialog, QLabel, QDialogButtonBox


class FolderSelector(QWidget):
    def __init__(self, placeholder_text=None, folder_path=None, selector_title='Select Folder'):
        super().__init__()
        layout = QVBoxLayout()
        self.initial_folder_path = folder_path
        self.folder_path_entry = self.ClickableLineEdit(self, placeholder_text=placeholder_text, text=folder_path,
                                                        selector_title=selector_title)
        layout.addWidget(self.folder_path_entry)
        self.setLayout(layout)

    def getFolderPath(self):
        return self.folder_path_entry.text()

    class ClickableLineEdit(QLineEdit):
        def __init__(self, parent=None, placeholder_text=None, text=None, selector_title='Select Folder'):
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

class FolderSelectorDialog(QDialog):
    def __init__(self, label_text='Select Folder', placeholder_text=None, folder_path=None, selector_title='Select Folder',width=300):
        super().__init__()
        self.setWindowTitle(selector_title)
        self.setMinimumWidth(width)

        layout = QVBoxLayout()

        # Label above the folder selector
        self.label = QLabel(label_text)
        layout.addWidget(self.label)

        # Folder selector
        self.folder_selector = FolderSelector(placeholder_text, folder_path, selector_title)
        layout.addWidget(self.folder_selector)

        # OK & Cancel buttons
        self.button_box = QDialogButtonBox(
#            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
             QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def getFolderPath(self):
        return self.folder_selector.getFolderPath()
