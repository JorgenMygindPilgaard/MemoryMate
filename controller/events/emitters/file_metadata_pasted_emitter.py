from PyQt6.QtCore import QObject, pyqtSignal

class FileMetadataPastedEmitter(QObject):
    instance = None
    paste_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileMetadataPastedEmitter.instance is None:
            FileMetadataPastedEmitter.instance = FileMetadataPastedEmitter()
        return FileMetadataPastedEmitter.instance
    def emit(self, file_name):
        self.paste_signal.emit(file_name)