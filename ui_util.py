from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel,  QCompleter, QAction
from PyQt5.QtCore import QThread, QStringListModel, Qt
from PyQt5.QtGui import QIcon
import os

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
            self.worker.progress_init_signal.connect(self.initProgress)
            self.worker.progress_signal.connect(self.updateProgress)
            self.worker.done_signal.connect(self.thread.quit)
            self.worker.done_signal.connect(self.worker.deleteLater)
            self.worker.done_signal.connect(self.close)
            self.thread.started.connect(self.worker.start)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()

    def updateProgress(self, count):
        self.current_count = count
        self.left_count = self.end_count - self.current_count
        self.progress_bar.setValue(self.current_count)
        self.left_count = self.end_count - self.current_count
        self.progress_label.setText(str(self.left_count))

    def initProgress(self, count):
        self.end_count = count
        self.progress_bar.setRange(0, self.end_count)

class AutoCompleteList(QCompleter):
    get_instance_active = False  # To be able to give error when instantiated directly, outside get_instance
    instance_index = {}

    def __init__(self, list_name):
        # Check that instantiation is called from get_instance-method
        if not AutoCompleteList.get_instance_active:
            raise Exception('Please use get_instance method')
        super().__init__()
        self.list_name = list_name
        self.file_name = ""
        self.list = []
#        self.completer = QCompleter()
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.model = QStringListModel()
        self.setModel(self.model)

    @staticmethod
    def getInstance(list_name):
        auto_complete_list = AutoCompleteList.instance_index.get(list_name)
        if auto_complete_list is None:
            AutoCompleteList.get_instance_active = True
            auto_complete_list = AutoCompleteList(list_name)
            AutoCompleteList.get_instance_active = False
            AutoCompleteList.instance_index[list_name] = auto_complete_list  # Add new instance to instance-index
        return auto_complete_list

    # def eventFilter(self, obj, event):
    #     if event.type() == QKeyEvent.KeyPress:
    #         if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
    #             return False
    #     else:
    #         return True

    def pathFromIndex(self, index):
        path = super().pathFromIndex(index)
        # Add a delete action to the popup menu
        action = QAction(QIcon(":/delete.png"), "Delete", self.popup())
        action.setData(path)
        action.triggered.connect(self.onDeleteActionTriggered)
        self.popup().addAction(action)
        return path

    def onDeleteActionTriggered(self):
        # Get the data associated with the action (i.e. the completion path)
        path = self.sender().data()
        # Remove the path from the model
        model = self.model()
        model.removeRow(model.stringList().indexOf(path))
        # Rebuild the completer
        self.setModel(model)

    def collectItem(self,list_item):
        if not list_item in self.list:
            self.list.append(list_item)
            self.model.setStringList(self.list)
            if self.file_name != "":
                self.__appendFile([list_item])

    def collectItems(self,list_items=[]):
        appended_list_items = []
        for list_item in list_items:
            if not list_item in self.list:
                self.list.append(list_item)
                appended_list_items.append(list_item)

        if appended_list_items != []:
            self.model.setStringList(self.list)
            if self.file_name != None:
                self.__appendFile(appended_list_items)

    def setFileName(self,file_name):          # Optional to use. If set, file will be loaded at start, and kept updated
        if file_name != self.file_name:
            self.file_name = file_name
            self.__prepareFile()      # Check that file exist. Create it, if no

    def __prepareFile(self):
        if os.path.isfile(self.file_name):             #File exist. Merge current list with file list.
            list_in_memory = self.list
            self.list = self.__loadFromFile()
            self.collectItems(list_in_memory)
            self.model.setStringList(self.list)
        else:                                          #File does not exist: Create it, and save list to it
            with open(self.file_name, "w") as outfile:
                for list_item in self.list:
                    outfile.write(list_item + '\n')

    def __appendFile(self,list_items):
        with open(self.file_name, 'a') as outfile:
            for list_item in list_items:
                outfile.write(list_item + '\n')

    def __loadFromFile(self):
        list = []
        with open(self.file_name, 'r') as infile:
            for list_item in infile:
                list.append(list_item.strip())
        return list


