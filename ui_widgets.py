from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QTreeView, QFileSystemModel, QLabel, QLineEdit, QPlainTextEdit, QDateTimeEdit, QDateEdit, QPushButton, QListWidget, QAbstractItemView, QMenu, QAction, QDialog, QApplication, QCompleter, QSpacerItem,QSizePolicy
from PyQt5.QtCore import Qt, QDir, QDateTime, QDate, QThread,QObject,QModelIndex,QItemSelection,QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
import settings
from file_metadata_util import FileMetadata, StandardizeFilenames, CopyLogicalTags, ConsolidateMetadata
from util import clearLayout, AutoCompleteList
from ui_util import ProgressBarWidget
import os
from file_util import FileRenamer

class FolderTree(QTreeView):
    def __init__(self,dir_path,file_list=None):
        super().__init__()
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.setModel(self.model)
        self.setRootPath(dir_path)
        self.file_list=file_list
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

#        self.selectionModel().SelectCurrent
        for column_index in range(1,self.model.columnCount()):
            self.hideColumn(column_index)

        # Prepare context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def createMenu(self, position):
        # Create the context menu
        self.menu = QMenu()

        # Add actions to the menu
        action_texts = settings.folder_context_menu_actions.get("standardize_filenames")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.standardize_filenames = self.menu.addAction(action_text)

        action_texts = settings.folder_context_menu_actions.get("consolidate_metadata")  # All language descriptions of action
        action_text = action_texts.get(settings.language)
        self.consolidate_metadata = self.menu.addAction(action_text)

    def openMenu(self, position):
        if not hasattr(self,'menu'):    # First time clicked: Create context-menu
            self.createMenu(position)
        if self.menu == None:
            self.createMenu(position)

        action = self.menu.exec_(self.viewport().mapToGlobal(position))

        if action == self.standardize_filenames:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                start_folder_name = self.model.filePath(index)
                file_name_pattern_dialog = InputFileNamePattern()
                result = file_name_pattern_dialog.exec_()
                if result == QDialog.Accepted:
                    # Get the input values
                    file_name_pattern = file_name_pattern_dialog.get_input()
                    prefix, num_pattern, suffix = file_name_pattern

                    # Rename all files in folders and subfolders
                    self.file_list.unselectAll()
                    self.standardizer=StandardizeFilenames(start_folder_name,prefix,num_pattern,suffix,await_start_signal=True)  # worker-instance
                    self.progress_bar=ProgressBarWidget('Standardize',self.standardizer)   # Progress-bar will start worker

        elif action == self.consolidate_metadata:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                start_folder_names = []
                for index in self.selectedIndexes():
                    start_folder_names.append(self.model.filePath(index))
                self.consolidator=ConsolidateMetadata(target=start_folder_names, await_start_signal=True)
                self.progress_bar=ProgressBarWidget('Consolidate',self.consolidator)   # Progress-bar will start worker

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
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.Files )
        self.setModel(self.model)
        self.__setFiletypeFilter(settings.file_types)
        self.hideFilteredFiles()    #Default is to hide filetered files. They can also be shown dimmed
                                    #by calling self.showFilteredFiles()

        #Set root-path
        self.setRootPath(dir_path)
        self.current_file = current_file

        # Prepare context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def createMenu(self, position):
        # Create the context menu
        self.menu = QMenu()


        # Add actions to the menu
        action_texts = settings.file_context_menu_actions.get("consolidate_metadata")  # All language descriptions of action
        action_text = action_texts.get(settings.language)
        self.consolidate_metadata = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("copy_metadata")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.copy_metadata = self.menu.addAction(action_text)

        action_texts = settings.file_context_menu_actions.get("paste_metadata")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        self.paste_metadata = self.menu.addAction(action_text)

        self.menu.addSeparator()
        action_texts = settings.file_context_menu_actions.get("choose_tags_to_paste")  # All language descriptions of action
        action_text  = action_texts.get(settings.language)
        menu_text_line = QAction(action_text, self, enabled=False)
        self.menu.addAction(menu_text_line)   # Just a textline in menu saying "Choose what to paste"

        # Ad checkable actions for each logical tag
        self.logical_tag_actions = {}
        for logical_tag in settings.logical_tags:
            tag_labels = settings.logical_tag_descriptions.get(logical_tag)  # All language descriptions of tag
            tag_label = tag_labels.get(settings.language)  # User-language description of tag
            tag_action = QAction(tag_label, self, checkable=True)
            tag_action.setChecked(True)
            self.logical_tag_actions[logical_tag] = tag_action

            self.menu.addAction(tag_action)
            tag_action.triggered.connect(self.toggleAction)

    def openMenu(self, position):
        if not hasattr(self,'menu'):    # First time clicked: Create context-menu
            self.createMenu(position)
        if self.menu == None:
            self.createMenu(position)

        action = self.menu.exec_(self.viewport().mapToGlobal(position))
        if action == self.consolidate_metadata:
            index = self.indexAt(position)  # Get index in File-list
            if index.isValid():
                file_names = []
                for index in self.selectedIndexes():
                    file_names.append(self.model.filePath(index))
                self.consolidator = ConsolidateMetadata(file_names)
                self.progress_bar = ProgressBarWidget('Consolidate', self.consolidator)  # Progress-bar will start worker

                for file_name in file_names:
                    ConsolidateMetadata(file_name)


        elif action == self.copy_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():
                self.menu.source_file_name = self.model.filePath(index)
            else:
                self.menu.source_file_name = None                # No item was clicked
        elif action == self.paste_metadata:
            index = self.indexAt(position)  # Get index in File-list
            # Check if an item was clicked
            if index.isValid():    # A valid file was right-clicked
                target_file_names = []
                for index in self.selectedIndexes():
                    target_file_names.append(self.model.filePath(index))

                target_logical_tags = []
                for logical_tag in self.logical_tag_actions:
                    if self.logical_tag_actions[logical_tag].isChecked():
                        target_logical_tags.append(logical_tag)

                self.copier = CopyLogicalTags(self.menu.source_file_name, target_file_names, target_logical_tags, await_start_signal=True)
                self.progress_bar = ProgressBarWidget('Copy Tags', self.copier)  # Progress-bar will start worker

            else:
                self.menu.target_file_name = None                # No item was clicked
        elif action == None:
            pass
        else:
            self.openMenu(position)    # Toggle one of te logical tags was chosen

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
                self.current_file=File.get_instance(chosen_path)   # Gets file-singleton. At the same time set singleton to chosen file

