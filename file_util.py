import os
import json
from fnmatch import fnmatch
from PyQt5.QtCore import QObject,pyqtSignal
from util import rreplace
import threading
import time

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

def splitFileName(file_name):
    file_type = file_name.split(".")[-1]
    short_file_name = file_name.split("\\")[-1]  # Take last part of string splitted at ""
    short_file_name = short_file_name.split("/")[-1]  # Take last part of string splitted at "/"
    short_file_name_ex_type = rreplace(short_file_name, "." + file_type, "")  # Remove .jpg
    file_path = rreplace(file_name, short_file_name, "")
    return [file_path, short_file_name_ex_type, file_type]

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

# An instance of the JsonQueue can hold a queue with sets of json-data. The queue-data is stored in the self.queue list,
# and mirrored in a file (if a filepath is provided).
# The file-mirror is used to restore queue at start of application (after crash or application-closure)
class JsonQueue:
    instances={}
    def __init__(self, file_path):
        JsonQueue.instances[file_path]=self
        self.file_path = file_path
        self.lock = threading.Lock()
        self.queue = []  #Queue is empty list
        self.last_enqueue_time = time.time()-10

        # Create file, if it is missing
        if not os.path.isfile(file_path):
            with self.lock:
                with open(file_path, 'w'):
                    pass
        else:
            with self.lock:
                with open(file_path, 'r') as file:
                    lines=file.readlines()
                    for line in lines:
                        self.queue.append(json.loads(line))

    @staticmethod
    def getInstance(file_path):
        json_queue=JsonQueue.instances.get(file_path.replace('/','\\'))
        if not json_queue:
            json_queue=JsonQueue(file_path.replace('/','\\'))
        return json_queue

    def enqueue(self, data):
        self.last_enqueue_time = time.time()
        with self.lock:
            with open(self.file_path, 'a') as file:
                self.queue.append(data)                                          # Append data in memory
                file.write(json.dumps(data).replace('\n','<newline>') + '\n')    # Append data in file

    def dequeue(self):
        if time.time() - self.last_enqueue_time < 5:
            data = None                       # Return nothing, if queue has just been written to within the last 5 seconds
        else:
            lock_acquired = self.lock.acquire(blocking=True,timeout=0)
            if not lock_acquired:
                data = None                   # File is locked in other process: Return nothing
            else:
                try:
                    if len(self.queue)>0:
                        data = self.queue[0]
                        del self.queue[0]
                        lines = [json.dumps(d).replace('\n','<newline>') + '\n' for d in self.queue]
                        with open(self.file_path, 'w') as file:
                            file.writelines(lines)
                    else:
                        data = None         # Queue is empty: Return nothing
                finally:
                    self.lock.release()
        return data


