import copy
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
        self.source_type, self.source_value = source
        self.logical_tags=logical_tags
        self.overwrite = overwrite
        self.match_file_name = match_file_name

        # source can be
        # 1. ("file_path_list",(a list of paths to dirs and/or files)),
        # 2. ("file_info", "{info}". info can be "original_file_base_name", "file_base_name", "file_name" or "file_path"
        # 3. ("tag", "{tag name}". tag_name can be any of the file metadata tags
        # 4. ("value", (value to put in logical tags))

        self.source_file_names = []
        if self.source_type == "file_path_list":
            if isinstance(self.source_value, str):
                self.source_value = [self.source_value]  # Convert to list in case a string is provided
            for file_path in self.source_value:
                self.source_file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))

        self.target_file_names = []
        if isinstance(target, list):
            for file_path in target:
                self.target_file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))
        else:
            self.target_file_names.extend(
                getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        if not await_start_signal:
            self.start()

    def start(self):
        # Check not attempting to  copy from many files to many files
        if self.source_type == "file_path_list":
            if len(self.source_file_names)>1 and not self.match_file_name:
                return

        # Make a dummy-source_file entry in self.source_file_names, in source_type is not "file_path_list".
        if self.source_type != "file_path_list":
            self.source_file_names = ["dummy"]

        # Find all source - target combinations to copy
        source_targets=[]
        for source_file_name in self.source_file_names:
            for target_file_name in self.target_file_names:
                if self.source_type == "file_path_list":
                    if self.match_file_name and FileMetadata.getInstance(target_file_name).name_alone != FileMetadata.getInstance(source_file_name).name_alone:
                        continue
                source_targets.append([source_file_name,target_file_name])
        copy_file_count=len(source_targets)
        self.progress_init_signal.emit(copy_file_count)

        # Instanciate file metadata instances for all source-files

        # Stack all source-files with meta-data read pending, if they are used for copying from
        if self.source_type == "file_path_list":
            for source_target in source_targets:
                source_file_name = source_target[0]
                if FileMetadata.getInstance(source_file_name).getStatus() == 'PENDING_READ':
                    Stack.getInstance('metadata.read').push(source_file_name)

        # Stack all target-files with meta-data read pending, if their tags are used for copying to logical tags
        if self.source_type == "tag":
            for source_target in source_targets:
                target_file_name = source_target[1]
                if FileMetadata.getInstance(target_file_name).getStatus() == 'PENDING_READ':
                    Stack.getInstance('metadata.read').push(target_file_name)

        # Read metadata for the files and consolidate (force-saving)
        for index, source_target in enumerate(reversed(source_targets)):
            self.progress_signal.emit(index+1)
            source_file_name = source_target[0]
            if self.source_type == "file_path_list":
                source_file_metadata = FileMetadata.getInstance(source_file_name)
                while source_file_metadata.getStatus() != '':
                    time.sleep(self.delay)

            target_file_name = source_target[1]
            target_file_metadata = FileMetadata.getInstance(target_file_name)
            if self.source_type == "tag":
                while target_file_metadata.getStatus() != '':
                    time.sleep(self.delay)


            target_tag_values = {}
            for logical_tag in self.logical_tags:
                if self.source_type == "file_path_list":
                    source_tag_values = source_file_metadata.getLogicalTagValues()
                    source_tag_value = source_tag_values.get(logical_tag)
                elif self.source_type == "tag":
                    source_tag_value = target_file_metadata.tag_values.get(self.source_value)
                    if source_tag_value is None:    # If tag not found, then don't paste
                        continue
                elif self.source_type == 'file_info':
                    source_tag_value = (
#                        "original_file_base_name", "file_base_name", "file_name" or "file_path"
                        target_file_metadata.name_alone if self.source_value == "original_file_base_name" else
                        target_file_metadata.name       if self.source_value == "file_base_name" else
                        target_file_metadata.name+target_file_metadata.extension  if self.source_value == "file_name" else
                        target_file_metadata.file_name if self.source_value == "file_path" else
                        None)
                    if source_tag_value is None:
                        continue
                elif self.source_type == "value":
                    source_tag_value = self.source_value
                target_tag_values[logical_tag] = source_tag_value
            if target_tag_values == {}:
                continue
            target_file_metadata.setLogicalTagValues(logical_tag_values=target_tag_values, overwrite=self.overwrite)
            if target_file_metadata.getStatus() == '':
                file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
                file_metadata_pasted_emitter.emit(target_file_name)
        self.done_signal.emit()