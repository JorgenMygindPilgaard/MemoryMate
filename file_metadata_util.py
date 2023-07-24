import copy
from PyQt5.QtCore import QThread, QCoreApplication

import file_preview_util
from exiftool_wrapper import ExifTool
from PyQt5.QtCore import QObject,pyqtSignal
import settings
import  os
import file_util
from collections import OrderedDict
import time

class FileMetadata(QObject):
    exif_executable = os.path.join(settings.app_data_location, 'exiftool_memory_mate.exe')
    exif_configuration = os.path.join(settings.app_data_location, 'exiftool.cfg')
    if not os.path.isfile(exif_configuration):
        exif_configuration=''
    getInstance_active = False  # To be able to give error when instantiated directly, outside getInstance
    instance_index = {}
    change_signal = pyqtSignal(str)

    def __init__(self, file_name=""):
        super().__init__()
        # Check that instantiation is called from getInstance-method
        if not FileMetadata.getInstance_active:
            raise Exception('Please use getInstance method')
        # Check existence of image_file. Raise exception if not existing

        # Set data for filename
        self.file_name = file_name
        split_file_name = file_util.splitFileName(file_name)  # ["c:\pictures\", "my_picture", "jpg"]
        self.path = split_file_name[0]                        # "c:\pictures\"
        self.name_alone = split_file_name[1]                  # "my_picture"
        self.type = split_file_name[2]                        # "jpg"
        self.is_virgin=False                                  # "Virgin means memory_mate never write metadata to file before. Assume not virgin tll metadata has been read

        # Initialize data for logical tags
        self.__getLogicalTagValues()

    @staticmethod
    def getInstance(file_name):
        file_metadata = FileMetadata.instance_index.get(file_name)
        if file_metadata is None:
            FileMetadata.getInstance_active = True
            file_metadata = FileMetadata(file_name)
            FileMetadata.getInstance_active = False
            FileMetadata.instance_index[file_name] = file_metadata  # Add new instance to instance-index
        return file_metadata

    def __getLogicalTagValues(self):
        #Get names of tags in tags for the filetype from settings
        logical_tags_tags = settings.file_type_tags.get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:    # Filename blank or unknown filetype
            return {}    # logical tag values as empty dictionary "

        tags = []                                           #These are the physical tags
#        for logical_tag in settings.logical_tags:
        for logical_tag in logical_tags_tags:
            tags.extend(logical_tags_tags[logical_tag])

        # Now get values for these tags using exif-tool
        with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
            exif_data = ex.getTags(self.file_name, tags)
        tag_values = {}
        for tag in tags:
            tag_value = exif_data[0].get(tag)
            if tag_value != None and tag_value != "" and tag_value != []:
                if isinstance(tag_value,list):
                    tag_value = list(map(str, tag_value))   # Convert any numbers in list ti string
                else:
                    tag_value = str(tag_value)
                tag_values[tag] = tag_value

        # Finally map tag_values to logical_tag_values
        logical_tag_values = {}
