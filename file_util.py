import copy
import os
import json
from fnmatch import fnmatch
from PyQt6.QtCore import QObject,pyqtSignal
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
    dummy = 'mmmmmmm'
    if '.' in file_name:
        dir_end_pos = file_name.rfind('/')
        if dir_end_pos != -1:
            directory = file_name[:dir_end_pos+1]
            full_filename = file_name[dir_end_pos + 1:]
        else:
            directory = ''
            full_filename = file_name

        ext_start_pos = full_filename.rfind('.')
        filename = full_filename[:ext_start_pos]
        file_extension = full_filename[ext_start_pos+1:]
        return [directory, filename, file_extension]
    else:
        if file_name != '':
            if file_name.endswith('/'):
                directory = file_name
            else:
                directory = file_name + '/'
        else:
            directory = ''
        return [directory, '', '']

class FileNameChangedEmitter(QObject):
    instance = None
    change_signal = pyqtSignal(str, str, bool)  # old filename, new file name, update_original_filename_tag

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileNameChangedEmitter.instance == None:
            FileNameChangedEmitter.instance = FileNameChangedEmitter()
        return FileNameChangedEmitter.instance
    def emit(self, old_file_name, new_file_name, update_original_filename_tag):
        self.change_signal.emit(old_file_name, new_file_name, update_original_filename_tag)

class FileRenamer(QObject):
    __instance = None
    change_signal = FileNameChangedEmitter.getInstance()  # Old filename, New filename

    def __init__(self, files=[]):
        super().__init__()
        self.files = copy.deepcopy(files)

    @staticmethod
    def getInstance(files=[]):
        if FileRenamer.__instance==None:
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

            if old_name == None or old_name == '':
                if new_name == None or new_name == '':
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name and new_name are both missing in files-entry number '+str(index))
                else:
                    self.__roll_back(renamed_files)
                    raise FileRenameError('old_name is missing in files-entry number ' + str(index))
            if new_name == None or new_name == '':
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

        # Send signal for renaming to tmp-filename
        if flag_create_tmp_files==True:
            for file in self.files:
                self.change_signal.emit(file.get('old_name'), file.get('tmp_name'),False)
        for file in self.files:
            if flag_create_tmp_files==True:
                self.change_signal.emit(file.get('tmp_name'), file.get('new_name'),True)
            else:
                self.change_signal.emit(file.get('old_name'), file.get('new_name'),True)


    def __roll_back(self,files):
        for file in files.reverse():
            old_name = file.get('old_name')
            new_name = file.get('new_name')
            os.rename(new_name, old_name)


# An instance of the JsonQueue can hold a queue with sets of json-data. The queue-data is stored in the self.queue list,
# and mirrored in a file (if a filepath is provided).
# The file-mirror is used to restore queue at start of application (after crash or application-closure)
class JsonQueue(QObject):
    instances={}
    queue_size_changed = pyqtSignal(dict)      # {<queue_file_name>: <count_of_entries_in_queue>}
    def __init__(self, file_path):
        super().__init__()
        JsonQueue.instances[file_path] = self
        self.file_path = file_path
        self.lock = threading.Lock()
        self.queue = []             #Queue is empty list
        self.queue_size = 0
        self.index = 0              #Current index to be processed
        self.committed_index = -1   #Last index for which processing has ended
        self.last_file_write_time = time.time()-10
        self.queue_being_changed=False
        self.instance_just_created = True
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
            self.queue_size = len(self.queue)

    @staticmethod
    def getInstance(file_path):
        json_queue=JsonQueue.instances.get(file_path.replace('/','\\'))
        if not json_queue:
            json_queue=JsonQueue(file_path.replace('/','\\'))
        return json_queue

    def enqueue(self, data):
        self.last_file_write_time = time.time()
        with self.lock:
            with open(self.file_path, 'a') as file:
                self.queue.append(data)                                          # Append data in memory
                file.write(json.dumps(data).replace('\n','<newline>') + '\n')    # Append data in file instantly (prevent data-loss)
                self.queue_size = len(self.queue)
        self.queue_size_changed.emit({self.file_path: self.queue_size})

    def dequeue(self):
        if self.instance_just_created:
            self.queue_size_changed.emit({self.file_path: len(self.queue)})   # Send size when processing starts
            self.instance_just_created = False
        if len(self.queue) > self.index:
            data = self.queue[self.index]
            self.index += 1
        else:
            data = None
        self.queue_size = len(self.queue)


        return data

    def change_queue(self, find={}, change={}):
        if change == {}:
            return

        while self.queue_being_changed:   # Wait till queue is ready for change
            pass

        self.queue_being_changed = True
        for index, queue_entry in enumerate(self.queue):
            passed_find_filter = True
            for find_key, find_value in find.items():
                if not queue_entry.get(find_key) == find_value:
                    passed_find_filter = False
                    break
            if passed_find_filter:
                for change_key, change_value in change.items():
                    if self.queue[index].get(change_key):
                        self.queue[index][change_key] = change_value
        self.queue_being_changed = False
    def dequeue_commit(self):
        self.committed_index = self.index - 1

    def dequeue_from_file(self, delay=5):
        if time.time() - self.last_file_write_time < delay:
            return                       # Prevent storming file with updates
        if len(self.queue) == 0:   # Queue is already emptied. That means that file is also already empty
            return
        if self.committed_index < 0:    # Nothing to remove from file
            return
        if self.queue_being_changed:
            return

        lock_acquired = self.lock.acquire(blocking=True, timeout=0)
        if not lock_acquired:
            return

        self.queue_being_changed = True
        lines = [json.dumps(d).replace('\n','<newline>') + '\n' for d in self.queue[self.committed_index+1:]]
        with open(self.file_path, 'w') as file:
            file.writelines(lines)
            self.queue = self.queue[self.committed_index+1:]
            self.index = 0
            self.committed_index = -1
            self.last_file_write_time = time.time()
        self.queue_being_changed = False
        self.lock.release()
        self.queue_size = len(self.queue)
        self.queue_size_changed.emit({self.file_path: self.queue_size})


