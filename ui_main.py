from PyQt6.QtWidgets import QTreeView, QMenu, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,QPushButton, QAbstractItemView, QDialog, QComboBox
from PyQt6.QtCore import Qt, QDir, QModelIndex,QItemSelectionModel, QObject, pyqtSignal
from PyQt6.QtGui import QFileSystemModel,QAction
import settings
from file_metadata_util import FileMetadata, QueueHost, FileMetadataChangedEmitter
from file_util import FileNameChangedEmitter
from ui_util import ProgressBarWidget
import os
from ui_widgets import TextLine, Text, DateTime, Date, TextSet, GeoLocation, Orientation, Rotation, Rating, ImageRotatedEmitter
import file_util
from collections import OrderedDict
from exiftool_wrapper import ExifTool
from ui_file_preview import FilePreview
from PyQt6.QtGui import QPixmap

class FileMetadataPastedEmitter(QObject):
    instance = None
    paste_signal = pyqtSignal(str)  # Filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if FileMetadataPastedEmitter.instance == None:
            FileMetadataPastedEmitter.instance = FileMetadataPastedEmitter()
        return FileMetadataPastedEmitter.instance
    def emit(self, file_name):
        self.paste_signal.emit(file_name)

class FilePanel(QScrollArea):
    instance = None
    file_metadata = None
    file_name = ''
    old_file_name = ''

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(350)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width() != event.size().width():
            self.prepareFilePanel()

    @staticmethod
    def getInstance(file_name):
        new_file_name = file_name
        if new_file_name == None:
            # Show sample photo in stead of an empty wndow
            new_file_name = "Memory Mate Sample Photo.jpg"
        if new_file_name != '' and new_file_name != FilePanel.old_file_name:
            if not os.path.exists(new_file_name):
                new_file_name = ''
        FilePanel.old_file_name = FilePanel.file_name
        FilePanel.file_name = new_file_name

        FilePanel.focus_tag = ''  # Forget focus-tag when changing to different photo
        if FilePanel.file_metadata != None and FilePanel.old_file_name != '':  # Changing to different picture: Save this pictures metadata
            FilePanel.file_metadata.save()
        if FilePanel.instance == None:
            FilePanel.instance = FilePanel()
        if FilePanel.file_name == '':
            FilePanel.file_metadata = None
        else:
            if os.path.isfile(FilePanel.file_name):
                FilePanel.file_metadata = FileMetadata.getInstance(FilePanel.file_name)

        FilePanel.instance.prepareFilePanel()
        FilePanel.old_file_name = FilePanel.file_name
        return FilePanel.instance

    @staticmethod
    def updateFilename(file_name):
        FilePanel.file_name = file_name
#       FilePanel.file_metadata = FileMetadata.getInstance(FilePanel.file_name)
#       FilePanel.instance.prepareFilePanel()

    @staticmethod
    def saveMetadata():
        if FilePanel.file_metadata != None:
            logical_tag_values = {}
            for logical_tag in FilePanel.tags:
                tag_widget = FilePanel.tags[logical_tag][1]
                if tag_widget != None:
                    logical_tag_values[logical_tag] = tag_widget.logical_tag_value()
            if logical_tag_values != {}:
                FilePanel.file_metadata.setLogicalTagValues(logical_tag_values)
                FilePanel.file_metadata.save()

    def prepareFilePanel(self):  # Happens each time a new filename is assigned or panel is resized
        scroll_position = FilePanel.instance.verticalScrollBar().value()  # Remember scroll-position
        self.takeWidget()

        FilePanel.__initializeLayout()

        if FilePanel.file_name != None and FilePanel.file_name != '':
            FilePanel.__initializeWidgets()  # Initialize all widgets, when changing to a different photo

        if FilePanel.file_name != None and FilePanel.file_name != '':
            # Prepare file-preview widget
            FilePanel.preview_widget = QLabel()
            FilePanel.file_preview = FilePreview.getInstance(FilePanel.file_name, self.width() - 60)
            if FilePanel.file_preview.pixmap != None:
                FilePanel.preview_widget.setPixmap(FilePanel.file_preview.pixmap)
                FilePanel.preview_widget.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                FilePanel.main_layout.addWidget(FilePanel.preview_widget)
            dummy_widget_for_width = QWidget()
            dummy_widget_for_width.setFixedWidth(self.width() - 60)
            FilePanel.main_layout.addWidget(dummy_widget_for_width)

            # Prepare metadata widgets and place them all in metadata_layout.
            FilePanel.metadata_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)  # No constraints
            tags = {}
            for logical_tag in FilePanel.file_metadata.logical_tag_values:
                if settings.logical_tags.get(logical_tag).get("widget") == None:
                    continue
                tags[logical_tag] = FilePanel.tags.get(logical_tag)
                tag_widget = FilePanel.tags[logical_tag][1]
                tag_widget.readFromImage()

            # Place all tags in V-box layout for metadata
            for logical_tag in tags:
                FilePanel.metadata_layout.addWidget(tags[logical_tag][0])  # Label-widget
                FilePanel.metadata_layout.addWidget(tags[logical_tag][1])  # Tag-widget
                space_label = QLabel(" ")
                FilePanel.metadata_layout.addWidget(space_label)

            FilePanel.main_layout.addLayout(FilePanel.metadata_layout)
