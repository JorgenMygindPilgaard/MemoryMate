# import os
#
# from PyQt6.QtCore import Qt, QStringListModel
# from PyQt6.QtGui import QAction, QIcon
# from PyQt6.QtWidgets import QCompleter
#
#
# class AutoCompleteList(QCompleter):
#     get_instance_active = False  # To be able to give error when instantiated directly, outside getInstance
#     instance_index = {}
#
#     def __init__(self, list_name):
#         # Check that instantiation is called from getInstance-method
#         if not AutoCompleteList.get_instance_active:
#             raise Exception('Please use getInstance method')
#         super().__init__()
#         self.list_name = list_name
#         self.file_name = ""
#         self.list = []
#         self.completer = QCompleter()
#         self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
#         self.model = QStringListModel()
#         self.setModel(self.model)
#
#     @staticmethod
#     def getInstance(list_name):
#         auto_complete_list = AutoCompleteList.instance_index.get(list_name)
#         if auto_complete_list is None:
#             AutoCompleteList.get_instance_active = True
#             auto_complete_list = AutoCompleteList(list_name)
#             AutoCompleteList.get_instance_active = False
#             AutoCompleteList.instance_index[list_name] = auto_complete_list  # Add new instance to instance-index
#         return auto_complete_list
#
#     def pathFromIndex(self, index):
#         path = super().pathFromIndex(index)
#         # Add a delete action to the popup menu
#         action = QAction(QIcon(":/delete.png"), "Delete", self.popup())
#         action.setData(path)
#         action.triggered.connect(self.onDeleteActionTriggered)
#         self.popup().addAction(action)
#         return path
#
#     def onDeleteActionTriggered(self):
#         # Get the data associated with the action (i.e. the completion path)
#         path = self.sender().data()
#         # Remove the path from the model
#         model = self.model()
#         model.removeRow(model.stringList().indexOf(path))
#         # Rebuild the completer
#         self.setModel(model)
#
#     def collectItem(self,list_item):
#         if not list_item in self.list:
#             self.list.append(list_item)
#             self.model.setStringList(self.list)
#             if self.file_name != "":
#                 self.__appendFile([list_item])
#
#     def collectItems(self,list_items=[]):
#         appended_list_items = []
#         for list_item in list_items:
#             if not list_item in self.list:
#                 self.list.append(list_item)
#                 appended_list_items.append(list_item)
#
#         if appended_list_items != []:
#             self.model.setStringList(self.list)
#             if self.file_name != None:
#                 self.__appendFile(appended_list_items)
#
#     def setFileName(self,file_name):          # Optional to use. If set, file will be loaded at start, and kept updated
#         if file_name != self.file_name:
#             self.file_name = file_name
#             self.__prepareFile()      # Check that file exist. Create it, if no
#
#     def __prepareFile(self):
#         if os.path.isfile(self.file_name):             #File exist. Merge current list with file list.
#             list_in_memory = self.list
#             self.list = self.__loadFromFile()
#             self.collectItems(list_in_memory)
#             self.model.setStringList(self.list)
#         else:                                          #File does not exist: Create it, and save list to it
#             with open(self.file_name, "w") as outfile:
#                 for list_item in self.list:
#                     outfile.write(list_item + '\n')
#
#     def __appendFile(self,list_items):
#         with open(self.file_name, 'a') as outfile:
#             for list_item in list_items:
#                 outfile.write(list_item + '\n')
#
#     def __loadFromFile(self):
#         list = []
#         with open(self.file_name, 'r') as infile:
#             for list_item in infile:
#                 list.append(list_item.strip())
#         return list

import os

from PyQt6.QtCore import Qt, QStringListModel, QEvent
from PyQt6.QtWidgets import QCompleter


class AutoCompleteList(QCompleter):
    get_instance_active = False
    instance_index = {}

    def __init__(self, list_name):
        if not AutoCompleteList.get_instance_active:
            raise Exception('Please use getInstance method')
        super().__init__()
        self.list_name = list_name
        self.file_name = ""
        self.list = []
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.model = QStringListModel()
        self.setModel(self.model)

        # Let the popup's view notify us of key presses
        self.popup().installEventFilter(self)

    @staticmethod
    def getInstance(list_name):
        auto_complete_list = AutoCompleteList.instance_index.get(list_name)
        if auto_complete_list is None:
            AutoCompleteList.get_instance_active = True
            auto_complete_list = AutoCompleteList(list_name)
            AutoCompleteList.get_instance_active = False
            AutoCompleteList.instance_index[list_name] = auto_complete_list
        return auto_complete_list

    def eventFilter(self, obj, event):
        # obj is the popup's QListView
        if obj is self.popup() and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                index = self.popup().currentIndex()
                if index.isValid():
                    item = index.data()
                    self.removeItem(item)
                    return True  # swallow the key so it doesn't do anything else
        return super().eventFilter(obj, event)

    def removeItem(self, item):
        if item in self.list:
            self.list.remove(item)
            self.model.setStringList(self.list)
            if self.file_name:
                self.__saveFile()

    def collectItem(self, list_item):
        if not list_item in self.list:
            self.list.append(list_item)
            self.model.setStringList(self.list)
            if self.file_name != "":
                self.__appendFile([list_item])

    def collectItems(self, list_items=[]):
        appended_list_items = []
        for list_item in list_items:
            if not list_item in self.list:
                self.list.append(list_item)
                appended_list_items.append(list_item)

        if appended_list_items != []:
            self.model.setStringList(self.list)
            if self.file_name != None:
                self.__appendFile(appended_list_items)

    def setFileName(self, file_name):
        if file_name != self.file_name:
            self.file_name = file_name
            self.__prepareFile()

    def __prepareFile(self):
        if os.path.isfile(self.file_name):
            list_in_memory = self.list
            self.list = self.__loadFromFile()
            self.collectItems(list_in_memory)
            self.model.setStringList(self.list)
        else:
            with open(self.file_name, "w") as outfile:
                for list_item in self.list:
                    outfile.write(list_item + '\n')

    def __appendFile(self, list_items):
        with open(self.file_name, 'a') as outfile:
            for list_item in list_items:
                outfile.write(list_item + '\n')

    def __saveFile(self):
        # Full rewrite needed since removal can't just append
        with open(self.file_name, "w") as outfile:
            for list_item in self.list:
                outfile.write(list_item + '\n')

    def __loadFromFile(self):
        result = []
        with open(self.file_name, 'r') as infile:
            for list_item in infile:
                result.append(list_item.strip())
        return result