#        for logical_tag in settings.logical_tags:
        logical_tags_missing_value = []
        for logical_tag in logical_tags_tags:
            logical_tag_type = settings.logical_tags.get(logical_tag)
            logical_tag_tags = logical_tags_tags.get(logical_tag)
            if logical_tag_type == 'text_set':
                tag_value = []
            else:
                tag_value = ""
            logical_tag_values[logical_tag] = tag_value  # Set to empty value to begin with"

            logical_tag_value_found = False
            for tag in logical_tag_tags:
                tag_value = tag_values.get(tag)
                if tag_value:
                    logical_tag_value_found = True
                if logical_tag_type != 'text_set' and isinstance(tag_value, list):     #E.g. Author contains multiple entries. Concatenate ti a string then
                    tag_value = ', '.join(tag_value)
                if tag_value != None and tag_value != "":
                    logical_tag_values[logical_tag] = tag_value
                    break
            if not logical_tag_value_found:
                logical_tags_missing_value.append(logical_tag)

        self.saved_logical_tag_values = copy.deepcopy(logical_tag_values)

        # Read fallback_tag (if assigned) into missing logical tags
        if not tag_values.get('XMP:MemoryMateSaveDateTime'):     #Memory Mate never wrote to file before. Get fall-back tag-values for missing logical tags that has fall-back tag assigned
            self.is_virgin=True
            for logical_tag in logical_tags_missing_value:
                fallback_tag = settings.logical_tag_attributes.get(logical_tag).get('fallback_tag')
                if fallback_tag:
                    fallback_tag_value = logical_tag_values.get(fallback_tag)
                    if fallback_tag_value:
                        logical_tag_values[logical_tag] = fallback_tag_value
        self.logical_tag_values = copy.deepcopy(logical_tag_values)

        # Update logical tags in memory from queue-file (Queue originates from previous run)
        json_queue = file_util.JsonQueue.getInstance(settings.queue_file_path)
        for queue_entry in json_queue.queue:
            if queue_entry.get('file') == self.file_name:
                queue_logical_tag_values=queue_entry.get('logical_tag_values')
                if queue_logical_tag_values != None and queue_logical_tag_values != {}:
                    self.setLogicalTagValues(queue_logical_tag_values)


    def __updateReferenceTags(self):
        first = True
        for logical_tag in settings.reference_tag_content:
            logical_tag_value = ''
            for tag_content in settings.reference_tag_content[logical_tag]:
                if tag_content.get('type') =='text_line':
                    tag_content_text = tag_content.get('text')
                    if tag_content_text != None:
                        if not first:
                            logical_tag_value += '\n'
                        logical_tag_value += tag_content_text
                        first = False
                elif tag_content.get('type') == 'tag':
                    ref_logical_tag = tag_content.get('tag_name')
                    if ref_logical_tag:
                        labels = settings.logical_tag_descriptions.get(ref_logical_tag)
                        label = labels.get(settings.language)
                        ref_logical_tag_value = self.logical_tag_values.get(ref_logical_tag)
                        if type(ref_logical_tag_value) == str:
                            if ref_logical_tag_value != "":
                                if not first:
                                    logical_tag_value += '\n'
                                if tag_content.get('tag_label'):
                                    logical_tag_value += label + ': '
                                logical_tag_value += ref_logical_tag_value
                                first = False
                        elif type(ref_logical_tag_value) == list:
                            if ref_logical_tag_value != []:
                                if not first:
                                    logical_tag_value += '\n'
                                if tag_content.get('tag_label'):
                                    logical_tag_value += label + ': '
                                logical_tag_value += ', '.join(ref_logical_tag_value)
            self.logical_tag_values[logical_tag]=logical_tag_value

    def __put_in_queue(self,force_rewrite):
        # Find updated logical tags
        updated_logical_tag_values = {}
        for logical_tag in self.logical_tag_values:
            if self.logical_tag_values[logical_tag] != self.saved_logical_tag_values.get(logical_tag):
                updated_logical_tag_values[logical_tag]=self.logical_tag_values[logical_tag]

        # Put in queue if something to do
        if updated_logical_tag_values != {} or force_rewrite:
            json_queue_file=file_util.JsonQueue.getInstance(settings.queue_file_path)
            json_queue_file.enqueue({'file': self.file_name, 'logical_tag_values': updated_logical_tag_values, 'force_rewrite': force_rewrite})
            QueueHost.get_instance().start_queue_worker()    # Make Queue-host instance start Queue-worker, if it is not running
            self.change_signal.emit(self.file_name)



    def __update_file(self, force_rewrite):
        if self.logical_tag_values != self.saved_logical_tag_values or force_rewrite or self.is_virgin:
            logical_tags_tags = settings.file_type_tags.get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_values:
                #               logical_tag_type = settings.logical_tags.get(logical_tag)
                if self.logical_tag_values[logical_tag] != self.saved_logical_tag_values.get(
                        logical_tag) or force_rewrite or self.is_virgin:  # New value to be saved
                    self.saved_logical_tag_values[logical_tag] = self.logical_tag_values[logical_tag]
                    tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    for tag in tags:
                        tag_value = self.logical_tag_values[logical_tag]
                        tag_values[tag] = tag_value

            if tag_values != {} and tag_values != None:
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values)
                self.change_signal.emit(self.file_name)

    def setLogicalTagValues(self,logical_tag_values,overwrite=True):
        for logical_tag in logical_tag_values:
            old_logical_tag_value = self.logical_tag_values.get(logical_tag)
            if old_logical_tag_value != logical_tag_values[logical_tag]:
                if overwrite:
                    self.logical_tag_values[logical_tag] = logical_tag_values[logical_tag]
                else:
                    if old_logical_tag_value == None:
                        self.logical_tag_values[logical_tag] = logical_tag_values[logical_tag]
                    else:
                        if type(old_logical_tag_value) == str:
                            if old_logical_tag_value == '':
                                self.logical_tag_values[logical_tag] = logical_tag_values[logical_tag]
                        elif type(old_logical_tag_value) == list:
                            if old_logical_tag_value == []:
                                self.logical_tag_values[logical_tag] = logical_tag_values[logical_tag]

    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        split_file_name = file_util.splitFileName(new_file_name)  # ["c:\pictures\", "my_picture", "jpg"]
        self.path = split_file_name[0]                        # "c:\pictures\"
        self.name_alone = split_file_name[1]                  # "my_picture"
        self.type = split_file_name[2]                        # "jpg"
        FileMetadata.instance_index[new_file_name] = self
        del FileMetadata.instance_index[old_file_name]

    def save(self,force_rewrite=False,put_in_queue=True):
        self.__updateReferenceTags()
        if put_in_queue:
            self.__put_in_queue(force_rewrite)
        else:
            self.__update_file(force_rewrite)
        self.is_virgin=False

