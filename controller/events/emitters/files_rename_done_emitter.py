from PyQt6.QtCore import QObject, pyqtSignal

class FileRenameDoneEmitter(QObject):
    instance = None
    done_signal = pyqtSignal(list)  # [{"old_name":<old filename>,"new_name":<new filename>}]

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileRenameDoneEmitter.instance is None:
            FileRenameDoneEmitter.instance = FileRenameDoneEmitter()
        return FileRenameDoneEmitter.instance
    def emit(self, files):
        self.done_signal.emit(files)