#            FilePanel.main_widget.setFixedWidth(self.width() - 30)
            FilePanel.main_widget.setLayout(FilePanel.main_layout)
            self.setWidget(FilePanel.main_widget)


            FilePanel.instance.verticalScrollBar().setValue(scroll_position)  # Remember scroll-position

    @staticmethod
    def __initializeLayout():
        FilePanel.main_widget = QWidget()
        FilePanel.main_widget.setMinimumHeight(
            5000)  # Ensure that there is enough available place in widget for scroll-area
        FilePanel.main_layout = QVBoxLayout()
        FilePanel.main_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        FilePanel.metadata_layout = QVBoxLayout()
        FilePanel.metadata_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

    @staticmethod
    def __initializeWidgets():
        FilePanel.tags = {}
        for logical_tag in settings.logical_tags:
            tag_label = None
            tag_label_key = settings.logical_tags.get(logical_tag).get("label_text_key")
            if tag_label_key:
                tag_label = settings.text_keys.get(tag_label_key).get(settings.language)
            tag_widget_type = settings.logical_tags.get(logical_tag).get("widget")

            if tag_label:
                label_widget = QLabel(tag_label + ":")
                label_widget.setStyleSheet("color: #868686;")
            else:
                label_widget = None

            if tag_widget_type == "text_line":
                tag_widget = TextLine(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "text":
                tag_widget = Text(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "date_time":
                tag_widget = DateTime(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "date":
                tag_widget = Date(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "text_set":
                tag_widget = TextSet(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "geo_location":
                tag_widget = GeoLocation(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "orientation":
                tag_widget = Orientation(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "rotation":
                tag_widget = Rotation(FilePanel.file_name, logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            elif tag_widget_type == "rating":
                tag_widget = Rating(FilePanel.file_name, logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type]
            else:
                pass

            if settings.logical_tags.get(logical_tag).get("reference_tag"):
                tag_widget.setDisabled(True)

    @staticmethod
    def onPixmapChanged(file_name):
        if file_name == FilePanel.file_name:
            FilePanel.__instance.prepareFilePanel()  # If pixmap changed in file shown in panel, then update preview

class FileList(QTreeView):
    def __init__(self, dir_path=''):
        super().__init__()

        # Many files can be selected in one go
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        #        self.setSelectionBehavior(QAbstractItemView.SelectItems)   #6-problem guess right

        # Only show image- and video-files
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)

        self.setModel(self.model)
        self.__setFiletypeFilter(settings.file_types)
        self.hideFilteredFiles()  # Default is to hide filetered files. They can also be shown dimmed
        # by calling self.showFilteredFiles()

        self.hideColumn(2)  # Hide File-type
        self.setColumnWidth(0, 400)  # Filename
        self.setColumnWidth(1, 80)  # Filesize
        self.setColumnWidth(2, 150)  # Date modified

        column_count = self.model.columnCount()

        # Set root-path
        self.setRootPath(dir_path)

        # Prepare context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def createMenu(self, position):

        self.menu = QMenu()

        # Add actions to the menu
        action_text_key = settings.file_context_menu_actions.get("consolidate_metadata").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.consolidate_metadata = self.menu.addAction(action_text)

        action_text_key = settings.folder_context_menu_actions.get("standardize_filenames").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.standardize_filenames = self.menu.addAction(action_text)

        action_text_key = settings.file_context_menu_actions.get("copy_metadata").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.copy_metadata = self.menu.addAction(action_text)

        action_text_key = settings.file_context_menu_actions.get("paste_metadata").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.paste_metadata = self.menu.addAction(action_text)

        action_text_key = settings.file_context_menu_actions.get("patch_metadata").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.patch_metadata = self.menu.addAction(action_text)

        action_text_key = settings.file_context_menu_actions.get("paste_by_filename").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.paste_by_filename = self.menu.addAction(action_text)

        action_text_key = settings.file_context_menu_actions.get("patch_by_filename").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        self.patch_by_filename = self.menu.addAction(action_text)

        self.menu.addSeparator()
        action_text_key = settings.file_context_menu_actions.get("choose_tags_to_paste").get("text_key")
        action_text = settings.text_keys.get(action_text_key).get(settings.language)
        menu_text_line = QAction(action_text, self, enabled=False)
        self.menu.addAction(menu_text_line)  # Just a textline in menu saying "Choose what to paste"

        # Ad checkable actions for each logical tag
        self.logical_tag_actions = {}
        for logical_tag in settings.logical_tags:
            if settings.logical_tags.get(logical_tag).get(
                    "reference_tag"):  # Can't copy-paste a reference tag. It is derrived from the other tags
                continue
            if settings.logical_tags.get(logical_tag).get("widget") == None:  # Cant copy-paste tags now shown in widget
                continue

            tag_label_text_key = settings.logical_tags.get(logical_tag).get("label_text_key")
            if tag_label_text_key:
                tag_label = settings.text_keys.get(tag_label_text_key).get(settings.language)
                tag_action = QAction(tag_label, self, checkable=True)
                tag_action.setChecked(True)
                self.logical_tag_actions[logical_tag] = tag_action
                self.menu.addAction(tag_action)
                tag_action.triggered.connect(self.toggleAction)

    def openMenu(self, position):
        if not hasattr(self, 'menu'):
            self.createMenu(position)

        if not hasattr(self, 'source'):
            self.source = []
            self.source_is_single_file = False

        if self.source_is_single_file and len(self.source) == 1:  # Exactly one field selected
            self.paste_metadata.setEnabled(True)
            self.patch_metadata.setEnabled(True)
            self.paste_by_filename.setEnabled(True)
            self.patch_by_filename.setEnabled(True)
        elif len(self.source) >= 1:
            self.paste_metadata.setEnabled(False)
            self.patch_metadata.setEnabled(False)
            self.paste_by_filename.setEnabled(True)
            self.patch_by_filename.setEnabled(True)
        else:
            self.paste_metadata.setEnabled(False)
            self.patch_metadata.setEnabled(False)
            self.paste_by_filename.setEnabled(False)
            self.patch_by_filename.setEnabled(False)

        action = self.menu.exec(self.viewport().mapToGlobal(position))

        if action == self.consolidate_metadata:

            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))  # Can be both files and folders
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                self.consolidator = ConsolidateMetadata(target, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Consolidate',
                                                      self.consolidator)  # Progress-bar will start worker

        elif action == self.standardize_filenames:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))  # Can be both files and folders
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                file_name_pattern_dialog = InputFileNamePattern()
                result = file_name_pattern_dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    # Get the input values
                    file_name_pattern = file_name_pattern_dialog.getInput()
                    prefix, num_pattern, suffix = file_name_pattern

                    # Rename all files in folders and subfolders
                    self.unselectAll()
                    self.standardizer = StandardizeFilenames(target, prefix, num_pattern, suffix,
                                                             await_start_signal=True)  # worker-instance
                    self.progress_bar = ProgressBarWidget('Standardize',
                                                          self.standardizer)  # Progress-bar will start worker

        elif action == self.copy_metadata:
            self.source_is_single_file = False
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                self.source = []
                for index in self.selectedIndexes():
                    self.source.append(self.model.filePath(index))
                self.source = list(set(self.source))  # Remove duplicate filenames. Row contains one index per column

                if len(self.source) == 1:
                    if os.path.isfile(self.source[0]):
                        self.source_is_single_file = True
            else:
                self.source = []  # No item was clicked
            for sorrce_file_name in self.source:
                onMetadataCopied(sorrce_file_name)
        elif action == self.paste_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []



        elif action == self.paste_by_filename:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, match_file_name=True,
                                              await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []

        elif action == self.patch_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)
                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, overwrite=False,
                                              await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []


        elif action == self.patch_by_filename:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, overwrite=False,
                                              match_file_name=True, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []

            else:
                self.menu.target_file_name = None  # No item was clicked
        elif action == None:
            pass
        else:
            self.openMenu(position)  # Toggle one of the logical tags was chosen

    def unselectAll(self):
        self.selectionModel().clearSelection()  # Unselect any file, as soon selection will be renamed
        self.setCurrentIndex(QModelIndex())
        # self.selection_model.setCurrentIndex(QModelIndex(), QTreeView.NoIndex)

    def toggleAction(self):
        # Get the action that triggered the signal
        action = self.sender()
        is_checked = not action.isChecked()
        if is_checked:
            action.setChecked(False)
        else:
            action.setChecked(True)

    def setRootPath(self, dir_path):
        self.model.setRootPath(dir_path)
        self.setRootIndex(self.model.index(dir_path))

    def __setFiletypeFilter(self, file_types=["*.*"]):
        self.file_type_filter = []
        for file_type in file_types:
            file_type_filter_item = "*." + file_type
            self.file_type_filter.append(file_type_filter_item)
        self.model.setNameFilters(self.file_type_filter)

    def hideFilteredFiles(self):
        self.model.setNameFilterDisables(False)  # Filtered files are not shown

    def showFilteredFiles(self):
        self.model.setNameFilterDisables(True)  # Filtered files are shown as dimmed, and are not selectable

    def currentChanged(self, current, previous):  # Redefinet method called at event "current file changed"
        chosen_path = self.model.filePath(current)
        previous_path = self.model.filePath((previous))
        if chosen_path != previous_path:
            if os.path.isfile(chosen_path):
                CurrentFileChangedEmitter.getInstance().emit(chosen_path)

    def getOpenFolders(self):
        open_folders = []
        stack = []
        root_index = self.model.index(self.rootIndex().data())
        if self.model.hasChildren(root_index):  # Check if the current index has children (i.e., is a directory)
            child_count = self.model.rowCount(root_index)
            for i in range(child_count):
                child_index = self.model.index(i, 0, root_index)
                stack.append(child_index)

        while stack:
            current_index = stack.pop()
            if self.isExpanded(current_index):
                current_file_info = self.model.fileInfo(current_index)
                if current_file_info.isDir():
                    open_folders.append(current_file_info.absoluteFilePath())

                child_count = self.model.rowCount(current_index)
                for i in range(child_count):
                    child_index = self.model.index(i, 0, current_index)
                    stack.append(child_index)
        return list(set(open_folders))

    def getSelectedItems(self):
        selected_items = []
        selected_indexes = self.selectedIndexes()

        for index in selected_indexes:
            if index.column() == 0:
                selected_file_info = self.model.fileInfo(index)
                selected_items.append(selected_file_info.absoluteFilePath())
        return list(set(selected_items))

    def setOpenFolders(self, open_folders=[]):
        if open_folders:
            for open_folder in open_folders:
                # Find the QModelIndex corresponding to the folder_path
                folder_index = self.model.index(open_folder)
                if folder_index.isValid():  # Check if the folder exists in the model
                    # Expand the folder
                    self.setExpanded(folder_index, True)

    def setSelectedItems(self, selected_items=[]):
        self.clearSelection()
        if selected_items:
            for selected_item in selected_items:
                # Find the QModelIndex corresponding to the item_path
                item_index = self.model.index(selected_item)
                if item_index.isValid():  # Check if the item exists in the model
                    # Select the item
                    self.selectionModel().select(item_index, QItemSelectionModel.SelectionFlag.Select)

class SettingsWheeel(QLabel):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap('settings.png').scaled(20,20)
        self.setPixmap(pixmap)
        self.mousePressEvent = self.onMousePress
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave
    def onEnter(self,event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def onLeave(self,event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

    def onMousePress(self,event):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Prepare window
        window_title = settings.text_keys.get("settings_window_title").get(settings.language)
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 400, 200)
        settings_layout = QVBoxLayout()
        self.setLayout(settings_layout)

        # Add language selection box
        self.language_combobox = QComboBox(self)
        for index, (key, value) in enumerate(settings.languages.items()):
            self.language_combobox.addItem(key+" - "+value)
            if key == settings.language:
                self.language_combobox.setCurrentIndex(index)
        language_label = QLabel(settings.text_keys.get("settings_labels_application_language").get(settings.language), self)
        language_layout = QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        settings_layout.addLayout(language_layout)

        # Connect the ComboBox's item selection to a slot
        self.language_combobox.currentIndexChanged.connect(self.onLanguageSelected)

    def onLanguageSelected(self, index):
        settings.settings["language"] = self.language_combobox.currentText()[:2]
        settings.writeSettingsFile()

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
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

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
            file_name_pattern.append("*."+filetype)

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
        sorted_files_missing_date = [d for d in sorted_files if d.get('date') == '' or d.get('date') == None]
        sorted_files_missing_date = sorted(sorted_files_missing_date, key=lambda x: x['name_alone'])
        sorted_files_with_date = [d for d in sorted_files if d.get('date') != '' and d.get('date') != None]
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
            try:
                ExifTool.close(close_read_process=False,
                               close_write_process=True)  # Close write-process, so that data in queue can be changed safely
                QueueHost.get_instance().stop_queue_worker()  # Make sure not to collide with update of metadata

                renamer.start()
                QueueHost.get_instance().start_queue_worker()  # Start Queue-worker again
            except Exception as e:
                self.error_signal.emit(e,False)
                self.done_signal.emit()
                return

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
                        file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
                        file_metadata_pasted_emitter.emit(file_name)

        self.done_signal.emit()

class CopyLogicalTags(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self, source, target, logical_tags, match_file_name=False, overwrite=True, await_start_signal=False):
        super().__init__()

#       Source and target converted to list of files
        file_name_pattern=[]
        for filetype in settings.file_types:
            file_name_pattern.append("*."+filetype)
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
            source_file_name = source_target[0]
            target_file_name = source_target[1]
            source_file_metadata = FileMetadata.getInstance(source_file_name)
            target_file_metadata = FileMetadata.getInstance(target_file_name)
            self.progress_signal.emit(index + 1)
            target_tag_values = {}
            for logical_tag in self.logical_tags:
                source_tag_value = None
                source_tag_value = source_file_metadata.logical_tag_values.get(logical_tag)
                if source_tag_value != None:
                    target_tag_values[logical_tag] = source_tag_value
            target_file_metadata.setLogicalTagValues(target_tag_values, self.overwrite)
            target_file_metadata.save()
            file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
            file_metadata_pasted_emitter.emit(target_file_name)
        self.done_signal.emit()

class ConsolidateMetadata(QObject):
# This class force-saves logical tags to all physical tags in files

    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)            # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)  # Sends exception and retry_allowed (true/false)


    def __init__(self,target, await_start_signal=False):
        # target is a filename, a foldername, a list of filenames or a list of folder-names
        super().__init__()
        self.target=target
        if not await_start_signal:
            self.start()

    def start(self):
        file_name_pattern=[]
        for filetype in settings.file_types:
            file_name_pattern.append("*."+filetype)
        file_names = []
        if isinstance(self.target, list):
            for file_path in self.target:
                file_names.extend(file_util.getFileList(root_folder=file_path,recursive=True,pattern=file_name_pattern))
        else:
            file_names.extend(file_util.getFileList(root_folder=self.target, recursive=True, pattern=file_name_pattern))
        file_count = len(file_names)
        self.progress_init_signal.emit(file_count)

        # Consolidate file metadata force-saving
        for index, file_name in enumerate(file_names):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file_name)
            file_metadata.save(force_rewrite=True)
            file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
            file_metadata_pasted_emitter.emit(file_name)

        self.done_signal.emit()

class InputFileNamePattern(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add labels and input fields
        prefix_label = QLabel("Prefix:")

        self.prefix = QLineEdit()
        layout.addWidget(prefix_label)
        layout.addWidget(self.prefix)

        num_pattern_label = QLabel("Number Pattern:")
        self.num_pattern = QLineEdit()
        layout.addWidget(num_pattern_label)
        layout.addWidget(self.num_pattern)

        suffix_label = QLabel("Suffix:")
        self.suffix = QLineEdit()
        layout.addWidget(suffix_label)
        layout.addWidget(self.suffix)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

    def getInput(self):
        # Return the input values as a tuple
        return (self.prefix.text(), self.num_pattern.text(), self.suffix.text())

class CurrentFileChangedEmitter(QObject):
    instance = None
    change_signal = pyqtSignal(str)  # Old filename, new filename

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if CurrentFileChangedEmitter.instance == None:
            CurrentFileChangedEmitter.instance = CurrentFileChangedEmitter()
        return CurrentFileChangedEmitter.instance
    def emit(self, new_file_name):
        self.change_signal.emit(new_file_name)

def onMetadataChanged(file_name,old_logical_tags,new_logical_tags):
    pass

def onMetadataCopied(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()   # ..not to copy old data, save what is in screen

def onMetadataPasted(file_name):
    if file_name == FilePanel.file_name:
        dummy = FilePanel.getInstance(file_name)   #Triggers update of Filepanel

def onFileRenamed(old_file_name, new_file_name):     # reacts on change filename signal from
    # Update filename in file-panel
    if FilePanel.file_name == old_file_name:
        FilePanel.updateFilename(new_file_name)

    # Update filename in preview-instance
    file_preview = FilePreview.instance_index.get(old_file_name)
    if file_preview:
        file_preview.updateFilename(new_file_name)

    # Update filename in metadata-instance
    file_metadata = FileMetadata.instance_index.get(old_file_name)
    if file_metadata:
        file_metadata.updateFilename(new_file_name)

    # Update fileename in queue
    json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
    json_queue_file.change_queue(find={'file': old_file_name}, change={'file': new_file_name})

def onCurrentFileChanged(new_file_name):
    FilePanel.saveMetadata()                      # Saves metadata for file currently in filepanel (if any)
    dummy = FilePanel.getInstance(new_file_name)  # Puts new file in file-panel

def onImageRotated(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()
        file_preview = FilePreview.instance_index.get(file_name)  # Get existing preview, if exist
        if file_preview:
            file_preview.updatePixmap()
            FilePanel.preview_widget.setPixmap(file_preview.pixmap)


file_metadata_changed_emitter = FileMetadataChangedEmitter.getInstance()
file_metadata_changed_emitter.change_signal.connect(onMetadataChanged)

file_name_changed_emitter = FileNameChangedEmitter.getInstance()
file_name_changed_emitter.change_signal.connect(onFileRenamed)

current_file_changed_emitter = CurrentFileChangedEmitter.getInstance()
current_file_changed_emitter.change_signal.connect(onCurrentFileChanged)

file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
file_metadata_pasted_emitter.paste_signal.connect(onMetadataPasted)

image_rotated_emitter = ImageRotatedEmitter.getInstance()
image_rotated_emitter.rotate_signal.connect(onImageRotated)

