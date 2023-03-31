import json
from PyQt5.QtWidgets import QCompleter, QAction
from PyQt5.QtCore import  QStringListModel, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeyEvent
import os


# Replace a substring with other substring starting from rear end
def rreplace(source_string,old_string,new_string,replace_count = 1):
    reverse_source_string = source_string[::-1]
    reverse_old_string = old_string[::-1]
    reverse_new_string = new_string[::-1]
    reverse_target_string = reverse_source_string.replace(reverse_old_string,reverse_new_string,replace_count)
    return reverse_target_string[::-1]

# Clear all content of layout and sublayouts and deletes widgets placed in layout
def clearLayout(layout):
    count = layout.count()
    for i in reversed(range(count)):
        item = layout.itemAt(i)
        if item != None:
            if item.widget() != None:
                item.widget().deleteLater()
        layout.removeItem(item)

# Instanciate a signal, e.g self.file_saved = Signal() in emitter class.
# Subscribe to signal in class that subscribes to signal, e.g. my_file.file_saved.subscribe(self,"method_to_react_on_file_saved")
class Signal:
    def __init__(self):
        self.subscribers = {}
    def subscribe(self,subscriber_object, subscriber_method_name=""):
        self.subscribers[subscriber_object]=subscriber_method_name
    def unsubscribe(self,subscriber_object):
        dummy = self.subscribers.pop(subscriber_object, None)   # Removes subscriber if it is there
    def emit(self,parameters=None):
        for subscriber_object in self.subscribers:
            try:
                subscriber_method = getattr(subscriber_object, self.subscribers[subscriber_object])
                if parameters:
                    subscriber_method(parameters)
                else:
                    subscriber_method()
            except AttributeError:
                pass

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
    def get_instance(list_name):
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

    def collect_item(self,list_item):
        if not list_item in self.list:
            self.list.append(list_item)
            self.model.setStringList(self.list)
            if self.file_name != "":
                self.__append_file([list_item])

    def collect_items(self,list_items=[]):
        appended_list_items = []
        for list_item in list_items:
            if not list_item in self.list:
                self.list.append(list_item)
                appended_list_items.append(list_item)

        if appended_list_items != []:
            self.model.setStringList(self.list)
            if self.file_name != None:
                self.__append_file(appended_list_items)

    def set_file_name(self,file_name):          # Optional to use. If set, file will be loaded at start, and kept updated
        if file_name != self.file_name:
            self.file_name = file_name
            self.__prepare_file()      # Check that file exist. Create it, if no

    def __prepare_file(self):
        if os.path.isfile(self.file_name):             #File exist. Merge current list with file list.
            list_in_memory = self.list
            self.list = self.__load_from_file()
            self.collect_items(list_in_memory)
            self.model.setStringList(self.list)
        else:                                          #File does not exist: Create it, and save list to it
            with open(self.file_name, "w") as outfile:
                for list_item in self.list:
                    outfile.write(list_item + '\n')

    def __append_file(self,list_items):
        with open(self.file_name, 'a') as outfile:
            for list_item in list_items:
                outfile.write(list_item + '\n')

    def __load_from_file(self):
        list = []
        with open(self.file_name, 'r') as infile:
            for list_item in infile:
                list.append(list_item.strip())
        return list

























