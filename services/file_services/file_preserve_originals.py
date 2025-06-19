import os
import shutil

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.settings import Settings
from configuration.language import Texts
from services.file_services.file_split_name import splitFileName
from services.file_services.file_get_list import getFileList


class PreserveOriginals(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,target, await_start_signal=False):
        # target is a folder
        super().__init__()
        self.target=target
        if not await_start_signal:
            self.start()

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
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_raw_file = target_raw_files.get(base_name)[0]
                original_raw_file = shutil.copy2(target_raw_file, originals_path)
                original_raw_files[base_name]=[original_raw_file]    # Keep track that the original now exists

        # Copy non-raw files from target to originals, if missing in originals both as non-raw and raw files
        for base_name in target_non_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None and original_non_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_non_raw_file = target_non_raw_files.get(base_name)[0]
                original_non_raw_file = shutil.copy2(target_non_raw_file, originals_path)
                original_non_raw_files[base_name]=[original_non_raw_file]    # Keep track that the original now exists

        # Delete originals from target-folder if non-original exists in target folder
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if target_non_raw_files.get(base_name) is not None:
                for file in target_raw_files.get(base_name):
                    os.remove(file)

        self.done_signal.emit()