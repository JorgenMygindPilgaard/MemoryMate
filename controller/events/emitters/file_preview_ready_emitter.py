from PyQt6.QtCore import QObject, pyqtSignal

class FilePreviewReadyEmitter(QObject):
    instance = None
    ready_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FilePreviewReadyEmitter.instance is None:
            FilePreviewReadyEmitter.instance = FilePreviewReadyEmitter()
        return FilePreviewReadyEmitter.instance

    def emit(self, file_name):
        self.ready_signal.emit(file_name)