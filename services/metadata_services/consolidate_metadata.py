import time

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.settings import Settings
from controller.events.emitters.file_metadata_pasted_emitter import FileMetadataPastedEmitter
from services.file_services.file_get_list import getFileList
from services.metadata_services.metadata import FileMetadata
from services.stack_services.stack import Stack


class ConsolidateMetadata(QObject):
# This class force-saves logical tags to all physical tags in files

    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)            # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)  # Sends exception and retry_allowed (true/false)


    def __init__(self,target, await_start_signal=False):
        # target is a filename, a foldername, a list of filenames or a list of folder-names
        super().__init__()
        self.delay = 1
        self.target=target
        if not await_start_signal:
            self.start()

    def start(self):
        file_name_pattern=[]
        for filetype in Settings.get('file_types'):
            file_name_pattern.append("*."+filetype)
        file_names = []
        if isinstance(self.target, list):
            for file_path in self.target:
                file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))
        else:
            file_names.extend(getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))
        file_count = len(file_names)
        self.progress_init_signal.emit(file_count)


        # Instanciate file metadata instances for all files
        # Stack all files with meta-data read pending
        for file_name in file_names:
            if FileMetadata.getInstance(file_name).getStatus() == 'PENDING_READ':
                Stack.getInstance('metadata.read').push(file_name)

        # Read metadata for the files and consolidate (force-saving)
        for index, file_name in enumerate(reversed(file_names)):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file_name)
#            while file_metadata.getStatus() != '':
#                time.sleep(self.delay)
            file_metadata.setLogicalTagValues(logical_tag_values={},force_rewrite=True)
#            file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
#            file_metadata_pasted_emitter.emit(file_name)

        self.done_signal.emit()
