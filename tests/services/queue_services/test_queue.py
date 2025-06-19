import sys

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication

from services.queue_services.queue import Queue


class QueueProcessor(QObject):
    def __init__(self):
        super().__init__()

    @staticmethod
    def processQueueEntry(queue_entry):
        print(queue_entry)


queue = Queue.getInstance('test_queue', QueueProcessor,'processQueueEntry','C:\\Users\\jorge\\Documents\\midlertidig\\queue.json')
queue.start()
queue.enqueue({'første': 'Noget tekst', 'anden': 'Noget andet tekst'})
queue.enqueue({'tredie': 'Atter noget tekst', 'anden': 'Atter noget andet tekst'})


app = QApplication(sys.argv)
app.exec()