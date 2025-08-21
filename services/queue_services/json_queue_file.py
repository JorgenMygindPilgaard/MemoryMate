# An instance of the JsonQueueFile can hold a queue with sets of json-data. The queue-data is stored in the self.queue list,
# and mirrored in a file (if a filepath is provided).
# The file-mirror is used to restore queue at start of application (after crash or application-closure)
import json
import os
import time
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

class JsonQueueFile(QObject):
    instances={}

    queue_size_changed = pyqtSignal(int)      # {<queue_file_name>: <count_of_entries_in_queue>}
    def __init__(self, file_path):
        super().__init__()
        JsonQueueFile.instances[file_path] = self
        self.file_path = file_path
        self.queue_mutex = QMutex()
        self.queue = []             #Queue is empty list
        self.queue_size = 0
        self.index = 0              #Current index to be processed
        self.committed_index = -1   #Last index for which processing has ended
        self.last_file_write_time = time.time()-10
        # Create file, if it is missing
        with QMutexLocker(self.queue_mutex):   # Exclusive access to file
            if not os.path.isfile(file_path):
                with open(file_path, 'w'):
                    pass
            else:
                with open(file_path, 'r') as file:
                    lines=file.readlines()
                    for line in lines:
                        self.queue.append(json.loads(line))
            self.queue_size = len(self.queue)
        self.queue_size_changed.emit(self.queue_size)  # Send size when queue-manager has initialized

    @staticmethod
    def getInstance(file_path):
        json_queue=JsonQueueFile.instances.get(file_path.replace('/','\\'))
        if not json_queue:
            json_queue=JsonQueueFile(file_path.replace('/','\\'))
        return json_queue

    def enqueue(self, data,unique_data=None):
        with QMutexLocker(self.queue_mutex):
            if unique_data:   # Return, if a queue-entry with same unique data already exist
                if isinstance(unique_data, dict):
                    match_found = any(all(item.get(key) == value for key, value in unique_data.items()) for item in self.queue)
                else:
                    match_found = unique_data in self.queue
                if match_found:
                    return
            self.queue.append(data)  # Append data in memory
            self.queue_size += 1
            self.queue_size_changed.emit(self.queue_size)
            with open(self.file_path, 'a') as file:
                file.write(json.dumps(data).replace('\n','<newline>') + '\n')    # Append data in file instantly (prevent data-loss)
                self.last_file_write_time = time.time()


    def dequeue(self):
        with QMutexLocker(self.queue_mutex):
            if self.queue_size > 0:
                data = self.queue[self.index]
            else:
                data = None
            self._periodic_update_queue_file()
            return data

    def dequeue_commit(self):
        with QMutexLocker(self.queue_mutex):
            self.index += 1
            self.queue_size = len(self.queue[self.index:])
            self.queue_size_changed.emit(self.queue_size)

    def quitPrepare(self):
        with QMutexLocker(self.queue_mutex):
            self._update_queue_file()

    def change_queue(self, queue_changes=[]):   # queue_changes = [{'find': {<find_key1>: <find_key1_value>, <find_key2>: <find_key2_value>...}, 'change':{<change_key1>: <change_key1_value>, <change_key2>: <change_key2_value>...}}]
        if queue_changes == []:
            return
        queue_changed = False

        with QMutexLocker(self.queue_mutex):
            for queue_change in queue_changes:
                find = queue_change.get('find')
                change = queue_change.get('change')
                for index, queue_entry in enumerate(self.queue):
                    passed_find_filter = True
                    for find_key, find_value in find.items():
                        dummy = queue_entry.get(find_key)
                        print(dummy)
                        print(find_value)
                        if not queue_entry.get(find_key) == find_value:
                            passed_find_filter = False
                            break
                    if passed_find_filter:
                        for change_key, change_value in change.items():
                            old_value = self.queue[index].get(change_key)
                            if old_value is not None and old_value != change_value:
                                self.queue[index][change_key] = change_value
                                queue_changed = True
            if queue_changed:
                self._update_queue_file()  # Update file with changed queue immediately

    def entries(self):
        with QMutexLocker(self.queue_mutex):
            return self.queue[self.index:]

    def size(self):
        with QMutexLocker(self.queue_mutex):
            return self.queue_size

    def _periodic_update_queue_file(self, delay=5):
        delta = time.time() - self.last_file_write_time
        if time.time() - self.last_file_write_time < delay:
            return                       # Prevent storming file with updates
        self._update_queue_file()

    def _update_queue_file(self):
        if len(self.queue) == 0:  # Queue is already emptied. That means that file is also already empty
            return
        self.queue = self.queue[self.index:]
        self.index = 0
        self.queue_size = len(self.queue)
        file_lines = [json.dumps(d).replace('\n','<newline>') + '\n' for d in self.queue]    # Removes also committed changes
        with open(self.file_path, 'w') as file:
            file.writelines(file_lines)
            self.last_file_write_time = time.time()

