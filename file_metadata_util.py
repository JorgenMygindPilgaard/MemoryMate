import copy
import os
from exiftool_wrapper import ExifTool
from PyQt6.QtCore import QThread, QCoreApplication,QObject,pyqtSignal,QSize, Qt
from PyQt6.QtGui import QMovie, QPixmap, QImage,QTransform, QImageReader
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QSizePolicy
import settings
import time
import file_util, sys
import pillow_heif
import rawpy
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

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
    def emit(self, file_name, old_logical_tag_values, new_logical_tag_values):
        self.change_signal.emit(file_name, old_logical_tag_values, new_logical_tag_values)

class FileMetadata(QObject):
    app_path = sys.argv[0]
    app_dir = os.path.dirname(os.path.abspath(app_path))
    exif_executable = os.path.join(app_dir, 'exiftool_memory_mate.exe')
    exif_configuration = os.path.join(app_dir, 'exiftool_memory_mate.cfg')
#    exif_executable = os.path.join(settings.app_data_location, 'exiftool_memory_mate.exe')
#    exif_configuration = os.path.join(settings.app_data_location, 'exiftool.cfg')
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
        if not os.path.isfile(file_name):
            raise FileNotFoundError('File '+file_name+' does not exist')

        # Set data for filename
        FileMetadata.instance_index[file_name]=self
        # Statuses to ensure correct multithread-access to data
        self.file_status = 'PENDING_READ'       # A lock telling status of file-read/write: PENDING_READ, READING, WRITING, QUEUING <blank>
        self.metadata_status = 'PENDING_READ'   # A lock telling status of metadata-variables: PENDING_READ, READING, WRITING, <blank>

        self.file_name = file_name
        self.split_file_name = file_util.splitFileName(file_name)  # ["c:\pictures\", "my_picture", "jpg"]
        self.path = self.split_file_name[0]                        # "c:\pictures\"
        self.name_alone = self.split_file_name[1]                  # "my_picture"
        self.is_virgin=False                                       # "Virgin means memory_mate never wrote metadata to file before. Assume not virgin tll metadata has been read

    @staticmethod
    def getInstance(file_name):
        file_metadata = FileMetadata.instance_index.get(file_name)
        if file_metadata is None:
            FileMetadata.getInstance_active = True
            file_metadata = FileMetadata(file_name)
            FileMetadata.getInstance_active = False
        return file_metadata

    def getStatus(self):       # Status can be PENDING_READ (Metadata not yet read from file), READ (Metadata being read) or <blank> (Metadata read)
        return self.metadata_status
    def getFileType(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is '+ self.metadata_status)
        return self.type

    def getLogicalTagValues(self):
        if self.metadata_status != '':
            raise Exception('Metadata not yet read. status is ' + self.metadata_status)
        return self.logical_tag_values
    def __readFileType(self):
        file_type = self.split_file_name[2]
        tags = ['File:FileTypeExtension']
        with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
            exif_data = ex.getTags(self.file_name, tags, process_id='READ')
        tag_value = exif_data[0].get('File:FileTypeExtension')
        if not tag_value is None:
            file_type = tag_value
        self.type = file_type

    def readLogicalTagValues(self):
        if self.metadata_status != 'PENDING_READ':   # Means that some other thread is reading or writing to metadata-variables
            return
        self.metadata_status = 'READING'
        self.__readFileType()
        #Get names of tags in tags for the filetype from settings
        logical_tags_tags = settings.file_type_tags.get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        if logical_tags_tags is None:    # Filename blank or unknown filetype
            return {}    # logical tag values as empty dictionary "
        tags = []                                           #These are the physical tags

        for logical_tag in logical_tags_tags:
            tags.extend(logical_tags_tags[logical_tag])

        # Now get values for these tags using exif-tool
        with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
            exif_data = ex.getTags(self.file_name, tags,process_id='READ')
        tag_values = {}
        for tag in tags:
            tag_alone = tag.rstrip('#')               #Remove #-character, as it is not a part of tag-name, it is a controll-character telling exiftool to deliver/recieve tag in nummeric format
            tag_value = exif_data[0].get(tag_alone)
            if tag_value != None and tag_value != "" and tag_value != []:
                if isinstance(tag_value,list):
                    tag_value = list(map(str, tag_value))
                if tag_alone == 'Composite:GPSPosition':
                    tag_value = tag_value.replace(' ',',',1)    # Hack: ExifTool delivers space-saparated but expect comma-separated on updates
                if tag_alone == 'XMP-microsoft:RatingPercent':  # Hack: Map rating-percent to a scale from 0-5 1>1, 25>2, 50>3, 75>4, 100>5
                    if tag_value != 1:
                        tag_value = int((tag_value + 25)/25)
                tag_values[tag] = tag_value

        # Finally map tag_values to logical_tag_values
        self.logical_tag_values = {}
        logical_tags_missing_value = []
        for logical_tag in logical_tags_tags:
            logical_tag_data_type = settings.logical_tags.get(logical_tag).get("data_type")
            logical_tag_tags = logical_tags_tags.get(logical_tag)
            if logical_tag_data_type == 'list':
                tag_value = []
            elif logical_tag_data_type == 'string':
                tag_value = ''
            else:
                tag_value = None

            self.logical_tag_values[logical_tag] = tag_value  # Set to empty value to begin with"

            logical_tag_value_found = False
            for tag in logical_tag_tags:
                tag_value = tag_values.get(tag)
                if tag_value:
                    logical_tag_value_found = True
                if logical_tag_data_type != 'list' and isinstance(tag_value, list):     # If e.g. Author contains multiple entries. Concatenate to a string then
                    tag_value = ', '.join(str(tag_value))
                if logical_tag_data_type == 'list' and isinstance(tag_value, str):      # If e.g. persons contains only one entrie, exiftool returns it as a string, not a list
                    tag_value = [tag_value]
                if tag_value != None and tag_value != '':
                    self.logical_tag_values[logical_tag] = tag_value
                    break
            if not logical_tag_value_found:
                logical_tags_missing_value.append(logical_tag)

        self.saved_logical_tag_values = copy.deepcopy(self.logical_tag_values)
        self.confirmed_logical_tag_values = copy.deepcopy(self.logical_tag_values)

        # Update logical tags in memory from queue-file (Queue originates from previous run)
        json_queue = file_util.JsonQueue.getInstance(settings.queue_file_path)
        for queue_entry in json_queue.queue:
            if queue_entry.get('file') == self.file_name:
                queue_logical_tag_values = queue_entry.get('logical_tag_values')
                if queue_logical_tag_values != None and queue_logical_tag_values != {}:
                    self.setLogicalTagValues(queue_logical_tag_values,supress_signal=True)
                    for queue_logical_tag in queue_logical_tag_values:
                        while queue_logical_tag in logical_tags_missing_value:
                            logical_tags_missing_value.remove(queue_logical_tag)

        self.confirmed_logical_tag_values = copy.deepcopy(self.logical_tag_values)    # Confirmed means that tag has been put in queue

        # Read fallback_tag (if assigned) into missing logical tags
        if not tag_values.get('XMP:MemoryMateSaveDateTime'):     #Memory Mate never wrote to file before. Get fall-back tag-values for missing logical tags that has fall-back tag assigned
            self.is_virgin=True
            for logical_tag in logical_tags_missing_value:
                fallback_tag = settings.logical_tags.get(logical_tag).get('fallback_tag')
                if fallback_tag:
                    fallback_tag_value = self.logical_tag_values.get(fallback_tag)
                    if fallback_tag_value:
                        self.logical_tag_values[logical_tag] = fallback_tag_value
        self.metadata_status = ''


    def __updateReferenceTags(self):
        first = True
        logical_tags_tags = settings.file_type_tags.get(self.type.lower())  #Logical_tags for filetype with corresponding tags
        for logical_tag in logical_tags_tags:
            if not settings.logical_tags[logical_tag].get("reference_tag"):    #Continue if not a reference tag
                continue

            logical_tag_value = ''
            for tag_content in settings.logical_tags[logical_tag].get("reference_tag_content"):
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
                        label_key = settings.logical_tags.get(ref_logical_tag).get("label_text_key")
                        label = settings.text_keys.get(label_key).get(settings.language)
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
            if self.logical_tag_values[logical_tag] != self.confirmed_logical_tag_values.get(logical_tag):
                updated_logical_tag_values[logical_tag] = self.logical_tag_values[logical_tag]

        # Put in queue if something to do
        if updated_logical_tag_values != {} or force_rewrite:
            json_queue_file=file_util.JsonQueue.getInstance(settings.queue_file_path)
            json_queue_file.enqueue({'file': self.file_name, 'logical_tag_values': updated_logical_tag_values, 'force_rewrite': force_rewrite})
            self.confirmed_logical_tag_values = copy.deepcopy(self.logical_tag_values)
            QueueHost.get_instance().start_queue_worker()    # Make Queue-host instance start Queue-worker, if it is not running

    def __update_file(self, force_rewrite):
        if self.logical_tag_values != self.saved_logical_tag_values or force_rewrite or self.is_virgin:
            logical_tags_tags = settings.file_type_tags.get(self.type.lower())
            tag_values = {}
            for logical_tag in self.logical_tag_values:

                #               logical_tag_type = settings.logical_tags.get(logical_tag)
                if self.logical_tag_values[logical_tag] != self.saved_logical_tag_values.get(
                        logical_tag) or force_rewrite or self.is_virgin:  # New value to be saved
                    tags = logical_tags_tags.get(logical_tag)  # All physical tags for logical tag"
                    for tag in tags:
                        tag_value = self.logical_tag_values[logical_tag]
                        if tag == 'XMP-microsoft:RatingPercent':
                            if tag_value != 1 and tag_value != None:                      # Hack: Map rating scale from 0-5 to rating-percent 1>1, 2>25, 3>50, 4>75, 5>100
                                tag_value = (tag_value-1) * 25
                        tag_values[tag] = tag_value

            if tag_values != {} and tag_values != None:
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values,'WRITE')

            self.confirmed_logical_tag_values = copy.deepcopy(self.logical_tag_values)
            self.saved_logical_tag_values = copy.deepcopy(self.logical_tag_values)

    def setLogicalTagValues(self,logical_tag_values,overwrite=True,supress_signal=False):
        if self.metadata_status == '':     # Ready to set values, when status in blank
            pass
        elif supress_signal and self.metadata_status == 'READING':    # Setting values from queue furing read is allowed
            pass
        else:
            raise Exception('Can´t set tag-values. Status is ' + self.metadata_status)   # setting values during read, write or if read is pending, is not allowed

        if not supress_signal:    # If not reading, set status to updating
            self.status = 'UPDATING'

        old_logical_tag_values = copy.deepcopy(self.logical_tag_values)
        for logical_tag in logical_tag_values:
            if not logical_tag in old_logical_tag_values:          # If the file-type does not support the logical tag, then skip it
                continue
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
        if not supress_signal:    # If not reading, clear status
            self.metadata_status = ''
        if self.logical_tag_values != old_logical_tag_values and not supress_signal:
            self.change_signal.emit(self.file_name, old_logical_tag_values, self.logical_tag_values)
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
        if self.metadata_status != '':
            raise Exception('Can´t save tag-values. Status is ' + self.metadata_status)   # saving values during read, write, update, queuing  or if read is pending, is not allowed

        if put_in_queue:
            self.file_status = 'QUEUING'
            self.__updateReferenceTags()
            self.__put_in_queue(force_rewrite)
            self.file_status = ''
        else:
            self.file_status = 'WRITING'
            self.__updateReferenceTags()
            self.__update_file(force_rewrite)
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

    def run(self):
        self.waiting.emit()
        self.about_to_quit.connect(self.onAboutToQuit)
        json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
        json_queue_file.queue_size_changed.connect(self.onQueueSizeChanged)
        while True:
            queue_entry = json_queue_file.dequeue()
            if queue_entry:
                self.processing.emit()
                file = queue_entry.get('file')
                logical_tag_values = queue_entry.get('logical_tag_values')
                force_rewrite = queue_entry.get('force_rewrite')
                try:
                    file_metadata = FileMetadata.getInstance(file)
                    file_metadata.readLogicalTagValues()
                    while file_metadata.getStatus() != '':    # If instance being processed, wait for it to finalize
                        status = file_metadata.getStatus()     # Line added to be able to see status during debugging
                        time.sleep(self.delay)
                    file_metadata.save(force_rewrite=force_rewrite, put_in_queue=False)
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
            self.queue_worker = None
            self.queue_worker_running = False
            self.queue_worker_processing = False

