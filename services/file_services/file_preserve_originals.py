import os
import shutil
import time

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.settings import Settings
from configuration.language import Texts
from services.file_services.file_get_sidecar_files import fileGetSidecarFiles
from services.file_services.file_split_name import splitFileName
from services.file_services.file_get_list import getFileList
from services.metadata_services.metadata import FileMetadata
from services.stack_services.stack import Stack


class PreserveOriginals(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,target, await_start_signal=False):
        # target is a folder
        super().__init__()
        self.target=target
        self.delay = 1
        if not await_start_signal:
            self.start()

    def copySidecarFiles(self, source_file, destination_path):
        """Copies all existing sidecar files of source_file into destination_path.
           Skips any sidecar that already exists there."""
        sidecar_files = fileGetSidecarFiles(source_file)
        copied_sidecars = []
        for source_id, sidecar_file_names in sidecar_files.items():
            for sidecar_file_name in sidecar_file_names:
                destination_file = destination_path + '/' + os.path.basename(sidecar_file_name)
                if not os.path.isfile(destination_file):
                    copied_sidecars.append(shutil.copy2(sidecar_file_name, destination_path).replace('\\', '/'))
        return copied_sidecars
    def getRawNonRawByBaseName(self,files):
        # Returns lists of raw-files and list of non-raw files per basename
        raw_files = {}
        non_raw_files = {}
        for file in files:
            split_file_name = splitFileName(file)
            base_name = split_file_name[1]
            file_type = split_file_name[2].lower()
            if file_type in Settings.get('raw_file_types'):
                if raw_files.get(base_name) is None:
                    raw_files[base_name]=[file]
                else:
                    raw_files[base_name].append(file)
            elif file_type in Settings.get('file_types'):
                if non_raw_files.get(base_name) is None:
                    non_raw_files[base_name]=[file]
                else:
                    non_raw_files[base_name].append(file)
        return raw_files, non_raw_files


    def start(self):
        if not os.path.isdir(self.target):  # Only works for one single dir as target
            return

        # Create originals folder if it does not exist
        originals_path = self.target + '/' + Texts.get('originals_folder_name')
        os.makedirs(originals_path,exist_ok=True)  #Create originals folder if it is missing

        # Get files from originals folder
        file_name_pattern = ["*." + filetype for filetype in Settings.get('file_types')]
        original_files = getFileList(originals_path,pattern=file_name_pattern)  #Image files already in originals folder
        original_raw_files, original_non_raw_files = self.getRawNonRawByBaseName(original_files)

        # Get files from target-folder
        target_files = getFileList(self.target,pattern=file_name_pattern)  #Image files in target-folder
        target_raw_files, target_non_raw_files = self.getRawNonRawByBaseName(target_files)


        total_count = len(target_raw_files) * 2 + len(target_non_raw_files)
        self.progress_init_signal.emit(total_count)
        count = 0

        # Copy raw-files from target to originals, if missing in originals
        copied_files = {}
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_raw_file = target_raw_files.get(base_name)[0]
                original_raw_file = shutil.copy2(target_raw_file, originals_path).replace('\\', '/')
                copied_files[target_raw_file] = original_raw_file
                original_raw_files[base_name]=[original_raw_file]    # Keep track that the original now exists
                self.copySidecarFiles(target_raw_file, originals_path)
        #
        # Copy non-raw files from target to originals, if missing in originals both as non-raw and raw files
        for base_name in target_non_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None and original_non_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_non_raw_file = target_non_raw_files.get(base_name)[0]
                original_non_raw_file = shutil.copy2(target_non_raw_file, originals_path).replace('\\', '/')
                copied_files[target_non_raw_file] = original_non_raw_file
                original_non_raw_files[base_name]=[original_non_raw_file]    # Keep track that the original now exists
                self.copySidecarFiles(target_non_raw_file, originals_path)

        # Stack all files for reading
        for from_file, to_file in reversed(copied_files.items()):
            if FileMetadata.getInstance(from_file).getStatus() == 'PENDING_READ':
                Stack.getInstance('metadata.read').push(from_file)
            if FileMetadata.getInstance(to_file).getStatus() == 'PENDING_READ':
                Stack.getInstance('metadata.read').push(to_file)

        # Write all tags to the created originals (To update from write queue)
        for from_file, to_file in copied_files.items():
            from_file_metadata = FileMetadata.getInstance(from_file)
            while from_file_metadata.getStatus() != '':
                time.sleep(self.delay)
            to_file_metadata = FileMetadata.getInstance(to_file)
            while to_file_metadata.getStatus() != '':
                time.sleep(self.delay)
            from_file_logical_tag_values=from_file_metadata.getLogicalTagValues(filter_writable_only=True)
            to_file_metadata.setLogicalTagValues(from_file_logical_tag_values)

        # Delete originals from target-folder if non-original exists in target folder
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if target_non_raw_files.get(base_name) is not None:
                for file in target_raw_files.get(base_name):
                    sidecar_files = fileGetSidecarFiles(file)
                    for source_id, sidecar_file_names in sidecar_files.items():
                        for sidecar_file_name in sidecar_file_names:
                            os.remove(sidecar_file_name)
                    os.remove(file)

        self.done_signal.emit()