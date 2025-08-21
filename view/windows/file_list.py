import copy
import os

from PyQt6.QtCore import QDir, Qt, QModelIndex, QItemSelectionModel, QTimer
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtWidgets import QTreeView, QAbstractItemView, QMenu, QDialog

from configuration.language import Texts
from configuration.settings import Settings
from configuration.paths import Paths
from controller.events.emitters.current_file_changed_emitter import CurrentFileChangedEmitter
from controller.events.handlers.on_metadata_copied import onMetadataCopied
from services.file_services.file_delete_unused_originals import DeleteUnusedOriginals
from services.file_services.file_fetch_originals import FetchOriginals
from services.file_services.file_preserve_originals import PreserveOriginals
from services.file_services.file_standardize_names import StandardizeFilenames
from services.metadata_services.consolidate_metadata import ConsolidateMetadata
from services.metadata_services.copy_logical_tags import CopyLogicalTags
from view.windows.folder_selector import FolderSelectorDialog
from view.windows.input_file_name_pattern import InputFileNamePattern
from view.ui_components.progress_bar import ProgressBarWidget
from services.utility_services.parameter_manager import ParameterManager


class FileList(QTreeView):
    def __init__(self, dir_path=''):
        super().__init__()
        # Many files can be selected in one go
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Only show image- and video-files
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)

        self.setModel(self.model)
        self.__setFiletypeFilter(Settings.get('file_types'))
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

        # Keep track of when all directories are loaded, and set scroll position after last one is loaded
        self.pending_folders = set()
        self.pending_vertical_scroll_position = None  # Set in method setVerticalScrollPosition
        if dir_path is not None and dir_path !='':
            self.pending_folders.add(dir_path)
        self.model.directoryLoaded.connect(self.onDirectoryLoaded)

    def createMenu(self, position):

        self.actions = {}   # {action: id}
        self.menues = {"file_context_menu": QMenu()}

        for file_context_menu_entry in Settings.get('file_context_menu'):
            parent_menu_id = file_context_menu_entry.get('parent_id')
            entry_type = file_context_menu_entry.get("type")
            parent_menu = self.menues.get(parent_menu_id)

            if entry_type == "menu":
                menu = QMenu(Texts.get(file_context_menu_entry.get("text_key")))
                self.menues[file_context_menu_entry.get("id")]=menu
                parent_menu.addMenu(menu)
            elif entry_type == 'action':   #action
                action = QAction(Texts.get(file_context_menu_entry.get("text_key")))
                self.actions[file_context_menu_entry.get("id")] = action
                parent_menu.addAction(action)
            elif entry_type == 'text':
                action = QAction(Texts.get(file_context_menu_entry.get("text_key")),self,enabled=False)
                parent_menu.addAction(action)  # Just a textline in menu saying "Choose what to paste"
            elif entry_type == 'separator':
                parent_menu.addSeparator()


        # Ad checkable actions for each logical tag
        parent_menu = self.menues.get("file_context_menu")
        self.logical_tag_actions = {}
        for logical_tag in Settings.get('logical_tags'):
            if Settings.get('logical_tags').get(logical_tag).get("reference_tag"):  # Can't copy-paste a reference tag. It is derrived from the other tags
                continue
            if Settings.get('logical_tags').get(logical_tag).get('disable_in_context_menu') == True:   # Disable in context-menu
                continue
            if Settings.get('logical_tags').get(logical_tag).get("widget") == None:  # Can't copy-paste tags not shown in widget
                continue

            tag_label_text_key = Settings.get('logical_tags').get(logical_tag).get("label_text_key")
            if tag_label_text_key:
                tag_label = Texts.get(tag_label_text_key)
                tag_action = QAction(tag_label, self, checkable=True)
                if Settings.get('logical_tags').get(logical_tag).get("default_paste_select") == False:
                    tag_action.setChecked(False)
                else:
                    tag_action.setChecked(True)
                self.logical_tag_actions[logical_tag] = tag_action
                parent_menu.addAction(tag_action)
                tag_action.triggered.connect(self.toggleAction)

                if Settings.get('logical_tags').get(logical_tag).get("value_parts") is not None:
                    for value_part in Settings.get('logical_tags').get(logical_tag).get("value_parts"):
                        if Settings.get('logical_tags').get(logical_tag).get("value_parts").get(value_part).get('disable_in_context_menu') is True:
                            continue
                        tag_label_text_key = Settings.get('logical_tags').get(logical_tag).get("value_parts").get(value_part).get("label_text_key")
                        if tag_label_text_key:
                            tag_label = Texts.get(tag_label_text_key)
                            tag_action = QAction(tag_label, self, checkable=True)
                            if Settings.get('logical_tags').get(logical_tag).get("value_parts").get(value_part).get("default_paste_select") == False:
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
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_consolidate_metadata'),self.consolidator)  # Progress-bar will start worker

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
                    self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_standardize_filenames'),self.standardizer)  # Progress-bar will start worker

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
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
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
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
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
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
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
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_paste_metadata'), self.copier)  # Progress-bar will start worker
                self.source = []

            else:
                self.menu.target_file_name = None  # No item was clicked
        elif action_id == 'preserve_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                self.preserver = PreserveOriginals(target)
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_preserve_originals'), self.preserver)  # Progress-bar will start worker

        elif action_id == 'delete_unused_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                self.deleter = DeleteUnusedOriginals(target,await_start_signal=True)
                self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_delete_unused_originals'), self.deleter)  # Progress-bar will start worker

        elif action_id == 'fetch_originals':
            index = self.indexAt(self.position)  # Get index in File-list
            if index.isValid():
                target = self.model.filePath(index)
                ui_status = ParameterManager.getInstance(Paths.get('ui_status'))  # Fetch latest used originals location
                folder_dialog = FolderSelectorDialog(label_text=Texts.get('fetch_originals_dialog_label'),
                                                     placeholder_text=Texts.get('fetch_originals_dialog_placeholder_text'),
                                                     folder_path=ui_status.getParameter('originals_fetch_folder'),
                                                     selector_title=Texts.get('fetch_originals_dialog_selector_title'))
                if folder_dialog.exec():
                    source = folder_dialog.getFolderPath()
                    ui_status.setParameters({'originals_fetch_folder': source})  # Save last used originals location
                    self.fetcher = FetchOriginals(source=source,target=target,await_start_signal=True)
                    self.progress_bar = ProgressBarWidget(Texts.get('progress_bar_title_fetch_originals'), self.fetcher)  # Progress-bar will start worker


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
        pending_folders = []
        if open_folders:
            for open_folder in open_folders:
                # Find the QModelIndex corresponding to the folder_path
                folder_index = self.model.index(open_folder)
                if folder_index.isValid():  # Check if the folder exists in the model
                    pending_folders.append(open_folder)
        if pending_folders:
            self.pending_folders.update(pending_folders)
            for pending_folder in pending_folders:
                folder_index = self.model.index(pending_folder)
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
        if scroll_position is None:
            return
        self.pending_vertical_scroll_position = scroll_position
        if not self.pending_folders:
            self.verticalScrollBar().setValue(scroll_position)

    def onDirectoryLoaded(self, path: str):
        # This is called whe a folder is expanded. It keeps track of when the last folder has been expanded.
        # When that happens, it sets the correct scroll-position from last time program was loaded, but only at program-load,
        # where the pendig-folder list gets populated from last program run.
        if not self.pending_folders:
            return   # Pending folders from last program run has already been loaded. Now user just navigates the tree.
        self.pending_folders.discard(path)
        if not self.pending_folders:
            if self.pending_vertical_scroll_position:
                QTimer.singleShot(0, lambda: self.setVerticalScrollPosition(self.pending_vertical_scroll_position))

