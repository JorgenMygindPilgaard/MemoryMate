from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QDateTimeEdit, QDateEdit, QPushButton, QListWidget, QAbstractItemView,QSpacerItem,QSizePolicy,QAbstractSpinBox
from PyQt6.QtCore import Qt, QDateTime, QDate, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFontMetrics,QPixmap,QIcon,QKeyEvent, QFocusEvent
from configuration.settings import Settings
from configuration.paths import Paths
from services.metadata_services.metadata import FileMetadata
from view.ui_components.auto_complete_list import  AutoCompleteList
from view.windows.map_location_selector import MapView, MapLocationSelector
from controller.events.emitters.image_rotated_emitter import ImageRotatedEmitter
import os



class TextLine(QLineEdit):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMaximumWidth(1250)
        self.auto_complete_list = None

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                       #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(Paths.get('data'), "autocomplete_" + self.logical_tag + '.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()

    def setDisabled(self, a0):
        super().setFrame(False)
        super().setDisabled(a0)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            text_line = file_metadata.getLogicalTagValues().get(self.logical_tag)
            if isinstance(text_line,str):
                if text_line.isspace():
                    text_line = ''
            if text_line is None:
                return
            self.setText(text_line)
            if self.auto_complete_list is not None and self.text() != '':
                self.auto_complete_list.collectItem(self.text())    # Collect new entry in auto_complete_list
    def logicalTagValue(self):
        logical_tag_value = self.text()
        if logical_tag_value == '':
            logical_tag_value = None   # Empty string corresponds to None-value
        if self.auto_complete_list is not None and logical_tag_value is not None:  # Collect in autocomplete-list
            self.auto_complete_list.collectItem(logical_tag_value)
        return logical_tag_value

    def updateFilename(self, file_name):
        self.file_name = file_name

