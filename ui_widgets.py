from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTreeView, QFileSystemModel, QLabel, QLineEdit, QPlainTextEdit, QDateTimeEdit, QDateEdit, QPushButton, QListWidget, QAbstractItemView, QMenu, QAction, QDialog, QCompleter, QScrollArea,QSizePolicy
from PyQt5.QtCore import Qt, QDir, QDateTime, QDate, QModelIndex,QTimer, pyqtSignal,QSize
from PyQt5.QtGui import QPixmap,QFontMetrics
import settings
from file_metadata_util import FileMetadata, StandardizeFilenames, CopyLogicalTags, ConsolidateMetadata
from ui_util import ProgressBarWidget, AutoCompleteList
import os
from file_preview_util import FilePreview

class FolderTree(QTreeView):
    def __init__(self,dir_path,file_list=None):
        super().__init__()
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.setModel(self.model)
        self.setRootPath(dir_path)
        self.file_list=file_list

        for column_index in range(1,self.model.columnCount()):
            self.hideColumn(column_index)

    def setRootPath(self, dir_path):
        self.model.setRootPath(dir_path)
        self.setRootIndex(self.model.index(dir_path))

    def currentChanged(self, current, previous):
        chosen_path = self.model.filePath(current)
        previous_path = self.model.filePath((previous))
        if chosen_path != previous_path:
            if not self.file_list == None:
                self.file_list.setRootPath(chosen_path)

class FileList(QTreeView):
    def __init__(self,dir_path='', current_file=None):
        super().__init__()

        # Many files can be selected in one go
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        # Only show image- and video-files
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files )

        self.setModel(self.model)
        self.__setFiletypeFilter(settings.file_types)
        self.hideFilteredFiles()    #Default is to hide filetered files. They can also be shown dimmed
                                    #by calling self.showFilteredFiles()

        self.hideColumn(2)    #Hide File-type
        self.setColumnWidth(0,260)    #Filename
        self.setColumnWidth(1,80)    #Filesize
        self.setColumnWidth(2,150)    #Date modified


        column_count = self.model.columnCount()

        # Print the header data for each column
        for column in range(column_count):
            header_data = self.model.headerData(column, Qt.Horizontal, Qt.DisplayRole)

        #Set root-path
        self.setRootPath(dir_path)
        self.current_file = current_file

        # Prepare context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def createMenu(self, position):

        self.menu = QMenu()
      
        # Add actions to the menu
        action_texts = settings.file_context_menu_actions.get("consolidate_metadata")  # All language descriptions of action
        action_text = action_texts.get(settings.language)
        self.consolidate_metadata = self.menu.addAction(action_text)

        action_texts = settings.folder_context_menu_actions.get("standardize_filenames")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.standardize_filenames = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("copy_metadata")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.copy_metadata = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("paste_metadata")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.paste_metadata = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("patch_metadata")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.patch_metadata = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("paste_by_filename")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.paste_by_filename = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("patch_by_filename")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.patch_by_filename = self.menu.addAction(action_text)

        self.menu.addSeparator()
        action_texts = settings.file_context_menu_actions.get("choose_tags_to_paste")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        menu_text_line = QAction(action_text, self, enabled=False)
        self.menu.addAction(menu_text_line)   # Just a textline in menu saying "Choose what to paste"

        # Ad checkable actions for each logical tag
        self.logical_tag_actions = {}
        for logical_tag in settings.logical_tags:
            if settings.logical_tags.get(logical_tag)=='reference_tag':    #Can't copy-paste a reference tag. It is derrived from the other tags
                continue
            tag_labels = settings.logical_tag_descriptions.get(logical_tag)  # All language descriptions of tag
            tag_label = tag_labels.get(settings.language)  # User-language description of tag
            tag_action = QAction(tag_label, self, checkable=True)
            tag_action.setChecked(True)
            self.logical_tag_actions[logical_tag] = tag_action

            self.menu.addAction(tag_action)
            tag_action.triggered.connect(self.toggleAction)

    def openMenu(self, position):
        if not hasattr(self, 'menu'):
            self.createMenu(position)

        if not hasattr(self, 'source'):
            self.source=[]
            self.source_is_single_file=False

        if self.source_is_single_file and len(self.source) == 1:   #Exactly one field selected
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

        action = self.menu.exec_(self.viewport().mapToGlobal(position))

        if action == self.consolidate_metadata:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))   #Can be both files and folders
                self.consolidator = ConsolidateMetadata(target,await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Consolidate', self.consolidator)  # Progress-bar will start worker

        elif action == self.standardize_filenames:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))   #Can be both files and folders
                file_name_pattern_dialog = InputFileNamePattern()
                result = file_name_pattern_dialog.exec_()
                if result == QDialog.Accepted:
                    # Get the input values
                    file_name_pattern = file_name_pattern_dialog.getInput()
                    prefix, num_pattern, suffix = file_name_pattern

                    # Rename all files in folders and subfolders
                    self.unselectAll()
                    self.standardizer=StandardizeFilenames(target,prefix,num_pattern,suffix,await_start_signal=True)  # worker-instance
                    self.progress_bar=ProgressBarWidget('Standardize',self.standardizer)   # Progress-bar will start worker

        elif action == self.copy_metadata:
            self.source_is_single_file = False
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():    # A valid file was right-clicked
                self.source = []
                for index in self.selectedIndexes():
                    self.source.append(self.model.filePath(index))
                if len(self.source) == 1:
                    if os.path.isfile(self.source[0]):
                        self.source_is_single_file = True
            else:
                self.source = []                # No item was clicked

            # index = self.indexAt(position)  # Get index in File-list
            # # Check if an item was clicked
            # if index.isValid():
            #     self.source = self.model.filePath(index)
            # else:
            #     self.source = None                # No item was clicked
        elif action == self.paste_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():    # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))

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

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, match_file_name=True, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []

        elif action == self.patch_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)
                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, overwrite=False, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []


        elif action == self.patch_by_filename:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():  # A valid file was right-clicked
                target = []
                for index in self.selectedIndexes():
                    target.append(self.model.filePath(index))

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.source, target, target_logical_tags, overwrite=False, match_file_name=True, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker
                self.source = []

            else:
                self.menu.target_file_name = None                # No item was clicked
        elif action == None:
            pass
        else:
            self.openMenu(position)    # Toggle one of the logical tags was chosen

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
        self.file_type_filter = file_types
        for i in range(len(file_types)):
            self.file_type_filter[i] = "*." + self.file_type_filter[i]
        self.model.setNameFilters(self.file_type_filter)

    def hideFilteredFiles(self):
        self.model.setNameFilterDisables(False)   #Filtered files are not shown

    def showFilteredFiles(self):
        self.model.setNameFilterDisables(True)    #Filtered files are shown as dimmed, and are not selectable

    def currentChanged(self, current, previous):       #Redefinet method called at event "current file changed"
        chosen_path = self.model.filePath(current)
        previous_path = self.model.filePath((previous))
        if chosen_path != previous_path:
            if not self.current_file == None:
                if os.path.isfile(chosen_path):
                    self.current_file=FilePanel.getInstance(chosen_path)   # Gets file-singleton. At the same time set singleton to chosen file

