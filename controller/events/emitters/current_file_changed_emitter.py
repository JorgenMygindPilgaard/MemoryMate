from PyQt6.QtCore import QObject, pyqtSignal


class CurrentFileChangedEmitter(QObject):
    instance = None
    change_signal = pyqtSignal(str)  # Old filename, new filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if CurrentFileChangedEmitter.instance is None:
            CurrentFileChangedEmitter.instance = CurrentFileChangedEmitter()
        return CurrentFileChangedEmitter.instance
    def emit(self, new_file_name):
        self.change_signal.emit(new_file_name)