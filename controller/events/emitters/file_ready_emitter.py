from PyQt6.QtCore import QObject, pyqtSignal

class FileReadyEmitter(QObject):
    instance = None
    ready_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileReadyEmitter.instance is None:
            FileReadyEmitter.instance = FileReadyEmitter()
        return FileReadyEmitter.instance

    def emit(self, file_name):
        self.ready_signal.emit(file_name)