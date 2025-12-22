import os
import time
from PyQt6.QtCore import QObject, QMutex, QMutexLocker
import re

from configuration.language import Texts
from configuration.paths import Paths
from controller.events.emitters.file_metadata_changed_emitter import FileMetadataChangedEmitter
from controller.events.emitters.file_metadata_ready_emitter import FileMetadataReadyEmitter
from services.file_services.file_split_name import splitFileName
from services.metadata_services.exiftool_wrapper import ExifTool
from services.stack_services.stack import Stack
from services.queue_services.queue import Queue
from services.utility_services.hash import hashCode
from services.utility_services.rreplace import rreplace
from services.metadata_services.metadata_value_classes import *
from services.file_services.file_get_original import fileGetOriginal
from services.integration_services.garmin_integration import GarminIntegration
from repository.gps_location_repo.gps_location_api import GpsApi

class FileMetadata(QObject):
#   app_path = sys.argv[0]
#   app_dir = os.path.dirname(os.path.abspath(app_path))
#   exif_executable = os.path.join(app_dir, 'exiftool_memory_mate.exe')
#   exif_configuration = os.path.join(app_dir, 'exiftool_memory_mate.cfg')

    exif_executable = os.path.join(Paths.get('resources'), 'exiftool_memory_mate.exe')
    exif_configuration = os.path.join(Paths.get('resources'), 'exiftool_memory_mate.cfg')
    service_users = {}    # Contains buffered values for service_name, user_name, user_id. Service could be garmin_connect. It is populated at first use
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
        self.working_copy_file_name = None       #
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
            if file_metadata.getStatus() != '':  # If instance being processed, wait for it to finalize
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

    def getTagsHashTag(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        hash_code = self.tag_values.get('XMP:MemoryMateTagsHash')
        return self.tag_values.get('XMP:MemoryMateTagsHash')

    def getTagsHash(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        tag_values = copy.deepcopy(self.tag_values)

        # Remove MemoryMate controll-tags. These should not be a part of the hash
        tag_values.pop('XMP:MemoryMateSaveVersion', None)   # Don't include MemoryMate control tags in Hash
        tag_values.pop('XMP:MemoryMateSaveDateTime', None)  # Don't include MemoryMate control tags in Hash
        tag_values.pop('XMP:MemoryMateTagsHash', None)      # Don't include MemoryMate control tags in Hash

        write_tag_values = copy.deepcopy(tag_values)

        # Remove all non-writable tags. these should not be a part of hash
        for tag in write_tag_values:
            value = tag_values.get(tag)
            if isinstance(value,str):
                value = value.strip(' ')
                if value == '':
                    value = None
            if value is None:
                tag_values.pop(tag, None)
                continue
            access = Settings.get('tags').get(tag).get('access')
            if not access:
                tag_values.pop(tag,None)
            else:
                if not 'Write' in access:
                    tag_values.pop(tag, None)

        if tag_values == {}:
            return None
        hash_code = hashCode(tag_values)
        return hash_code

    def getStatus(self):       # Status can be PENDING_READ (Metadata not yet read from file), READ (Metadata being read) or <blank> (Metadata read)
        return self.metadata_status

    def getFileType(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is '+ self.metadata_status)
        return self.type

    def getLogicalTagValues(self,filter_writable_only=False):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        return self.__logicalTagValues(filter_writable_only)

    def __logicalTagValues(self,filter_writable_only=False):
        logical_tag_values = {}
        for logical_tag in self.logical_tag_instances:
            if filter_writable_only:
                if not 'Write' in Settings.get('logical_tags').get(logical_tag).get("access"):
                    continue
            logical_tag_values[logical_tag] = self.logical_tag_instances.get(logical_tag).getValue()
            if Settings.get('logical_tags').get(logical_tag).get("value_parts") is not None:
                for logical_tag_part in Settings.get('logical_tags').get(logical_tag).get("value_parts"):
                    logical_tag_values[logical_tag + '.' + logical_tag_part] = self.logical_tag_instances.get(
                        logical_tag).getValue(logical_tag_part)
        return logical_tag_values

    def getSavedLogicalTagValues(self,filter_writable_only=False):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        return self.__savedLogicalTagValues(filter_writable_only)

    def __savedLogicalTagValues(self,filter_writable_only=False):
        logical_tag_values = {}
        for logical_tag in self.saved_logical_tag_instances:
            if filter_writable_only:
                if not 'Write' in Settings.get('logical_tags').get(logical_tag).get("access"):
                    continue
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
        # print("Reading Metadata for "+ self.file_name)
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

        # Initialize result-variables
        self.tag_values = {}
        self.logical_tag_instances = {}
        self.saved_logical_tag_instances = {}
        self.logical_tags_missing_value = []

        # Prepare list of pending tags (will be used in while-iteration below
        pending_tags = [tag for tags in logical_tags_tags.values() for tag in tags]  # A complete list of tags to be read
        pending_logical_tags = list(logical_tags_tags.keys())   # All logical tags are pending
        old_pending_tags = []
        old_pending_logical_tags = []

        while len(pending_tags) != 0 or len(pending_logical_tags) != 0:
            if pending_tags==old_pending_tags and pending_logical_tags==old_pending_logical_tags:
                break   # Prevent eternal while loop if same tags keeps being pending

            old_pending_tags = copy.deepcopy(pending_tags)
            old_pending_logical_tags = copy.deepcopy(pending_logical_tags)

            tags = copy.deepcopy(pending_tags)
            logical_tags = copy.deepcopy(pending_logical_tags)

            pending_tags = []
            pending_logical_tags = []



            file_names_tags = {}  # A dictionary with image-file-name and it's tags plus sidecar file-name(s) and it's/their tags
            api_tags = {}  # A dictionary with tags to be read from api, with corresponding source_id (e.g. GpsApi)
            sidecar_file_names = {}
            for tag in tags:
                tag_attributes = Settings.get('tags').get(tag)
                if tag_attributes is not None:

                    # If tag is switched off, set value to None
                    active_switch = tag_attributes.get("active_switch")  # E.g. garmin_integration_active
                    if active_switch is not None:
                        tag_active = Settings.get(active_switch)
                        if tag_active is not True:  # E.g.  garmin_integration_active is False
                            self.tag_values[tag] = None
                            continue

                    source_type = tag_attributes.get("source_type")  # "sidecar_file" or "api" or None (if data read from metadata of file itself)
                    source_id = tag_attributes.get(                        "source_id")  # "JSON" (sidecar file type) or "GpsApi" (api-name) or None
                    source_parameters = tag_attributes.get("source_parameters")

                    if source_type == "sidecar_file":
                        sidecar_file_name_pattern = Settings.get('sidecar_file_source_ids').get(source_id).get(
                            'file_name_pattern')
                        sidecar_file_name_pri_1 = self.path + sidecar_file_name_pattern.replace('<file_name>',
                                                                                                self.name).replace(
                            '<ext>', self.extension)  # c:\pictures\image-Enhanced-NR-SAI.jpg.json
                        sidecar_file_name_pri_2 = self.path + sidecar_file_name_pattern.replace('<file_name>',
                                                                                                self.name_alone).replace(
                            '<ext>', self.extension)  # c:\pictures\image-Enhanced-NR-SAI.jpg.json
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

                        if sidecar_file_name is not None:  # Sidecar file exist
                            file_name_tags = file_names_tags.get(sidecar_file_name)
                            if file_name_tags is None:
                                file_names_tags[sidecar_file_name] = [tag]
                            else:
                                file_name_tags.append(tag)
                        else:
                            self.tag_values[tag] = None  # No sidecar file
                    elif source_type == "api":
                        api_tags[tag] = {"source_id": source_id,
                                         "source_parameters": source_parameters}  # e.g { "Garmin:GPSPosition": {"source_id: "GpsApi", "source_parameters": {"service_name": "garmin_connect"}}
                    else:  # Source is files own metadata
                        file_name_tags = file_names_tags.get(self.file_name)
                        if file_name_tags is None:
                            file_names_tags[self.file_name] = [tag]
                        else:
                            file_name_tags.append(tag)

            # Get values for tags in files and sidecar files  using exif-tool
            for file_name in file_names_tags:
                file_name_tags = file_names_tags.get(file_name)
                if file_name == self.file_name:
                    file_name_tags.append('XMP:MemoryMateSaveDateTime')
                    file_name_tags.append('XMP:MemoryMateSaveVersion')
                    file_name_tags.append('XMP:MemoryMateTagsHash')
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    exif_data = ex.getTags(file_name, file_name_tags, process_id='READ')
                for tag in file_name_tags:
                    tag_alone = tag.rstrip('#')  # Remove #-character, as it is not a part of tag-name, it is a control-character telling exiftool to deliver/recieve tag in nummeric format
                    tag_value = exif_data[0].get(tag_alone)
                    if tag_value is None or tag_value == "" or tag_value == []:
                        tag_value = None
                    else:
                        if isinstance(tag_value, list):
                            tag_value = list(map(str, tag_value))
                    self.tag_values[tag] = tag_value  # These are the physical tag name-value pairs (tag-name includes # where relevant)

            # Get values for tags with api as source
            for tag, tag_attributes in api_tags.items():
                source_id = tag_attributes.get("source_id")
                source_parameters = tag_attributes.get("source_parameters")
                if source_id == "GpsApi":
                    service_name = source_parameters.get("service_name")
                    if service_name == "garmin_connect":
                        user_name = None
                        user_id = None
                        service_user = FileMetadata.service_users.get(
                            "garmin_connect")  # Look for buffered user_name and user_id
                        if service_user is None:
                            user_name = GarminIntegration.getInstance().user_name
                            if user_name is not None:
                                user_id = GpsApi.getInstance().get_user_id("garmin_connect", user_name)
                                if user_id is not None:
                                    FileMetadata.service_users["garmin_connect"] = {"user_name": user_name,"user_id": user_id}
                        else:
                            user_name = service_user.get("user_name")
                            user_id = service_user.get("user_id")

                        if user_id is not None:
                            if 'date' in self.logical_tag_instances:
                                time_utc = self.logical_tag_instances['date'].getValue(part='utc_date_time')
                                location = GpsApi.getInstance().get_location(user_id=user_id,time_utc=time_utc)
                                if location is not None:
                                    latitude,longitude = location
                                    self.tag_values[tag] = f"{latitude:.8f},{longitude:.8f}"
                            else:
                                pending_tags.append(tag)



        # Finally map tag_values to logical_tag_instances
            for logical_tag in logical_tags:
                logical_tag_value_found = False
                logical_tag_pending = False   # Logical tag becomes pending if the under-laying tags are not all precent yet


                # Get instance of value-class for the logical tag
                logical_tag_class_name = (Settings.get('logical_tags') or {}).get(logical_tag, {}).get("value_class")
                if logical_tag_class_name is None:   # in case of tag assigned to logical tag nemed -unassigned-
                    continue
                logical_tag_class = globals().get(logical_tag_class_name) if logical_tag_class_name is not None else None
                logical_tag_instance = logical_tag_class(logical_tag=logical_tag) if logical_tag_class is not None else None
                saved_logical_tag_instance = logical_tag_class(logical_tag=logical_tag) if logical_tag_class is not None else None # Holds only what is written to file-tags, not external values (sidecar or api)

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
                    tag_access = tag_attrib.get('access')   # Some tags are only written, not read
                    source_type = tag_attrib.get('source_type')
                    if tag_access is not None:
                        if 'Read' not in tag_access:
                            continue
                    if tag in self.tag_values:
                        logical_tag_instance.setValueFromExif(value=self.tag_values[tag],exif_tag=tag)
                        if source_type is None:  # Source-type None: From file metadata itself
                            saved_logical_tag_instance.setValueFromExif(value=self.tag_values[tag],exif_tag=tag)
                    else:
                        pending_logical_tags.append(logical_tag)   # Will be found in next loop pass of while-condition
                        logical_tag_pending = True
                        break

                if logical_tag_pending:
                    continue

                if logical_tag_instance.getValue() is not None:
                    logical_tag_value_found = True
                    # print(logical_tag + " found its value in " + ",".join(map(str, logical_tag_instance.getUsedTags())))

                self.logical_tag_instances[logical_tag] = logical_tag_instance  # Save logical tag value-instance in dictionary
                self.saved_logical_tag_instances[logical_tag] = saved_logical_tag_instance

                if not logical_tag_value_found:
                    self.logical_tags_missing_value.append(logical_tag)



        if not self.tag_values.get('XMP:MemoryMateSaveDateTime'):     #Memory Mate never wrote to file before. Get fall-back tag-values for missing logical tags that has fall-back tag assigned
            self.is_virgin=True

        self.saved_tag_values = copy.deepcopy(self.tag_values)

#        self.__patchLogicalTagValuesFromOriginals()    # If a new Lightroom-export has overwritten jpg, the custom XMP-tags (MemoryMate version, save-date/time, description_only) are lost. These are recreated from original
        self.__updateLogicalTagValuesFromQueue()   #Sets self.is_virgin to False, if file found in Queue
        self.__updateLogicalTagValuesFromFallbackTags()
        self.__updateReferenceTags()
        self.__updateTagValuesFromLogicalTagValues()       # Find how tag-values would look like after save

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
                self.is_virgin = False

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
            if not (Settings.get('logical_tags') or {}).get(logical_tag, {}).get("reference_tag"):    #Continue if not a reference tag
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

    def __updateTagValuesFromLogicalTagValues(self):
        logical_tag_values = self.__logicalTagValues()
        saved_logical_tag_values = self.__savedLogicalTagValues()
        if logical_tag_values != saved_logical_tag_values:
            logical_tags_tags = Settings.get('file_type_tags').get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_instances:
                logical_tag_value = logical_tag_values.get(logical_tag)
                saved_logical_tag_value = saved_logical_tag_values.get(logical_tag)
                if logical_tag_value != saved_logical_tag_value:
                    logical_tag_tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    if logical_tag_tags is None:
                        print(logical_tag+" mangler tags")
                        pass
                    for tag in logical_tag_tags:
                        tag_access = Settings.get('tags').get(tag).get('access')
                        if 'Write' in tag_access:
                            self.tag_values[tag] = self.logical_tag_instances[logical_tag].getExifValue(tag)

    def setLogicalTagValues(self,logical_tag_values,overwrite=True,force_rewrite = False):
        due_for_queuing=False

        # Update tag-values in instance from queue
        if self.metadata_status == '':     # Metadata has already been read from file
            old_logical_tag_values = self.getLogicalTagValues()

            # Update all logical tags and then tags
            self.__updateLogicalTagValues(logical_tag_values,overwrite)
            self.__updateReferenceTags()
            self.__updateTagValuesFromLogicalTagValues()  # Find how tag-values would look like after save


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
            # Special case for consolidation should only be added once:
            if overwrite and logical_tag_values == {} and force_rewrite:
                unique_data = {'file': self.file_name, 'overwrite': overwrite, 'logical_tag_values': logical_tag_values,'force_rewrite': force_rewrite}
            else:
                unique_data = None
            metadata_write_queue.enqueue({'file': self.file_name, 'overwrite': overwrite,'logical_tag_values': logical_tag_values, 'force_rewrite': force_rewrite},unique_data)
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
        if self.is_virgin or force_rewrite or logical_tag_values != saved_logical_tag_values:
            print("Saving metadata to "+self.file_name)
            self.file_status = 'WRITING'
            logical_tags_tags = Settings.get('file_type_tags').get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_instances:
                logical_tag_value = logical_tag_values.get(logical_tag)
                saved_logical_tag_value = saved_logical_tag_values.get(logical_tag)
                if logical_tag_value != saved_logical_tag_value or force_rewrite or self.is_virgin:  # New value to be saved
                    logical_tag_tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    for tag in logical_tag_tags:
                        tag_access = Settings.get('tags').get(tag).get('access')
                        if 'Write' in tag_access:
                            if force_rewrite:
                                tag_values[tag] = self.logical_tag_instances[logical_tag].getExifValue(tag)  # fix corruptions and consolidation
                            else:
                                tag_values[tag] = self.tag_values.get(tag)    # self.tag_values already updated with latest value
            if tag_values != {} and tag_values is not None:
                tag_values['XMP:MemoryMateTagsHash'] = self.tag_values['XMP:MemoryMateTagsHash'] = self.getTagsHash()   # Hashes only tags with value
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values,'WRITE')
            self.saved_logical_tag_instances = copy.deepcopy(self.logical_tag_instances)
            self.saved_tag_values = copy.deepcopy(self.tag_values)
            self.file_status = ''
            self.is_virgin=False