def renameFileInstances(old_file_name, new_file_name):     # reacts on change filename signal from
    # Rename filename in metadata-instance
    file_metadata = FileMetadata.instance_index.get(old_file_name)
    if file_metadata:
        file_metadata.updateFilename(new_file_name)

    # Rename filename in preview-instance
    file_preview = file_preview_util.FilePreview.instance_index.get(old_file_name)
    if file_preview:
        file_preview.updateFilename(new_file_name)

    # Rename file in queue
    json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
    json_queue_file.change_queue(find={'file': old_file_name}, change={'file': new_file_name})

class StandardizeFilenames(QObject):
    # The purpose of this class is to rename files systematically. The naming pattern in the files will be
    # <prefix><number><suffix>.<ext>. Example: 2023-F001-001.jpg (prefix="2023-F001-', number='nnn',suffix='').
    # If folders or subfolders holds files with same neme, but different extension (e.g. IMG_0021557.JPG and corresponding
    # raw-file, IMG_0021557.CR3) they will end up with same name.
    # Files will be numbered according to date/time where taken with oldest having lowest number. If files misses date
    # and a file with same name but other extension has a date, it is assumed that both files were taken on the same date
    # when sorting.
    # If files are missing dates all together, they are "squeezed" in to the sequence with date by comparing file-names.
    # At the same time as renaming (standardizing) the filenames, the new file-name is written to metadata in logical tag
    # named "original_filename" (...only if the logical tag exists in settings).

    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()

    def __init__(self,target, prefix='', number_pattern='nnn', suffix='',await_start_signal=False):
        super().__init__()
        self.target=target
        self.prefix=prefix
        self.number_pattern=number_pattern
        self.suffix=suffix
        if not await_start_signal:
            self.start()


    def start(self):
        file_name_pattern=[]
        for filetype in settings.file_types:
            file_name_pattern.append(filetype)

        self.target_file_names = []
        if isinstance(self.target, list):
            for file_path in self.target:
                self.target_file_names.extend(file_util.getFileList(root_folder=file_path,recursive=True,pattern=file_name_pattern))
        else:
            self.target_file_names.extend(file_util.getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        file_count=len(self.target_file_names)*2     # What takes time is 1. Read metadata for files, 2. Write original filename to metadata

        #Instanciate file metadata instances for all files
        files = []
        self.progress_init_signal.emit(file_count)
        for index, file_name in enumerate(self.target_file_names):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file_name)
            files.append({"file_name": file_name, "path": file_metadata.path, "name_alone": file_metadata.name_alone, "type": file_metadata.type, "date": file_metadata.logical_tag_values.get("date")})

        # Try find date on at least one of the files (Raw or jpg) and copy to the other
        sorted_files = sorted(files, key=lambda x: (x['name_alone'], x['date']), reverse=True)       # Sort files in reverse order to get the file with date first
        previous_date = ''
        previous_name_alone = ''
        for file in sorted_files:
            if file.get('date') == '':   # Missing date
                if file.get('name_alone') == previous_name_alone:
                    file['date'] = previous_date
                    file_metadata = FileMetadata.getInstance(file.get('file_name'))
                    # if previous_date !='':
                    #     logical_tags = {'date': previous_date}
                    #     file_metadata.setLogicalTagValues(logical_tags)
                    #     file_metadata.save()
            previous_name_alone = file.get('name_alone')
            previous_date = file.get('date')
        sorted_files = sorted(sorted_files, key=lambda x: (x['name_alone'], x['date']))       # Sort files in order by filename and date



        # Make a final list primarily sorted by date with files without date squezed in where name of file matches sequence
        sorted_files_missing_date = [d for d in sorted_files if d.get('date') == '']
        sorted_files_missing_date = sorted(sorted_files_missing_date, key=lambda x: x['name_alone'])
        sorted_files_with_date = [d for d in sorted_files if d.get('date') != '']
        sorted_files_with_date = sorted(sorted_files_with_date, key=lambda x: (x['date'], x['name_alone']))
        sorted_files = []
        while sorted_files_missing_date != []:
            file_missing_date = sorted_files_missing_date[0]
            if sorted_files_with_date != []:
                file_with_date = sorted_files_with_date[0]
                while file_with_date.get('name_alone') < file_missing_date.get('name_alone'):
                    sorted_files.append(file_with_date)
                    del sorted_files_with_date[0]
                    if sorted_files_with_date == []:
                        break
                    file_with_date = sorted_files_with_date[0]
            sorted_files.append(file_missing_date)
            del sorted_files_missing_date[0]
        sorted_files.extend(sorted_files_with_date)

        # Find unique sorted filenames
        sorted_name_alones = [d['name_alone'] for d in sorted_files]
        sorted_name_alones = list(OrderedDict.fromkeys(sorted_name_alones))
        sorted_old_new_name_alones = []

        # Create a list with old and new filename (filename alone)
        number_width = len(self.number_pattern)
        number = 1
        for name_alone in sorted_name_alones:
            number_string = str(number).zfill(number_width)
            new_name_alone = self.prefix + number_string + self.suffix
            sorted_old_new_name_alones.append({'old_name_alone': name_alone, 'new_name_alone': new_name_alone})
            number += 1

        # Now insert new filename in files-list
        for old_new_name_alone in sorted_old_new_name_alones:
            old_name_alone = old_new_name_alone.get('old_name_alone')
            new_name_alone = old_new_name_alone.get('new_name_alone')
            for file in files:
                if file.get('name_alone') == old_name_alone:
                    new_file_name = file.get('path') + new_name_alone + '.' + file.get('type')
                    file['new_name_alone'] = new_name_alone
                    file['new_file_name'] = new_file_name

        # Rename files
        files_for_renaming = []
        for file in files:
            file_name = file.get('file_name')
            new_file_name = file.get('new_file_name')
            if new_file_name != file_name:
                files_for_renaming.append({'old_name': file_name, 'new_name': new_file_name})
        if files_for_renaming != []:
            renamer=file_util.FileRenamer.getInstance(files_for_renaming)
            renamer.filename_changed_signal.connect(renameFileInstances)
            renamer.start()


        # Set original filename tag in all files
        if settings.logical_tags.get('original_filename'):
            for file in files:
                index+=1
                self.progress_signal.emit(index+1)
                file_name = file.get('new_file_name')
                if file_name != '' and file_name != None:
                    file_metadata = FileMetadata.getInstance(file_name)
                    new_name_alone = file.get('new_name_alone')
                    if new_name_alone !='' and new_name_alone != None:
                        logical_tags = {'original_filename': new_name_alone}
                        file_metadata.setLogicalTagValues(logical_tags)
                        file_metadata.save()

        self.done_signal.emit()

