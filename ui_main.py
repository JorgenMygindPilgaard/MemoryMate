import copy
import subprocess
import sys
from language import getText

from PyQt6.QtWidgets import QTreeView, QMenu, QScrollArea, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QAbstractItemView, QDialog, QComboBox, QApplication, QCheckBox, QTextEdit
from PyQt6.QtCore import QModelIndex, Qt, QDir, QModelIndex,QItemSelectionModel, QObject, pyqtSignal
from PyQt6.QtGui import QFileSystemModel,QAction

import lightroom_integration
import settings
from file_metadata_util import FileMetadata, QueueHost, FileMetadataChangedEmitter, FileReadQueue, FileReadyEmitter, FilePreview
from file_util import FileRenameDoneEmitter, getFileList,splitFileName,FolderSelectorDialog
from ui_status import UiStatusManager
from ui_util import ProgressBarWidget
import os
from ui_widgets import TextLine, Text, DateTime, Date, TextSet, GeoLocation, Rotation, Rating, ImageRotatedEmitter
import file_util
from collections import OrderedDict
from exiftool_wrapper import ExifTool
from PyQt6.QtGui import QPixmap
import webbrowser
import time
import shutil


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
    file_preview = None
    preview_widget = None
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
            new_file_name = os.path.join(settings.resource_path,"Memory Mate Sample Photo.jpg")
        if new_file_name != '' and new_file_name != FilePanel.old_file_name:
            if not os.path.exists(new_file_name):
                new_file_name = ''
        FilePanel.old_file_name = FilePanel.file_name
        FilePanel.file_name = new_file_name

        # If first chosen image, instantiate filepanel
        if FilePanel.instance == None:
            FilePanel.instance = FilePanel()

        # Save metadata from previous file
        FilePanel.focus_tag = ''  # Forget focus-tag when changing to different photo

        # Get instances of metadata and preview
        if FilePanel.file_name == '':
            FilePanel.file_metadata = None
            FilePanel.file_preview = None
        else:
            if os.path.isfile(FilePanel.file_name):
                FilePanel.file_metadata = FileMetadata.getInstance(FilePanel.file_name)
                FilePanel.file_preview = FilePreview.getInstance(FilePanel.file_name)

        # Prepare panel, if preview and metadata is ready (else, the file-ready-event will trigger preparing panel later
        if FilePanel.file_metadata != None and FilePanel.file_preview != None:
            if FilePanel.file_metadata.getStatus() == '' and FilePanel.file_preview.getStatus() == '':
                FilePanel.instance.prepareFilePanel()
        return FilePanel.instance

    @staticmethod
    def updateFilename(file_name):
        FilePanel.file_name = file_name

    @staticmethod
    def saveMetadata():
        if FilePanel.file_metadata != None:
            if FilePanel.file_metadata.getStatus() != '':    # File being processed proves that metadata not changed by user in UI. No need for update from screen
                return
            logical_tag_values = {}
            for logical_tag in FilePanel.tags:
                tag_widget = FilePanel.tags[logical_tag][1]
                if tag_widget != None:
                    logical_tag_values[logical_tag] = tag_widget.logical_tag_value()
            if logical_tag_values != {}:
                FilePanel.file_metadata.setLogicalTagValues(logical_tag_values)

    def prepareFilePanel(self):  # Happens each time a new filename is assigned or panel is resized
        if FilePanel.file_metadata != None and FilePanel.file_preview != None:      # Skip, if metadata or preview not yet ready
            if FilePanel.file_metadata.getStatus() != '' or FilePanel.file_preview.getStatus() != '':
                return

        scroll_position = FilePanel.instance.verticalScrollBar().value()  # Remember scroll-position
        self.takeWidget()

        FilePanel.__initializeLayout()

        if FilePanel.file_name != None and FilePanel.file_name != '':
            FilePanel.__initializeWidgets()  # Initialize all widgets, when changing to a different photo

        if FilePanel.file_name != None and FilePanel.file_name != '':
            # Prepare file-preview widget
            FilePanel.preview_widget = QLabel()
            file_preview_pixmap = FilePanel.file_preview.getPixmap(panel_width=self.width() - 60)
            if file_preview_pixmap != None:
                FilePanel.preview_widget.setPixmap(file_preview_pixmap)
                FilePanel.preview_widget.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                FilePanel.main_layout.addWidget(FilePanel.preview_widget)

                # Connect the context menu to the QLabel
                FilePanel.preview_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                FilePanel.preview_widget.customContextMenuRequested.connect(self.showContextMenu)

            dummy_widget_for_width = QWidget()
            dummy_widget_for_width.setFixedWidth(self.width() - 60)
            FilePanel.main_layout.addWidget(dummy_widget_for_width)

            # Prepare metadata widgets and place them all in metadata_layout.
            FilePanel.metadata_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)  # No constraints
            tags = {}
            logical_tags_values = FilePanel.file_metadata.getLogicalTagValues()
            for logical_tag in FilePanel.file_metadata.getLogicalTagValues():
                if settings.logical_tags.get(logical_tag) == None: # Is the case for parts, e.g date.utc_offset
                    continue
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
            FilePanel.main_widget.setLayout(FilePanel.main_layout)
            self.setWidget(FilePanel.main_widget)


            FilePanel.instance.verticalScrollBar().setValue(scroll_position)  # Remember scroll-position

    def showContextMenu(self, pos):
        context_menu = QMenu()

        # Add the "Open in Browser" action to the context menu
        open_in_browser_action_text = getText("preview_menu_open_in_browser")
        open_in_browser_action = QAction(open_in_browser_action_text)
        open_in_browser_action.triggered.connect(FilePanel.openInBrowser)
        context_menu.addAction(open_in_browser_action)

        # Add the "Open in Default Program" action to the context menu
        open_in_default_program_action_text = getText("preview_menu_open_in_default_program")
        open_in_default_program_action = QAction(open_in_default_program_action_text)
        open_in_default_program_action.triggered.connect(FilePanel.openInDefaultProgram)
        context_menu.addAction(open_in_default_program_action)


        # Show the context menu at the specified position
        context_menu.exec(FilePanel.preview_widget.mapToGlobal(pos))

    def openInBrowser(self):
        if FilePanel.file_preview != None:
            current_image_path = os.path.join(settings.app_data_location, "current_image.jpg")
            FilePanel.file_preview.getImage().save(current_image_path)
            current_image_html_path = os.path.join(settings.app_data_location, "current_image.html")
            webbrowser.open(current_image_html_path)

    def openInDefaultProgram(self):
        try:
            os.startfile(FilePanel.file_name)
        except Exception as e:
            pass


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
            new_line = settings.logical_tags.get(logical_tag).get("new_line")
            if new_line == None:
                new_line = True
            tag_label_key = settings.logical_tags.get(logical_tag).get("label_text_key")
            if tag_label_key:
                tag_label = getText(tag_label_key)
            tag_widget_type = settings.logical_tags.get(logical_tag).get("widget")

            if tag_label:
                label_widget = QLabel(tag_label + ":")
                label_widget.setStyleSheet("color: #868686;")
            else:
                label_widget = None

            if tag_widget_type == "TextLine":
                tag_widget = TextLine(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "Text":
                tag_widget = Text(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "DateTime":
                tag_widget = DateTime(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "Date":
                tag_widget = Date(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "TextSet":
                tag_widget = TextSet(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "GeoLocation":
                tag_widget = GeoLocation(FilePanel.file_name,logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "Rotation":
                tag_widget = Rotation(FilePanel.file_name, logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
            elif tag_widget_type == "Rating":
                tag_widget = Rating(FilePanel.file_name, logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget, tag_widget_type, new_line]
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

        # Prepare ontext menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def createMenu(self, position):

        self.actions = {}   # {action: id}
        self.menues = {"file_context_menu": QMenu()}

        for file_context_menu_entry in settings.file_context_menu:
            parent_menu_id = file_context_menu_entry.get('parent_id')
            entry_type = file_context_menu_entry.get("type")
            parent_menu = self.menues.get(parent_menu_id)

            if entry_type == "menu":
                menu = QMenu(getText(file_context_menu_entry.get("text_key")))
                self.menues[file_context_menu_entry.get("id")]=menu
                parent_menu.addMenu(menu)
            elif entry_type == 'action':   #action
                action = QAction(getText(file_context_menu_entry.get("text_key")))
                self.actions[file_context_menu_entry.get("id")] = action
                parent_menu.addAction(action)
            elif entry_type == 'text':
                action = QAction(getText(file_context_menu_entry.get("text_key")),self,enabled=False)
                parent_menu.addAction(action)  # Just a textline in menu saying "Choose what to paste"
            elif entry_type == 'separator':
                parent_menu.addSeparator()


        # Ad checkable actions for each logical tag
        parent_menu = self.menues.get("file_context_menu")
        self.logical_tag_actions = {}
        for logical_tag in settings.logical_tags:
            if settings.logical_tags.get(logical_tag).get("reference_tag"):  # Can't copy-paste a reference tag. It is derrived from the other tags
                continue
            if settings.logical_tags.get(logical_tag).get('disable_in_context_menu') == True:   # Disable in context-menu
                continue
            if settings.logical_tags.get(logical_tag).get("widget") == None:  # Can't copy-paste tags not shown in widget
                continue

            tag_label_text_key = settings.logical_tags.get(logical_tag).get("label_text_key")
            if tag_label_text_key:
                tag_label = getText(tag_label_text_key)
                tag_action = QAction(tag_label, self, checkable=True)
                if settings.logical_tags.get(logical_tag).get("default_paste_select") == False:
                    tag_action.setChecked(False)
                else:
                    tag_action.setChecked(True)
                self.logical_tag_actions[logical_tag] = tag_action
                parent_menu.addAction(tag_action)
                tag_action.triggered.connect(self.toggleAction)

                if settings.logical_tags.get(logical_tag).get("value_parts") is not None:
                    for value_part in settings.logical_tags.get(logical_tag).get("value_parts"):
                        if settings.logical_tags.get(logical_tag).get("value_parts").get(value_part).get('disable_in_context_menu') is True:
                            continue
                        tag_label_text_key = settings.logical_tags.get(logical_tag).get("value_parts").get(value_part).get("label_text_key")
                        if tag_label_text_key:
                            tag_label = getText(tag_label_text_key)
                            tag_action = QAction(tag_label, self, checkable=True)
                            if settings.logical_tags.get(logical_tag).get("value_parts").get(value_part).get("default_paste_select") == False:
                                tag_action.setChecked(False)
                            else:
                                tag_action.setChecked(True)
                            self.logical_tag_actions[logical_tag+'.'+value_part] = tag_action
                            parent_menu.addAction(tag_action)
                            tag_action.triggered.connect(self.toggleAction)

    def openMenu(self, position=None):
        if not hasattr(self, 'menues'):
            self.createMenu(position)

        if not hasattr(self, 'source'):
            self.source = []
            self.source_is_single_file = False

        if self.source_is_single_file and len(self.source) == 1:  # Exactly one file selected
            self.actions.get('paste_metadata').setEnabled(True)
            self.actions.get('patch_metadata').setEnabled(True)
            self.actions.get('paste_by_filename').setEnabled(True)
            self.actions.get('patch_by_filename').setEnabled(True)
        elif len(self.source) >= 1:
            self.actions.get('paste_metadata').setEnabled(False)
            self.actions.get('patch_metadata').setEnabled(False)
            self.actions.get('paste_by_filename').setEnabled(True)
            self.actions.get('patch_by_filename').setEnabled(True)
        else:
            self.actions.get('paste_metadata').setEnabled(False)
            self.actions.get('patch_metadata').setEnabled(False)
            self.actions.get('paste_by_filename').setEnabled(False)
            self.actions.get('patch_by_filename').setEnabled(False)

        if position:
            self.position = copy.deepcopy(position)

        action = self.menues.get("file_context_menu").exec(self.viewport().mapToGlobal(self.position))
        action_id = next((k for k, v in self.actions.items() if v == action), None)  # Reverse lookup action_id from action

        if action_id == 'consolidate_metadata':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))  # Can be both files and folders
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column

                self.consolidator = ConsolidateMetadata(target, await_start_signal=True)
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_consolidate_metadata'),self.consolidator)  # Progress-bar will start worker

        elif action_id == 'standardize_filenames':
            index = self.indexAt(self.position)  # Get index in File-list
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
                    self.progress_bar = ProgressBarWidget(getText('progress_bar_title_standardize_filenames'),self.standardizer)  # Progress-bar will start worker

        elif action_id == 'copy_metadata':
            self.source_is_single_file = False
            index = self.indexAt(self.position)  # Get index in File-list
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
            for source_file_name in self.source:
                onMetadataCopied(source_file_name)

        elif action_id == 'paste_metadata':
            index = self.indexAt(self.position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))
                target = list(set(target))  # Remove duplicate filenames. Row contains one index per column
                self.clearSelection()
                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, await_start_signal=True)
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
                self.source = []



        elif action_id == 'paste_by_filename':
            index = self.indexAt(self.position)  # Get index in File-list
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
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
                self.source = []

        elif action_id == 'patch_metadata':
            index = self.indexAt(self.position)  # Get index in File-list
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
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
                self.source = []


        elif action_id == 'patch_by_filename':
            index = self.indexAt(self.position)  # Get index in File-list
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
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
                self.source = []

            else:
                self.menu.target_file_name = None  # No item was clicked
        elif action_id == 'preserve_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                self.preserver = PreserveOriginals(target)
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_preserve_originals'), self.preserver)  # Progress-bar will start worker

        elif action_id == 'delete_unused_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                self.deleter = DeleteUnusedOriginals(target,await_start_signal=True)
                self.progress_bar = ProgressBarWidget(getText('progress_bar_title_delete_unused_originals'), self.deleter)  # Progress-bar will start worker

        elif action_id == 'fetch_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                ui_status = UiStatusManager.getInstance(os.path.join(settings.app_data_location, "ui_status.json"))  # Fetch latest used originals location
                folder_dialog = FolderSelectorDialog(label_text=getText('fetch_originals_dialog_label'),
                                                     placeholder_text=getText('fetch_originals_dialog_placeholder_text'),
                                                     folder_path=ui_status.getStatusParameter('originals_fetch_folder'),
                                                     selector_title=getText('fetch_originals_dialog_selector_title'))
                if folder_dialog.exec():
                    source = folder_dialog.getFolderPath()
                    ui_status.setUiStatusParameters({'originals_fetch_folder': source})  # Save last used originals location
                    self.fetcher = FetchOriginals(source=source,target=target,await_start_signal=True)
                    self.progress_bar = ProgressBarWidget(getText('progress_bar_title_fetch_originals'), self.fetcher)  # Progress-bar will start worker


        elif action == None:
            pass
        else:
            self.openMenu()  # Toggle one of the logical tags was chosen. No position provided: Position on screen is kept

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

    def currentChanged(self, current, previous):  # Redefined method called at event "current file changed"
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

    def setOpenFolders(self, open_folders=[]):
        if open_folders:
            for open_folder in open_folders:
                # Find the QModelIndex corresponding to the folder_path
                folder_index = self.model.index(open_folder)
                if folder_index.isValid():  # Check if the folder exists in the model
                    # Expand the folder
                    self.setExpanded(folder_index, True)

    def getSelectedItems(self):
        selected_items = []
        selected_indexes = self.selectedIndexes()

        for index in selected_indexes:
            if index.column() == 0:
                selected_file_info = self.model.fileInfo(index)
                selected_items.append(selected_file_info.absoluteFilePath())
        return list(set(selected_items))

    def setSelectedItems(self, selected_items=[]):
        self.clearSelection()
        if selected_items:
            for selected_item in selected_items:
                # Find the QModelIndex corresponding to the item_path
                item_index = self.model.index(selected_item)
                if item_index.isValid():  # Check if the item exists in the model
                    # Select the item
                    self.selectionModel().select(item_index, QItemSelectionModel.SelectionFlag.Select)

    def getCurrentItem(self):
        current_index = self.currentIndex()
        if current_index.isValid():
            current_item = self.model.filePath(self.currentIndex())
        else:
            current_item = ''
        return current_item

    def setCurrentItem(self, current_path):
        current_index = self.model.index(current_path)
        if current_index.isValid():
            self.setCurrentIndex(current_index)

    def getVerticalScrollPosition(self):
       return self.verticalScrollBar().value()

    def setVerticalScrollPosition(self, scroll_position):
        if scroll_position != None:

            self.verticalScrollBar().setValue(scroll_position)

class SettingsWheeel(QLabel):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap(os.path.join(settings.resource_path,'settings.png')).scaled(20,20)
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

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Prepare window
        window_title = getText("settings_window_title")
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
        language_label = QLabel(getText("settings_labels_application_language"), self)
        language_layout = QHBoxLayout()
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        settings_layout.addLayout(language_layout)

        # Add ui_mode-selection
        self.ui_mode_combobox = QComboBox(self)
        for index, ui_mode in enumerate(settings.ui_modes):
            self.ui_mode_combobox.addItem(getText("settings_ui_mode."+ui_mode))
            if ui_mode == settings.ui_mode:
                self.ui_mode_combobox.setCurrentIndex(index)
        if self.ui_mode_combobox.currentIndex() is None:
            self.ui_mode_combobox.setCurrentIndex(0)
        ui_mode_label = QLabel(getText("settings_labels_ui_mode"), self)
        ui_mode_layout = QHBoxLayout()
        ui_mode_layout.addWidget(ui_mode_label)
        ui_mode_layout.addWidget(self.ui_mode_combobox)
        settings_layout.addLayout(ui_mode_layout)

        # Add Lightroom integration fields
        lr_integration_headline = QLabel(getText('settings_lr_integration_headline'))
        settings_layout.addWidget(lr_integration_headline)
        self.lr_integration_active_checkbox = QCheckBox(getText('settings_labels_lr_integration_active'))
        self.lr_integration_active_checkbox.setChecked(settings.lr_integration_active)
        settings_layout.addWidget(self.lr_integration_active_checkbox)
        lr_integration_disclaimer_label = QLabel(getText('settings_lr_integration_disclaimer'))
        lr_integration_disclaimer_label.setStyleSheet("color: #868686;")
        settings_layout.addWidget(lr_integration_disclaimer_label)
        self.lr_cat_file_selector = file_util.FileSelector(getText('settings_lr_file_selector_placeholder_text'),
                                                           settings.lr_db_path,
                                                           getText('settings_lr_file_selector_title'))
        lr_cat_file_selector_label = QLabel(getText('settings_labels_lr_db_file'))
        lr_cat_file_selector_layout = QHBoxLayout()
        lr_cat_file_selector_layout.addWidget(lr_cat_file_selector_label)
        lr_cat_file_selector_layout.addWidget(self.lr_cat_file_selector)
        settings_layout.addLayout(lr_cat_file_selector_layout)


        settings_layout.addSpacing(20)
        self.ok_button = QPushButton("OK")
        settings_layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.saveSettings)

    def saveSettings(self):
        settings.settings["language"] = self.language_combobox.currentText()[:2]
        ui_mode = settings.ui_modes[self.ui_mode_combobox.currentIndex()]
        settings.settings["ui_mode"] = ui_mode
        settings.settings["lr_integration_active"]=self.lr_integration_active_checkbox.isChecked()
        settings.settings["lr_db_path"]=self.lr_cat_file_selector.getFilePath()
        settings.writeSettingsFile()
        python = sys.executable  # Get Python executable path
        script = sys.argv[0]  # Get the current script file
        subprocess.Popen([python, script])  # Start a new instance
        QApplication.quit()  # Close current instance
        self.accept()

class StandardizeFilenames(QObject):
    # The purpose of this class is to rename files systematically. The naming pattern in the files will be
    # <prefix><number><suffix>.<ext>. Example: 2023-F001-001.jpg (prefix="2023-F001-', number='nnn',suffix='').
    # If folders or subfolders holds files with same name, but different extension (e.g. IMG_0021557.JPG and corresponding
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
        self.delay = 1
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

        file_count=len(self.target_file_names)     # What takes time is 1. Read metadata for files, 2. Write original filename to metadata

        # Instanciate file metadata instances for all files
        files = []
        self.progress_init_signal.emit(file_count)
        for index, file_name in enumerate(self.target_file_names):
            self.progress_signal.emit(index+1)
            file_metadata = FileMetadata.getInstance(file_name)
            while file_metadata.getStatus() != '':
                if file_metadata.getStatus() == 'PENDING_READ':
                    FileReadQueue.appendQueue(file_name)
                time.sleep(self.delay)
            file_date = file_metadata.getLogicalTagValues().get("date")
            if file_date == None:
                file_date = ''
            files.append({"file_name": file_name, "path": file_metadata.path, "name_alone": file_metadata.name_alone, "name_prefix": file_metadata.name_prefix, "name_postfix": file_metadata.name_postfix, "type": file_metadata.getFileType(), "date": file_date})

        # Try find date on at least one of the files (Raw or jpg) and copy to the other
        sorted_files = sorted(files, key=lambda x: (x['name_alone'], x['date']), reverse=True)       # Sort files in reverse order to get the file with date first
        previous_date = ''
        previous_name_alone = ''
        for file in sorted_files:
            if file.get('date') == '':   # Missing date
                if file.get('name_alone') == previous_name_alone:
                    file['date'] = previous_date
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
                    new_file_name = file.get('path') + file.get('name_prefix') + new_name_alone + file.get('name_postfix') + '.' + file.get('type')
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
                ExifTool.closeProcess(process_id='WRITE')  # Close write-process, so that data in queue can be changed safely
                QueueHost.get_instance().stop_queue_worker()  # Make sure not to collide with update of metadata

                renamer.start()
                QueueHost.get_instance().start_queue_worker()  # Start Queue-worker again
            except Exception as e:
                self.error_signal.emit(e,False)
                self.done_signal.emit()
                return

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
        self.delay = 1
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
                if self.match_file_name and FileMetadata.getInstance(target_file_name).name_alone != FileMetadata.getInstance(source_file_name).name_alone:
                    continue
                source_targets.append([source_file_name,target_file_name])
        copy_file_count=len(source_targets)
        self.progress_init_signal.emit(copy_file_count)

        for index, source_target in enumerate(source_targets):
            source_file_name = source_target[0]
            target_file_name = source_target[1]
            source_file_metadata = FileMetadata.getInstance(source_file_name)
            while source_file_metadata.getStatus() != '':
                if source_file_metadata.getStatus() == 'PENDING_READ':
                    FileReadQueue.appendQueue(source_file_name)
                    time.sleep(self.delay)
            target_file_metadata = FileMetadata.getInstance(target_file_name)
            self.progress_signal.emit(index + 1)
            target_tag_values = {}
            for logical_tag in self.logical_tags:
                source_tag_value = None
                source_tag_values = source_file_metadata.getLogicalTagValues()
                source_tag_value = source_tag_values.get(logical_tag)
                if source_tag_value != None:
                    target_tag_values[logical_tag] = source_tag_value
            target_file_metadata.setLogicalTagValues(logical_tag_values=target_tag_values, overwrite=self.overwrite)
            if target_file_metadata.getStatus() == '':
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
        self.delay = 1
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
            FileReadQueue.appendQueue(file_name)
            while file_metadata.getStatus() == 'READ':  # If instance being read, wait for it to finalize
                time.sleep(self.delay)
                status = file_metadata.getStatus()  # Line added to be able to see status during debugging
            file_metadata.setLogicalTagValues(logical_tag_values={},force_rewrite=True)
            file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
            file_metadata_pasted_emitter.emit(file_name)

        self.done_signal.emit()

class PreserveOriginals(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,target, await_start_signal=False):
        # target is a folder
        super().__init__()
        self.target=target
        if not await_start_signal:
            self.start()

    def getRawNonRawByBaseName(self,files):
        # Returns lists of raw-files and list of non-raw files per basename
        raw_files = {}
        non_raw_files = {}
        for file in files:
            split_file_name = splitFileName(file)
            base_name = split_file_name[1]
            file_type = split_file_name[2].lower()
            if file_type in settings.raw_file_types:
                if raw_files.get(base_name) is None:
                    raw_files[base_name]=[file]
                else:
                    raw_files[base_name].append(file)
            elif file_type in settings.file_types:
                if non_raw_files.get(base_name) is None:
                    non_raw_files[base_name]=[file]
                else:
                    non_raw_files[base_name].append(file)
        return raw_files, non_raw_files


    def start(self):
        if not os.path.isdir(self.target):  # Only works for one single dir as target
            return

        # Create originals folder if it does not exist
        originals_path = self.target + '/' + getText('originals_folder_name')
        os.makedirs(originals_path,exist_ok=True)  #Create originals folder if it is missing

        # Get files from originals folder
        file_name_pattern = ["*." + filetype for filetype in settings.file_types]
        original_files = getFileList(originals_path,pattern=file_name_pattern)  #Image files already in originals folder
        original_raw_files, original_non_raw_files = self.getRawNonRawByBaseName(original_files)

        # Get files from target-folder
        target_files = getFileList(self.target,pattern=file_name_pattern)  #Image files in target-folder
        target_raw_files, target_non_raw_files = self.getRawNonRawByBaseName(target_files)


        total_count = len(target_raw_files) * 2 + len(target_non_raw_files)
        self.progress_init_signal.emit(total_count)
        count = 0

        # Copy raw-files from target to originals, if missing in originals
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_raw_file = target_raw_files.get(base_name)[0]
                original_raw_file = shutil.copy2(target_raw_file, originals_path)
                original_raw_files[base_name]=[original_raw_file]    # Keep track that the original now exists

        # Copy non-raw files from target to originals, if missing in originals both as non-raw and raw files
        for base_name in target_non_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None and original_non_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                target_non_raw_file = target_non_raw_files.get(base_name)[0]
                original_non_raw_file = shutil.copy2(target_non_raw_file, originals_path)
                original_non_raw_files[base_name]=[original_non_raw_file]    # Keep track that the original now exists

        # Delete originals from target-folder if non-original exists in target folder
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if target_non_raw_files.get(base_name) is not None:
                for file in target_raw_files.get(base_name):
                    os.remove(file)

        self.done_signal.emit()


class DeleteUnusedOriginals(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,target, await_start_signal=False):
        # target is a folder
        super().__init__()
        self.target=target
        if not await_start_signal:
            self.start()

    def getFilesByBaseName(self,files):
        # Returns lists of raw-files and list of non-raw files per basename
        base_name_files = {}
        for file in files:
            split_file_name = splitFileName(file)
            base_name = split_file_name[1]
            if base_name_files.get(base_name) is None:
                base_name_files[base_name]=[file]
            else:
                base_name_files[base_name].append(file)
        return base_name_files


    def start(self):
        if not os.path.isdir(self.target):  # Only works for one single dir as target
            return

        # Set path to originals
        originals_path = self.target + '/' + getText('originals_folder_name')
        if not os.path.isdir(originals_path):  # Nothing to do if originals does not exist
            return

        # Get files from originals folder
        file_name_pattern = ["*." + filetype for filetype in settings.file_types]
        original_files = getFileList(originals_path,pattern=file_name_pattern)  # Image files already in originals folder
        original_base_name_files = self.getFilesByBaseName(original_files)

        # Get files from target-folder
        target_files = getFileList(self.target,pattern=file_name_pattern)  #Image files in target-folder
        target_base_name_files = self.getFilesByBaseName(target_files)

        # Investigate if original basename esist in target(main) folder, and delete original files for base-name if not
        file_count = len(original_base_name_files)
        self.progress_init_signal.emit(file_count)

        for index, base_name in enumerate(original_base_name_files):
            self.progress_signal.emit(index+1)
            if target_base_name_files.get(base_name) is None:   # Original-folder is missing the raw-file
                for file in original_base_name_files[base_name]:
                    os.remove(file)
        self.done_signal.emit()

class FetchOriginals(QObject):
    progress_init_signal = pyqtSignal(int)       # Sends number of entries to be processed
    progress_signal = pyqtSignal(int)    # Sends number of processed records
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, bool)     #Sends exception and retry_allowed (true/false)

    def __init__(self,source,target, await_start_signal=False):
        # target is a folder
        super().__init__()
        self.target=target
        self.source=source
        if not await_start_signal:
            self.start()

    def getRawNonRawByBaseName(self,files):
        # Returns lists of raw-files and list of non-raw files per basename
        raw_files = {}
        non_raw_files = {}
        for file in files:
            split_file_name = splitFileName(file)
            base_name = split_file_name[1]
            file_type = split_file_name[2].lower()
            if file_type in settings.raw_file_types:
                if raw_files.get(base_name) is None:
                    raw_files[base_name]=[file]
                else:
                    raw_files[base_name].append(file)
            elif file_type in settings.file_types:
                if non_raw_files.get(base_name) is None:
                    non_raw_files[base_name]=[file]
                else:
                    non_raw_files[base_name].append(file)
        return raw_files, non_raw_files


    def start(self):
        if not os.path.isdir(self.target):  # Only works for one single dir as target
            return

        # Create originals folder if it does not exist
        originals_path = self.target + '/' + getText('originals_folder_name')
        os.makedirs(originals_path,exist_ok=True)  #Create originals folder if it is missing

        # Get files from source (Normally memory-card)
        file_name_pattern = ["*." + filetype for filetype in settings.file_types]
        source_files = getFileList(self.source,pattern=file_name_pattern)  #Image files already in originals folder
        source_raw_files, source_non_raw_files = self.getRawNonRawByBaseName(source_files)

        # Get files from originals folder
        file_name_pattern = ["*." + filetype for filetype in settings.file_types]
        original_files = getFileList(originals_path,pattern=file_name_pattern)  #Image files already in originals folder
        original_raw_files, original_non_raw_files = self.getRawNonRawByBaseName(original_files)

        # Get files from target
        file_name_pattern = ["*." + filetype for filetype in settings.file_types]
        target_files = getFileList(self.target,pattern=file_name_pattern)  #Image files already in originals folder
        target_raw_files, target_non_raw_files = self.getRawNonRawByBaseName(target_files)

        total_count = len(target_raw_files) + len(target_non_raw_files)
        self.progress_init_signal.emit(total_count)
        count = 0

        # Copy raw-files from source to originals, if missing in originals
        for base_name in target_non_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                source_file_entry = source_raw_files.get(base_name)
                if source_file_entry is None:
                    source_file_entry = source_non_raw_files.get(base_name)
                if source_file_entry is not None:
                    source_file = source_file_entry[0]
                    original_raw_file = shutil.copy2(source_file, originals_path)
                    original_raw_files[base_name]=[original_raw_file]    # Keep track that the original now exists

        # Copy non-raw files from source to originals, if missing in originals both as non-raw and raw files
        for base_name in target_raw_files:
            count += 1
            self.progress_signal.emit(count)
            if original_raw_files.get(base_name) is None:   # Original-folder is missing the raw-file
                source_file_entry = source_raw_files.get(base_name)
                if source_file_entry is None:
                    source_file_entry = source_non_raw_files.get(base_name)
                if source_file_entry is not None:
                    source_file = source_file_entry[0]
                    original_raw_file = shutil.copy2(source_file, originals_path)
                    original_raw_files[base_name]=[original_raw_file]    # Keep track that the original now exists

        self.done_signal.emit()

class InputFileNamePattern(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(getText("standardize_dialog_title"))
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add labels and input fields
        prefix_label = QLabel(getText("standardize_dialog_prefix_label"))

        self.prefix = QLineEdit()
        layout.addWidget(prefix_label)
        layout.addWidget(self.prefix)

        num_pattern_label = QLabel(getText("standardize_dialog_number_pattern_label"))
        self.num_pattern = QLineEdit()
        layout.addWidget(num_pattern_label)
        layout.addWidget(self.num_pattern)

        suffix_label = QLabel(getText("standardize_dialog_postfix_label"))
        self.suffix = QLineEdit()
        layout.addWidget(suffix_label)
        layout.addWidget(self.suffix)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton(getText("general_ok"))
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton(getText("general_cancel"))
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
        pass
        self.change_signal.emit(new_file_name)

def onMetadataChanged(file_name,old_logical_tags,new_logical_tags):
    pass

def onMetadataCopied(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()   # ..not to copy old data, save what is in screen

def onMetadataPasted(file_name):
    if file_name == FilePanel.file_name:
        dummy = FilePanel.getInstance(file_name)   #Triggers update of Filepanel

def onFileRenameDone(files,update_original_filename_tag=False):
# Update filenames in Lightroom Classic Catalog
    if settings.lr_integration_active:
        lightroom_integration.appendLightroomQueue(settings.lr_queue_file_path,files)
        lightroom_integration.processLightroomQueue(settings.lr_db_path,settings.lr_queue_file_path)

# Update file-names in queue
    queue_changes = []
    for file in files:
        queue_changes.append({'find': {'file': file.get('old_name')},'change': {'file': file.get('new_name')}})
    json_queue_file = file_util.JsonQueue.getInstance(settings.queue_file_path)
    json_queue_file.change_queue(queue_changes)

# Update filename in preview-instance
    for file in files:
        file_preview = FilePreview.instance_index.get(file.get('old_name'))
        if file_preview is not None:
            file_preview.updateFilename(file.get('new_name'))

# Update filename in metadata-instance
    for file in files:
        file_metadata = FileMetadata.instance_index.get(file.get('old_name'))
        if file_metadata is not None:
            file_metadata.updateFilename(file.get('new_name'))

# Set original filename tag in all files
    if update_original_filename_tag==True and settings.logical_tags.get('original_filename') is not None:
        for file in files:
            new_file_name = file.get('new_name')
            if 'tmp' in new_file_name:
                continue
            file_metadata = FileMetadata.getInstance(new_file_name)
            new_name_alone = file_util.splitFileName(new_file_name)[1]
            if new_name_alone != '' and new_name_alone != None:
                logical_tags = {'original_filename': new_name_alone}
                file_metadata.setLogicalTagValues(logical_tags)
                file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
                file_metadata_pasted_emitter.emit(new_file_name)

def onCurrentFileChanged(new_file_name):
    if new_file_name != FilePanel.file_name:
        FilePanel.saveMetadata()                      # Saves metadata for file currently in filepanel (if any)
        dummy = FilePanel.getInstance(new_file_name)  # Puts new file in file-panel
        FileReadQueue.appendQueue(new_file_name)

def onImageRotated(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()
        file_preview = FilePreview.instance_index.get(file_name)  # Get existing preview, if exist
        if file_preview:
            file_preview.updatePixmap()
            FilePanel.preview_widget.setPixmap(file_preview.getPixmap(FilePreview.latest_panel_width))

def onFileReady(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.instance.prepareFilePanel()

file_metadata_changed_emitter = FileMetadataChangedEmitter.getInstance()
file_metadata_changed_emitter.change_signal.connect(onMetadataChanged)

file_rename_done_emitter = FileRenameDoneEmitter.getInstance()
file_rename_done_emitter.done_signal.connect(onFileRenameDone)

current_file_changed_emitter = CurrentFileChangedEmitter.getInstance()
current_file_changed_emitter.change_signal.connect(onCurrentFileChanged)

file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
file_metadata_pasted_emitter.paste_signal.connect(onMetadataPasted)

image_rotated_emitter = ImageRotatedEmitter.getInstance()
image_rotated_emitter.rotate_signal.connect(onImageRotated)

file_ready_emitter = FileReadyEmitter.getInstance()
file_ready_emitter.ready_signal.connect(onFileReady)