class FilePanel(QScrollArea):
    __instance = None
    file_metadata = None
    file_name = ''
    focus_tag = None        # After refreshing FilePanel, bring focus back to the tag that had focus before

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(350)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width() != -1:  # ignore first call to resizeEvent
            if event.oldSize().width()!=event.size().width():
                self.prepareFilePanel()

    @staticmethod
    def getInstance(file_name):
        FilePanel.focus_tag = None      #Forget focus-tag when changing to different photo
        if FilePanel.file_metadata != None and FilePanel.file_name !='':                      #Changing to different picture: Save this pictures metadata
            FilePanel.file_metadata.save()
        if FilePanel.__instance==None:
            FilePanel.__instance=FilePanel()
        FilePanel.file_name=file_name
        FilePanel.file_metadata=FileMetadata.getInstance(file_name)
        FilePanel.file_metadata.change_signal.connect(FilePanel.metadataChanged)    # If a copy-process changes file
        FilePanel.__instance.prepareFilePanel()
        return FilePanel.__instance

    @staticmethod
    def saveMetadata():
        if FilePanel.file_metadata != None and FilePanel.file_name !='':
            FilePanel.file_metadata.save()

    def prepareFilePanel(self):       # Happens each time a new filename is assigned
        scroll_position = FilePanel.__instance.verticalScrollBar().value()    # Remember scroll-position
        self.takeWidget()

        if FilePanel.file_name != None and FilePanel.file_name != '':
            FilePanel.__initializeWidgets()    #Widgets for metadata only

        if FilePanel.file_name != None and FilePanel.file_name != '':
            # Prepare file-preview widget
            FilePanel.file_preview = QLabel()
            FilePanel.pixmap = FilePreview.getInstance(FilePanel.file_name,self.width()-60).pixmap
            FilePanel.file_preview.setPixmap(FilePanel.pixmap)
            FilePanel.file_preview.setAlignment(Qt.AlignHCenter)
            FilePanel.main_layout.addWidget(FilePanel.file_preview)
            dummy_widget_for_width = QWidget()
            dummy_widget_for_width.setFixedWidth(self.width() - 60)
            FilePanel.main_layout.addWidget(dummy_widget_for_width)

            # Prepare metadata widgets and place them all in metadata_layout.
            FilePanel.metadata_layout.setSizeConstraint(1)   #No constraints
            tags = {}
            for logical_tag in FilePanel.file_metadata.logical_tag_values:
                tags[logical_tag]=FilePanel.tags.get(logical_tag)
                tag_widget=FilePanel.tags[logical_tag][1]
                tag_widget.readFromImage()

            # Place all tags in V-box layout for metadata
            focus_widget = None
            for logical_tag in tags:
                FilePanel.metadata_layout.addWidget(tags[logical_tag][0])  # Label-widget
                FilePanel.metadata_layout.addWidget(tags[logical_tag][1])  # Tag-widget
                space_label=QLabel(" ")
                FilePanel.metadata_layout.addWidget(space_label)
                if logical_tag == FilePanel.focus_tag:
                    if tags[logical_tag][2] == 'text_set':
                        focus_widget = tags[logical_tag][1].text_input
                    else:
                        focus_widget = tags[logical_tag][1]

            FilePanel.main_layout.addLayout(FilePanel.metadata_layout)
            FilePanel.main_widget.setFixedWidth(self.width() - 30)
            FilePanel.main_widget.setLayout(FilePanel.main_layout)
            self.setWidget(FilePanel.main_widget)
            if focus_widget:
                focus_widget.setFocus()
            FilePanel.__instance.verticalScrollBar().setValue(scroll_position)  # Remember scroll-position

    @staticmethod
    def __initializeWidgets():
        FilePanel.main_widget = QWidget()
        FilePanel.main_widget.setMinimumHeight(5000)   # Ensure that there is enough available place in widget for scroll-area
        FilePanel.main_layout=QVBoxLayout()
        FilePanel.main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        FilePanel.metadata_layout=QVBoxLayout()
        FilePanel.metadata_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

        FilePanel.tags = {}
        for logical_tag in settings.logical_tags:
            tag_labels = settings.logical_tag_descriptions.get(logical_tag)  # All language descriptions of tag
            tag_label = tag_labels.get(settings.language)  # User-language description of tag
            tag_type = settings.logical_tags.get(logical_tag)

            label_widget = QLabel(tag_label + ":")
            label_widget.setStyleSheet("color: #868686;")
            if tag_type == "text_line":
                tag_widget = TextLine(logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            elif tag_type == "text":
                tag_widget = Text(logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            elif tag_type == "reference_tag":
                tag_widget = Text(logical_tag)
                tag_widget.setDisabled(True)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            elif tag_type == "date_time":
                tag_widget = DateTime(logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            elif tag_type == "date":
                tag_widget = Date(logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            elif tag_type == "text_set":
                tag_widget = TextSet(logical_tag)
                FilePanel.tags[logical_tag] = [label_widget, tag_widget,tag_type]
            else:
                pass

    @staticmethod
    def metadataChanged(file_name):
        if file_name==FilePanel.file_name:
            FilePanel.__instance.prepareFilePanel()      # If matadata changed in file shown in panel, then update metadata in panel

    @staticmethod
    def filenemeChanged(old_filename, new_filename):     # reacts on change filename
        FileMetadata.deleteInstance(old_filename)        # file for this instance does not exist anymore

class TextLine(QLineEdit):
    def __init__(self, logical_tag):
        super().__init__()
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMaximumWidth(1250)

        #Get attributes of tag
        tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                       #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()
        self.editingFinished.connect(self.__edited)

    def readFromImage(self):
        if FilePanel.file_metadata:
            self.setText(FilePanel.file_metadata.logical_tag_values.get(self.logical_tag))
            if hasattr(self, 'auto_complete_list') and self.text() != "":
                self.auto_complete_list.collectItem(self.text())    # Collect new entry in auto_complete_list

    def __edited(self):
        FilePanel.file_metadata.setLogicalTagValues({self.logical_tag: self.text()})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.text())    # Collect new entry in auto_complete_list
        FilePanel.focus_tag=self.logical_tag

class Text(QPlainTextEdit):
    def __init__(self, logical_tag):
        super().__init__()     #Puts text in Widget
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMinimumHeight(50)
        self.setMaximumWidth(1250)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.ClickFocus)

        #Get attributes of tag
        tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width()!=event.size().width():
            self.setFixedHeight(self.widgetHeight(event.size().width()))   #Calculates new height from new width
    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()
    def readFromImage(self):
        if FilePanel.file_metadata:
            text=FilePanel.file_metadata.logical_tag_values.get(self.logical_tag)
            self.setPlainText(text)
            self.setFixedHeight(self.widgetHeight(self.width()))      #Calculates needed height from width and text
            if hasattr(self, 'auto_complete_list') and self.toPlainText() != "":
                self.auto_complete_list.collectItem(self.toPlainText())    # Collect new entry in auto_complete_list
    def focusOutEvent(self, event):
        self.__edited()

    def __edited(self):
        FilePanel.file_metadata.setLogicalTagValues({self.logical_tag: self.toPlainText()})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.toPlainText())    # Collect new entry in auto_complete_list
        FilePanel.focus_tag=self.logical_tag
#        FilePanel.file_metadata.save()

    def widgetHeight(self, new_widget_width=-1):

        # Get text from document
        text=self.toPlainText()
        text_length = len(text)

        if text_length == 0:
            return 60

        document = self.document()
        font = document.defaultFont()

        # Calculate the width of each line of text
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.width(self.toPlainText())


        if new_widget_width != -1:
            document_width = new_widget_width
        else:
            document_width = self.document().size().width()

        num_lines = text_width / document_width


        # Add lines for wasted space at line shift
        wasted_space_factor = 1 + 5 * num_lines / text_length   # Approx 5 characters wasted at each line
        num_lines = num_lines * wasted_space_factor

        # Add extra lines for new-line characters
        for str_ln in range(10, 0, -1):
            repeat_newline = str_ln * "\n"
            repeat_newline_count = text.count(repeat_newline)
            if repeat_newline_count > 0:
                num_lines = num_lines + repeat_newline_count * ( str_ln - 0.5 )
                text = text.replace(repeat_newline, "")

        # Add extra space for frame and last line
        num_lines = num_lines + 5

        # Calculate the height of the text
        line_height = font_metrics.height()
        text_height = int(num_lines * line_height)

        return text_height


class DateTime(QDateTimeEdit):
    def __init__(self, logical_tag):
        super().__init__()
        self.logical_tag = logical_tag                                    #Widget should remember who it serves

        self.setCalendarPopup(True)
        self.setFixedWidth(250)

        #Get attributes of tag
        tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)

        self.readFromImage()
        self.editingFinished.connect(self.__edited)

    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()


    def readFromImage(self):
        if FilePanel.file_metadata:
            date_time = FilePanel.file_metadata.logical_tag_values.get(self.logical_tag)
            self.clear()
            self.setStyleSheet("color: #D3D3D3;")
            if date_time != "":  # Data was found
                date_time = ''.join(date_time.split('+')[:1]) # 2022/12/24 13:50:00+02:00 --> 2022/12/24 13:50:00
                date_time = date_time.replace(" ", ":")       # 2022/12/24 13:50:00 --> 2022/12/24:13:50:00
                date_time = date_time.replace("/", ":")       # 2022/12/24:13:50:00 --> 2022:12:24:13:50:00
                date_time_parts = date_time.split(":")        # 2022:12:24:13:50:00 --> ["2022", "12", "24", "13", "50", "00"]
                while len(date_time_parts) < 6:
                    date_time_parts.append("")
                self.setDateTime(QDateTime(int(date_time_parts[0]), int(date_time_parts[1]), int(date_time_parts[2]),
                                           int(date_time_parts[3]), int(date_time_parts[4]), int(date_time_parts[5])))
                self.setStyleSheet("color: black")
                if hasattr(self, 'auto_complete_list'):
                    self.auto_complete_list.collectItem(date_time)    # Collect new entry in auto_complete_list


    def __edited(self):
        date_time_string = self.dateTime().toString("yyyy:MM:dd hh:mm:ss")
        FilePanel.file_metadata.setLogicalTagValues({self.logical_tag: date_time_string})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.dateTime())    # Collect new entry in auto_complete_list
        self.setStyleSheet("color: black")
        FilePanel.focus_tag=self.logical_tag




