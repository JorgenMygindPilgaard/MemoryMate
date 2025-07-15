import time
from collections import OrderedDict

from PyQt6.QtCore import QObject, pyqtSignal

from configuration.settings import Settings
from services.file_services.file_rename import FileRenamer
from services.file_services.file_get_list import getFileList
from services.metadata_services.exiftool_wrapper import ExifTool
from services.metadata_services.metadata import FileMetadata
from services.stack_services.stack import Stack
from services.queue_services.queue import Queue


class StandardizeFilenames(QObject):
    # The purpose of this class is to rename files systematically. The naming pattern in the files will be
    # <prefix><number><suffix>.<ext>. Example: 2023-F001-001.jpg (prefix="2023-F001-', number='nnn',suffix='').
    # If folders or subfolders holds files with same name, but different extension (e.g. IMG_0021557.JPG and corresponding
    # raw-file, IMG_0021557.CR3) they will end up with same name.
    # Files will be numbered according to date/time where taken with oldest having lowest number. If files misses date
    # and a file with same name but other extension has a date, it is assumed that both files were taken on the same date
    # when sorting.
    # If files are missing dates all together, they are "squeezed" in to the sequence with date by comparing file-names.
    # At the same time as renaming (standardizing) the filenames, the new file-name is written to metadata in logical tag
    # named "original_filename" (...only if the logical tag exists in settings).
    # Some image enhancement tools adds padding in beginning of filename or in end of filename. Settings holds a list of known file_paddings.
    # A file padded with one of the paddings are still considered coming from same source-file during standardization of filenames.
    # Example: IMG_0920.jpg and IMG_0920-Enhanced-NR.jpg will end up being e.t 2024-F005-007.jpg and 2024-F005-007-Enhanced-NR.jpg.
    #          The original filename tag will, however, hold 2024-F005-007 in both cases.

    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,target, prefix='', number_pattern='nnn', suffix='',await_start_signal=False):
        super().__init__()
        self.delay = 1
        self.target=target
        self.prefix=prefix
        self.number_pattern=number_pattern
        self.suffix=suffix
        if not await_start_signal:
            self.start()


    def start(self):
        file_name_pattern=[]
        for filetype in Settings.get('file_types'):
            file_name_pattern.append("*."+filetype)

        self.target_file_names = []
        if isinstance(self.target, list):
            for file_path in self.target:
                self.target_file_names.extend(
                    getFileList(root_folder=file_path, recursive=True, pattern=file_name_pattern))
        else:
            self.target_file_names.extend(
                getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        file_count=len(self.target_file_names)     # What takes time is 1. Read metadata for files, 2. Write original filename to metadata

        # Instanciate file metadata instances for all files
        files = []
        self.progress_init_signal.emit(file_count)
        # Stack all files with meta-data read pending
        for file_name in self.target_file_names:
            if FileMetadata.getInstance(file_name).getStatus() == 'PENDING_READ':
                Stack.getInstance('metadata.read').push(file_name)

        # Read metadata for the files
        for index, file_name in enumerate(reversed(self.target_file_names)):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file_name)
            while file_metadata.getStatus() != '':
                time.sleep(self.delay)
            file_date = file_metadata.getLogicalTagValues().get("date")
            if file_date is None:
                file_date = ''
            files.append({"file_name": file_name, "path": file_metadata.path, "name_alone": file_metadata.name_alone, "name_prefix": file_metadata.name_prefix, "name_postfix": file_metadata.name_postfix, "type": file_metadata.getFileType(), "date": file_date})

        # Try find date on at least one of the files (Raw or jpg) and copy to the other
        sorted_files = sorted(files, key=lambda x: (x['name_alone'], x['date']), reverse=True)       # Sort files in reverse order to get the file with date first
        previous_date = ''
        previous_name_alone = ''
        for file in sorted_files:
            if file.get('date') == '':   # Missing date
                if file.get('name_alone') == previous_name_alone:
                    file['date'] = previous_date
            previous_name_alone = file.get('name_alone')
            previous_date = file.get('date')
        sorted_files = sorted(sorted_files, key=lambda x: (x['name_alone'], x['date']))       # Sort files in order by filename and date



        # Make a final list primarily sorted by date with files without date squezed in where name of file matches sequence
        sorted_files_missing_date = [d for d in sorted_files if d.get('date') == '' or d.get('date') is None]
        sorted_files_missing_date = sorted(sorted_files_missing_date, key=lambda x: x['name_alone'])
        sorted_files_with_date = [d for d in sorted_files if d.get('date') != '' and d.get('date') is not None]
        sorted_files_with_date = sorted(sorted_files_with_date, key=lambda x: (x['date'], x['name_alone']))
        sorted_files = []
        while sorted_files_missing_date != []:
            file_missing_date = sorted_files_missing_date[0]
            if sorted_files_with_date != []:
                file_with_date = sorted_files_with_date[0]
                while file_with_date.get('name_alone') < file_missing_date.get('name_alone'):
                    sorted_files.append(file_with_date)
                    del sorted_files_with_date[0]
                    if sorted_files_with_date == []:
                        break
                    file_with_date = sorted_files_with_date[0]
            sorted_files.append(file_missing_date)
            del sorted_files_missing_date[0]
        sorted_files.extend(sorted_files_with_date)

        # Find unique sorted filenames
        sorted_name_alones = [d['name_alone'] for d in sorted_files]
        sorted_name_alones = list(OrderedDict.fromkeys(sorted_name_alones))
        sorted_old_new_name_alones = []

        # Create a list with old and new filename (filename alone)
        number_width = len(self.number_pattern)
        number = 1
        for name_alone in sorted_name_alones:
            number_string = str(number).zfill(number_width)
            new_name_alone = self.prefix + number_string + self.suffix
            sorted_old_new_name_alones.append({'old_name_alone': name_alone, 'new_name_alone': new_name_alone})
            number += 1

        # Now insert new filename in files-list
        for old_new_name_alone in sorted_old_new_name_alones:
            old_name_alone = old_new_name_alone.get('old_name_alone')
            new_name_alone = old_new_name_alone.get('new_name_alone')
            for file in files:
                if file.get('name_alone') == old_name_alone:
                    new_file_name = file.get('path') + file.get('name_prefix') + new_name_alone + file.get('name_postfix') + '.' + file.get('type')
                    file['new_name_alone'] = new_name_alone
                    file['new_file_name'] = new_file_name

        # Rename files
        files_for_renaming = []
        for file in files:
            file_name = file.get('file_name')
            new_file_name = file.get('new_file_name')
            if new_file_name != file_name:
                files_for_renaming.append({'old_name': file_name, 'new_name': new_file_name})
        if files_for_renaming != []:
            renamer= FileRenamer.getInstance(files_for_renaming)
            try:
                metadata_write_queue = Queue.getInstance('metadata.write')
                ExifTool.closeProcess(process_id='WRITE')  # Close write-process, so that data in queue can be changed safely
                metadata_write_queue.stop()  # Make sure not to collide with update of metadata
                renamer.start()
                metadata_write_queue.start()  # Start Queue-worker again
            except Exception as e:
                self.error_signal.emit(e,False)
                self.done_signal.emit()
                return

        self.done_signal.emit()
