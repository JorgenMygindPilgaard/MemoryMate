import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import QThread
import time
class ProgressBarWidget(QWidget):
    def __init__(self, title='',worker=None):
        super().__init__()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)

        # If worker is supplied, start worker in thread and show progress
        # The worker should emit these signals:
        #    -progress_init_signal(int): Initial signal to set total count for progress
        #    -progress_signal(int): Processd count so far
        #    -done_signal: When worker is done, this signal should be emitted from worker
        #
        # The worker should have a start-method with no parameters. The start-method will
        # be called immediately after after instanciating the progress-bar (this class)
        if worker != None:
            self.worker=worker
            self.show()
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.worker.progress_init_signal.connect(self.init_progress)
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.done_signal.connect(self.thread.quit)
            self.worker.done_signal.connect(self.worker.deleteLater)
            self.worker.done_signal.connect(self.close)
            self.thread.started.connect(self.worker.start)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    def update_progress(self, count):
        self.current_count = count
        self.left_count = self.end_count - self.current_count
        self.progress_bar.setValue(self.current_count)
        self.left_count = self.end_count - self.current_count
        self.progress_label.setText(str(self.left_count))

    def init_progress(self, count):
        self.end_count = count
        self.progress_bar.setRange(0, self.end_count)


