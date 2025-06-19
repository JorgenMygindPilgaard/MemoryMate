import os
import webbrowser

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QScrollArea, QLabel, QWidget, QVBoxLayout, QMenu

from configuration.language import Texts
from configuration.settings import Settings
from configuration.paths import Paths
from view.ui_components.file_preview import FilePreview
from services.metadata_services.metadata import FileMetadata
from view.ui_components.metadata_widgets import TextLine, Text, DateTime, Date, TextSet, GeoLocation, Rotation, Rating


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
            new_file_name = os.path.join(Paths.get('resources'), "Memory Mate Sample Photo.jpg")
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
        if FilePanel.file_metadata is not None:
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
                if Settings.get('logical_tags').get(logical_tag) == None: # Is the case for parts, e.g date.utc_offset
                    continue
                if Settings.get('logical_tags').get(logical_tag).get("widget") == None:
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
        open_in_browser_action_text = Texts.get("preview_menu_open_in_browser")
        open_in_browser_action = QAction(open_in_browser_action_text)
        open_in_browser_action.triggered.connect(FilePanel.openInBrowser)
        context_menu.addAction(open_in_browser_action)

        # Add the "Open in Default Program" action to the context menu
        open_in_default_program_action_text = Texts.get("preview_menu_open_in_default_program")
        open_in_default_program_action = QAction(open_in_default_program_action_text)
        open_in_default_program_action.triggered.connect(FilePanel.openInDefaultProgram)
        context_menu.addAction(open_in_default_program_action)


        # Show the context menu at the specified position
        context_menu.exec(FilePanel.preview_widget.mapToGlobal(pos))

    def openInBrowser(self):
        if FilePanel.file_preview != None:
            current_image_path = os.path.join(Paths.get('data'), "current_image.jpg")
            FilePanel.file_preview.getImage().save(current_image_path)
            current_image_html_path = os.path.join(Paths.get('data'), "current_image.html")
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
        for logical_tag in Settings.get('logical_tags'):
            tag_label = None
            new_line = Settings.get('logical_tags').get(logical_tag).get("new_line")
            if new_line == None:
                new_line = True
            tag_label_key = Settings.get('logical_tags').get(logical_tag).get("label_text_key")
            if tag_label_key:
                tag_label = Texts.get(tag_label_key)
            tag_widget_type = Settings.get('logical_tags').get(logical_tag).get("widget")

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

            if Settings.get('logical_tags').get(logical_tag).get("reference_tag"):
                tag_widget.setDisabled(True)


    @staticmethod
    def onPixmapChanged(file_name):
        if file_name == FilePanel.file_name:
            FilePanel.__instance.prepareFilePanel()  # If pixmap changed in file shown in panel, then update preview