class QueueStatusMonitor(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.queue_host = QueueHost.get_instance()
        self.queue_host.queue_size_changed.connect(self.onQueueSizeChanged)

    def init_ui(self):

        # Create a label for displaying the queue size
        self.queue_size_label = QLabel("")
        self.queue_size_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Load the processing.gif and display it using a QMovie
        self.movie = QMovie("processing.gif")
        self.movie.setScaledSize(QSize(25,18))


        # Set the maximum height for the gif label to match the queue size label
        self.gif_label = QLabel()
#        self.gif_label.setMaximumHeight(self.queue_size_label.sizeHint().height())
        self.gif_label.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)  # Set size policy

        # Create an empty label to take up space
        self.space_label = QLabel()
        self.space_label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

        # Create a horizontal layout and add the widgets
        self.addWidget(self.gif_label)
        self.addWidget(self.queue_size_label)
        self.addWidget(self.space_label)

    def onQueueSizeChanged(self, size):
        self.queue_size_label.setText(str(size))
        if size > 0:
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.queue_size_label.clear()
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
                FileReadQueue.last_appended_file = file_name
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
        FileMetadata.getInstance(file_name).readLogicalTagValues()
        FilePreview.getInstance(file_name).readImage()
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
        self.file_name = file_name
        self.panel_width = 0
        self.image = None
        self.pixmap = None
        self.original_rotation = None
        self.status = 'PENDING_READ'   # A lock telling status of metadata-variables: PENDING_READ, READING, WRITING, <blank>
        FilePreview.instance_index[file_name] = self
        self.web_server = None

    def readImage(self):
        if self.status != 'PENDING_READ':
            return
        file_type = FileMetadata.getInstance(self.file_name).getFileType()

        # Read image from file
        if self.image == None:     # Only read image from file once
            if file_type == 'heic':
                self.image = self.__heic_to_qimage(self.file_name)
            elif file_type == 'cr2' or file_type == 'cr3' or file_type == 'arw' or file_type == 'nef' or file_type == 'dng':
                 self.image = self.__raw_to_qimage(self.file_name)
            elif file_type == 'mov' or file_type == 'mp4':
                self.image = self.__movie_to_qimage(self.file_name)
            else:
                self.image = self.__default_to_qimage(self.file_name)
            if self.image != None:
                if self.image.height()>1500 or self.image.width()>1500:
                    self.image = self.image.scaled(1500,1500,Qt.AspectRatioMode.KeepAspectRatio)
        if FilePreview.latest_panel_width != 0:
            self.__setPixmap(FilePreview.latest_panel_width)
        self.status = ''


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
            ratio_width  = panel_width / image.width()
            ratio_height = panel_width / image.height() / 16 * 9   # Image same height as a 9/16 landscape filling screen-width
            ratio = min(ratio_width,ratio_height)

            width = int(image.width() * ratio)
            height = int(image.height() * ratio)

            self.pixmap = QPixmap.fromImage(image)
            self.pixmap = self.pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        else:
            self.pixmap = None

    def getImage(self):
        file_type = FileMetadata.getInstance(self.file_name).type

        # Set right rotation/orientation
        if file_type == 'mov' or file_type == 'mp4':
            image = self.image
        elif file_type == 'heic':
            image = self.__rotatedImage()
        else:
            image = self.__orientedImage()
        return image

    def __orientedImage(self):
        # Apply transformations based on EXIF orientation
        if self.image == None:
            return None
        else:
            orientation = FileMetadata.getInstance(self.file_name).logical_tag_values.get("orientation")
            transform = QTransform()
            if orientation == None:
                orientation = 1             #Horizontal (normal), Default orientation
            if orientation == 1:            #Horizontal (normal)'
                transform.rotate(0)
            if orientation == 3:            #Rotate 180'
                transform.rotate(180)
            elif orientation == 6:          #Rotate 90 CW':
                transform.rotate(90)
            elif orientation == 8:          #Rotate 270 CW'
                transform.rotate(270)

            # Apply transformation to the QImage
            oriented_image = self.image.transformed(transform)
            return oriented_image

    def __rotatedImage(self):
        if self.image == None:
            return None
        else:
            rotation = FileMetadata.getInstance(self.file_name).logical_tag_values.get("rotation")
            if rotation == None:
                rotation = 0.
            if self.original_rotation == None:
                saved_rotation = FileMetadata.getInstance(self.file_name).saved_logical_tag_values.get("rotation")
                if saved_rotation != None:
                    self.original_rotation = saved_rotation
                else:
                    self.original_rotation = 0

            rotation_change = self.original_rotation - rotation
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
            video_clip = VideoFileClip(file_name)
            thumbnail = video_clip.get_frame(0)  # Get the first frame as the thumbnail
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



































