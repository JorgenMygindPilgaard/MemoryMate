from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QDateTimeEdit, QDateEdit, QPushButton, QListWidget, QAbstractItemView, QDialog
from PyQt6.QtCore import Qt, QDateTime, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFontMetrics,QPixmap
import settings
from file_metadata_util import FileMetadata
from ui_util import AutoCompleteList
from ui_pick_gps_location import MapView, MapLocationSelector
import os

class TextLine(QLineEdit):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMaximumWidth(1250)

        #Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                       #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()
        self.editingFinished.connect(self.__edited)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            text_line = file_metadata.logical_tag_values.get(self.logical_tag)
            if text_line == None:
                return
            self.setText(text_line)
            if hasattr(self, 'auto_complete_list') and self.text() != "":
                self.auto_complete_list.collectItem(self.text())    # Collect new entry in auto_complete_list

    def __edited(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: self.text()})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.text())    # Collect new entry in auto_complete_list
    def updateFilename(self,file_name):
        self.file_name = file_name
#        FilePanel.focus_tag=self.logical_tag
class Text(QPlainTextEdit):
    def __init__(self, file_name, logical_tag):
        super().__init__()     #Puts text in Widget
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMinimumHeight(50)
        self.setMaximumWidth(1250)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        #Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            text = file_metadata.logical_tag_values.get(self.logical_tag)
            if text == None:
                return
            self.setPlainText(text)
            self.setFixedHeight(self.widgetHeight(self.width()))      #Calculates needed height from width and text
            if hasattr(self, 'auto_complete_list') and self.toPlainText() != "":
                self.auto_complete_list.collectItem(self.toPlainText())    # Collect new entry in auto_complete_list
    def focusOutEvent(self, event):
        self.__edited()

    def __edited(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: self.toPlainText()})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.toPlainText())    # Collect new entry in auto_complete_list
#        FilePanel.focus_tag=self.logical_tag

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
        text_width = font_metrics.horizontalAdvance(self.toPlainText())

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
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves

        self.setCalendarPopup(True)
        self.setFixedWidth(250)

        display_format = self.displayFormat()
        if not 'mm.ss' in display_format.lower():
            self.setDisplayFormat(display_format+'.ss')
        display_format = self.displayFormat()



        #Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            date_time = file_metadata.logical_tag_values.get(self.logical_tag)
            if date_time == None:
                return
            self.clear()
            self.setStyleSheet("color: #D3D3D3;")
            if date_time != "" and date_time != None:  # Data was found
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: date_time_string})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.dateTime())    # Collect new entry in auto_complete_list
        self.setStyleSheet("color: black")
#        FilePanel.focus_tag=self.logical_tag
class Date(QDateEdit):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves

        self.setCalendarPopup(True)
        self.setFixedWidth(250)

        #Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            date = file_metadata.logical_tag_values.get(self.logical_tag)
            if date == None:
                return
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: date_string})
        if hasattr(self, 'auto_complete_list'):
            self.auto_complete_list.collectItem(self.date())    # Collect new entry in auto_complete_list
#        FilePanel.focus_tag=self.logical_tag
class TextSet(QWidget):

    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag  # Widget should remember who it serves
        self.text_list = self.TextList()
        self.text_list.setFixedWidth(300)

        self.text_input = self.TextInput('Tast navn')
        self.__initUI()
        self.readFromImage()

        self.timer_text_input_clear = QTimer(self)
        self.timer_text_input_clear.timeout.connect(self.__clearTextInput)

    def __initUI(self):
        # Prepare text_input with completer
        # Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
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
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        # Connect buttons to functions
        self.text_input.returnPressed.connect(self.__onReturnPressed)
        self.text_list.edit_signal.connect(self.__edited)
        if self.auto_complete_list != None:
           self.auto_complete_list.activated.connect(self.__onCompleterActivated)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            tags = file_metadata.logical_tag_values.get(self.logical_tag)
            if tags == None:
                return
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
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: items})
#        FilePanel.focus_tag=self.logical_tag
    def __clearTextInput(self):
        self.text_input.clear()
        self.timer_text_input_clear.stop()

    def __onReturnPressed(self):
        self.text_list.addTag(self.text_input.text())  # Return pressed from QLineEdit
        self.auto_complete_list.collectItem(self.text_input.text())
        self.text_input.clear()
        self.timer_text_input_clear.start(100)

    def __onCompleterActivated(self, text):
        if self.text_input.text() !='':
            self.text_list.addTag(self.text_input.text())
            self.timer_text_input_clear.start(100)

    class TextList(QListWidget):
        edit_signal = pyqtSignal()


        def __init__(self,text_set=None):
            super().__init__()
            self.text_set=text_set    #Remember who you are serving
            self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        def dropEvent(self, event):
            super().dropEvent(event)
            self.edit_signal.emit()

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() == Qt.Key.Key_Delete:
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
class GeoLocation(MapView):
    def __init__(self, file_name, logical_tag):
        super().__init__(marker_editable=False, drag_enabled=False, zoom_enabled=False)
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setFixedWidth(250)
        self.setFixedHeight(250)

        #Get attributes of tag
        tag_attributes = settings.logical_tags.get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(settings.app_data_location, "autocomplete_" + self.logical_tag +'.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()
        self.setLocationZoom(location=self.marker_location, zoom=15)
        self.setMarkerLocation(self.marker_location)

    def onMarkerLocationChanged(self, marker_location=[]):
        self.marker_location = marker_location
        self.setLocationZoom(location=self.marker_location, zoom=15)
        self.setMarkerLocation(self.marker_location)
        self.__edited()

    def onLeftButton(self):          #redefined
        if self.marker_location:
            self.map_location_selector = MapLocationSelector(location=self.marker_location,marker_location=self.marker_location)
        else:
            self.map_location_selector = MapLocationSelector(location=[0,0], zoom=1)
        self.map_location_selector.marker_location_changed.connect(self.onMarkerLocationChanged)
        self.map_location_selector.show()


    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            gps_position_string = file_metadata.logical_tag_values.get(self.logical_tag)    # "50.454545 -0.959595"
            if gps_position_string == None:
                return
            if gps_position_string != "" and gps_position_string != None:
                if ',' in gps_position_string:
                    gps_position_parts = gps_position_string.split(",")
                else:
                    gps_position_parts = gps_position_string.split(" ")
                self.marker_location = [float(gps_position_parts[0]),float(gps_position_parts[1])]
                if hasattr(self, 'auto_complete_list'):
                    self.auto_complete_list.collectItem(gps_position_string)  # Collect new entry in auto_complete_list
            else:
                self.marker_location = None

    def __edited(self):
        if self.marker_location:
            marker_location_string = str(self.marker_location[0])+','+str(self.marker_location[1])
        else:
            marker_location_string = ''
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: marker_location_string})
        # if hasattr(self, 'auto_complete_list'):
        #     self.auto_complete_list.collectItem(self.date())    # Collect new entry in auto_complete_list
