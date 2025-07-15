import os
import time
from PyQt6.QtCore import QObject, QMutex, QMutexLocker
from configuration.language import Texts
from configuration.paths import Paths
from controller.events.emitters.file_metadata_changed_emitter import FileMetadataChangedEmitter
from controller.events.emitters.file_metadata_ready_emitter import FileMetadataReadyEmitter
from services.file_services.file_split_name import splitFileName
from services.metadata_services.exiftool_wrapper import ExifTool
from services.stack_services.stack import Stack
from services.queue_services.queue import Queue
from services.utility_services.rreplace import rreplace
from services.metadata_services.metadata_value_classes import *
from services.file_services.file_get_original import fileGetOriginal


class FileMetadata(QObject):
#   app_path = sys.argv[0]
#   app_dir = os.path.dirname(os.path.abspath(app_path))
#   exif_executable = os.path.join(app_dir, 'exiftool_memory_mate.exe')
#   exif_configuration = os.path.join(app_dir, 'exiftool_memory_mate.cfg')

    exif_executable = os.path.join(Paths.get('resources'), 'exiftool_memory_mate.exe')
    exif_configuration = os.path.join(Paths.get('resources'), 'exiftool_memory_mate.cfg')
    get_instance_mutex = QMutex()


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
        self.split_file_name = splitFileName(file_name)       # ["c:\pictures\", "copy_of_my_picture-Enhanced-NR-SAI", "jpg"]
        self.path = self.split_file_name[0]                             # "c:\pictures\"
        self.name = self.split_file_name[1]                             # "copy_of_my_picture-Enhanced-NR-SAI"
        self.extension = self.split_file_name[2].rstrip('_backup')      # .jpg
        self.name_alone = self.split_file_name[1]                       # <---Remove this line whendepad method is ready
        self.split_name = self.__depad(self.split_file_name[1])           # ["copy_of_","my_picture", "-Enhanced-NR-SAI]]
        self.name_prefix = self.split_name[0]                           # "copy_of_"
        self.name_alone = self.split_name[1]                            # "my_picture"
        self.name_postfix = self.split_name[2]                          # "-Enhanced-NR-SAI"
        self.is_virgin=False                                       # "Virgin means memory_mate never wrote metadata to file before. Assume not virgin tll metadata has been read
        self.date_time_change = None
        self.delay = 1

    @staticmethod
    def getInstance(file_name):
        file_metadata = FileMetadata.instance_index.get(file_name)
        if file_metadata is None:
            with QMutexLocker(FileMetadata.get_instance_mutex):
                file_metadata = FileMetadata.instance_index.get(file_name)
                if file_metadata is None:
                    FileMetadata.getInstance_active = True
                    file_metadata = FileMetadata(file_name)
                    FileMetadata.getInstance_active = False
        return file_metadata

    @staticmethod
    def processWriteQueueEntry(queue_entry):    # metadata.write Queue calls this method for processing
        file = queue_entry.get('file')
        logical_tag_values = queue_entry.get('logical_tag_values')
        force_rewrite = queue_entry.get('force_rewrite')
        try:
            file_metadata = FileMetadata.getInstance(file)
            metadata_read_stack = Stack.getInstance('metadata.read')
            metadata_read_stack.push(file)
            while file_metadata.getStatus() != '':    # If instance being processed, wait for it to finalize
                time.sleep(1)
                status = file_metadata.getStatus()     # Line added to be able to see status during debugging
            file_metadata.save(force_rewrite)
        except FileNotFoundError:
            pass

    @staticmethod
    def processReadStackEntry(stack_entry):
        metadata_action_done = FileMetadata.getInstance(stack_entry).readLogicalTagValues()
        # if metadata_action_done != 'NOTHING DONE':
        #     FileMetadataReadyEmitter.getInstance().emit(stack_entry)

    def __escapeExceptDotStar(self,pattern):
        escaped_pattern = ''
        for char in pattern:
            if char == '.' or char == '*':
                escaped_pattern += char
            else:
                escaped_pattern += re.escape(char)
        return escaped_pattern

    def __depad(self,name):
        name_alone = name
        prefix = ""
        postfix = ""

        padding_patterns = Settings.get('file_name_padding')
        if padding_patterns:
            prefix_patterns = padding_patterns.get("file_name_prefix")
            if prefix_patterns:
                while True:
                    prefix_found = False
                    for prefix_pattern in prefix_patterns:
                        escaped_prefix_pattern = self.__escapeExceptDotStar(prefix_pattern)
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
                        escaped_postfix_pattern = self.__escapeExceptDotStar(postfix_pattern)
                        match = re.search(escaped_postfix_pattern,
                                          name_alone)  # ! added to make sure to find last occurrence postfix
                        if match:
                            end_pos = len(name_alone)
                            if match.end() == end_pos:
                                postfix_found = True
                                found_postfix_pattern = match.group(0)  # Remove ! from found_postfix
                                postfix = found_postfix_pattern + postfix
                                name_alone = rreplace(name_alone, found_postfix_pattern, '')
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
            if Settings.get('logical_tags').get(logical_tag).get("value_parts") is not None:
                for logical_tag_part in Settings.get('logical_tags').get(logical_tag).get("value_parts"):
                    logical_tag_values[logical_tag + '.' + logical_tag_part] = self.logical_tag_instances.get(
                    logical_tag).getValue(logical_tag_part)
        return logical_tag_values

    def getSavedLogicalTagValues(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        logical_tag_values = {}
        for logical_tag in self.saved_logical_tag_instances:
            logical_tag_values[logical_tag] = self.saved_logical_tag_instances.get(logical_tag).getValue()
            if Settings.get('logical_tags').get(logical_tag).get("value_parts") is not None:
                for logical_tag_part in Settings.get('logical_tags').get(logical_tag).get("value_parts"):
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
        logical_tags_tags = Settings.get('file_type_tags').get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:    # Filename blank or unknown filetype
            self.logical_tag_instances = {}
            self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
            self.logical_tags_missing_value = []
            self.metadata_status = ''
            FileMetadataReadyEmitter.getInstance().emit(self.file_name)
            return 'DATA READ'

        file_names_tags = {}                                 #A dictionary with imate-file-name and it's tags plus sidecar file-name(s) and it's/their tags


        for logical_tag in logical_tags_tags:
            logical_tag_tags = logical_tags_tags[logical_tag]
            sidecar_file_names = {}
            for tag in logical_tag_tags:
                sidecar_file_name = None
                tag_attributes = Settings.get('tags').get(tag)
                if tag_attributes is not None:
                    sidecar_tag_group = tag_attributes.get('sidecar_tag_group')
                    if sidecar_tag_group is not None:
                        sidecar_file_name_pattern = Settings.get('sidecar_tag_groups').get(sidecar_tag_group).get('file_name_pattern')
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
                if tag_value is not None and tag_value != "" and tag_value != []:
                    if isinstance(tag_value,list):
                        tag_value = list(map(str, tag_value))
                    self.tag_values[tag] = tag_value    # These are the physical tag name-value pairs (tag-name includes # where relevant)
        if not self.tag_values.get('XMP:MemoryMateSaveDateTime'):     #Memory Mate never wrote to file before. Get fall-back tag-values for missing logical tags that has fall-back tag assigned
            self.is_virgin=True

        # Finally map tag_values to logical_tag_instances
        self.logical_tag_instances = {}
        self.logical_tags_missing_value = []
        for logical_tag in logical_tags_tags:
            logical_tag_value_found = False

            # Get instance of value-class for the logical tag
            logical_tag_class_name = Settings.get('logical_tags').get(logical_tag).get("value_class")
            logical_tag_class = globals().get(logical_tag_class_name) if logical_tag_class_name is not None else None
            logical_tag_instance = logical_tag_class(logical_tag=logical_tag ) if logical_tag_class is not None else None

            if logical_tag_instance is None:
                print('Logical tag Class not found: ' + logical_tag)
                continue

            # Get physical tags for the logical tag
            logical_tag_tags = logical_tags_tags.get(logical_tag)

            # Set value of logical tag inside instance of logical tag value-instance
            for tag in logical_tag_tags:
                tag_attrib = Settings.get('tags').get(tag)
                if tag_attrib is None:
                    print('Physical tag attributes not found: ' + tag)
                    continue
                tag_access = Settings.get('tags').get(tag).get('access')   # Some tags are only written, not read
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

#        self.__patchLogicalTagValuesFromOriginals()    # If a new Lightroom-export has overwritten jpg, the custom XMP-tags (MemoryMate version, save-date/time, description_only) are lost. These are recreated from original
        self.__updateLogicalTagValuesFromQueue()
        self.__updateLogicalTagValuesFromFallbackTags()
        self.__updateReferenceTags()

        # Read fallback_tag (if assigned) into missing logical tags
        self.metadata_status = ''
        FileMetadataReadyEmitter.getInstance().emit(self.file_name)
        return 'DATA READ'

    def __updateLogicalTagValuesFromFallbackTags(self):
        if self.is_virgin:
            for logical_tag in self.logical_tags_missing_value:
                fallback_tag = Settings.get('logical_tags').get(logical_tag).get('fallback_tag')
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
        metadata_write_queue = Queue.getInstance('metadata.write')
        for queue_entry in metadata_write_queue.entries():
            if queue_entry.get('file') == self.file_name:
                queue_logical_tag_values = queue_entry.get('logical_tag_values')
                self.__updateLogicalTagValues(queue_logical_tag_values,queue_entry.get('overwrite'))

    def __patchLogicalTagValuesFromOriginals(self):
        if not self.tag_values.get('XMP:MemoryMateSaveDateTime'):    # If this is missing, a new lightroom-export from original has taken place, and custom tags are lost.
            original_file_name = fileGetOriginal(self.file_name)
            if original_file_name is None:
                return
            original_file_metadata = FileMetadata.getInstance(original_file_name)
            original_file_metadata.readLogicalTagValues()
            original_logical_tag_values = original_file_metadata.getLogicalTagValues()
            self.__updateLogicalTagValues(original_logical_tag_values, overwrite=False)


    def __updateReferenceTags(self):
        new_line = False
        logical_tags_tags = Settings.get('file_type_tags').get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:
            pass
        for logical_tag in logical_tags_tags:
            if not Settings.get('logical_tags')[logical_tag].get("reference_tag"):    #Continue if not a reference tag
                continue

            logical_tag_value = ''
            tag_separator = Settings.get('logical_tags')[logical_tag].get("reference_tag_separator")
            if tag_separator is None:
                tag_separator = ""
            for i, tag_content in enumerate(Settings.get('logical_tags')[logical_tag].get("reference_tag_content")):
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
                    if tag_content_text is not None:
                        if new_line:
                            logical_tag_value += '\n'
                        logical_tag_value += tag_separator_this + prefix + tag_content_text + postfix
                        new_line = tag_content.get('new_line')
                elif tag_content.get('type') == 'tag':
                    ref_logical_tag = tag_content.get('tag_name')
                    if ref_logical_tag:
                        if tag_content.get('tag_label') == True:
                            label_key = Settings.get('logical_tags').get(ref_logical_tag).get("label_text_key")
                            if label_key is not None:
                                label = Texts.get(label_key) + ': '
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
                self.change_signal.emit(self.file_name, old_logical_tag_values, new_logical_tag_values )

        if self.metadata_status != '':    # Put everything in queue, if file has not yet been read
            due_for_queuing = True
        if force_rewrite:
            due_for_queuing = True

        # Write tags to queue
        if due_for_queuing:
            self.file_status = 'QUEUING'
            metadata_write_queue = Queue.getInstance('metadata.write')
            metadata_write_queue.enqueue({'file': self.file_name, 'overwrite': overwrite,'logical_tag_values': logical_tag_values, 'force_rewrite': force_rewrite})
            self.file_status = ''
            metadata_write_queue.start()

    def updateFilename(self, new_file_name):
        old_file_name = self.file_name
        self.file_name = new_file_name
        split_file_name = splitFileName(new_file_name)  # ["c:\pictures\", "my_picture", "jpg"]
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
            logical_tags_tags = Settings.get('file_type_tags').get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_instances:
                saved_logical_tag_instance = self.saved_logical_tag_instances.get(logical_tag)
                saved_logical_tag_value = saved_logical_tag_instance.getValue() if saved_logical_tag_instance is not None else None
                if self.logical_tag_instances[logical_tag].getValue() != saved_logical_tag_value or force_rewrite or self.is_virgin:  # New value to be saved
                    logical_tag_tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    for tag in logical_tag_tags:
                        tag_access = Settings.get('tags').get(tag).get('access')
                        if 'Write' in tag_access:
                            tag_values[tag] = self.logical_tag_instances[logical_tag].getExifValue(tag)

            if tag_values != {} and tag_values is not None:
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values,'WRITE')

            self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
            self.file_status = ''
            self.is_virgin=False
