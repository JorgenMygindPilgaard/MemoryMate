import os

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.language import Texts
from configuration.settings import Settings
from services.file_services.file_split_name import splitFileName
from services.file_services.file_get_list import getFileList


class DeleteUnusedOriginals(QObject):
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

    def getFilesByBaseName(self,files):
        # Returns lists of raw-files and list of non-raw files per basename
        base_name_files = {}
        for file in files:
            split_file_name = splitFileName(file)
            base_name = split_file_name[1]
            if base_name_files.get(base_name) is None:
                base_name_files[base_name]=[file]
            else:
                base_name_files[base_name].append(file)
        return base_name_files


    def start(self):
        if not os.path.isdir(self.target):  # Only works for one single dir as target
            return

        # Set path to originals
        originals_path = self.target + '/' + Texts.get('originals_folder_name')
        if not os.path.isdir(originals_path):  # Nothing to do if originals does not exist
            return

        # Get files from originals folder
        file_name_pattern = ["*." + filetype for filetype in Settings.get('file_types')]
        original_files = getFileList(originals_path,pattern=file_name_pattern)  # Image files already in originals folder
        original_base_name_files = self.getFilesByBaseName(original_files)

        # Get files from target-folder
        target_files = getFileList(self.target,pattern=file_name_pattern)  #Image files in target-folder
        target_base_name_files = self.getFilesByBaseName(target_files)

        # Investigate if original basename esist in target(main) folder, and delete original files for base-name if not
        file_count = len(original_base_name_files)
        self.progress_init_signal.emit(file_count)

        for index, base_name in enumerate(original_base_name_files):
            self.progress_signal.emit(index+1)
            if target_base_name_files.get(base_name) is None:   # Original-folder is missing the raw-file
                for file in original_base_name_files[base_name]:
                    os.remove(file)
        self.done_signal.emit()