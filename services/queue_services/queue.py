import time

from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication, QThread
from services.queue_services.json_queue_file import JsonQueueFile
from services.queue_services.memory_queue import MemoryQueue

class Queue(QObject):
    queue_size_changed = pyqtSignal(int)
    instance_index = {}
    get_instance_active = False

    def __init__(self,id,processor_class,processor_method, queue_file_path=None):
        super().__init__()

        # Check that getInstance was called
        if not Queue.get_instance_active:
            raise Exception('Please use getInstance method')

        # Set data for Queue
        Queue.instance_index[id]=self
        self.id = id
        self.queue_file_path = queue_file_path
        self.processor_class = processor_class
        self.processor_method = processor_method
        if self.queue_file_path is not None:
            self.queue_manager = JsonQueueFile.getInstance(self.queue_file_path)
        else:
            self.queue_manager = MemoryQueue()
        self.queue_worker_running = False
        self.queue_worker_processing = False
        self.queue_worker_paused = False

    @staticmethod
    def getInstance(id,processor_class=None,processor_method=None,queue_file_path=None):
        queue = Queue.instance_index.get(id)
        if queue is None:
            Queue.get_instance_active = True
            queue = Queue(id,processor_class, processor_method,queue_file_path)
            Queue.get_instance_active = False
        return queue

    def enqueue(self,data):
        self.queue_manager.enqueue(data)

    def start(self):
        if not self.queue_worker_running:
            self.queue_worker_running = True
            self.queue_worker = QueueWorker(queue=self)
            self.queue_worker.waiting.connect(self.onWorkerWaiting)       # Queue-worker is waiting for something to process
            self.queue_worker.processing.connect(self.onWorkerProcessing) # Queue is being processed. This can be used to show running-indicator in app.
            self.queue_worker.queue_size_changed.connect(self.onQueueSizeChanged)
            self.queue_worker.start()
            if QCoreApplication.instance() is not None:
                QCoreApplication.instance().aboutToQuit.connect(self.queue_worker.onAboutToQuit)

    def stop(self):
        if self.queue_worker_running:
            self.queue_worker.terminate()
            self.queue_worker_running = False
            self.queue_worker_processing = False

    def pause(self):
        if self.queue_worker_paused:
            return
        self.queue_worker_paused = True

    def resume(self):
        if not self.queue_worker_paused:
            return
        self.queue_worker_paused = False

    def entries(self):
        return self.queue_manager.entries()

    def onWorkerWaiting(self):
        self.queue_worker_running = True
        self.queue_worker_processing = False

    def onWorkerProcessing(self):
        self.queue_worker_running = True
        self.queue_worker_processing = True

    def onQueueSizeChanged(self,queue_size):
        self.queue_size = queue_size
        self.queue_size_changed.emit(self.queue_size)


class QueueWorker(QThread):
    waiting = pyqtSignal()
    processing = pyqtSignal()
    queue_size_changed = pyqtSignal(int)   # Queue size: e.g. 1kb

    def __init__(self,queue,delay=5):
        super().__init__()
        self.delay = delay
        self.paused = False
        self.queue = queue

    def run(self):
        self.waiting.emit()
        self.queue.queue_manager.queue_size_changed.connect(self.onQueueSizeChanged)
        self.queue_size = self.queue.queue_manager.queue_size
        self.queue_size_changed.emit(self.queue_size)
        while True:
            if self.queue.queue_worker_paused:
                time.sleep(self.delay)
            else:
                queue_entry = self.queue.queue_manager.dequeue()
                if queue_entry:
                    self.processing.emit()
                    getattr(self.queue.processor_class, self.queue.processor_method)(queue_entry)  #Calls processing-method in processing class, if it is there, else raises an exception
                    self.queue.queue_manager.dequeue_commit()
                else:
                    self.waiting.emit()
                    time.sleep(self.delay)

    def onAboutToQuit(self):
        self.queue.queue_manager.quitPrepare()
        self.quit()

    def onQueueSizeChanged(self,queue_size):
        self.queue_size_changed.emit(queue_size)

