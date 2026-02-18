from datetime import datetime, timedelta,timezone
from configuration.settings import Settings
import copy

class StringValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None                # String
        self.used_tags = []

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if self.value is not None:    # Only set value from first exif-tag with value
            return
        self.value = str(value).strip()
        if self.value == '':
            self.value = None
        else:
            self.used_tags = [exif_tag]


    def setValue(self,value,part=None,overwrite=True):
        if not overwrite and self.value is not None:
            return
        if isinstance(value,str):
            self.value = str(value).strip()
            if self.value == '':
                self.value = None
        else:
            self.value = None

    def getExifValue(self,exif_tag):
        if self.value is None:
            return None
        if exif_tag == 'IPTC:Caption-Abstract':
            if len(self.value.encode('utf-8')) >= 2000:
                return None
        return self.value

    def getValue(self,part=None):
        return self.value

    def getUsedTags(self):
        return self.used_tags

class ListValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None                # List of strings
        self.used_tags = []

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if self.value is not None:    # Only set value from first exif-tag with value
            return

        if isinstance(value, list):
            cleaned_list = [str(list_entry).strip() for list_entry in value if str(list_entry).strip() != '' and list_entry is not None]
            if cleaned_list == []:
                self.value = None
            else:
                self.value = cleaned_list
        elif isinstance(value,str):
            if exif_tag == "EXIF:XPKeywords":
                self.value = [str(keyword).strip() for keyword in value.split(";")]
            else:
                cleaned_value = str(value).strip()
                if cleaned_value == '':
                    self.value = None
                else:
                    self.value = [cleaned_value]
        if self.value is not None:
            self.used_tags = [exif_tag]

    def setValue(self,value,part=None,overwrite=True):
        if not overwrite and self.value is not None:
            return
        if isinstance(value, list):
            cleaned_list = [str(list_entry).strip() for list_entry in value if str(list_entry).strip() != '' and list_entry is not None]
            if cleaned_list == []:
                self.value = None
            else:
                self.value = cleaned_list
        elif isinstance(value, str):
            cleaned_value = str(value).strip()
            if cleaned_value == '':
                self.value = None
            else:
                self.value = [cleaned_value]
        else:
            self.value = None

    def getExifValue(self,exif_tag):
        if exif_tag == "EXIF:XPKeywords":
            if self.value is None:
                return None
            else:
                return ";".join(map(str, self.value))
        else:
            if self.value is None:
                return None
            else:
                if len(self.value)==1:
                    return self.value[0]   #If only one value in list, it should return as string, not list, as this is how exiftool delivers it
                else:
                    return self.value

    def getValue(self,part=None):
        return self.value

    def getUsedTags(self):
        return self.used_tags

class RotationValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None                # Rotation 0, 90, 180, 270
        self.orientation = None          # 0°:1, 90°:8, 180°:3, 270°:6
        self.used_tags = []

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if self.value is not None:    # Only set value from first exif-tag with value
            return

        if exif_tag == 'EXIF:Orientation#':     #Orientation id-number being set
            if value == 1 or value == 2:     # 1: Normal, 2: Flipped horizontally (mirrored)
                self.value = 0
            elif value == 3 or value == 4:   # 3: Rotated 180°, 4: Flipped vertically (mirrored)
                self.value = 180
            elif value == 5 or value == 6:   # 5: Transpose (Mirror across top-left ↔ bottom-right line), 6: Rotated 270° CCW
                self.value = 270
            elif value == 7 or value == 8:   # 7: Traverse (Mirror across top-right ↔ bottom-left line), 8: Rotated 90° CCW
                self.value = 90
            else:
                self.value = None   #Not defined value leads to "None"
        elif exif_tag == 'Composite:Rotation':      # Composite:Rotation direction is clockwise, logical tag Rotation is counter clockwise
            self.value = 360 - value
            if self.value >=  360:
                self.value -= 360
        else:
            self.value = value
        if self.value is not None:
            self.used_tags = [exif_tag]

    def setValue(self,value,part=None,overwrite=True):
        if not overwrite and self.value is not None:
            return
        self.value = value

    def getExifValue(self,exif_tag):
        if exif_tag == 'EXIF:Orientation#':     #Orientation id-number being read
            if self.value == 0:
                return 1
            elif self.value == 90:
                return  8
            elif self.value == 180:
                return 3
            elif self.value == 270:
                return 6
            else:
                return None
        elif exif_tag == 'Composite:Rotation':      # Composite:Rotation direction is clockwise, logical tag Rotation is counter clockwise
            if self.value is None:
                value = None
            else:
                value = 360 - self.value
            if value >=  360:
                value -= 360
            return value
        else:                                  #Rotation in degree being read. Being used in QuickTime:Rotation (heic-images)
            return self.value

    def getValue(self,part=None):
        return self.value

    def getUsedTags(self):
        return self.used_tags

class RatingValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None                # Rating between 0 and 5
        self.used_tags = []

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if self.value is not None:    # Only set value from first exif-tag with value
            return
        if exif_tag == 'XMP:RatingPercent':
            if value == 0:                          # 0% --> Rating 0
                self.value = 0
            elif value == 1:                        # 1% --> Rating 1
                self.value = 1
            else:
                self.value = value / 25 + 1         # 25% --> Rating 2, 50% --> Rating 3, 75% -->Rating 4, 100% --> Rating 5
        else:
            self.value = value
        if self.value is not None:
            self.used_tags = [exif_tag]


    def setValue(self,value,part=None,overwrite=True):
        if not overwrite and self.value is not None:
            return
        self.value = value

    def getExifValue(self, exif_tag):
        if self.value is None:
            return self.value
        elif exif_tag == 'XMP:RatingPercent':
            if self.value == 0:
                return 0
            elif self.value == 1:
                return 1
            else:
                return ( self.value - 1 ) * 25
        else:
            return self.value

    def getValue(self,part=None):
        return self.value

    def getUsedTags(self):
        return self.used_tags

class DateTimeValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None
        self.used_tags = []
        self.date_time_change = None
        self.old_value = None
        # "2024-08-30T10:02:58"         Local date time known. Fraction of sec unknown. UTC-offset unknown.
        # "2024-08-30T10:02:58.000000"  Local date time known. Fraction of sec know. UTC-offset unknown.
        # "2024-08-30T10:02:58Z"        Only UTC date time (not local) known. Fraction of sec unknown. UTC-offset unknown.
        # "2024-08-30T10:02:58+00:00"   Local date time known. Fraction of sec unknown. UTC-offset known.
        # "+00:00"                      date time unknown. Fraction of sec unknown. UTC-offset known.
        # ".000000"                     date time unknown. Fraction of sec unknown. UTC-offset unknown.
        # ".000000+00:00"               date time unknown. Fraction of sec known. UTC-offset known
        self.date_time_parts = self.__splitDateTime()

    def __splitDateTime(self,date_time=None):
        date_time_parts = {'utc_date_time': None,
                           'local_date_time': None,
                           'fraction_of_second': None,
                           'utc_offset': None
                           }
        # Date/time is empty
        if date_time is None or date_time == "":
            return date_time_parts

        # Date/time contains date/time, possible with fraction of second and possible with UTC-ofset
        else:   # Holds date time and/or utc-offset
            if len(date_time) > 6:  # Containd date/time
                start_pos = 19
            else:
                start_pos = 0

            # Set Utc-offset
            utc_offset_index = date_time.find('+', start_pos)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('-', start_pos)
            if utc_offset_index == -1:
                utc_offset_index = date_time.find('Z', start_pos)
            if utc_offset_index != -1:
                date_time_parts['utc_offset'] = date_time[utc_offset_index:]

            # Date/time is UTC-date/time
            if date_time_parts['utc_offset'] == 'Z':
                if start_pos == 19:   # Holds date/time
                    date_time_parts['utc_date_time'] = date_time[0:19]   # Date/time without fraction of second
            else:
                if start_pos == 19:   # Holds date/time
                    date_time_parts['local_date_time'] = date_time[0:19]   # Date/time without fraction of second

            # Fraction of second
            if date_time_parts['utc_date_time'] is not None or date_time_parts['local_date_time'] is not None:   # Date/time was found
                dot_index = date_time.find('.')
                if dot_index != -1:
                    if utc_offset_index == -1:
                        fraction_of_second = date_time[dot_index + 1:]
                    else:
                        fraction_of_second = date_time[dot_index + 1:utc_offset_index]

                    if fraction_of_second.strip('0 '):     # String contains more than just space and 0
                        date_time_parts['fraction_of_second'] = fraction_of_second
                    else:
                        date_time_parts['fraction_of_second'] = None
        return date_time_parts

    def __mergeDataTimeParts(self, date_time_parts):
        date_time = ''
        if date_time_parts.get('utc_offset') == 'Z':
            if date_time_parts['utc_date_time'] is not None:
                date_time = date_time + date_time_parts['utc_date_time']
        else:
            if date_time_parts.get('local_date_time') is not None:
                date_time = date_time + date_time_parts['local_date_time']

        if date_time != '':
            if date_time_parts.get('fraction_of_second') is not None:
                date_time = date_time + '.' + date_time_parts['fraction_of_second']
        if date_time_parts.get('utc_offset') is not None:
            date_time = date_time + date_time_parts['utc_offset']
        if date_time == '':
            return None
        else:
            return date_time

    def __getUtcOffset(self,local_date_time,utc_date_time):
        # Return None if can't be calculated
        if local_date_time is None or local_date_time == "" or utc_date_time is None or utc_date_time == "":
            return None

        # Parse the date strings into datetime objects
        local_dt_value = datetime.fromisoformat(local_date_time)
        utc_dt_value = datetime.fromisoformat(utc_date_time)

        # Calculate the difference between local and UTC times
        utc_offset_value = local_dt_value - utc_dt_value
        utc_offset_seconds = utc_offset_value.total_seconds()

        if utc_offset_seconds >= 0:
            sign_str = '+'
        else:
            sign_str = '-'

        # Convert the difference to hours and minutes for the UTC offset format
        hours, remainder = divmod(utc_offset_seconds, 3600)
        minutes = int(remainder // 60 // 15 + 0.5) * 15  # only 00, 15, 30, 45 is allowed

        # Format the offset as "+HH:MM" or "-HH:MM"
        utc_offset = f"{sign_str}{int(abs(hours)):02}:{int(abs(minutes)):02}"
        return utc_offset
    
    def __getLocalDateTime(self,utc_offset,utc_date_time):
        # Return None if can't be calculated. (Notice that Z means that time is UTC and that UTC-offset for local time is unknown)
        if utc_offset is None or utc_offset == "" or utc_offset == 'Z' or utc_date_time is None or utc_date_time == "":
            return None

        # Parse the UTC time
        utc_dt_value = datetime.fromisoformat(utc_date_time)

        # Parse the UTC offset
        hours = int(utc_offset[1:3])
        minutes = int(utc_offset[4:])
        offset = timedelta(hours=hours, minutes=minutes)
        local_timezone = timezone(offset)

        # Convert UTC time to local time with the specified offset
        local_dt_value = utc_dt_value.astimezone(local_timezone)

        # Format as ISO 8601 string in local time
        local_date_time = local_dt_value.isoformat(sep='T',timespec='seconds')
        offset_index = local_date_time.find("+")
        if offset_index == -1:
            offset_index = local_date_time.find("-")
        if offset_index != -1:
            local_date_time = local_date_time[:offset_index]
        dot_index = utc_date_time.find(".")
        if dot_index != -1:    # Fraction of seconds exist
            local_date_time = local_date_time + utc_date_time[dot_index:]
        return local_date_time

    def __getUtcDateTime(self,utc_offset,local_date_time):
        # Return None if can't be calculated
        if utc_offset is None or utc_offset == "" or local_date_time is None or local_date_time == "":
            return None

        # Parse the local time string with timezone info
        local_dt_value = datetime.fromisoformat(local_date_time+utc_offset)

        # Convert to UTC
        utc_dt_value = local_dt_value.astimezone(timezone.utc)

        # Format as ISO 8601 string in UTC
        utc_date_time = utc_dt_value.isoformat(sep='T',timespec='seconds').replace("+00:00","")
        dot_index = local_date_time.find(".")  #Fraction of seconds exist
        if dot_index != -1:    # Fraction of seconds exist
            utc_date_time = utc_date_time + local_date_time[dot_index:]

        return utc_date_time

    def __enrichDateTime(self):
        # Try to derive missing parts
        if self.date_time_parts['utc_offset'] is None:
            self.date_time_parts['utc_offset'] = self.__getUtcOffset(self.date_time_parts['local_date_time'],self.date_time_parts['utc_date_time'])
        if self.date_time_parts['local_date_time'] is None:
            self.date_time_parts['local_date_time'] = self.__getLocalDateTime(self.date_time_parts['utc_offset'],self.date_time_parts['utc_date_time'])
        if self.date_time_parts['utc_date_time'] is None:
            self.date_time_parts['utc_date_time'] = self.__getUtcDateTime(self.date_time_parts['utc_offset'],self.date_time_parts['local_date_time'])

        # Set new value
        self.value = self.__mergeDataTimeParts(self.date_time_parts)

    def __replaceChar(self, s,position, new_char):
        # Ensure position is within bounds of the string
        if s is None:
            return None
        elif position < 0 or position >= len(s):
            return s
        else:
            # Reconstruct the string with the new character
            return s[:position] + new_char + s[position + 1:]

    def __difference(self,value_1,value_2):
        if value_1 is None or value_2 is None:
            return None
        if value_1 == value_2:
            return None
        try:
            time_delta = datetime.fromisoformat(value_2) - datetime.fromisoformat(value_1)
            return time_delta.total_seconds()
        except ValueError as e:
            return None

    def __addTime(self,value,delta):
        if value == '' or value is None:
            return None

        if delta is None:
            delta_sec = 0
        else:
            delta_sec = delta
        try:
            dt = datetime.fromisoformat(value) + timedelta(days=0,seconds=delta_sec)
            return dt.isoformat(sep='T',timespec='seconds')
        except ValueError as e:
            return None

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        str_value = str(value)   # Converts SubSec from number to string. The rest is already string

        # Do nothing, if string contains only zeros as number-digits
        if len(str_value) > 6:    # Means that it is a date (Not offset, not subsec)
            number_value = ''.join([char for char in str_value if char.isdigit()])   #All number-characters in string
            zero_value = ''.join([char for char in str_value if char == '0'])       #All zero number-characters in string
            if number_value == zero_value:     # If value contains 0000:00:00 00:00:00 do nothing
                return


        old_value = self.value

        # Local date-time with fraction and offset
        if exif_tag in ['XMP:Date','XMP:DateCreated','IPTC:DateCreated','QuickTime:CreationDate','RIFF:DateTimeOriginal','File:FileCreateDate']:   # 2024:10:15 14:00:00.123+02:00
            # Convert 2024:10:15 14:00:00.123+02:00 --> 2024-10-15T14:00:00.123+02:00
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')
            self.setValue(value=date_time,part=None,overwrite=False)

        # Local date-time without fraction and offset
        elif exif_tag in ['EXIF:DateTimeOriginal', 'EXIF:CreateDate']: # 2024:10:15 14:00:00
            # Convert 2024:10:15 14:00:00 --> 2024-10-15T14:00:00
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')
            self.setValue(value=date_time,part=None,overwrite=False)

        # UTC date-time with fraction, without utc-offset
        elif exif_tag in ['QuickTime:MediaCreateDate', 'QuickTime:CreateDate', 'QuickTime:ModifyDate', 'QuickTime:MediaModifyDate', 'QuickTime:TrackCreateDate', 'QuickTime:TrackModifyDate']: # 2024:10:15 14:00:00.123
            # Convert 2024:10:15 14:00:00.123 --> 2024-10-15T14:00:00.123Z
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')
            date_time += 'Z'
            self.setValue(value=date_time,part=None,overwrite=False)

        # UTC date-time with fraction, without utc-offset
        elif exif_tag == 'JSON:PhotoTakenTimeTimestamp':
            dt_value = datetime.utcfromtimestamp(float(value))
            date_time = dt_value.isoformat(sep='T', timespec='seconds') + "Z"
            self.setValue(value=date_time,part=None,overwrite=False)

        # utc-offset
        elif exif_tag in ['EXIF:OffsetTimeOriginal','EXIF:OffsetTimeDigitized','EXIF:OffsetTime']: # +02:00
            date_time = value
            self.setValue(value=date_time,part='utc_offset',overwrite=False)

        elif exif_tag in ['EXIF:SubSecTimeOriginal','EXIF:SubSecTimeDigitized','EXIF:SubSecTime']: # 123
            date_time = str(value)
            self.setValue(value=date_time,part='fraction_of_second',overwrite=False)

        if self.value != old_value:
            self.used_tags.append(exif_tag)

        test_value = self.value


    def setValue(self,value,part=None,overwrite=True):
        if value is None and part is None and overwrite:    # Delete scenario
            self.value = None
            self.date_time_parts = self. __splitDateTime(self.value)
            return
        if not overwrite:          # Don't overwrite existing values, if patching is chosen
            if part == 'latest_change':
                return      # updating by a delta will always overwrite, so patching is not an option
            elif part is not None and self.date_time_parts.get(part) is not None:
                return
            elif part is None and self.value is not None:
                return

        next_old_value = self.value  # Old value also will be shown in widget
        old_date_time_parts = copy.deepcopy(self.date_time_parts)
        if part is not None:
            if part == 'latest_change':
                self.date_time_parts['local_date_time'] = self.__addTime(self.date_time_parts.get('local_date_time'),value)  # Add delta to local date/time
                self.date_time_parts['utc_date_time'] = self.__addTime(self.date_time_parts.get('utc_date_time'),value)      # Add delta to local date/time
            elif part == 'fraction_of_second':
                if value is not None:
                    if str(value).strip("0 "):   # Contains no only space and 0
                        self.date_time_parts[part] = str(value)
            else:
                self.date_time_parts[part] = value
        else:
            date_time_parts = self.__splitDateTime(value)   # All parts set from provided date/time
            for date_time_part in date_time_parts:
                if date_time_parts.get(date_time_part) is None:
                    continue
                if not overwrite and self.date_time_parts.get(date_time_part) is not None:
                    continue
                self.date_time_parts[date_time_part] = date_time_parts.get(date_time_part)

        self.__enrichDateTime()   # Derrives missing parts if possible and value from parts
        date_time_change = self.__difference(old_date_time_parts.get('local_date_time'),self.date_time_parts.get('local_date_time'))
        if date_time_change is None:
            date_time_change = self.__difference(old_date_time_parts.get('utc_date_time'),self.date_time_parts.get('utc_date_time'))
        if date_time_change is not None:    # Change to date/time (not only change to UTC-offset)
            self.date_time_change = date_time_change
            self.old_value = next_old_value

        test_value = self.value

    def getExifValue(self,exif_tag):
        if self.value is None:
            return None
        # Local date-time with fraction and offset
        if exif_tag in ['XMP:Date','XMP:DateCreated','QuickTime:CreationDate','RIFF:DateTimeOriginal','File:FileCreateDate']:   # 2024:10:15 14:00:00.123+02:00
            if self.date_time_parts.get('local_date_time') is None and self.date_time_parts.get('utc_date_time') is None:
                return None
            else:
                date_time = self.value
                # 2024-15-15T14:00:00.123+02:00--> 2024:10:15 14:00:00.123+02:00
                date_time = self.__replaceChar(date_time,4,':')
                date_time = self.__replaceChar(date_time,7,':')
                date_time = self.__replaceChar(date_time,10,' ')
                return date_time


        # Local date
        elif exif_tag in ['IPTC:DateCreated']:   # 2024:10:15
            if self.date_time_parts.get('local_date_time') is None and self.date_time_parts.get('utc_date_time') is None:
                return None
            else:
                # 2024-15-15T14:00:00.123+02:00--> 2024:10:15
                date = self.value[:10]
                date = self.__replaceChar(date,4,':')
                date = self.__replaceChar(date,7,':')
                return date


        # Local date-time without fraction and offset
        elif exif_tag in ['EXIF:DateTimeOriginal', 'EXIF:CreateDate']:  # 2024:10:15 14:00:00
            if self.date_time_parts.get('local_date_time') is None:
                return None
            else:
                date_time = self.date_time_parts.get('local_date_time')
                date_time = self.__replaceChar(date_time,4,':')
                date_time = self.__replaceChar(date_time,7,':')
                date_time = self.__replaceChar(date_time,10,' ')
                return date_time

        # UTC date-time with fraction, without utc-offset
        elif exif_tag in ['QuickTime:MediaCreateDate', 'QuickTime:CreateDate', 'QuickTime:TrackCreateDate']:  # 2024:10:15T14:00:00.123
            date_time = self.date_time_parts.get('utc_date_time')
            if date_time is not None:
                if self.date_time_parts.get('fraction_of_second') is not None:
                    fraction_of_seconds = float('0.'+str(self.date_time_parts.get('fraction_of_second')))
                    if fraction_of_seconds >= 0.5:
                        date_time = self.__addTime(date_time,1)
                date_time = self.__replaceChar(date_time,4,':')
                date_time = self.__replaceChar(date_time,7,':')
                date_time = self.__replaceChar(date_time,10,' ')
            return date_time

        # utc-offset
        elif exif_tag in ['EXIF:OffsetTimeOriginal', 'EXIF:OffsetTimeDigitized', 'EXIF:OffsetTime']:  # +02:00
            if self.date_time_parts.get('local_date_time') is None:
                return None
            else:
                utc_offset = self.date_time_parts.get('utc_offset')
                if  utc_offset == 'Z':   # Means that only UTC-time is known
                    return '+00:00'
                else:
                    return utc_offset

        elif exif_tag in ['EXIF:SubSecTimeOriginal', 'EXIF:SubSecTimeDigitized', 'EXIF:SubSecTime']:  # 123
            if self.date_time_parts.get('local_date_time') is None:
                return None
            else:
                fraction = None
                fraction_str = self.date_time_parts.get('fraction_of_second')
                if isinstance(fraction_str,str):
                    fraction_str = fraction_str.replace(".", "")
                try:
                    fraction = int(fraction_str)
                except:
                    pass
                return fraction


    def getValue(self,part=None):
        if part is None:
            return self.value
        elif part == 'utc_date_time':
            return self.date_time_parts.get('utc_date_time')
        elif part == 'utc_offset':
            return self.date_time_parts.get('utc_offset')
        elif part == 'latest_change':
            return self.date_time_change
        elif part == 'old_value':
            return self.old_value
        else:
            return None

    def getUsedTags(self):
        return self.used_tags

class GeoLocationValue():
    def __init__(self,logical_tag=None):
        self.logical_tag = logical_tag
        self.value = None                # 37.7749,-122.4194
        self.latitude = None
        self.longitude = None
        self.used_tags = []

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if self.value is not None:    # Only set value from first exif-tag with value
            return

        if exif_tag in ['JSON:GeoDataExifLatitude','JSON:GeoDataLatitude']:
            if self.latitude is None and str(value) != '0.0':
                self.latitude = value
                self.used_tags.append(exif_tag)
        elif exif_tag in ['JSON:GeoDataExifLongitude','JSON:GeoDataLongitude']:
            if self.longitude is None and str(value) != '0.0':
                self.longitude = value
                self.used_tags.append(exif_tag)
        else:
            if ',' in value:
                self.latitude, self.longitude = (value.split(",", 1))    # " 55.65656565 N,  "9.65656565 E"

                self.latitude = self.latitude.replace(" ","")                 # "55.65656565N"
                self.latitude = self.latitude.replace("N","")                 # "55.65656565"
                if "S" in self.latitude:                                      # "10.65656565S"
                    self.latitude = "-"+self.latitude.replace("S","")         # "-10.65656565"

                self.longitude = self.longitude.replace(" ","")               # "9.65656565E"
                self.longitude = self.longitude.replace("E","")               # "9.65656565"
                if "W" in self.longitude:                                     # "10.65656565W"
                    self.longitude = "-"+self.longitude.replace("W","")     # "-10.65656565"
                self.used_tags.append(exif_tag)

        # Set missing values where possible
        if self.latitude is not None and self.latitude is not None:
            self.value = self.latitude + "," + self.longitude

    def setValue(self,value,part=None,overwrite=True):
        if not overwrite and self.value is not None:
            return
        self.value = value
        if self.value is None:
            self.latitude = None
            self.longitude = None
        else:
            self.latitude, self.longitude = (self.value.split(",", 1))  # "55.65656565,"9.65656565"

    def getExifValue(self,exif_tag):
        if self.value is None:
            return None
        else:
            if exif_tag == 'Composite:GPSPosition':
                if "-" in self.latitude:
                    latitude_string = self.latitude.replace("-","")+" S"
                else:
                    latitude_string = self.latitude + " N"
                if "-" in self.longitude:
                    longitude_string = self.longitude.replace("-","")+" W"
                else:
                    longitude_string = self.longitude+" E"
                result = latitude_string+", " + longitude_string
            else:
                result = self.value
            return result

    def getValue(self,part=None):
        return self.value

    def getUsedTags(self):
        return self.used_tags









