import time

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.settings import Settings
from controller.events.emitters.file_metadata_pasted_emitter import FileMetadataPastedEmitter
from services.file_services.file_get_list import getFileList
from services.metadata_services.metadata import FileMetadata
from services.stack_services.stack import Stack


class CopyLogicalTags(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self, source, target, logical_tags, match_file_name=False, overwrite=True, await_start_signal=False):
        super().__init__()

#       Source and target converted to list of files
        file_name_pattern=[]
        for filetype in Settings.get('file_types'):
            file_name_pattern.append("*."+filetype)
        self.delay = 1
        self.source_file_names = []
        if isinstance(source, list):
            for file_path in source:
                self.source_file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))
        else:
            self.source_file_names.extend(
                getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        self.target_file_names = []
        if isinstance(target, list):
            for file_path in target:
                self.target_file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))
        else:
            self.target_file_names.extend(
                getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        self.logical_tags=logical_tags
        self.overwrite = overwrite
        self.match_file_name = match_file_name
        if not await_start_signal:
            self.start()

    def start(self):
        if len(self.source_file_names)>1 and not self.match_file_name:   # Not possible to copy from many files to many files
            return
        # Find all source - targety combinations to copy
        source_targets=[]
        for source_file_name in self.source_file_names:
            for target_file_name in self.target_file_names:
                if self.match_file_name and FileMetadata.getInstance(target_file_name).name_alone != FileMetadata.getInstance(source_file_name).name_alone:
                    continue
                source_targets.append([source_file_name,target_file_name])
        copy_file_count=len(source_targets)
        self.progress_init_signal.emit(copy_file_count)

        for index, source_target in enumerate(source_targets):
            source_file_name = source_target[0]
            target_file_name = source_target[1]
            source_file_metadata = FileMetadata.getInstance(source_file_name)
            while source_file_metadata.getStatus() != '':
                if source_file_metadata.getStatus() == 'PENDING_READ':
                    Stack.getInstance('metadata.read)').push(source_file_name)
                    time.sleep(self.delay)
            target_file_metadata = FileMetadata.getInstance(target_file_name)
            self.progress_signal.emit(index + 1)
            target_tag_values = {}
            for logical_tag in self.logical_tags:
                source_tag_value = None
                source_tag_values = source_file_metadata.getLogicalTagValues()
                source_tag_value = source_tag_values.get(logical_tag)
                if source_tag_value is not None:
                    target_tag_values[logical_tag] = source_tag_value
            target_file_metadata.setLogicalTagValues(logical_tag_values=target_tag_values, overwrite=self.overwrite)
            if target_file_metadata.getStatus() == '':
                file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
                file_metadata_pasted_emitter.emit(target_file_name)
        self.done_signal.emit()