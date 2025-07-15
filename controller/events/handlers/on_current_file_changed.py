from PyQt6.QtCore import QObject

from configuration.settings import Settings
from services.file_services.file_get_list import getFileList
from services.file_services.file_split_name import splitFileName
from services.stack_services.stack import Stack
from view.windows.file_panel import FilePanel
from services.metadata_services.metadata import FileMetadata
from view.ui_components.file_preview import FilePreview


class StackCoordinator(QObject):    # Remembers what has been read already
    file_pattern = [f"*.{file_type}" for file_type in Settings.get('file_type_tags')]
    read_folders_done = []
    instance = None

    @staticmethod
    def getInstance():
        if StackCoordinator.instance is None:
            StackCoordinator.instance = StackCoordinator()
        return StackCoordinator.instance

    def doStacking(self,new_file_name):
        # Stack all other files in folder for reading ahead

        split_file_name = splitFileName(new_file_name)  # ["c:\pictures\", "my_picture", "jpg"]
        path = split_file_name[0]  # "c:\pictures\"
        metadata_read_stack = Stack.getInstance('metadata.read')
        preview_read_stack = Stack.getInstance('preview.read')
        if not path in self.read_folders_done:
            self.read_folders_done.append(path)
            file_names = getFileList(path, False, pattern=self.file_pattern)
            for file_name in file_names:
                if not file_name == new_file_name:   # Wait stacking new filename as last one, to process first
                    metadata_read_stack.push(file_name)
                    preview_read_stack.push(file_name)
        metadata_read_stack.push(new_file_name)
        entries = metadata_read_stack.entries()
        preview_read_stack.push(new_file_name)

def onCurrentFileChanged(new_file_name):
    if new_file_name != FilePanel.file_name:
        FilePanel.saveMetadata()  # Saves metadata for file currently in file-panel (if any)
        FileMetadata.getInstance(new_file_name).readLogicalTagValues()
        FilePreview.getInstance(new_file_name).readImage()
        FilePanel.getInstance(new_file_name)  # Puts new file in file-panel
        StackCoordinator.getInstance().doStacking(new_file_name)
