import copy
import os

from PyQt6.QtCore import QObject

from controller.events.emitters.files_rename_done_emitter import FileRenameDoneEmitter
from services.file_services.file_split_name import splitFileName


class FileRenameError(Exception):
    pass


class FileRenamer(QObject):
    __instance = None
    done_signal = FileRenameDoneEmitter.getInstance()

    def __init__(self, files=[]):
        super().__init__()
        self.files = copy.deepcopy(files)

    @staticmethod
    def getInstance(files=[]):
        if FileRenamer.__instance is None:
            FileRenamer.__instance=FileRenamer(files)
        elif files!=[]:
            FileRenamer.__instance.files = copy.deepcopy(files)
        return FileRenamer.__instance

    def _generate_tmp_name(self,old_name):
        parts = splitFileName(old_name)
        base_tmp = parts[0] + parts[1] + '_tmp.' + parts[2]

        if not os.path.isfile(base_tmp):
            return base_tmp

        index = 1
        while True:
            candidate = parts[0] + parts[1] + f'_tmp({index:02d}).' + parts[2]
            if not os.path.isfile(candidate):
                return candidate
            index += 1

    def start(self):
        index = 0
        renamed_files = []

        # Check that entries all have filenames and files exist
        for index, file in enumerate(self.files, start=1):
            old_name = file.get('old_name')
            new_name = file.get('new_name')

            # Old filename missing?
            if old_name is None or old_name == '':
                if new_name is None or new_name == '':
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name and new_name are both missing in files-entry number '+str(index))
                else:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name is missing in files-entry number ' + str(index))

            # New filename missing
            if new_name is None or new_name == '':
                self.__roll_back(renamed_files)
                raise FileRenameError('new_name is missing in files-entry number ' + str(index))

            # Old file missing on disk
            if not os.path.isfile(file.get('old_name')):
                self.__roll_back(renamed_files)
                raise FileRenameError('File not found: ' + file.get('old_name'))

        # Remove entries where old and new filename are the same
        self.files = [f for f in self.files if f.get('old_name') != f.get('new_name')]

        # Handle collisions by creating tmp-files if needed
        flag_create_tmp_files=False
        for file in self.files:
            new_name = file.get('new_name')

            if os.path.isfile(new_name)==True:
                flag_create_tmp_files=True
                break

        if flag_create_tmp_files==True:
            for file in self.files:
                old_name = file.get('old_name')

                tmp_name = self._generate_tmp_name(old_name)
                file['tmp_name'] = tmp_name
                try:
                    os.rename(old_name, tmp_name)
                    renamed_files.append({'old_name': old_name, 'new_name': tmp_name})
                except Exception as e:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('error renaming ' + old_name + ' to ' + tmp_name)

        # Rename files
        for file in self.files:
            old_name = file.get('old_name')
            new_name = file.get('new_name')
            tmp_name = file.get('tmp_name')
            if tmp_name!=None:
                try:
                    os.rename(tmp_name, new_name)
                    renamed_files.append({'old_name': tmp_name, 'new_name': new_name})
                except Exception as e:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('Error renaming ' + tmp_name + ' to ' + new_name + ':\n'+str(e))
            else:
                try:
                    os.rename(old_name, new_name)
                    renamed_files.append({'old_name': old_name, 'new_name': new_name})
                except Exception as e:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('Error renaming ' + old_name + ' to ' + new_name + ':\n'+str(e))

        # Send signal for renaming done
        self.done_signal.emit(renamed_files)

    def __roll_back(self,files):
        for file in reversed(files):
            old_name = file.get('old_name')
            new_name = file.get('new_name')
            os.rename(new_name, old_name)