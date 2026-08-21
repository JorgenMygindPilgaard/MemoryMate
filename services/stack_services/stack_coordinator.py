from PyQt6.QtCore import QObject
from configuration.settings import Settings
from services.file_services.file_get_list import getFileList
from services.file_services.file_split_name import splitFileName
from services.stack_services.stack import Stack

class StackCoordinator(QObject):  # Remembers what has been read already
    file_pattern = [f"*.{file_type}" for file_type in Settings.get('file_type_tags')]
    metadata_read_folders_done = []
    preview_read_folders_done = []
    instance = None

    @staticmethod
    def getInstance():
        if StackCoordinator.instance is None:
            StackCoordinator.instance = StackCoordinator()
        return StackCoordinator.instance

    def doStacking(self, file_or_folder, add_to_metadata_read_stack=True, add_to_preview_read_stack=True):
        # Stack all other files in folder for reading ahead

        split_file_name = splitFileName(file_or_folder)  # ["c:\pictures\", "my_picture", "jpg"]
        folder = split_file_name[0]  # "c:\pictures\"

        if add_to_metadata_read_stack and not folder in self.metadata_read_folders_done or add_to_preview_read_stack and not folder in self.preview_read_folders_done:
            file_names = getFileList(folder, False, pattern=self.file_pattern)
            if file_or_folder in file_names:
                new_file_index = file_names.index(file_or_folder)
            else:
                new_file_index = -1

        #       Add to metadata read stack
        if add_to_metadata_read_stack:
            if not folder in self.metadata_read_folders_done:
                metadata_read_stack = Stack.getInstance('metadata.read')
                self.metadata_read_folders_done.append(folder)

                # Stack the files leading up to file_or_folder
                for file_name in reversed(file_names[:new_file_index]):
                    if not file_name == file_or_folder:  # Wait stacking new filename as last one, to process first
                        metadata_read_stack.push(file_name)
                #                       preview_read_stack.push(file_name)

                # Stack the files following file_or_folder
                for file_name in reversed(file_names[new_file_index + 1:]):
                    if not file_name == file_or_folder:  # Wait stacking new filename as last one, to process first
                        metadata_read_stack.push(file_name)
            #                       preview_read_stack.push(file_name)

                metadata_read_stack.push(file_or_folder)
                entries = metadata_read_stack.entries()

            #  Add to preview read stack
            if add_to_preview_read_stack:
                if not folder in self.preview_read_folders_done:
                    preview_read_stack = Stack.getInstance('preview.read')
                    self.preview_read_folders_done.append(folder)

                    # Stack the files leading up to file_or_folder
                    for file_name in reversed(file_names[:new_file_index]):
                        if not file_name == file_or_folder:  # Wait stacking new filename as last one, to process first
                            preview_read_stack.push(file_name)

                    # Stack the files following file_or_folder
                    for file_name in reversed(file_names[new_file_index + 1:]):
                        if not file_name == file_or_folder:  # Wait stacking new filename as last one, to process first
                            preview_read_stack.push(file_name)

                    preview_read_stack.push(file_or_folder)
                    entries = preview_read_stack.entries()
