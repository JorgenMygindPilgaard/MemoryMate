import copy
from exiftool_wrapper import ExifTool
import os
from PyQt6.QtCore import QThread, QCoreApplication,QObject,pyqtSignal,QSize
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QSizePolicy
import settings
import time
import file_util, sys


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

        for logical_tag in logical_tags_tags:
            tags.extend(logical_tags_tags[logical_tag])

        # Now get values for these tags using exif-tool
        with ExifTool(executable=self.exif_executable,configuration=self.exif_configuration) as ex:
            exif_data = ex.getTags(self.file_name, tags)
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
                if logical_tag_data_type != 'list' and isinstance(tag_value, list):     #E.g. Author contains multiple entries. Concatenate t0 a string then
                    tag_value = ', '.join(str(tag_value))
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
                            if tag_value != 1:                      # Hack: Map rating scale from 0-5 to rating-percent 1>1, 2>25, 3>50, 4>75, 5>100
                                tag_value = (tag_value-1) * 25
                        tag_values[tag] = tag_value

            if tag_values != {} and tag_values != None:
                with ExifTool(executable=self.exif_executable, configuration=self.exif_configuration) as ex:
                    ex.setTags(self.file_name, tag_values)

            self.confirmed_logical_tag_values = copy.deepcopy(self.logical_tag_values)
            self.saved_logical_tag_values = copy.deepcopy(self.logical_tag_values)

    def setLogicalTagValues(self,logical_tag_values,overwrite=True,supress_signal=False):
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
        self.__updateReferenceTags()
        if put_in_queue:
            self.__put_in_queue(force_rewrite)
        else:
            self.__update_file(force_rewrite)
        self.is_virgin=False

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




