class Date(QDateEdit):
    def __init__(self, logical_tag):
        super().__init__()
        self.logical_tag = logical_tag                                    #Widget should remember who it serves

        self.setCalendarPopup(True)
        self.setFixedWidth(250)

        #Get attributes of tag
        tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)

        self.readFromImage()
        self.editingFinished.connect(self.__edited)

    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()

    def readFromImage(self):
        if FilePanel.file_metadata:
            date = FilePanel.file_metadata.logical_tag_values.get(self.logical_tag)
            self.setDate(QDate(1752,1,1))
            if date !="":
                date = date.replace("/", ":")          # 2022/12/24 --> 2022:12:24
                date_parts = date.split(":")           # 2022:12:24 --> ["2022", "12", "24"]
                while len(date_parts) < 3:
                    date_parts.append("")
                self.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                if hasattr(self, 'auto_complete_list'):
                    self.auto_complete_list.collectItem(date)  # Collect new entry in auto_complete_list

    def __edited(self):
        date_string = self.date().toString("yyyy:MM:dd")
        FilePanel.file_metadata.setLogicalTagValues({self.logical_tag: date_string})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.date())    # Collect new entry in auto_complete_list
        FilePanel.focus_tag=self.logical_tag



class TextSet(QWidget):

    def __init__(self, logical_tag):
        super().__init__()

        self.logical_tag = logical_tag  # Widget should remember who it serves
        self.text_list = self.TextList()
        self.text_list.setFixedWidth(300)

        self.text_input = self.TextInput('Tast navn')
        self.__initUI()
        self.readFromImage()

    def __initUI(self):
        # Prepare text_input with completer
        # Get attributes of tag
        tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        self.auto_complete_list = None
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(self.logical_tag)
            self.text_input.setCompleter(self.auto_complete_list)
            QTimer.singleShot(0, self.text_input.clear)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)

        # Set up layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_list)
        layout.addWidget(self.text_input)
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setLayout(layout)

        # Connect buttons to functions
        self.text_input.returnPressed.connect(self.__onReturnPressed)
        self.text_list.edit_signal.connect(self.__edited)
        if self.auto_complete_list != None:
           self.auto_complete_list.activated.connect(self.__onCompleterActivated)

    def readFromImage(self):
        if FilePanel.file_metadata:
            tags = FilePanel.file_metadata.logical_tag_values.get(self.logical_tag)
            if type(tags) == str:
                tag_list = [tags]
            else:
                tag_list = tags
            if hasattr(self, 'auto_complete_list'):
                self.auto_complete_list.collectItems(tag_list)
            self.text_list.clear()
            for tag in tag_list:
                self.text_list.addItem(tag)
            self.text_list.setFixedHeight(self.text_list.widgetHeight())  # Calculates needed height for the number of items

    def __edited(self):
        items = []
        count = self.text_list.count()
        for index in range(count):
            item = self.text_list.item(index)
            text = item.text()
            items.append(text)
        FilePanel.file_metadata.setLogicalTagValues({self.logical_tag: items})
        FilePanel.focus_tag=self.logical_tag

    def __onReturnPressed(self):
        if self.auto_complete_list.currentCompletion():  # Return pressed in completer-list
            pass  # Return pressed from completer
        else:
            self.text_list.addTag(self.text_input.text())  # Return pressed from QLineEdit
            self.auto_complete_list.collectItem(self.text_input.text())
            self.text_input.clear()

    def __onCompleterActivated(self, text):
        self.text_list.addTag(text)
        QTimer.singleShot(0, self.text_input.clear)

    class TextList(QListWidget):
        edit_signal = pyqtSignal()

        def __init__(self,text_set=None):
            super().__init__()
            self.text_set=text_set    #Remember who you are serving
            self.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.setDragDropMode(QListWidget.InternalMove)

        def dropEvent(self, event):
            super().dropEvent(event)
            self.edit_signal.emit()

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() == Qt.Key_Delete:
                self.__removeTag()

        def __removeTag(self):
            items = self.selectedItems()
            if items:
                for item in items:
                    self.takeItem(self.row(item))
                self.edit_signal.emit()

        def addTag(self,text):
            self.addItem(text)
            self.edit_signal.emit()

        def widgetHeight(self):
            item_height = self.sizeHintForRow(0)
            num_items = self.count()
            list_height = num_items * item_height + 60
            return list_height

    class TextInput(QLineEdit):
        def __init__(self, text_set=None):
            super().__init__()
            self.text_set=text_set    #Remember who you are serving
            self.setPlaceholderText('Tast navn')



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

