import copy
import os
from exiftool_wrapper import ExifTool
from PyQt6.QtCore import QThread, QCoreApplication,QObject,pyqtSignal,QSize, Qt
from PyQt6.QtGui import QMovie, QPixmap, QImage,QTransform, QImageReader
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QSizePolicy
import settings
import time
import file_util
import sys
import pillow_heif
import rawpy
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
import re
import util
from value_classes import *


class FileMetadataChangedEmitter(QObject):
    instance = None
    change_signal = pyqtSignal(str, dict, dict)  # Filename, old logical tag values, new logical tag values

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileMetadataChangedEmitter.instance == None:
            FileMetadataChangedEmitter.instance = FileMetadataChangedEmitter()
        return FileMetadataChangedEmitter.instance
    def send(self, file_name, old_logical_tag_values, new_logical_tag_values):
        self.change_signal.emit(file_name, old_logical_tag_values, new_logical_tag_values)


class FileMetadata(QObject):
#   app_path = sys.argv[0]
#   app_dir = os.path.dirname(os.path.abspath(app_path))
#   exif_executable = os.path.join(app_dir, 'exiftool_memory_mate.exe')
#   exif_configuration = os.path.join(app_dir, 'exiftool_memory_mate.cfg')

    exif_executable = os.path.join(settings.resource_path,'exiftool_memory_mate.exe')
    exif_configuration = os.path.join(settings.resource_path,'exiftool_memory_mate.cfg')

    if not os.path.isfile(exif_configuration):
        exif_configuration=''
    getInstance_active = False  # To be able to give error when instantiated directly, outside getInstance
    instance_index = {}
    change_signal = FileMetadataChangedEmitter.getInstance()    #Filename, old logical tag values, new logical tag values

    def __init__(self, file_name=""):
        super().__init__()
        # Check that instantiation is called from getInstance-method
        if not FileMetadata.getInstance_active:
            raise Exception('Please use getInstance method')
        # Check existence of image_file. Raise exception if not existing
        file_exist = os.path.isfile(file_name)
        if not file_exist:
             FileMetadata.getInstance_active = False
             raise FileNotFoundError('File '+file_name+' does not exist')

        # Set data for filename
        FileMetadata.instance_index[file_name]=self
        # Statuses to ensure correct multithread-access to data
        self.file_status = 'PENDING_READ'       # A lock telling status of file-read/write: PENDING_READ, READING, WRITING, QUEUING <blank>
        self.metadata_status = 'PENDING_READ'   # A lock telling status of metadata-variables: PENDING_READ, READING, WRITING, <blank>

        self.file_name = file_name
        self.split_file_name = file_util.splitFileName(file_name)       # ["c:\pictures\", "copy_of_my_picture-Enhanced-NR-SAI", "jpg"]
        self.path = self.split_file_name[0]                             # "c:\pictures\"
        self.name = self.split_file_name[1]                             # "copy_of_my_picture-Enhanced-NR-SAI"
        self.extension = self.split_file_name[2].rstrip('_backup')      # .jpg
        self.name_alone = self.split_file_name[1]                       # <---Remove this line whendepad method is ready
        self.split_name = self.depad(self.split_file_name[1])           # ["copy_of_","my_picture", "-Enhanced-NR-SAI]]
        self.name_prefix = self.split_name[0]                           # "copy_of_"
        self.name_alone = self.split_name[1]                            # "my_picture"
        self.name_postfix = self.split_name[2]                          # "-Enhanced-NR-SAI"
        self.is_virgin=False                                       # "Virgin means memory_mate never wrote metadata to file before. Assume not virgin tll metadata has been read
        self.date_time_change = None

    @staticmethod
    def getInstance(file_name):
        file_metadata = FileMetadata.instance_index.get(file_name)
        if file_metadata is None:
            while FileMetadata.getInstance_active:   # Could be that some other process is creating an instance. Wait for that to finalize, and recheck, if instance is now created
                time.sleep(1)
                file_metadata = FileMetadata.instance_index.get(file_name)
                if file_metadata != None:
                    return file_metadata
            FileMetadata.getInstance_active = True
            file_metadata = FileMetadata(file_name)
            FileMetadata.getInstance_active = False
        return file_metadata

    def escape_except_dot_star(self,pattern):
        escaped_pattern = ''
        for char in pattern:
            if char == '.' or char == '*':
                escaped_pattern += char
            else:
                escaped_pattern += re.escape(char)
        return escaped_pattern

    def depad(self,name):
        name_alone = name
        prefix = ""
        postfix = ""

        padding_patterns = settings.file_name_padding
        if padding_patterns:
            prefix_patterns = padding_patterns.get("file_name_prefix")
            if prefix_patterns:
                while True:
                    prefix_found = False
                    for prefix_pattern in prefix_patterns:
                        escaped_prefix_pattern = self.escape_except_dot_star(prefix_pattern)
                        match = re.search(escaped_prefix_pattern, name_alone)
                        if match:
                            prefix_found = True
                            if match.start() == 0:
                                found_prefix_pattern = match.group(0)
                                prefix = prefix + found_prefix_pattern
                                name_alone = name_alone.replace(found_prefix_pattern, '', 1)
                    if not prefix_found:
                        break

            postfix_patterns = padding_patterns.get("file_name_postfix")
            if postfix_patterns:
                while True:
                    postfix_found = False
                    for postfix_pattern in postfix_patterns:
                        escaped_postfix_pattern = self.escape_except_dot_star(postfix_pattern)
                        match = re.search(escaped_postfix_pattern,
                                          name_alone)  # ! added to make sure to find last occurrence postfix
                        if match:
                            postfix_found = True
                            end_pos = len(name_alone)
                            if match.end() == end_pos:
                                found_postfix_pattern = match.group(0)  # Remove ! from found_postfix
                                postfix = found_postfix_pattern + postfix
                                name_alone = util.rreplace(name_alone, found_postfix_pattern, '')
                    if not postfix_found:
                        break

        return [prefix, name_alone, postfix]

    def getStatus(self):       # Status can be PENDING_READ (Metadata not yet read from file), READ (Metadata being read) or <blank> (Metadata read)
        return self.metadata_status
    def getFileType(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is '+ self.metadata_status)
        return self.type

    def getLogicalTagValues(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        logical_tag_values = {}
        for logical_tag in self.logical_tag_instances:
            logical_tag_values[logical_tag] = self.logical_tag_instances.get(logical_tag).getValue()
            if settings.logical_tags.get(logical_tag).get("value_parts") is not None:
                for logical_tag_part in settings.logical_tags.get(logical_tag).get("value_parts"):
                    logical_tag_values[logical_tag + '.' + logical_tag_part] = self.logical_tag_instances.get(
                    logical_tag).getValue(logical_tag_part)
        return logical_tag_values

    def getSavedLogicalTagValues(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        logical_tag_values = {}
        for logical_tag in self.saved_logical_tag_instances:
            logical_tag_values[logical_tag] = self.saved_logical_tag_instances.get(logical_tag).getValue()
            if settings.logical_tags.get(logical_tag).get("value_parts") is not None:
                for logical_tag_part in settings.logical_tags.get(logical_tag).get("value_parts"):
                    logical_tag_values[logical_tag+'.'+logical_tag_part] = self.saved_logical_tag_instances.get(logical_tag).getValue(logical_tag_part)
        return logical_tag_values

    def __readFileType(self):
        file_type = self.split_file_name[2].rstrip('_backup')   # Remove _backup from filetype
        tags = ['File:FileTypeExtension']
        with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
            exif_data = ex.getTags(self.file_name, tags, process_id='READ')
        tag_value = exif_data[0].get('File:FileTypeExtension')
        if not tag_value is None:
            file_type = tag_value
        self.type = file_type

    def readLogicalTagValues(self):
        if self.metadata_status != 'PENDING_READ':   # Means that some other thread is reading or writing to metadata-variables
            return 'NOTHING DONE'
        self.metadata_status = 'READING'
        self.__readFileType()
        #Get names of tags in tags for the filetype from settings
        logical_tags_tags = settings.file_type_tags.get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:    # Filename blank or unknown filetype
            self.logical_tag_instances = {}
            self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
            self.logical_tags_missing_value = []
            self.metadata_status = ''
            return 'DATA READ'

        file_names_tags = {}                                 #A dictionary with imate-file-name and it's tags plus sidecar file-name(s) and it's/their tags


        for logical_tag in logical_tags_tags:
            logical_tag_tags = logical_tags_tags[logical_tag]
            sidecar_file_names = {}
            for tag in logical_tag_tags:
                sidecar_file_name = None
                tag_attributes = settings.tags.get(tag)
                if tag_attributes is not None:
                    sidecar_tag_group = tag_attributes.get('sidecar_tag_group')
                    if sidecar_tag_group is not None:
                        sidecar_file_name_pattern = settings.sidecar_tag_groups.get(sidecar_tag_group).get('file_name_pattern')
                        sidecar_file_name_pri_1 = self.path + sidecar_file_name_pattern.replace('<file_name>',self.name).replace('<ext>',self.extension)   # c:\pictures\image-Enhanced-NR-SAI.jpg.json
                        sidecar_file_name_pri_2  = self.path + sidecar_file_name_pattern.replace('<file_name>',self.name_alone).replace('<ext>',self.extension)   # c:\pictures\image-Enhanced-NR-SAI.jpg.json
                        if sidecar_file_names.get(sidecar_file_name_pri_1) is None:
                            if os.path.isfile(sidecar_file_name_pri_1):
                                sidecar_file_names[sidecar_file_name_pri_1] = 'EXISTING'
                            else:
                                sidecar_file_names[sidecar_file_name_pri_1] = 'NON_EXISTING'
                        if sidecar_file_names.get(sidecar_file_name_pri_2) is None:
                            if os.path.isfile(sidecar_file_name_pri_2):
                                sidecar_file_names[sidecar_file_name_pri_2] = 'EXISTING'
                            else:
                                sidecar_file_names[sidecar_file_name_pri_2] = 'NON_EXISTING'

                        if sidecar_file_names.get(sidecar_file_name_pri_1) == 'EXISTING':
                            sidecar_file_name = sidecar_file_name_pri_1
                        elif sidecar_file_names.get(sidecar_file_name_pri_2) == 'EXISTING':
                            sidecar_file_name = sidecar_file_name_pri_2
                        else:
                            sidecar_file_name = None

                        if sidecar_file_name is not None:       # Sidecar file exist
                            file_name_tags = file_names_tags.get(sidecar_file_name)
                            if file_name_tags is None:
                                file_names_tags[sidecar_file_name] = [tag]
                            else:
                                file_name_tags.append(tag)
                    else:
                        file_name_tags = file_names_tags.get(self.file_name)
                        if file_name_tags is None:
                            file_names_tags[self.file_name] = [tag]
                        else:
                            file_name_tags.append(tag)

        # Now get values for these tags using exif-tool
        self.tag_values = {}
        for file_name in file_names_tags:
            tags = file_names_tags.get(file_name)
            with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
                exif_data = ex.getTags(file_name, tags,process_id='READ')
            for tag in tags:
                tag_alone = tag.rstrip('#')               #Remove #-character, as it is not a part of tag-name, it is a control-character telling exiftool to deliver/recieve tag in nummeric format
                tag_value = exif_data[0].get(tag_alone)
                if tag_value != None and tag_value != "" and tag_value != []:
                    if isinstance(tag_value,list):
                        tag_value = list(map(str, tag_value))
                    self.tag_values[tag] = tag_value    # These are the physical tag name-value pairs (tag-name includes # where relevant)

        # Finally map tag_values to logical_tag_instances
        self.logical_tag_instances = {}
        self.logical_tags_missing_value = []
        for logical_tag in logical_tags_tags:
            logical_tag_value_found = False

            # Get instance of value-class for the logical tag
            logical_tag_class_name = settings.logical_tags.get(logical_tag).get("value_class")
            logical_tag_class = globals().get(logical_tag_class_name) if logical_tag_class_name is not None else None
            logical_tag_instance = logical_tag_class() if logical_tag_class is not None else None

            if logical_tag_instance is None:
                print('Logical tag Class not found: ' + logical_tag)
                continue

            # Get physical tags for the logical tag
            logical_tag_tags = logical_tags_tags.get(logical_tag)

            # Set value of logical tag inside instance of logical tag value-instance
            for tag in logical_tag_tags:
                tag_attrib = settings.tags.get(tag)
                if tag_attrib is None:
                    print('Physical tag attributes not found: ' + tag)
                    continue
                tag_access = settings.tags.get(tag).get('access')   # Some tags are only written, not read
                if tag_access is not None:
                    if 'Read' not in tag_access:
                        continue
                logical_tag_instance.setValueFromExif(value=self.tag_values.get(tag),exif_tag=tag)
            if logical_tag_instance.getValue() is not None:
                logical_tag_value_found = True

            self.logical_tag_instances[logical_tag] = logical_tag_instance  # Save logical tag value-instance in dictionary

            if not logical_tag_value_found:
                self.logical_tags_missing_value.append(logical_tag)

        self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
        self.__updateLogicalTagValuesFromQueue()
        self.__updateLogicalTagValuesFromFallbackTags()
        self.__updateReferenceTags()

        # Read fallback_tag (if assigned) into missing logical tags
        self.metadata_status = ''
        return 'DATA READ'

    def __updateLogicalTagValuesFromFallbackTags(self):
        if not self.tag_values.get('XMP:MemoryMateSaveDateTime'):     #Memory Mate never wrote to file before. Get fall-back tag-values for missing logical tags that has fall-back tag assigned
            self.is_virgin=True
            for logical_tag in self.logical_tags_missing_value:
                fallback_tag = settings.logical_tags.get(logical_tag).get('fallback_tag')
                if fallback_tag:
                    fallback_tag_instance = self.logical_tag_instances.get(fallback_tag)
                    fallback_tag_value = fallback_tag_instance.getValue() if fallback_tag_instance is not None else None
                    if fallback_tag_value:
                        self.logical_tag_instances[logical_tag].setValue(fallback_tag_value)



    def __splitTag(self,full_logical_tag):
        if "." in full_logical_tag:
            logical_tag, part = full_logical_tag.split(".", 1)  # Split at the first dot
        else:
            logical_tag = full_logical_tag
            part = None
        return logical_tag, part

    def __updateLogicalTagValues(self,logical_tag_values, overwrite=True):
        if logical_tag_values is not None and logical_tag_values != {}:
            for full_logical_tag in logical_tag_values:
                # Here split of logical tag at .  E.g  date.utc_offset --> logical_tag=date, part=utc_offset
                logical_tag, part = self.__splitTag(full_logical_tag)
                if not logical_tag in self.logical_tag_instances:  # If the file-type does not support the logical tag, then skip it
                    continue
                self.logical_tag_instances.get(logical_tag).setValue(logical_tag_values[full_logical_tag],part=part,overwrite=overwrite)

    def __updateLogicalTagValuesFromQueue(self):
        json_queue = file_util.JsonQueue.getInstance(settings.queue_file_path)
        for queue_entry in json_queue.queue:
            if queue_entry.get('file') == self.file_name:
                queue_logical_tag_values = queue_entry.get('logical_tag_values')
                self.__updateLogicalTagValues(queue_logical_tag_values,queue_entry.get('overwrite'))

    def __updateReferenceTags(self):
        new_line = False
        logical_tags_tags = settings.file_type_tags.get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:
            pass
        for logical_tag in logical_tags_tags:
            if not settings.logical_tags[logical_tag].get("reference_tag"):    #Continue if not a reference tag
                continue

            logical_tag_value = ''
            tag_separator = settings.logical_tags[logical_tag].get("reference_tag_separator")
            if tag_separator is None:
                tag_separator = ""
            for i, tag_content in enumerate(settings.logical_tags[logical_tag].get("reference_tag_content")):
                tag_separator_this = tag_separator
                if i == 0:
                    tag_separator_this = ""      #first loop pass
                prefix = tag_content.get('prefix')
                if prefix is None:
                    prefix = ""
                postfix = tag_content.get('postfix')
                if postfix is None:
                    postfix = ""
                if tag_content.get('type') =='text_line':
                    tag_content_text = tag_content.get('text')
                    if tag_content_text != None:
                        if new_line:
                            logical_tag_value += '\n'
                        logical_tag_value += tag_separator_this + prefix + tag_content_text + postfix
                        new_line = tag_content.get('new_line')
                elif tag_content.get('type') == 'tag':
                    ref_logical_tag = tag_content.get('tag_name')
                    if ref_logical_tag:
                        if tag_content.get('tag_label') == True:
                            label_key = settings.logical_tags.get(ref_logical_tag).get("label_text_key")
                            if label_key is not None:
                                label = settings.text_keys.get(label_key).get(settings.language) + ': '
                            else:
                                label = ""
                        else:
                            label = ""
                        ref_logical_tag_instance = self.logical_tag_instances.get(ref_logical_tag)
                        ref_logical_tag_value = ref_logical_tag_instance.getValue() if ref_logical_tag_instance is not None else None
                        if type(ref_logical_tag_value) == str:
                            if ref_logical_tag_value != "":
                                if new_line:
                                    logical_tag_value += '\n'
                                logical_tag_value += tag_separator_this + label + prefix + ref_logical_tag_value + postfix
                                new_line = tag_content.get('new_line')
                        elif type(ref_logical_tag_value) == list:
                            if ref_logical_tag_value != []:
                                if new_line:
                                    logical_tag_value += '\n'
                                ref_logical_tag_value_str = ', '.join(ref_logical_tag_value)
                                logical_tag_value += tag_separator_this + label + prefix + ref_logical_tag_value_str + postfix
                                new_line = tag_content.get('new_line')
            logical_tag_instance  = self.logical_tag_instances.get(logical_tag)
            if logical_tag_instance is not None:
                logical_tag_instance.setValue(logical_tag_value)


    def setLogicalTagValues(self,logical_tag_values,overwrite=True,force_rewrite = False):
        due_for_queuing=False

        # Update tag-values in instance from queue
        if self.metadata_status == '':     # Metadata has already been read from file
            old_logical_tag_values = self.getLogicalTagValues()
            self.__updateLogicalTagValues(logical_tag_values,overwrite)
            self.__updateReferenceTags()
            new_logical_tag_values = self.getLogicalTagValues()
            if new_logical_tag_values != old_logical_tag_values:
                due_for_queuing=True
                self.change_signal.send(self.file_name, old_logical_tag_values, new_logical_tag_values )

        if self.metadata_status != '':    # Put everything in queue, if file has not yet been read
            due_for_queuing = True
        if force_rewrite:
            due_for_queuing = True

        # Write tags to queue
        if due_for_queuing:
            self.file_status = 'QUEUING'
            json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
            json_queue_file.enqueue({'file': self.file_name, 'overwrite': overwrite,'logical_tag_values': logical_tag_values, 'force_rewrite': force_rewrite})
            self.file_status = ''

        # Make Queue-host instance start Queue-worker, if it is not running
            QueueHost.get_instance().start_queue_worker()

    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        split_file_name = file_util.splitFileName(new_file_name)  # ["c:\pictures\", "my_picture", "jpg"]
        self.path = split_file_name[0]                        # "c:\pictures\"
        self.name_alone = split_file_name[1]                  # "my_picture"
        self.type = split_file_name[2]                        # "jpg"
        FileMetadata.instance_index[new_file_name] = self
        del FileMetadata.instance_index[old_file_name]


    def save(self,force_rewrite=False):
        logical_tag_values = self.getLogicalTagValues()
        saved_logical_tag_values = self.getSavedLogicalTagValues()
        if self.is_virgin or force_rewrite or self.getLogicalTagValues() != self.getSavedLogicalTagValues():
            self.file_status = 'WRITING'
            logical_tags_tags = settings.file_type_tags.get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_instances:
                saved_logical_tag_instance = self.saved_logical_tag_instances.get(logical_tag)
                saved_logical_tag_value = saved_logical_tag_instance.getValue() if saved_logical_tag_instance is not None else None
                if self.logical_tag_instances[logical_tag].getValue() != saved_logical_tag_value or force_rewrite or self.is_virgin:  # New value to be saved
                    logical_tag_tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    for tag in logical_tag_tags:
                        tag_access = settings.tags.get(tag).get('access')
                        if 'Write' in tag_access:
                            tag_values[tag] = self.logical_tag_instances[logical_tag].getExifValue(tag)

            if tag_values != {} and tag_values != None:
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values,'WRITE')

            self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
            self.file_status = ''
            self.is_virgin=False

#----------------------------------------------------------------------------------------#
# Write Queue handling
#----------------------------------------------------------------------------------------#
class QueueWorker(QThread):
    waiting = pyqtSignal()
    processing = pyqtSignal()
    about_to_quit = pyqtSignal()
    queue_size_changed = pyqtSignal(int)   # Queue size: e.g. 1kb

    def __init__(self,delay=5):
        super().__init__()
        self.delay = delay
        self.paused = False
        self.queue_host = QueueHost.get_instance()

    def run(self):
        self.waiting.emit()
        self.about_to_quit.connect(self.onAboutToQuit)
        json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
        json_queue_file.queue_size_changed.connect(self.onQueueSizeChanged)
        self.queue_size = json_queue_file.queue_size
        self.queue_size_changed.emit(self.queue_size)
        while True:
            if self.queue_host.queue_worker_paused:
                time.sleep(self.delay)
            else:
                queue_entry = json_queue_file.dequeue()
                if queue_entry:
                    self.processing.emit()
                    file = queue_entry.get('file')
                    logical_tag_values = queue_entry.get('logical_tag_values')
                    force_rewrite = queue_entry.get('force_rewrite')
                    try:
                        file_metadata = FileMetadata.getInstance(file)
                        FileReadQueue.appendQueue(file)
    # #                   file_metadata.readLogicalTagValues()
                        while file_metadata.getStatus() != '':    # If instance being processed, wait for it to finalize
                            time.sleep(self.delay)
                            status = file_metadata.getStatus()     # Line added to be able to see status during debugging
                        file_metadata.save(force_rewrite)
                    except FileNotFoundError:
                        pass
                    json_queue_file.dequeue_commit()
                else:
                    self.waiting.emit()
                    time.sleep(self.delay)
                json_queue_file.dequeue_from_file()    # Updates file every 5 seconds if anything to update
    def onAboutToQuit(self):
        json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
        json_queue_file.dequeue_from_file(delay=0)
        self.quit()

    def onQueueSizeChanged(self,queue_size_dictionary={}):
        queue_size = None
        queue_size = queue_size_dictionary.get(settings.queue_file_path)
        if queue_size != None:
            self.queue_size_changed.emit(queue_size)

class QueueHost(QObject):
    queue_size_changed = pyqtSignal(int)
    instance=None
    def __init__(self):
        super().__init__()
        self.queue_worker_running = False
        self.queue_worker_processing = False
        self.queue_worker_paused = False

    @staticmethod
    def get_instance():
        if QueueHost.instance == None:
            QueueHost.instance = QueueHost()
        return QueueHost.instance

    def onWorkerWaiting(self):
        self.queue_worker_running = True
        self.queue_worker_processing = False

    def onWorkerProcessing(self):
        self.queue_worker_running = True
        self.queue_worker_processing = True
    def onQueueSizeChanged(self,queue_size):
        self.queue_size = queue_size
        self.queue_size_changed.emit(self.queue_size)


    def start_queue_worker(self):
        if not self.queue_worker_running:
            self.queue_worker_running = True
            self.queue_worker = QueueWorker()
            self.queue_worker.waiting.connect(self.onWorkerWaiting)       # Queue-worker is waiting for something to process
            self.queue_worker.processing.connect(self.onWorkerProcessing) # Queue is being processed. This can be used to show running-indicator in app.
            self.queue_worker.queue_size_changed.connect(self.onQueueSizeChanged)
            self.queue_worker.start()
            QCoreApplication.instance().aboutToQuit.connect(self.queue_worker.about_to_quit.emit)

    def stop_queue_worker(self):
        if self.queue_worker_running:
            self.queue_worker.terminate()
#            self.queue_worker = None
            self.queue_worker_running = False
            self.queue_worker_processing = False

    def pause_queue_worker(self):
        if self.queue_worker_paused:
            return
        self.queue_worker_paused = True


    def resume_queue_worker(self):
        if not self.queue_worker_paused:
            return
        self.queue_worker_paused = False

class QueueStatusMonitor(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.queue_host = QueueHost.get_instance()
        self.queue_host.queue_size_changed.connect(self.onQueueSizeChanged)
        self.queue_size = 0
        self.init_ui()

    def init_ui(self):
        # Create a label for pause/play
        self.play_pause_label = QLabel()
        self.play_pixmap = QPixmap(os.path.join(settings.resource_path,"play.png")).scaled(12,12)
        self.pause_pixmap = QPixmap(os.path.join(settings.resource_path,"pause.png")).scaled(12,12)
        self.play_pause_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        if self.queue_host.queue_worker_paused:
            self.play_pause_label.setPixmap(self.play_pixmap)
        else:
            self.play_pause_label.setPixmap((self.pause_pixmap))
        self.play_pause_label.mousePressEvent = self.onPlayPausePress
        self.play_pause_label.enterEvent = self.onPlayPauseEnter
        self.play_pause_label.leaveEvent = self.onPlayPauseLeave

        # Create a label for displaying the queue size
        self.queue_size_label = QLabel("")
        self.queue_size_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Load the processing.gif and display it using a QMovie
        self.movie = QMovie(os.path.join(settings.resource_path,"processing.gif"))
        self.movie.setScaledSize(QSize(25,18))


        # Set the maximum height for the gif label to match the queue size label
        self.gif_label = QLabel()
#        self.gif_label.setMaximumHeight(self.queue_size_label.sizeHint().height())
        self.gif_label.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)  # Set size policy

        # Create an empty label to take up space
        self.space_label = QLabel()
        self.space_label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

        # Create a horizontal layout and add the widgets
        self.addWidget(self.play_pause_label)
        self.addWidget(self.gif_label)
        self.addWidget(self.queue_size_label)
        self.addWidget(self.space_label)


    def onPlayPauseEnter(self,event):
        self.play_pause_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def onPlayPauseLeave(self,event):
        self.play_pause_label.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

    def onPlayPausePress(self,event):
        if self.queue_host.queue_worker_paused:   # Toggle to playing if paused
            self.play_pause_label.setPixmap(self.pause_pixmap)
            if self.queue_size > 0:
                self.gif_label.setMovie(self.movie)
                self.movie.start()
            self.queue_host.resume_queue_worker()
        else:                                     # Toggle to paused if playing
            self.play_pause_label.setPixmap(self.play_pixmap)
            self.gif_label.clear()
            self.movie.stop()
            self.queue_host.pause_queue_worker()

    def onQueueSizeChanged(self, size):
        self.queue_size = size
        if size > 0:
            self.queue_size_label.setText(str(size))
        else:
            self.queue_size_label.clear()
        if size > 0 and not self.queue_host.queue_worker_paused:
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.clear()
            self.movie.stop()

#----------------------------------------------------------------------------------------#
# Read Queue handling
#----------------------------------------------------------------------------------------#
class FileReadyEmitter(QObject):
    instance = None
    ready_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileReadyEmitter.instance == None:
            FileReadyEmitter.instance = FileReadyEmitter()
        return FileReadyEmitter.instance

    def emit(self, file_name):
        self.ready_signal.emit(file_name)

class FileReadQueue(QThread):
    getInstance_active = False
    instance = None
    read_folders_queue = []
    read_folders_done = []
    last_appended_file = ''
    running = False
    file_pattern = [f"*.{file_type}" for file_type in settings.file_type_tags]

    def __init__(self):
        super().__init__()
        # Check that instantiation is called from getInstance-method
        if not FileReadQueue.getInstance_active:
            raise Exception('Please use getInstance method')

    @staticmethod
    def getInstance():
        if not FileReadQueue.running:
            FileReadQueue.getInstance_active = True
            FileReadQueue.instance = FileReadQueue()
            FileReadQueue.getInstance_active = False
        return FileReadQueue.instance

    @staticmethod
    def appendQueue(file_name):     #Will extract folder-path from path and queue it if not already queued or processed
        if file_name:
            if os.path.isfile(file_name):
                FileReadQueue.last_appended_file = file_name      # Last appended file gets first priority when reading metadata
            split_file_name = file_util.splitFileName(file_name)  # ["c:\pictures\", "my_picture", "jpg"]
            path = split_file_name[0]                             # "c:\pictures\"
            if not path in FileReadQueue.read_folders_done and not path in FileReadQueue.read_folders_queue:
                FileReadQueue.read_folders_queue.append(path)
                if not FileReadQueue.running:
                    FileReadQueue.getInstance().start()

    def run(self):
        FileReadQueue.running = True
        self.__prepareFile(FileReadQueue.last_appended_file)    # Make sure to process last appended file instantly
        while FileReadQueue.read_folders_queue:
            folder=FileReadQueue.read_folders_queue.pop()
            folder_file_names = file_util.getFileList(folder,False,FileReadQueue.file_pattern)
            for folder_file_name in folder_file_names:
                self.__prepareFile(FileReadQueue.last_appended_file)  # Make sure to process last appended file instantly
                self.__prepareFile(folder_file_name)
        FileReadQueue.running = False

    def __prepareFile(self,file_name):
        if file_name == '':
            return
        if file_name == FileReadQueue.last_appended_file:
            FileReadQueue.last_appended_file = ''
        metadata_action_done = FileMetadata.getInstance(file_name).readLogicalTagValues()
        image_action_done = FilePreview.getInstance(file_name).readImage()
        if metadata_action_done != 'NOTHING DONE' or image_action_done != 'NOTHING DONE':
            FileReadyEmitter.getInstance().emit(file_name)

#----------------------------------------------------------------------------------------#
# File Preview
#----------------------------------------------------------------------------------------#
current_image_html = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden; /* This prevents scroll bars */
        }

        img {
            max-width: 100%;
            height: 100vh; /* Set image height to 100% of viewport height */
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <img src="current_image.jpg">
</body>
</html>
'''

current_image_html_path = os.path.join(settings.app_data_location,"current_image.html")
if not os.path.isfile(current_image_html_path):
    with open(current_image_html_path, "w") as outfile:
        outfile.write(current_image_html)


class FilePreview(QObject):
    instance_index = {}
    latest_panel_width = 0

    def __init__(self,file_name):
        super().__init__()
        self.sleep = 0.1
        self.file_name = file_name
        self.panel_width = 0
        self.image = None
        self.pixmap = None
        self.current_rotation = None
        self.status = 'PENDING_READ'   # A lock telling status of metadata-variables: PENDING_READ, READING, WRITING, <blank>
        FilePreview.instance_index[file_name] = self
        self.web_server = None

    def readImage(self):
        if self.status != 'PENDING_READ':
            return 'NOTHING DONE'
        file_metadata = FileMetadata.getInstance(self.file_name)
        while file_metadata.getStatus() != '':
            time.sleep(self.sleep)

        file_type = FileMetadata.getInstance(self.file_name).getFileType()

        # Read image from file
        if self.image == None:     # Only read image from file once
            if file_type == 'heic':
                self.image = self.__heic_to_qimage(self.file_name)
                self.original_image_rotated = True  # Conversion from HEIC takes rotation-metadata into account. Returned QImage is already rotated
            elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef' or file_type == 'dng':
                 self.image = self.__raw_to_qimage(self.file_name)
                 self.original_image_rotated = False # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            elif file_type == 'mov' or file_type == 'mp4' or file_type == 'm4v' or file_type == 'm2t' or file_type == 'm2ts' or file_type == 'mts':
                self.image = self.__movie_to_qimage(self.file_name)
                self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            else:
                self.image = self.__default_to_qimage(self.file_name)
                self.original_image_rotated = False  # Conversion does not takes rotation-metadata into account. Returned QImage is not rotated
            if self.image != None:
                if self.image.height()>1500 or self.image.width()>1500:
                    self.image = self.image.scaled(1500,1500,Qt.AspectRatioMode.KeepAspectRatio)
        if FilePreview.latest_panel_width != 0:
            self.__setPixmap(FilePreview.latest_panel_width)
        self.status = ''
        return 'IMAGE READ'


    def getStatus(self):
        return self.status
    def getPixmap(self,panel_width):
        if self.status != '':
            raise Exception('Preview pixmap not ready yet. Status is '+ self.status)
        if panel_width != self.panel_width:
            self.__setPixmap(panel_width)
        return self.pixmap

    def __setPixmap(self,panel_width):
        self.panel_width = panel_width
        FilePreview.latest_panel_width = panel_width
        # Set right rotation/orientation
        image = self.getImage()

        if image != None:
            if image.width() > 0:
                ratio_width  = panel_width / image.width()
                ratio_height = panel_width / image.height() / 16 * 9   # Image same height as a 9/16 landscape filling screen-width
                ratio = min(ratio_width,ratio_height)

                width = int(image.width() * ratio)
                height = int(image.height() * ratio)

                self.pixmap = QPixmap.fromImage(image)
                self.pixmap = self.pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            else:
                self.pixmap = None
        else:
            self.pixmap = None

    def getImage(self):
        file_type = FileMetadata.getInstance(self.file_name).type

        # Set right rotation/orientation
        if file_type == 'mov' or file_type == 'mp4' or file_type == 'm2t' or file_type == 'm2ts' or file_type == 'mts':
            image = self.image
        else:
            image = self.__rotatedImage()
        return image

    def __rotatedImage(self):
        if self.image == None:
            return None
        else:
            rotation_instance = FileMetadata.getInstance(self.file_name).logical_tag_instances.get("rotation")
            if rotation_instance == None:
                rotation = 0.
            else:
                rotation = rotation_instance.getValue()
                if rotation is None:
                    rotation = 0
            if self.current_rotation is None:
                if self.original_image_rotated:
                    self.current_rotation = rotation
                else:
                    self.current_rotation = 0

            rotation_change = self.current_rotation - rotation
            if rotation_change != 0:
                transform = QTransform()
                transform.rotate(rotation_change)
                rotated_image = self.image.transformed(transform)
                return rotated_image
            else:
                return self.image

    def __heic_to_qimage(self,file_name):
        if self.image == None:
            if pillow_heif.is_supported(file_name):
                pillow_heif.register_heif_opener()
                pil_image = Image.open(file_name)
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")
                image_data = pil_image.tobytes()
                width, height = pil_image.size
                image_format = QImage.Format.Format_RGB888
                image = QImage(image_data, width, height, image_format)
            else:
                image = None
        else:
            image = self.image
        return image

    def __raw_to_qimage(self,file_name):
        if self.image == None:
            with rawpy.imread(file_name) as raw:
                try:
                    thumb = raw.extract_thumb()
                except rawpy.LibRawNoThumbnailError:
                    print('no thumbnail found')
                else:
                    if thumb.format in [rawpy.ThumbFormat.JPEG, rawpy.ThumbFormat.BITMAP]:
                        if thumb.format is rawpy.ThumbFormat.JPEG:
                            image = QImage.fromData(thumb.data)
                        else:
                            thumb_pil = Image.fromarray(thumb.data)
                            thumb_data = thumb_pil.tobytes()
                            image = QImage(thumb_data, thumb_pil.width, thumb_pil.height, QImage.Format.Format_RGB888)
        else:
            image = self.image

        return image

    def __movie_to_qimage(self,file_name):
        if self.image == None:
            try:
                # Attempt to create a VideoFileClip object
                video_clip = VideoFileClip(file_name)
                fps = video_clip.fps
                duration = video_clip.duration
                # Get frame 3% into the video. The first seconds are often black or blurry/shaked
                frame = int(duration * 3 / 100 * fps)  # Frame
                thumbnail = video_clip.get_frame(frame)  # Get the first frame as the thumbnail

                # If recorded in portrait-mode, swap height and width
                #            if hasattr(video_clip, 'rotation'):
                #                rotation = video_clip.rotation
                #                if rotation in [90, 270]:
                #                    original_width, original_height = video_clip.size
                #                    thumbnail = cv2.resize(thumbnail, (original_height, original_width))  # Swap hight and width
                video_clip.close()

                height, width, channel = thumbnail.shape
                bytes_per_line = 3 * width

                image = QImage(
                    thumbnail.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                )
                video_clip.close()
            except OSError as e:
                image = self.__default_to_qimage(os.path.join(settings.resource_path, "no_preview.png"))
                # Handle specific OSError from ffmpeg
                print(f"Error loading video file {file_name}: {e}")
            except Exception as e:
                image = self.__default_to_qimage(os.path.join(settings.resource_path, "no_preview.png"))
                # Catch all other exceptions
                print(f"An unexpected error occurred with file {file_name}: {e}")
        else:
            image = self.image
        return image

    def __default_to_qimage(self,file_name):
        if self.image == None:
            image_reader = QImageReader(file_name)
            image = image_reader.read()
        else:
            image = self.image
        return image

    @staticmethod
    def getInstance(file_name):
        new_needed = False

        file_preview = FilePreview.instance_index.get(file_name)
        if file_preview is None:
           file_preview = FilePreview(file_name)

        return file_preview

    def updatePixmap(self):
        self.__setPixmap(FilePreview.latest_panel_width)


    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        FilePreview.instance_index[new_file_name] = self
        del FilePreview.instance_index[old_file_name]

class TagConverter():
    @staticmethod
    def __localDateTimeToUtc(local_date_time_str):
        # Define the date/time format
        date_time_format = "%Y:%m:%d %H:%M:%S"

        # Isolate date_time
        date_time_str = local_date_time_str[:19]
        date_time = datetime.strptime(date_time_str, date_time_format)

        # Isolate utc_offset
        utc_offset_str = local_date_time_str[19:]
        utc_offset_hours, utc_offset_minutes = map(int, utc_offset_str[1:].split(':'))
        utc_offset_sign = utc_offset_str[0]
        utc_offset = timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
        if utc_offset_sign == '-':
            utc_offset = -utc_offset

        # Calculate utc_date_time
        utc_date_time = date_time - utc_offset

        # Convert utc_date_time to string
        utc_date_time_str = utc_date_time.strftime(date_time_format)

        return utc_date_time_str


    @staticmethod
    def logicalTagRead(logical_tag, tag_set_values):    # The input holds only one tag or tag_set in tag_values
        logical_tag_value = None
        tag_iterator = iter(tag_set_values.items())
        try:
            tag, tag_value = next(tag_iterator)
            logical_tag_value = tag_value    # Almost always the case
        except StopIteration:
            pass

        if logical_tag_value == None:
            return logical_tag_value

        elif logical_tag == 'geo_location' and tag == 'Composite:GPSPosition#':
            logical_tag_value = tag_value.replace(' ', ',',1)  # ExifTool delivers space-saparated but expect comma-separated on updates

        elif logical_tag == 'rating' and tag == 'XMP-microsoft:RatingPercent':
            if tag_value != 1:
                logical_tag_value = int((tag_value + 25) / 25)

        elif logical_tag == 'rotation' and tag == 'EXIF:Orientation#':
            if tag_value == 1:
                logical_tag_value = 0
            elif tag_value == 8:
                logical_tag_value = 90
            elif tag_value == 3:
                logical_tag_value = 180
            elif tag_value == 6:
                logical_tag_value = 270
            else:
                logical_tag_value = 0
        elif logical_tag == 'date':
            second_tag = None
            second_tag_value = None
            try:
                second_tag, second_tag_value = next(tag_iterator)
            except StopIteration:
                pass
            if second_tag is not None:
                if second_tag in ['EXIF:OffsetTimeOriginal', 'EXIF:OffsetTimeDigitized', 'EXIF:OffsetTime']:
                    logical_tag_value = logical_tag_value + second_tag_value

        return logical_tag_value

    @staticmethod
    def tagWrite(logical_tag, tag_set, logical_tag_value):    # The input holds only one tag or tag_set in tags_set
        tag_values = {tag: logical_tag_value for tag in tag_set} # Almost always the case

        if logical_tag == 'rating':
            tag_value = tag_values.get('XMP-microsoft:RatingPercent')
            if tag_value is not None:
                if tag_value != 1:
                    tag_value = (tag_value - 1) * 25
                    tag_values['XMP-microsoft:RatingPercent'] = tag_value

        elif logical_tag == 'rotation':
            if 'EXIF:Orientation#' in tag_set:
                if logical_tag_value == 0:
                    tag_value = 1
                elif logical_tag_value == 90:
                    tag_value = 8
                elif logical_tag_value == 180:
                    tag_value = 3
                elif logical_tag_value == 270:
                    tag_value = 6
                else:
                    tag_value = 1
                tag_values['EXIF:Orientation#'] = tag_value

        elif logical_tag == 'date':
            tag_value = None
            if tag_value == None:   # Always true. Just to keep pattern
                tag_value = tag_values.get('EXIF:DateTimeOriginal')
                if tag_value is not None:
                    tag_values['EXIF:DateTimeOriginal'] = logical_tag_value[:19]
                    if 'EXIF:OffsetTimeOriginal' in tag_set:
                        tag_values['EXIF:OffsetTimeOriginal'] = logical_tag_value[19:]
            if tag_value == None:
                tag_value = tag_values.get('EXIF:CreateDate')
                if tag_value is not None:
                    tag_values['EXIF:CreateDate'] = logical_tag_value[:19]
                    if 'EXIF:OffsetTimeDigitized' in tag_set:
                        tag_values['EXIF:OffsetTimeDigitized'] = logical_tag_value[19:]
            if tag_value == None:
                tag_value = tag_values.get('EXIF:ModifyDate')
                if tag_value is not None:
                    tag_values['EXIF:ModifyDate'] = logical_tag_value[:19]
                    if 'EXIF:OffsetTime' in tag_set:
                        tag_values['EXIF:OffsetTime'] = logical_tag_value[19:]
            if tag_value == None:
                tag_value = tag_values.get('QuickTime:CreateDate')
                if tag_value is not None:
                    tag_values['QuickTime:CreateDate'] = TagConverter.__localDateTimeToUtc(logical_tag_value)
            if tag_value == None:
                tag_value = tag_values.get('QuickTime:TrackCreateDate')
                if tag_value is not None:
                    tag_values['QuickTime:TrackCreateDate'] = TagConverter.__localDateTimeToUtc(logical_tag_value)
            if tag_value == None:
                tag_value = tag_values.get('QuickTime:MediaCreateDate')
                if tag_value is not None:
                    tag_values['QuickTime:MediaCreateDate'] = TagConverter.__localDateTimeToUtc(logical_tag_value)

        return tag_values








































