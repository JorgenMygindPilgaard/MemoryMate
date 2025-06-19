# #----------------------------------------------------------------------------------------#
# # Read Queue handling
# #----------------------------------------------------------------------------------------#
# import os
#
# from PyQt6.QtCore import QThread
#
# from configuration.settings import Settings
# from controller.events.emitters.file_ready_emitter import FileReadyEmitter
# from services.file_services.file_split_name import splitFileName
# from services.file_services.file_get_list import getFileList
# from services.metadata_services.metadata import FileMetadata
#
#
# class MetadataReadStack(QThread):
#     getInstance_active = False
#     instance = None
#     read_folders_queue = []
#     read_folders_done = []
#     last_appended_file = ''
#     running = False
#     file_pattern = [f"*.{file_type}" for file_type in settings.file_type_tags]
#
#     def __init__(self):
#         super().__init__()
#         # Check that instantiation is called from getInstance-method
#         if not MetadataReadStack.getInstance_active:
#             raise Exception('Please use getInstance method')
#
#     @staticmethod
#     def getInstance():
#         if MetadataReadStack.instance is None:
#             MetadataReadStack.getInstance_active = True
#             MetadataReadStack.instance = MetadataReadStack()
#             MetadataReadStack.getInstance_active = False
#         return MetadataReadStack.instance
#
#     @staticmethod
#     def push(file_name):     #Will extract folder-path from path and queue it if not already queued or processed
#         if file_name:
#             if os.path.isfile(file_name):
#                 MetadataReadStack.last_appended_file = file_name      # Last appended file gets first priority when reading metadata
#             split_file_name = splitFileName(file_name)  # ["c:\pictures\", "my_picture", "jpg"]
#             path = split_file_name[0]                             # "c:\pictures\"
#             if not path in MetadataReadStack.read_folders_done and not path in MetadataReadStack.read_folders_queue:
#                 MetadataReadStack.read_folders_queue.append(path)
#                 if not MetadataReadStack.running:
#                     MetadataReadStack.getInstance().start()
#
#     def run(self):
#         MetadataReadStack.running = True
#         self.__prepareFile(MetadataReadStack.last_appended_file)    # Make sure to process last appended file instantly
#         while MetadataReadStack.read_folders_queue:
#             folder=MetadataReadStack.read_folders_queue.pop()
#             folder_file_names = getFileList(folder, False, MetadataReadStack.file_pattern)
#             for folder_file_name in folder_file_names:
#                 self.__prepareFile(MetadataReadStack.last_appended_file)  # Make sure to process last appended file instantly
#                 self.__prepareFile(folder_file_name)
#         MetadataReadStack.running = False
#
#     def __prepareFile(self,file_name):
#         if file_name == '':
#             return
#         if file_name == MetadataReadStack.last_appended_file:
#             MetadataReadStack.last_appended_file = ''
#         metadata_action_done = FileMetadata.getInstance(file_name).readLogicalTagValues()
#         image_action_done = self.file_preview_class.getInstance(file_name).readImage()
#         if metadata_action_done != 'NOTHING DONE' or image_action_done != 'NOTHING DONE':
#             FileReadyEmitter.getInstance().emit(file_name)
