from PyQt6.QtCore import QObject, pyqtSignal

class FileMetadataReadyEmitter(QObject):
    instance = None
    ready_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileMetadataReadyEmitter.instance is None:
            FileMetadataReadyEmitter.instance = FileMetadataReadyEmitter()
        return FileMetadataReadyEmitter.instance

    def emit(self, file_name):
        self.ready_signal.emit(file_name)