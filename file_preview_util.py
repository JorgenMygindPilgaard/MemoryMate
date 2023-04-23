from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class FilePreview():
    instance_index = {}

    def __init__(self,file_name,width):
        height = int(width * 9 / 16)
        self.pixmap = QPixmap(file_name).scaled(width, height, Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.width = width
        FilePreview.instance_index[file_name] = self

    @staticmethod
    def getInstance(file_name,width):
        new_needed = False

        file_preview = FilePreview.instance_index.get(file_name)
        if file_preview is None:
            new_needed = True
        elif file_preview.width != width:
            del FilePreview.instance_index[file_name]
            new_needed = True
        if new_needed:
            file_preview =  FilePreview(file_name,width)

        return file_preview