class File(QObject):
    __instance=None
    __file_name=''
                                                          # Widgets for tags updates this with what is in focus
                                                          # That way, __prepare_metadata_widgets (when metadata has changed)
                                                          # the focus can be put back on same element.
                                                          # value exampels:
                                                          #  data   (date-tag)
                                                          #  persons.line   (the line below persons list for adding new person)

    def __init__(self,file_name=""):
        super().__init__()
        # Main Layout for File Pane
        self.layout = QVBoxLayout()

        # Add file preview window in file pane
        self.file_preview = QLabel()
        self.layout.addWidget(self.file_preview)
        self.file_preview.setFixedSize(500, 500)
        self.file_preview.size().width().as_integer_ratio()

        # Add metadata-layout in file-panel
        self.metadata_layout = QGridLayout()
        self.layout.addLayout(self.metadata_layout)

        # Connect to file-renamer changesignal
        self.file_renamer = FileRenamer.get_instance()
        self.file_renamer.filename_changed_signal.connect(self.filename_changed)

        self.focus_tag = ''

        if file_name!=None and file_name!="":
            self.prepare_file_panel()

    @staticmethod
    def get_instance(file_name):
        if File.__instance==None:
            File.__instance=File(file_name)
        if file_name!=File.__file_name:
            File.__file_name=file_name
            File.__instance.prepare_file_panel()

        return File.__instance



    def prepare_file_panel(self):       # Happens each time a new filename is assigned
        # Get metadata-instance, and subscribe to changes
        self.file_metadata = None
        self.focus_tag = ''
        if self.__file_name != '':
            self.file_metadata = FileMetadata.get_instance(self.__file_name)
            self.file_metadata.change_signal.connect(self.metadata_changed)

        # Preview
        self.__prepare_preview()

        # Metadata widgets
        self.__prepare_metadata_widgets()

    def __prepare_preview(self):
        # Prepare preview and place in layout
        self.file_preview.clear()
        if self.__file_name != None and self.__file_name != '':
            pixmap = QPixmap(self.__file_name)
            self.pixmap = pixmap.scaled(self.file_preview.size().width(), self.file_preview.size().height(),
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.file_preview.setPixmap(self.pixmap)
            self.file_preview.setAlignment(Qt.AlignHCenter)

    def __prepare_metadata_widgets(self):
        clearLayout(self.metadata_layout)
        if self.__file_name != None and self.__file_name != '':
            tags = {}
            for logical_tag in self.file_metadata.logical_tag_values:
                tag_labels = settings.logical_tag_descriptions.get(logical_tag)  # All language descriptions of tag
                tag_label = tag_labels.get(settings.language)  # User-language description of tag
                tag_type = settings.logical_tags.get(logical_tag)
                if tag_type == "text_line":
                    tag_widget = TextLine(self, logical_tag)
                    tags[logical_tag] = [tag_label, tag_widget]
                elif tag_type == "text":
                    tag_widget = Text(self, logical_tag)
                    tags[logical_tag] = [tag_label, tag_widget]
                elif tag_type == "reference_tag":
                    tag_widget = Text(self, logical_tag)
                    tag_widget.setDisabled(True)
                    tags[logical_tag] = [tag_label, tag_widget]
                elif tag_type == "date_time":
                    tag_widget = DateTime(self, logical_tag)
                    tags[logical_tag] = [tag_label, tag_widget]
                elif tag_type == "date":
                    tag_widget = Date(self, logical_tag)
                    tags[logical_tag] = [tag_label, tag_widget]
                elif tag_type == "text_set":
                    tag_widget = TextSet(self, logical_tag)
                    tags[logical_tag] = [tag_label, tag_widget]
                else:
                    pass


            # Place all tags in gridlayout
            grid_row = 0
            spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            for logical_tag in tags:
                label_widget = QLabel(tags[logical_tag][0]+":")
                label_widget.setStyleSheet("color: #868686;")
                self.metadata_layout.addWidget(label_widget,grid_row,0)     # Label in column 0 of layout"
                self.metadata_layout.addWidget(tags[logical_tag][1], grid_row+1, 0)           # Widget in column 1 of layout"
                self.metadata_layout.addItem(spacerItem, grid_row+2, 0)
                grid_row += 3
            grid_row += 1

            # Set focus back to the widget that had focus before
            if self.focus_tag != None and self.focus_tag != '':
                tag_components = []
                tag_components = self.focus_tag.split('.')
                tag = tag_components[0]
                subwidget = None
                if len(tag_components) > 1:
                    subwidget = tag_components[1]
                tag_data = tags.get(tag)
                if tag_data:
                    if subwidget:
                        if hasattr(tag_data[1], subwidget):
                            if subwidget == 'tagInput':
                                tag_data[1].tagInput.setFocus()
                    else:
                        tag_data[1].setFocus()

    @staticmethod
    def metadata_changed(file_name):
        if file_name==File.__file_name:
            File.__instance.__prepare_metadata_widgets()      # If matadata changed in file shown in panel, then update metadata in panel

    @staticmethod
    def filename_changed(old_filename, new_filename):     # reacts on change filename
        FileMetadata.delete_instance(old_filename)        # file for this instance does not exist anymore

class TextLine(QLineEdit):
    def __init__(self,file,logical_tag):
        self.file = file                                                  #Widget should remember who it serves
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        super().__init__()


        #Get attributes of tag
        self.tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if self.tag_attributes.get("Autocomplete"):                       #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.get_instance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.set_file_name(autocompleter_file)
        self.__read_from_image()                                          #Puts text in Widget
        self.editingFinished.connect(self.__edited)

    def __read_from_image(self):
        self.setText(self.file.file_metadata.logical_tag_values.get(self.logical_tag))
        if hasattr(self, 'auto_complete_list') and self.text() != "":
            self.auto_complete_list.collect_item(self.text())    # Collect new entry in auto_complete_list

    def __edited(self):
        self.file.focus_tag = self.logical_tag                              # File can then refocus after preparing metadata in screen
        self.file.file_metadata.set_logical_tag_values({self.logical_tag: self.text()})
        self.file.file_metadata.save()
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collect_item(self.text())    # Collect new entry in auto_complete_list

class Text(QPlainTextEdit):
    def __init__(self,file,logical_tag):
        self.file = file                                                  #Widget should remember who it serves
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        super().__init__()     #Puts text in Widget
        #Get attributes of tag
        self.tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if self.tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.get_instance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.set_file_name(autocompleter_file)

        self.__read_from_image()                                          #Puts text in Widget


    def __read_from_image(self):
        self.setPlainText(self.file.file_metadata.logical_tag_values.get(self.logical_tag))
        if hasattr(self, 'auto_complete_list') and self.toPlainText() != "":
            self.auto_complete_list.collect_item(self.toPlainText())    # Collect new entry in auto_complete_list

    def focusOutEvent(self, event):
        self.__edited()

    def __edited(self):
        self.file.focus_tag = self.logical_tag                              # File can then refocus after preparing metadata in screen
        self.file.file_metadata.set_logical_tag_values({self.logical_tag: self.toPlainText()})
        self.file.file_metadata.save()
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collect_item(self.toPlainText())    # Collect new entry in auto_complete_list


class DateTime(QDateTimeEdit):
    def __init__(self,file,logical_tag):
        self.file = file                                                  #Widget should remember who it serves
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        super().__init__()

        self.setCalendarPopup(True)


        #Get attributes of tag
        self.tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if self.tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.get_instance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.set_file_name(autocompleter_file)

        self.__read_from_image()
        self.dateTimeChanged.connect(self.__edited)

    def __read_from_image(self):
        date_time = self.file.file_metadata.logical_tag_values.get(self.logical_tag)
        self.clear()
        self.setStyleSheet("color: #D3D3D3;")
        if date_time != "":  # Data was found
            date_time = date_time.replace(" ", ":")  # 2022/12/24 13:50:00 --> 2022/12/24:13:50:00
            date_time = date_time.replace("/", ":")  # 2022/12/24:13:50:00 --> 2022:12:24:13:50:00
            date_time_parts = date_time.split(":")   # 2022:12:24:13:50:00 --> ["2022", "12", "24", "13", "50", "00"]
            while len(date_time_parts) < 6:
                date_time_parts.append("")
            self.setDateTime(QDateTime(int(date_time_parts[0]), int(date_time_parts[1]), int(date_time_parts[2]),
                                       int(date_time_parts[3]), int(date_time_parts[4]), int(date_time_parts[5])))
            self.setStyleSheet("color: black")
            if hasattr(self, 'auto_complete_list'):
                self.auto_complete_list.collect_item(date_time)    # Collect new entry in auto_complete_list


    def __edited(self, date_time):
        self.file.focus_tag = self.logical_tag                              # File can then refocus after preparing metadata in screen
        date_time_string = date_time.toString("yyyy:MM:dd hh:mm:ss")
        self.file.file_metadata.set_logical_tag_values({self.logical_tag: date_time_string})
        self.file.file_metadata.save()
        self.setStyleSheet("color: black")
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collect_item(date_time)    # Collect new entry in auto_complete_list



class Date(QDateEdit):
    def __init__(self,file,logical_tag):
        self.file = file                                                  #Widget should remember who it serves
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        super().__init__()

        self.setCalendarPopup(True)

        #Get attributes of tag
        self.tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        if self.tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.get_instance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.set_file_name(autocompleter_file)

        self.__read_from_image()
        self.dateChanged.connect(self.__edited)

    def __read_from_image(self):
        date = self.file.file_metadata.logical_tag_values.get(self.logical_tag)
        self.setDate(QDate(1752,1,1))
        if date !="":
            date = date.replace("/", ":")          # 2022/12/24 --> 2022:12:24
            date_parts = date.split(":")           # 2022:12:24 --> ["2022", "12", "24"]
            while len(date_parts) < 3:
                date_parts.append("")
            self.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            if hasattr(self, 'auto_complete_list'):
                self.auto_complete_list.collect_item(date)  # Collect new entry in auto_complete_list

    def __edited(self, date):
        self.file.focus_tag = self.logical_tag                              # File can then refocus after preparing metadata in screen
        date_string = date.toString("yyyy:MM:dd")
        self.file.file_metadata.set_logical_tag_values({self.logical_tag: date_string})
        self.file.file_metadata.save()
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collect_item(date)    # Collect new entry in auto_complete_list


class TextSet(QWidget):
    def __init__(self, file,logical_tag):
        class TextList(QListWidget):
            drag_drop_signal = pyqtSignal()
            def __init__(self,text_set):
                super().__init__()
                self.text_set=text_set

            def dropEvent(self, event):
                super().dropEvent(event)
                self.text_set.file.focus_tag = self.text_set.logical_tag  # File can then refocus after preparing metadata in screen
                self.drag_drop_signal.emit()

        self.file = file                                      # Widget should remember who it serves
        self.logical_tag = logical_tag
        self.tagList = TextList(self)
        super().__init__()
        self.__initUI()

        self.__read_from_image()

    def __initUI(self):
        # Prepare tagList
        self.tagList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tagList.setDragDropMode(QListWidget.InternalMove)

        # Prepare tagInput with completer
        self.tagInput = QLineEdit()

        # Get attributes of tag
        self.tag_attributes = settings.logical_tag_attributes.get(self.logical_tag)
        self.auto_complete_list = None
        if self.tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.get_instance(self.logical_tag)
            self.tagInput.setCompleter(self.auto_complete_list)
            QTimer.singleShot(0, self.tagInput.clear)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.set_file_name(autocompleter_file)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.tagList)
        layout.addWidget(self.tagInput)
        self.setLayout(layout)

        # Connect buttons to functions
        self.tagInput.returnPressed.connect(self.__on_return_pressed)
        self.tagList.drag_drop_signal.connect(self.__edited)
        if self.auto_complete_list != None:
            self.auto_complete_list.activated.connect(self.__on_completer_activated)

    def __on_return_pressed(self):
        if self.auto_complete_list.currentCompletion():    # Return pressed in completer-list
            pass  #Return pressed from completer
        else:
            self.__addTag()  #Return pressed from QLineEdit

    def __on_completer_activated(self,text=''):
        self.__addTag()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.__removeTag()
            print('Delete pressed')
        else:
            super().keyPressEvent(event)

    def __read_from_image(self):
        text_list = self.file.file_metadata.logical_tag_values.get(self.logical_tag)
        if type(text_list) == str:
            self.text_list = [text_list]
        else:
            self.text_list = text_list
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collect_items(self.text_list)

        for text in self.text_list:
            self.tagList.addItem(text)

    def __addTag(self,completer_text=''):
        self.file.focus_tag = self.logical_tag+'.tagInput'                              # File can then refocus after preparing metadata in screen
        text = self.tagInput.text()
        if completer_text:                                  #Text selected from completer
            if self.auto_complete_list.completionMode() == QCompleter.InlineCompletion:         #Enter-key
                text = ''         #Enter-event already handled in text-line

        QTimer.singleShot(0, self.tagInput.clear)
        if text:
            self.tagList.addItem(text)
            if hasattr(self, 'auto_complete_list'):
                self.auto_complete_list.collect_item(text)    # Collect new entry in auto_complete_list
            self.__edited()

    def __removeTag(self):
        self.file.focus_tag = self.logical_tag                              # File can then refocus after preparing metadata in screen
        items = self.tagList.selectedItems()
        if items:
            for item in items:
                self.tagList.takeItem(self.tagList.row(item))
            self.__edited()

    def __edited(self):
        items = []
        count = self.tagList.count()
        for index in range(count):
            item = self.tagList.item(index)
            text = item.text()
            items.append(text)
        self.file.file_metadata.set_logical_tag_values({self.logical_tag: items})
        self.file.file_metadata.save()

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

    def get_input(self):
        # Return the input values as a tuple
        return (self.prefix.text(), self.num_pattern.text(), self.suffix.text())

