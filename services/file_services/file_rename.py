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

    def start(self):
        index = 0
        renamed_files = []

        # Check that entries all have filenames
        for file in self.files:
            old_name = file.get('old_name')
            new_name = file.get('new_name')


            if old_name is None or old_name == '':
                if new_name is None or new_name == '':
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name and new_name are both missing in files-entry number '+str(index))
                else:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name is missing in files-entry number ' + str(index))
            if new_name is None or new_name == '':
                self.__roll_back(renamed_files)
                raise FileRenameError('new_name is missing in files-entry number ' + str(index))

        # Remove entries where old and new filename are the same
        files_tmp = copy.deepcopy(self.files)
        for file in files_tmp:
            if file.get('old_name') == file.get('new_name'):
                self.files.remove(file)

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
                old_name_parts = splitFileName(old_name)

                tmp_name = old_name_parts[0] + old_name_parts[1] + '_tmp.' + old_name_parts[2]
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
        if flag_create_tmp_files:
            old_new_files = [{"old_name": d["old_name"], "new_name": d["tmp_name"]} for d in self.files]
            old_new_files.extend([{"old_name": d["tmp_name"], "new_name": d["new_name"]} for d in self.files])
        else:
            old_new_files = [{"old_name": d["old_name"], "new_name": d["new_name"]} for d in self.files]
        self.done_signal.emit(old_new_files,True)

    def __roll_back(self,files):
        for file in files.reverse():
            old_name = file.get('old_name')
            new_name = file.get('new_name')
            os.rename(new_name, old_name)