class Text(QPlainTextEdit):
    instance_index = {}
    def __init__(self, file_name, logical_tag):
        super().__init__()     #Puts text in Widget
        Text.instance_index[file_name] = self
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMinimumHeight(50)
        self.setMaximumWidth(1250)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.auto_complete_list = None

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(Paths.get('data'), "autocomplete_" + self.logical_tag + '.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width()!=event.size().width():
            self.setFixedHeight(self.__widgetHeight(event.size().width()))   #Calculates new height from new width
    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()
    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            text = file_metadata.getLogicalTagValues().get(self.logical_tag)
            if isinstance(text,str):
                if text.isspace():
                    text = ''
            if text is None:
                return
            self.setPlainText(text)
            self.setFixedHeight(self.__widgetHeight(self.width()))      #Calculates needed height from width and text
            if self.auto_complete_list is not None and self.toPlainText() != '':
                self.auto_complete_list.collectItem(self.toPlainText())    # Collect new entry in auto_complete_list

    def logicalTagValue(self):
        logical_tag_value = self.toPlainText()
        if logical_tag_value == '':
            logical_tag_value = None
        if self.auto_complete_list is not None and logical_tag_value is not None:   # Collect value in autocomplete-list
            self.auto_complete_list.collectItem(logical_tag_value)
        return logical_tag_value

    def __widgetHeight(self, new_widget_width=-1):
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

class DateTime(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.auto_complete_list = None
        self.locked = True

        # Field for editing date/time
        self.date_time = None
        self.date_time_edit = self.DateTimeEdit(parent=self)
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.date_time_edit.setFixedWidth(150)
        self.date_time_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Field for showing old date/time from before latest edit
        self.old_date_time = None
        self.old_date_time_edit = self.DateTimeEdit()
        self.old_date_time_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.old_date_time_edit.setFixedWidth(150)
        self.old_date_time_edit.setFrame(False)  # Disable frame
        self.old_date_time_edit.setReadOnly(True)  # Make it non-editable
        self.old_date_time_edit.setDisabled(True)
        self.old_date_time_edit.setHidden(True)
        self.old_date_time_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.old_date_time_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        font = self.old_date_time_edit.font()
        font.setStrikeOut(True)  # Enable strikethrough
        self.old_date_time_edit.setFont(font)

        # Field for editing UTC-offset
        self.offset_edit = self.TimeOffsetLineEdit()
        self.offset_edit.setFixedWidth(60)
        self.offset_edit.setPlaceholderText("±00:00")

        # Fraction of seconds (kept unchanged)
        self.second_fraction = ''

        # Icon for locking/unlocking date/time edit
        self.padlock = self.Padlock('closed')
        self.__setEditMode('closed')
        self.padlock.toggled.connect(self.__setEditMode)

        # Space between fields
        self.space = QSpacerItem(0,0,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

        # Layout to hold both date-time edit and offset edit
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.date_time_edit,alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.offset_edit,alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.padlock,alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.old_date_time_edit,alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addSpacerItem(self.space)

        self.setLayout(self.layout)

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(Paths.get('data'), "autocomplete_" + self.logical_tag + '.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()

    class DateTimeEdit(QDateTimeEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.blank_date_time = QDateTime(1753, 1, 1, 0, 0, 0, 1)
            self.parent_widget = parent  # Store a reference to the parent widget
            self.setSpecialValueText(' ')
            self.setMinimumDateTime(self.blank_date_time)
            self.setDateTime(self.blank_date_time)

        def focusOutEvent(self, event: QFocusEvent):
            # Call the parent's focus-out handler if it exists
            if self.parent_widget:
                self.parent_widget.atFocusOutEvent()
            super().focusOutEvent(event)  # Ensure default behavior is preserved

    def __setEditMode(self,state):
        if state == 'open':
            self.date_time_edit.setDisabled(False)
            self.offset_edit.setDisabled(False)
            if self.date_time_edit.dateTime()==self.date_time_edit.blank_date_time:
                self.date_time_edit.setDateTime(QDateTime(2000,1,1,0,0,0))
        else:
            self.date_time_edit.setDisabled(True)
            self.offset_edit.setDisabled(True)

    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()

    def __fillDateTimeEdit(self,date_time_edit,date_time):
        if len(date_time)>6:  # Data was found
            year = int(date_time[0:4])
            month = int(date_time[5:7])
            day = int(date_time[8:10])
            hour = int(date_time[11:13])
            minute = int(date_time[14:16])
            second = int(date_time[17:19])
            date_time_edit.setDateTime(QDateTime(year, month, day, hour, minute, second))
        else:
            date_time_edit.setDateTime(self.date_time_edit.blank_date_time)
        return date_time_edit

    def __fillOffsetEdit(self,offset_edit,date_time):
        offset_edit.clear()
        if date_time != "" and date_time is not None:  # Data was found
            utc_offset = ''
            if len(date_time)>6:    # Containd date/time
                start_pos = 19
            else:
                start_pos = 0
            utc_offset_index = date_time.find('+', start_pos)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('-', start_pos)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('Z', start_pos)
            if utc_offset_index != -1:
                utc_offset = date_time[utc_offset_index:]
                if utc_offset == 'Z':
                    utc_offset = 'UTC'
            offset_edit.setText(utc_offset)
        return offset_edit

    def __fillSecondFraction(self,date_time):
        second_fraction_index = date_time.find('.')
        second_fraction = ''  # Widget never modifies fraction. It just remembers and reinsert after correction
        if second_fraction_index != -1:
            utc_offset_index = date_time.find('+', 19)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('-', 19)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('Z', 19)
            if utc_offset_index != -1:
                second_fraction = date_time[second_fraction_index:utc_offset_index]
            else:
                second_fraction = date_time[second_fraction_index:]
        return second_fraction

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            tags = file_metadata.getLogicalTagValues()
            self.date_time = file_metadata.getLogicalTagValues().get(self.logical_tag) # 2022-12-24T13:50:00+02:00

            if self.date_time is None:
                return

            # Fill date/time edit
            # if self.date_time!= "" and self.date_timeis not None:  # Data was found
            #     self.date_time_edit.setStyleSheet("color: black")
            # else:
            #     self.date_time_edit.setStyleSheet("color: #D3D3D3;")
            self.date_time_edit = self.__fillDateTimeEdit(self.date_time_edit,self.date_time)

            # Fill offset edit
            # if self.date_time!= "" and self.date_time is not None:  # Data was found
            #     self.offset_edit.setStyleSheet("color: black")
            # else:
            #     self.offset_edit.setStyleSheet("color: #D3D3D3;")
            self.offset_edit = self.__fillOffsetEdit(self.offset_edit,self.date_time)

            # Fill fraction of second
            self.second_fraction = self.__fillSecondFraction(self.date_time)

            # Fill old date/time edit (to display time before change with strike through)

            self.old_date_time = file_metadata.getLogicalTagValues().get(self.logical_tag+'.old_value')  # 2022-12-24T13:50:00+02:00
            if self.old_date_time!= "" and self.old_date_time is not None:     # If old time differs (exist)
                self.old_date_time_edit = self.__fillDateTimeEdit(self.old_date_time_edit,self.old_date_time)
                self.old_date_time_edit.setHidden(False)
            else:
                self.old_date_time_edit == self.__fillDateTimeEdit(self.old_date_time_edit,self.date_time)
                self.old_date_time_edit.setHidden(True)

            # Fill autocompleter
            if self.date_time!= "" and self.date_time is not None:  # Data was found
                if self.auto_complete_list is not None:
                    self.auto_complete_list.collectItem(self.date_time)    # Collect new entry in auto_complete_list

    def logicalTagValue(self):
        if self.date_time_edit.dateTime()==self.date_time_edit.blank_date_time:
            logical_tag_value = ''
        else:
            logical_tag_value = self.date_time_edit.dateTime().toString("yyyy-MM-ddThh:mm:ss")
            if self.second_fraction != '':
                logical_tag_value = logical_tag_value + self.second_fraction
        if self.offset_edit.text()=='UTC':
            logical_tag_value = logical_tag_value + 'Z'
        else:
            logical_tag_value = logical_tag_value + self.offset_edit.text()
        if logical_tag_value == '':
            logical_tag_value = None
        if self.auto_complete_list is not None and logical_tag_value is not None:  # Collect value in autocomplete-list
            self.auto_complete_list.collectItem(logical_tag_value)
        return logical_tag_value

    def atFocusOutEvent(self):
        next_old_date_time = self.date_time
        self.date_time = self.logicalTagValue()

        if next_old_date_time is None or next_old_date_time == "":   # Adding date for the first time
            self.old_date_time = next_old_date_time
            self.old_date_time_edit.clear()
            self.old_date_time_edit.setHidden(True)
        else:
            if self.date_time is None or self.date_time == "":    # Clearing a date
                self.old_date_time = next_old_date_time
                self.old_date_time_edit = self.__fillDateTimeEdit(self.old_date_time_edit, self.old_date_time)
                self.old_date_time_edit.setHidden(False)
            elif self.date_time[:19] != next_old_date_time[:19]:   # Changing a date
                self.old_date_time = next_old_date_time
                self.old_date_time_edit = self.__fillDateTimeEdit(self.old_date_time_edit, self.old_date_time)
                self.old_date_time_edit.setHidden(False)
            else:                                                 # Date/time not changed
                pass



        if self.date_time is None or self.date_time == "" or next_old_date_time is None or next_old_date_time == "":
            self.old_date_time_edit.setHidden(True)
        elif self.date_time[:19] != next_old_date_time[:19]:
            self.old_date_time = next_old_date_time
            self.old_date_time_edit.setHidden(False)
            self.old_date_time_edit = self.__fillDateTimeEdit(self.old_date_time_edit, self.old_date_time)
        else:
            self.old_date_time_edit.setHidden(True)



    class TimeOffsetLineEdit(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMaxLength(6)  # To ensure the format "+HH:MM"

        def focusInEvent(self, event: QFocusEvent):
            super().focusInEvent(event)
            self.selectAll()

        def keyPressEvent(self, event: QKeyEvent):
            if self.text() == self.selectedText():
                self.clear()
            text = self.text()
            key = event.key()
            input_char = event.text()

            # Allow navigation keys
            if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Left, Qt.Key.Key_Right):
                super().keyPressEvent(event)
                return

            if len(self.text()) == 0:
                if input_char in ['Z', 'U', 'z', 'u']:    #UTC Time-zone
                    self.setText('UTC')
                elif input_char in ['+', '-']:
                    self.setText(input_char)
                elif input_char in ['0', '1', '2']:
                    self.setText('+' + input_char)
                    self.first_hour_digit = input_char
            elif len(self.text()) == 1 and self.text() != 'Z':  # Expecting first digit in hours (HH)
                if input_char in ['0', '1', '2']:
                    text += input_char
                    self.setText(text)
                    self.first_hour_digit = input_char
            elif len(self.text()) == 2:  # Expecting second digit in hours (HH)
                if input_char.isdigit():
                    if self.first_hour_digit in ['0', '1'] or input_char in ['0', '1', '2',
                                                                             '3']:  # 00-09, 10-19 or 20-23"
                        text += input_char + ':'
                        self.setText(text)
            elif len(self.text()) == 4:  # Expecting first digit in minutes (MM)
                if input_char in ['0', '1', '3', '4']:  # 00, 15, 30 and 45 allowed
                    text += input_char
                    self.setText(text)
                    self.first_minute_digit = input_char
            elif len(self.text()) == 5:  # Expecting second digit in minutes (MM)
                if input_char.isdigit():
                    if self.first_minute_digit in ['0', '3'] and input_char in ['0'] or self.first_minute_digit in ['1','4'] and input_char in [ '5']:
                        text += input_char
                        self.setText(text)

    class Padlock(QLabel):
        toggled = pyqtSignal(str)
        def __init__(self,state):
            super().__init__()

            # Set up the layout and size
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setFixedSize(24, 24)

            # Load images
            self.closed_padlock = QPixmap(os.path.join(Paths.get('resources'), "closed_padlock.png")).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.open_padlock = QPixmap(os.path.join(Paths.get('resources'), "open_padlock.png")).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # Set initial image to closed padlock
            self.current_state = state
            if state == 'open':
                self.setPixmap(self.open_padlock)
                self.current_state = 'open'
            else:
                self.setPixmap(self.closed_padlock)
                self.current_state = 'closed'


            # Enable click event
            self.mousePressEvent = self.__togglePadlock

        def __togglePadlock(self, event):
            # Toggle the image on click
            if self.current_state == "closed":
                self.setPixmap(self.open_padlock)
                self.current_state = "open"
            else:
                self.setPixmap(self.closed_padlock)
                self.current_state = "closed"
            self.toggled.emit(self.current_state)

class Date(QDateEdit):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.blank_date = QDate(1753, 1, 1)
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setCalendarPopup(True)
        self.setFixedWidth(250)
        self.auto_complete_list = None

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(Settings.get('data'), "autocomplete_" + self.logical_tag + '.txt')
            self.auto_complete_list.setFileName(autocompleter_file)

        self.readFromImage()

    def wheelEvent(self, event):
        # Ignore the wheel event
        event.ignore()

    def readFromImage(self):
        self.setDate(self.blank_date)
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            date = file_metadata.getLogicalTagValues().get(self.logical_tag)
            if date is None:
                return
            if date !="":
                date = date.replace("/", ":")          # 2022/12/24 --> 2022:12:24
                date_parts = date.split(":")           # 2022:12:24 --> ["2022", "12", "24"]
                while len(date_parts) < 3:
                    date_parts.append("")
                self.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                if self.auto_complete_list is not None:
                    self.auto_complete_list.collectItem(date)  # Collect new entry in auto_complete_list
    def logicalTagValue(self):
        if self.date() == self.blank_date:
            logical_tag_value = None
        else:
            logical_tag_value = self.date().toString("yyyy:MM:dd")
            if self.auto_complete_list is not None:  # Collect value in autocomplete-list
                self.auto_complete_list.collectItem(logical_tag_value)
        return logical_tag_value

class TextSet(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag  # Widget should remember who it serves
        self.text_list = self.TextList()
        self.text_list.setFixedWidth(300)
        self.text_input = self.TextInput('Tast navn')
        self.auto_complete_list = None
        self.return_pressed = False        # Prevent return-pressed to add two entries in list, if autocompleter active
        self.__initUI()
        self.readFromImage()
        self.timer_text_input_clear = QTimer(self)
        self.timer_text_input_clear.timeout.connect(self.__clearTextInput)

    def __initUI(self):
        # Prepare text_input with completer
        # Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        self.auto_complete_list = None
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(self.logical_tag)
            self.text_input.setCompleter(self.auto_complete_list)
            QTimer.singleShot(0, self.text_input.clear)
            autocompleter_file = os.path.join(Paths.get('data'), "autocomplete_" + self.logical_tag + '.txt')
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
        if self.auto_complete_list is not None:
           self.auto_complete_list.activated.connect(self.__onCompleterActivated)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            tags = file_metadata.getLogicalTagValues().get(self.logical_tag)
            if tags is None:
                return
            if type(tags) == str:
                tag_list = [tags]
            else:
                tag_list = tags
            if self.auto_complete_list is not None:
                self.auto_complete_list.collectItems(tag_list)
            self.text_list.clear()
            for tag in tag_list:
                self.text_list.addItem(tag)
            self.text_list.setFixedHeight(self.text_list.widgetHeight())  # Calculates needed height for the number of items

    def logicalTagValue(self):
        # Collect the entry in autocomplete-list
        logical_tag_value = []
        count = self.text_list.count()
        for index in range(count):
            item = self.text_list.item(index)
            text = item.text()
            logical_tag_value.append(text)
        if self.auto_complete_list is not None:                             # Collect value in autocomplete-list
            self.auto_complete_list.collectItems(logical_tag_value)
        if logical_tag_value == []:
            logical_tag_value = None
        return logical_tag_value

    def __clearTextInput(self):
        self.text_input.clear()
        self.timer_text_input_clear.stop()

    def __onReturnPressed(self):
        self.return_pressed = True
        text_input_to_be_added = self.text_input.text()
        if text_input_to_be_added != '':
            if self.auto_complete_list is not None:
                self.auto_complete_list.collectItem(text_input_to_be_added)
            self.timer_text_input_clear.start(100)
            self.text_list.addTag(text_input_to_be_added)

    def __onCompleterActivated(self, text):
        text_input_to_be_added = self.text_input.text()
        if text_input_to_be_added !='':
            if self.return_pressed != True:
                self.text_list.addTag(text_input_to_be_added)
            self.timer_text_input_clear.start(100)
        self.return_pressed = False

    class TextList(QListWidget):

        def __init__(self,text_set=None):
            super().__init__()
            self.text_set=text_set    #Remember who you are serving
            self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        def keyPressEvent(self, event):
            super().keyPressEvent(event)
            if event.key() == Qt.Key.Key_Delete:
                self.__removeTag()

        def __removeTag(self):
            items = self.selectedItems()
            if items:
                for item in items:
                    self.takeItem(self.row(item))

        def addTag(self,text):
            self.addItem(text)

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
        self.auto_complete_list = None

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)
        if tag_attributes.get("Autocomplete"):                         #Enable autocompletion
            self.auto_complete_list = AutoCompleteList.getInstance(logical_tag)
            self.setCompleter(self.auto_complete_list)
            autocompleter_file = os.path.join(Settings.get('data'), "autocomplete_" + self.logical_tag + '.txt')
            self.auto_complete_list.setFileName(autocompleter_file)
        self.readFromImage()
        self.setLocationZoom(location=self.marker_location, zoom=15)
        self.setMarkerLocation(self.marker_location)

        self.enterEvent = self.__onEnter
        self.leaveEvent = self.__onLeave

    def __onEnter(self,event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def __onLeave(self,event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow



    def __onMarkerLocationChanged(self, marker_location=[]):
        self.marker_location = marker_location
        self.setLocationZoom(location=self.marker_location, zoom=15)
        self.setMarkerLocation(self.marker_location)

    def onLeftButton(self):          #redefined
        if self.marker_location:
            self.map_location_selector = MapLocationSelector(location=self.marker_location,marker_location=self.marker_location)
        else:
            self.map_location_selector = MapLocationSelector(location=[0,0], zoom=1)
        self.map_location_selector.marker_location_changed.connect(self.__onMarkerLocationChanged)
        self.map_location_selector.show()

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            gps_position_string = file_metadata.getLogicalTagValues().get(self.logical_tag)    # "50.454545 -0.959595"
            if gps_position_string is None:
                self.marker_location = None
                return
            if gps_position_string != '' and gps_position_string is not None:
                if ',' in gps_position_string:
                    gps_position_parts = gps_position_string.split(",")
                else:
                    gps_position_parts = gps_position_string.split(" ")
                self.marker_location = [float(gps_position_parts[0]),float(gps_position_parts[1])]
                if self.auto_complete_list is not None:
                    self.auto_complete_list.collectItem(gps_position_string)  # Collect new entry in auto_complete_list
            else:
                self.marker_location = None

    def logicalTagValue(self):
        # Collect the entry in autocomplete-list
        if self.marker_location is not None:
            logical_tag_value = str(self.marker_location[0])+','+str(self.marker_location[1])
        else:
            logical_tag_value = None
        if self.auto_complete_list is not None and logical_tag_value != '' and logical_tag_value is not None:    # Collect value in autocomplete-list
            self.auto_complete_list.collectItem(logical_tag_value)
        return logical_tag_value

class Rotation(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag
        self.rotation = None
        self.__initUI()

    def __initUI(self):
        self.layout = QHBoxLayout()

        # Create a QLabel for "rotate_left" image
        self.left_image_label = QLabel()
        rotate_left_pixmap = QPixmap(os.path.join(Paths.get('resources'), 'rotate_left.png')).scaled(25, 25, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.left_image_label.setPixmap(rotate_left_pixmap)  # Replace with your image file
        self.left_image_label.mousePressEvent = self.__onRotateLeft

        # Create a QLabel for "rotate_right" image
        self.right_image_label = QLabel()
        rotate_right_pixmap = QPixmap(os.path.join(Paths.get('resources'), 'rotate_right.png')).scaled(25, 25, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.right_image_label.setPixmap(rotate_right_pixmap)  # Replace with your image file
        self.right_image_label.mousePressEvent = self.__onRotateRight
        self.left_image_label.enterEvent = self.__onEnterLeft
        self.left_image_label.leaveEvent = self.__onLeaveLeft
        self.right_image_label.enterEvent = self.__onEnterRight
        self.right_image_label.leaveEvent = self.__onLeaveRight


        self.layout.addStretch(1)
        self.layout.addWidget(self.left_image_label)
        self.layout.addWidget(self.right_image_label)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            rotation = file_metadata.getLogicalTagValues().get(self.logical_tag)
            if rotation is None:
                return
            self.rotation = rotation

    def logicalTagValue(self):
        return self.rotation

    def __onRotateLeft(self, event):
        if self.rotation == 0 or self.rotation is None:
            self.rotation = 90        #  90° CCW
        elif self.rotation == 90:     #  90° CCW
            self.rotation = 180       # 180°
        elif self.rotation == 180:    # 180°
            self.rotation = 270       # 270° CCW
        elif self.rotation == 270:    # 270° CCW
            self.rotation = 0
        else:
            self.rotation = 0
        image_rotated_emitter = ImageRotatedEmitter.getInstance()
        image_rotated_emitter.emit(self.file_name)


    def __onRotateRight(self, event):
        if self.rotation == 0 or self.rotation is None:
            self.rotation = 270      # 270° CCW
        elif self.rotation == 270:   # 270° CCW
            self.rotation = 180      # 180° CCW
        elif self.rotation == 180:   # 180° CCW
            self.rotation = 90       #  90° CCW
        elif self.rotation == 90:    #  90° CCW
            self.rotation = 0
        else:
            self.rotation = 0
        image_rotated_emitter = ImageRotatedEmitter.getInstance()
        image_rotated_emitter.emit(self.file_name)

    def __onEnterLeft(self,event):
        self.left_image_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def __onLeaveLeft(self,event):
        self.left_image_label.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow
    def __onEnterRight(self,event):
        self.right_image_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def __onLeaveRight(self,event):
        self.right_image_label.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

class Rating(QWidget):
    def __init__(self, file_name, logical_tag):
        super().__init__()
        self.file_name = file_name
        self.logical_tag = logical_tag                                    #Widget should remember who it serves
        self.setMaximumWidth(200)
        self.auto_complete_list = None
        self.rating = 0
        self.icon_grey_star = QIcon(os.path.join(Paths.get('resources'), 'grey_star.png'))
        self.icon_grey_star_outline = QIcon(os.path.join(Paths.get('resources'), 'grey_star_outline.png'))
        self.icon_yellow_star = QIcon(os.path.join(Paths.get('resources'), 'yellow_star.png'))
        self.icon_reset = QIcon(os.path.join(Paths.get('resources'), 'reset_icon.png'))

        #Get attributes of tag
        tag_attributes = Settings.get('logical_tags').get(self.logical_tag)

        self.__initUI()
        self.readFromImage()

    def __initUI(self):
        self.stars = []
        self.layout = QHBoxLayout()

        button_and_star_style = (
            "border: none;"
            "background: transparent;"
            "outline: none;"
        )

        star_size = 15  # Define the size for stars (adjust as needed)
        button_size = 15  # Define the size for the reset button (adjust as needed)

        for i in range(5):
            star = QPushButton()
            star.setIcon(self.icon_grey_star_outline)  # Load a grey star icon
            star.setIconSize(QSize(star_size, star_size))
            star.clicked.connect(self.__onStarClick)
            star.setStyleSheet(button_and_star_style)
            self.stars.append(star)
            self.layout.addWidget(star)

#        spacer = QSpacerItem(100, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#        self.layout.addItem(spacer)  # Add a spacer to create space

        self.reset_button = QPushButton()
        self.reset_button.setIcon(self.icon_reset)  # Load a reset icon
        self.reset_button.setIconSize(QSize(button_size, button_size))
        self.reset_button.clicked.connect(self.__resetStars)
        self.reset_button.setStyleSheet(button_and_star_style)
        self.layout.addWidget(self.reset_button)

        self.setLayout(self.layout)

        self.enterEvent = self.__onEnter
        self.leaveEvent = self.__onLeave

    def __onEnter(self,event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def __onLeave(self,event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow



    def __onStarClick(self):
        sender = self.sender()
        star_index = self.stars.index(sender)

        if self.rating is None:     # If rating was not set before, set the start rating to clicked star
            self.rating = star_index + 1
        else:
            # Last yellow star can toggle. That enables setting zero stars
            if star_index == self.rating - 1:   #Last yellow star clicked
                self.rating = self.rating - 1   #Toggles to grey
            else:
                self.rating = star_index + 1

        # Set colour on all stars
        self.__setStarColour(self.rating)



    def __resetStars(self):
        self.rating = None
        self.__setStarColour(self.rating)

    def __setStarColour(self, value):
        if value is None:
            for star in self.stars:
                star.setIcon(self.icon_grey_star_outline)  # Load a grey star icon
        else:
            yellow_stars = min(max(value, 0), 5)  # Ensure value is between 0 and 5
            for i, star in enumerate(self.stars):
                if i < yellow_stars:
                    star.setIcon(self.icon_yellow_star)  # Load a yellow star icon
                else:
                    star.setIcon(self.icon_grey_star)  # Load a grey star icon

    def readFromImage(self):
        file_metadata = FileMetadata.getInstance(self.file_name)
        if file_metadata:
            self.rating = file_metadata.getLogicalTagValues().get(self.logical_tag)
            self.__setStarColour(self.rating)

    def logicalTagValue(self):
        logical_tag_value = self.rating
        return logical_tag_value

    def updateFilename(self, file_name):
        self.file_name = file_name
