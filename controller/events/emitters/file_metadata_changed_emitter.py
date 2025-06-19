from PyQt6.QtCore import QObject, pyqtSignal

class FileMetadataChangedEmitter(QObject):
    instance = None
    change_signal = pyqtSignal(str, dict, dict)  # Filename, old logical tag values, new logical tag values

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileMetadataChangedEmitter.instance is None:
            FileMetadataChangedEmitter.instance = FileMetadataChangedEmitter()
        return FileMetadataChangedEmitter.instance
    def emit(self, file_name, old_logical_tag_values, new_logical_tag_values):
        self.change_signal.emit(file_name, old_logical_tag_values, new_logical_tag_values)