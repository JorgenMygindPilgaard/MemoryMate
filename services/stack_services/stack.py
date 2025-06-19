import time

from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication, QThread
from services.stack_services.memory_stack import MemoryStack


class Stack(QObject):
    stack_size_changed = pyqtSignal(int)
    instance_index = {}
    get_instance_active = False
    def __init__(self,id,processor_class,processor_method):
        super().__init__()

        # Check that getInstance was called
        if not Stack.get_instance_active:
            raise Exception('Please use getInstance method')

        # Set data for Stack
        Stack.instance_index[id]=self
        self.id = id
        self.processor_class = processor_class
        self.processor_method = processor_method
        self.stack_manager = MemoryStack()
        self.stack_worker_running = False
        self.stack_worker_processing = False
        self.stack_worker_paused = False

    @staticmethod
    def getInstance(id,processor_class=None,processor_method=None):
        stack = Stack.instance_index.get(id)
        if stack is None:
            Stack.get_instance_active = True
            stack = Stack(id,processor_class,processor_method)
            Stack.get_instance_active = False
        return stack

    def onWorkerWaiting(self):
        self.stack_worker_running = True
        self.stack_worker_processing = False

    def onWorkerProcessing(self):
        self.stack_worker_running = True
        self.stack_worker_processing = True
    def onStackSizeChanged(self,stack_size):
        self.stack_size = stack_size
        self.stack_size_changed.emit(self.stack_size)

    def push(self,data):
        self.stack_manager.push(data)

    def start(self):
        if not self.stack_worker_running:
            self.stack_worker_running = True
            self.stack_worker = StackWorker(stack=self)
            self.stack_worker.waiting.connect(self.onWorkerWaiting)       # Stack-worker is waiting for something to process
            self.stack_worker.processing.connect(self.onWorkerProcessing) # Stack is being processed. This can be used to show running-indicator in app.
            self.stack_worker.stack_size_changed.connect(self.onStackSizeChanged)
            self.stack_worker.start()
            QCoreApplication.instance().aboutToQuit.connect(self.stack_worker.about_to_quit.emit)

    def stop(self):
        if self.stack_worker_running:
            self.stack_worker.terminate()
            self.stack_worker_running = False
            self.stack_worker_processing = False

    def pause(self):
        if self.stack_worker_paused:
            return
        self.stack_worker_paused = True

    def resume(self):
        if not self.stack_worker_paused:
            return
        self.stack_worker_paused = False

    def entries(self):
        return self.stack_manager.stack


class StackWorker(QThread):
    waiting = pyqtSignal()
    processing = pyqtSignal()
    about_to_quit = pyqtSignal()
    stack_size_changed = pyqtSignal(int)   # Stack size: e.g. 1kb

    def __init__(self,stack,delay=5):
        super().__init__()
        self.delay = delay
        self.paused = False
        self.stack = stack

    def run(self):
        self.waiting.emit()
        self.about_to_quit.connect(self.onAboutToQuit)
        self.stack.stack_manager.stack_size_changed.connect(self.onStackSizeChanged)
        self.stack_size = self.stack.stack_manager.stack_size
        self.stack_size_changed.emit(self.stack_size)
        while True:
            if self.stack.stack_worker_paused:
                time.sleep(self.delay)
            else:
                stack_entry = self.stack.stack_manager.pop()
                if stack_entry:
                    self.processing.emit()
                    getattr(self.stack.processor_class, self.stack.processor_method)(stack_entry)  # Calls processing-method in processing class, if it is there, else raises an exception
                else:
                    self.waiting.emit()
                    time.sleep(self.delay)

    def onAboutToQuit(self):
        self.stack.stack_manager.quitPrepare()
        self.quit()

    def onStackSizeChanged(self,stack_size):
        self.stack_size_changed.emit(stack_size)