#        FilePanel.focus_tag=self.logical_tag
class Orientation(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag
        self.orientation = None
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()


        # Create a QLabel for "rotate_left" image
        self.left_image_label = QLabel()
        self.left_image_label.setPixmap(QPixmap('rotate_left.png'))  # Replace with your image file
        self.left_image_label.mousePressEvent = self.onRotateLeft

        # Create a QLabel for "rotate_right" image
        self.right_image_label = QLabel()
        self.right_image_label.setPixmap(QPixmap('rotate_right.png'))  # Replace with your image file
        self.right_image_label.mousePressEvent = self.onRotateRight


        self.layout.addStretch(1)
        self.layout.addWidget(self.left_image_label)
        self.layout.addWidget(self.right_image_label)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.setWindowTitle('Image Rotator')
        self.setGeometry(20, 20, 800, 20)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            orientation = file_metadata.logical_tag_values.get(self.logical_tag)
            if orientation == None:
                return
            self.orientation = orientation

    def __edited(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: self.orientation})

    def onRotateLeft(self, event):
        if self.orientation == 1 or self.orientation == None:     # 1: Not Rotated
            self.orientation = 8                                  # 8: Rotated 270 CW
        elif self.orientation == 8:                               # 8: Rotated 270 CW
            self.orientation = 3                                  # 3: Rotated 180
        elif self.orientation == 3:                               # 3: Rotated 180
            self.orientation = 6                                  # 6: Rotated 90 CW
        elif self.orientation == 6:                               # 6: Rotated 90 CW
            self.orientation = 1                                  # 1: Not Rotated
        else:
            self.orientation = 1
        self.__edited()

    def onRotateRight(self, event):
        if self.orientation == 1 or self.orientation == None:     # 1: Not Rotated
            self.orientation = 6                                  # 6: Rotated 90 CW
        elif self.orientation == 6:                               # 6: Rotated 90 CW
            self.orientation = 3                                  # 3: Rotated 180
        elif self.orientation == 3:                               # 3: Rotated 180
            self.orientation = 8                                  # 8: Rotated 270 CW
        elif self.orientation == 8:                               # 8: Rotated 270 CW
            self.orientation = 1                                  # 1: Not Rotated
        else:
            self.orientation = 1
        self.__edited()

class Rotation(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag
        self.rotation = None
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()


        # Create a QLabel for "rotate_left" image
        self.left_image_label = QLabel()
        self.left_image_label.setPixmap(QPixmap('rotate_left.png'))  # Replace with your image file
        self.left_image_label.mousePressEvent = self.onRotateLeft

        # Create a QLabel for "rotate_right" image
        self.right_image_label = QLabel()
        self.right_image_label.setPixmap(QPixmap('rotate_right.png'))  # Replace with your image file
        self.right_image_label.mousePressEvent = self.onRotateRight


        self.layout.addStretch(1)
        self.layout.addWidget(self.left_image_label)
        self.layout.addWidget(self.right_image_label)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.setWindowTitle('Image Rotator')
        self.setGeometry(20, 20, 800, 20)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            rotation = file_metadata.logical_tag_values.get(self.logical_tag)
            if rotation == None:
                return
            self.rotation = rotation

    def __edited(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        file_metadata.setLogicalTagValues({self.logical_tag: self.rotation})

    def onRotateLeft(self, event):
        if self.rotation == 0 or self.rotation == None:
            self.rotation = 90
        elif self.rotation == 90:
            self.rotation = 180
        elif self.rotation == 180:
            self.rotation = 270
        elif self.rotation == 270:
            self.rotation = 0
        else:
            self.rotation = 0
        self.__edited()

    def onRotateRight(self, event):
        if self.rotation == 0 or self.rotation == None:
            self.rotation = 270
        elif self.rotation == 270:
            self.rotation = 180
        elif self.rotation == 180:
            self.rotation = 90
        elif self.rotation == 90:
            self.rotation = 0
        else:
            self.rotation = 0
        self.__edited()

