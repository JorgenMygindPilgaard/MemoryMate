from PyQt6.QtCore import QObject, pyqtSignal

class FileRenameDoneEmitter(QObject):
    instance = None
    done_signal = pyqtSignal(list,bool)  # [{"old_name":<old filename>,"new_name":<new filename>}]

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileRenameDoneEmitter.instance is None:
            FileRenameDoneEmitter.instance = FileRenameDoneEmitter()
        return FileRenameDoneEmitter.instance
    def emit(self, files,update_original_filename_tag):
        self.done_signal.emit(files,update_original_filename_tag)
