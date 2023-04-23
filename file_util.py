import os
from fnmatch import fnmatch
from PyQt5.QtCore import QObject,pyqtSignal


class FileRenameError(Exception):
    pass

def getFileList(root_folder='',recursive=False, pattern='*.*'):
    start_folder = root_folder.replace('/','\\')
    if type(pattern) == str:
        file_patterns = [pattern]
    else:
        file_patterns = pattern
        if file_patterns == [] or file_patterns == None:
            file_patterns = ['*.*']

    all_files = []
    if os.path.isfile(start_folder):       # root_folder points to a single file, then return that file alone
        for file_pattern in file_patterns:
            if fnmatch(start_folder, file_pattern):
                all_files.append(start_folder)
                break
    else:
        first_folder = ''
        for dirpath, dirnames, filenames in os.walk(start_folder):
            if first_folder == '':
                first_folder = dirpath
            else:
                if dirpath != first_folder and not recursive:
                    break
            for filename in filenames:
                for file_pattern in file_patterns:
                    if fnmatch(filename,file_pattern):
                        file_path = os.path.join(dirpath, filename)
                        all_files.append(file_path)
                        break
    all_files = [file.replace('\\', '/') for file in all_files]
    return all_files

class FileRenamer(QObject):
    __instance = None
    filename_changed_signal = pyqtSignal(str, str)

    def __init__(self, files=[]):
        super().__init__()
        self.files=files

    @staticmethod
    def getInstance(files=[]):
        if FileRenamer.__instance==None:
            FileRenamer.__instance=FileRenamer(files)
        elif files!=[]:
            FileRenamer.__instance.files = files
        return FileRenamer.__instance

    def start(self):
        def __roll_back(files):
            for file in files:
                old_name = file.get('old_name')
                new_name = file.get('new_name')
                os.rename(new_name, old_name)

        index = 0
        renamed_files = []
        for file in self.files:
            old_name = file.get('old_name')
            new_name = file.get('new_name')
            if old_name == None or old_name == '':
                if new_name == None or new_name == '':
                    __roll_back(renamed_files)
                    raise FileRenameError('old_name and new_name are both missing in files-entry number '+str(index))
                else:
                    __roll_back(renamed_files)
                    raise FileRenameError('old_name is missing in files-entry number ' + str(index))
            if new_name == None or new_name == '':
                __roll_back(renamed_files)
                raise FileRenameError('new_name is missing in files-entry number ' + str(index))
            try:
                os.rename(old_name, new_name)
                renamed_files.append(file)
            except Exception as e:
                __roll_back(renamed_files)
                raise FileRenameError('error renaming ' + old_name + ' to ' + new_name)
        for file in renamed_files:
            self.filename_changed_signal.emit(file.get('old_name'), file.get('new_name'))







