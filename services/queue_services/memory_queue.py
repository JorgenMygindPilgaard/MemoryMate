# An instance of the JsonQueueFile can hold a queue with sets of json-data. The queue-data is stored in the self.queue list,
# and mirrored in a file (if a filepath is provided).
# The file-mirror is used to restore queue at start of application (after crash or application-closure)
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

class MemoryQueue(QObject):
    queue_size_changed = pyqtSignal(int)  # {<queue_file_name>: <count_of_entries_in_queue>}

    def __init__(self):
        super().__init__()
        self.queue_mutex = QMutex()
        self.queue = []  # Queue is empty list
        self.queue_size = 0
        self.queue_size_changed.emit(self.queue_size)     # Emit queue-size 0 at start
        self.index = 0  # Current index to be processed

    def enqueue(self, data):
        with QMutexLocker(self.queue_mutex):
            self.queue.append(data)  # Append data in memory
            self.queue_size +=1
            self.queue_size_changed.emit(self.queue_size)

    def dequeue(self):
        with QMutexLocker(self.queue_mutex):
            if self.queue_size > 0:
                data = self.queue[0]
            else:
                data = None
            return data

    def dequeue_commit(self):
        with QMutexLocker(self.queue_mutex):
            self.queue = self.queue[1:]
            self.queue_size = len(self.queue)
            self.queue_size_changed.emit(self.queue_size)

    def quitPrepare(self):
        pass

    def change_queue(self,queue_changes=[]):  # queue_changes = [{'find': {<find_key1>: <find_key1_value>, <find_key2>: <find_key2_value>...}, 'change':{<change_key1>: <change_key1_value>, <change_key2>: <change_key2_value>...}}]
        if queue_changes == []:
            return

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

    def entries(self):
        with QMutexLocker(self.queue_mutex):
            return self.queue

