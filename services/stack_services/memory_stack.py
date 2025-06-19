# An instance of the JsonStackFile can hold a stack with sets of json-data. The stack-data is stored in the self.stack list,
# and mirrored in a file (if a filepath is provided).
# The file-mirror is used to restore stack at start of application (after crash or application-closure)
import json
import os
import threading
import time

from PyQt6.QtCore import QObject, pyqtSignal

class MemoryStack(QObject):
    instances = {}

    stack_size_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.stack = []  # Stack is empty list
        self.stack_size = 0
        self.stack_size = 0
        self.instance_just_created = True

    def push(self, data):
        self.stack.append(data)  # Append data in memory
        self.stack_size = len(self.stack)
        self.stack_size_changed.emit(self.stack_size)

    def pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            return None

    def quitPrepare(self):
        pass

    def change_stack(self,stack_changes=[]):  # stack_changes = [{'find': {<find_key1>: <find_key1_value>, <find_key2>: <find_key2_value>...}, 'change':{<change_key1>: <change_key1_value>, <change_key2>: <change_key2_value>...}}]
        if stack_changes == []:
            return

        for stack_change in stack_changes:
            find = stack_change.get('find')
            change = stack_change.get('change')
            for index, stack_entry in enumerate(self.stack):
                passed_find_filter = True
                for find_key, find_value in find.items():
                    dummy = stack_entry.get(find_key)
                    print(dummy)
                    print(find_value)
                    if not stack_entry.get(find_key) == find_value:
                        passed_find_filter = False
                        break
                if passed_find_filter:
                    for change_key, change_value in change.items():
                        old_value = self.stack[index].get(change_key)
                        if old_value is not None and old_value != change_value:
                            self.stack[index][change_key] = change_value