class CopyLogicalTags(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()

    def __init__(self, source, target, logical_tags, match_file_name=False, overwrite=True, await_start_signal=False):
        super().__init__()

#       Source and target converted to list of files
        file_name_pattern=[]
        for filetype in settings.file_types:
            file_name_pattern.append(filetype)
        self.source_file_names = []
        if isinstance(source, list):
            for file_path in source:
                self.source_file_names.extend(file_util.getFileList(root_folder=file_path,recursive=True,pattern=file_name_pattern))
        else:
            self.source_file_names.extend(file_util.getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        self.target_file_names = []
        if isinstance(target, list):
            for file_path in target:
                self.target_file_names.extend(file_util.getFileList(root_folder=file_path,recursive=True,pattern=file_name_pattern))
        else:
            self.target_file_names.extend(file_util.getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))

        self.logical_tags=logical_tags
        self.overwrite = overwrite
        self.match_file_name = match_file_name
        if not await_start_signal:
            self.start()

    def start(self):
        if len(self.source_file_names)>1 and not self.match_file_name:   # Not possible to copy from many files to many files
            return
        # Find all source - targety combinations to copy
        source_targets=[]
        for source_file_name in self.source_file_names:
            for target_file_name in self.target_file_names:
                if self.match_file_name and file_util.splitFileName(target_file_name)[1] != file_util.splitFileName(source_file_name)[1]:
                    continue
                source_targets.append([source_file_name,target_file_name])
        copy_file_count=len(source_targets)
        self.progress_init_signal.emit(copy_file_count)

        for index, source_target in enumerate(source_targets):
            source_file = FileMetadata.getInstance(source_target[0])
            target_file = FileMetadata.getInstance(source_target[1])
            self.progress_signal.emit(index + 1)
            target_tag_values = {}
            for logical_tag in self.logical_tags:
                source_tag_value = None
                source_tag_value = source_file.logical_tag_values.get(logical_tag)
                if source_tag_value != None:
                    target_tag_values[logical_tag] = source_tag_value
            target_file.setLogicalTagValues(target_tag_values, self.overwrite)
            target_file.save()
        self.done_signal.emit()

class ConsolidateMetadata(QObject):
# This class force-saves logical tags to all physical tags in files

    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)            # Sends number of processed records
    done_signal = pyqtSignal()

    def __init__(self,target, await_start_signal=False):
        # target is a filename, a foldername, a list of filenames or a list of folder-names
        super().__init__()
        self.target=target
        if not await_start_signal:
            self.start()

    def start(self):
        file_name_pattern=[]
        for filetype in settings.file_types:
            file_name_pattern.append(filetype)
        file_names = []
        if isinstance(self.target, list):
            for file_path in self.target:
                file_names.extend(file_util.getFileList(root_folder=file_path,recursive=True,pattern=file_name_pattern))
        else:
            file_names.extend(file_util.getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))
        file_count = len(file_names)
        self.progress_init_signal.emit(file_count)

        # Consolidate file metadata force-saving
        for index, file in enumerate(file_names):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file)
            file_metadata.save(force_rewrite=True)
        self.done_signal.emit()

