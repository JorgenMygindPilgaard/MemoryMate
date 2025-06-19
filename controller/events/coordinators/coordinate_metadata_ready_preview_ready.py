from PyQt6.QtCore import QObject
from controller.events.emitters.file_ready_emitter import FileReadyEmitter

class Coordinator(QObject):
    instance = None
    def __init__(self):
        super().__init__()
        self.metadata_ready_filenames = set()
        self.file_preview_ready_filenames = set()

    @staticmethod
    def getInstance():
        if Coordinator.instance is None:
            Coordinator.instance = Coordinator()
        return Coordinator.instance
    def metadataReady(self,file_name):
        if file_name in self.file_preview_ready_filenames:
            self.metadata_ready_filenames.discard(file_name)
            self.file_preview_ready_filenames.discard(file_name)   # It is not there. Just to be sure
            self.emit(file_name)
        else:
            self.metadata_ready_filenames.add(file_name)

    def filePreviewReady(self,file_name):
        if file_name in self.metadata_ready_filenames:
            self.metadata_ready_filenames.discard(file_name)
            self.file_preview_ready_filenames.discard(file_name)   # It is not there. Just to be sure
            self.emit(file_name)
        else:
            self.file_preview_ready_filenames.add(file_name)

    def emit(self, file_name):
        FileReadyEmitter.getInstance().emit(file_name)
