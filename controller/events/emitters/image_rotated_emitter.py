from PyQt6.QtCore import QObject, pyqtSignal

class ImageRotatedEmitter(QObject):
    instance = None
    rotate_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if ImageRotatedEmitter.instance is None:
            ImageRotatedEmitter.instance = ImageRotatedEmitter()
        return ImageRotatedEmitter.instance
    def emit(self, file_name):
        self.rotate_signal.emit(file_name)