class QueueWorker(QThread):
    waiting = pyqtSignal()
    processing = pyqtSignal()
    about_to_quit = pyqtSignal()

    def __init__(self,delay=5):
        super().__init__()
        self.delay = delay

    def run(self):
        self.waiting.emit()
        self.about_to_quit.connect(self.onAboutToQuit)
        json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
        while True:
            queue_entry = json_queue_file.dequeue()
            if queue_entry:
                self.processing.emit()
                file = queue_entry.get('file')
                logical_tag_values = queue_entry.get('logical_tag_values')
                force_rewrite = queue_entry.get('force_rewrite')
                file_metadata = FileMetadata.getInstance(file)
                file_metadata.setLogicalTagValues(logical_tag_values)
                file_metadata.save(force_rewrite=force_rewrite, put_in_queue=False)
                json_queue_file.dequeue_commit()
            else:
                self.waiting.emit()
                time.sleep(self.delay)
            json_queue_file.dequeue_from_file()    # Updates file every 5 seconds if anything to update
    def onAboutToQuit(self):
        json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
        json_queue_file.dequeue_from_file(delay=0)
        self.quit()


class QueueHost(QObject):
    __instance=None
    def __init__(self):
        super().__init__()
        self.queue_worker_running = False
        self.queue_worker_processing = False

    @staticmethod
    def get_instance():
        if QueueHost.__instance == None:
            QueueHost.__instance = QueueHost()
        return QueueHost.__instance

    def worker_waiting(self):
        self.queue_worker_running = True
        self.queue_worker_processing = False

    def worker_processing(self):
        self.queue_worker_running = True
        self.queue_worker_processing = True


    def start_queue_worker(self):
        if not self.queue_worker_running:
            self.queue_worker=QueueWorker()
            self.queue_worker.waiting.connect(self.worker_waiting)       # Queue-worker is waiting for something to process
            self.queue_worker.processing.connect(self.worker_processing) # Queue is being processed. This can be used to show running-indicator in app.
            self.queue_worker.start()
            QCoreApplication.instance().aboutToQuit.connect(self.queue_worker.about_to_quit.emit)
































