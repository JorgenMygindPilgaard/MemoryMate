from datetime import datetime, timedelta,timezone

class StringValue():
    def __init__(self):
        self.value = None                # String

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        self.value = value

    def setValue(self, value):
        if value == '':
            self.value = None
        else:
            self.value = value

    def getExifValue(self,exif_tag):
        if self.value is None:
            return ''
        else:
            return self.value

    def getValue(self):
        return self.value

class ListValue():
    def __init__(self):
        self.value = None                # List of strings

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if isinstance(value, list):
            self.value = value
        else:
            self.value = [value]

    def setValue(self, value):
        if value == '' or value == [] or value is None:
            self.value = None
        elif isinstance(value, list):
            self.value = value
        else:
            self.value = [value]

    def getExifValue(self,exif_tag):
        if self.value is None:
            return []
        else:
            return self.value

    def getValue(self):
        return self.value

class RotationValue():
    def __init__(self):
        self.value = None                # Rotation 0, 90, 180, 270
        self.orientation = None          # 0°:1, 90°:8, 180°:3, 270°:6

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if exif_tag == 'EXIF:Orientation#':     #Orientation id-number being set
            if value == 1:
                self.value = 0
            elif value == 8:
                self.value = 90
            elif value == 3:
                self.value = 180
            elif value == 6:
                self.value = 270
            else:
                self.value = 0
        else:                                  #Rotation in degree. Being used in QuickTime:Rotation (heic-images)
            self.value = value

    def setValue(self, value):
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
                return 1
        else:                                  #Rotation in degree being read. Being used in QuickTime:Rotation (heic-images)
            return self.value

    def getValue(self):
        return self.value

class RatingValue():
    def __init__(self):
        self.value = None                # Rating between 0 and 5

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        if exif_tag == 'XMP-microsoft:RatingPercent':
            if value == 0:                          # 0% --> Rating 0
                self.value = 0
            elif value == 1:                        # 1% --> Rating 1
                self.value = 1
            else:
                self.value = value / 25 + 1         # 25% --> Rating 2, 50% --> Rating 3, 75% -->Rating 4, 100% --> Rating 5
        else:
            self.value = value

    def setValue(self, value):
        self.value = value

    def getExifValue(self, exif_tag):
        if self.value is None:
            return self.value
        elif exif_tag == 'XMP-microsoft:RatingPercent':
            if self.value == 0:
                return 0
            elif self.value == 1:
                return 1
            else:
                return ( self.value - 1 ) * 25
        else:
            return self.value

    def getValue(self):
        return self.value

class DateTimeValue():
    def __init__(self):
        self.value = None
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
        if date_time is None:
            return date_time_parts

        # Date/time contains only fraction of second
        elif date_time.isdigit():  # If string contains only numbers, it can only contain fraction of seconds
            date_time_parts['fraction_of_second'] = date_time
            return date_time_parts

        # Date/time contains date/time, possible with fraction of second and possible with UTC-ofset
        elif len(date_time) > 6:   # Holds date time and/or utc-offset
            # Date/time is UTC-date/time
            utc_offset_index = date_time.find('Z')
            if utc_offset_index != -1:  # Is UTC date time
                if utc_offset_index != 0:
                    date_time_parts['utc_date_time'] = date_time[0:19]   # Date/time without fraction of second
                date_time_parts['utc_offset'] = 'Z'

            # Date/time is local date/time
            else:
                date_time_parts['local_date_time'] = date_time[0:19]  # Date/time without fraction of second
                utc_offset_index = date_time.find('+')
                if utc_offset_index == -1:
                    utc_offset_index = date_time.find('-',10)
                if utc_offset_index != -1:
                    date_time_parts['utc_offset'] = date_time[utc_offset_index:]

            # Fraction of second
            dot_index = date_time.find('.')
            if dot_index != -1:
                if utc_offset_index == -1:
                    date_time_parts['fraction_of_second'] = date_time[dot_index + 1:]
                else:
                    date_time_parts['fraction_of_second'] = date_time[dot_index + 1:utc_offset_index]

        # Date/time contains only UTC-offset
        else:
            date_time_parts['utc_offset'] = date_time

        return date_time_parts

    def __mergeDataTimeParts(self, date_time_parts):
        date_time = ''
        if date_time_parts.get('utc_offset') == 'Z':
            if date_time_parts['utc_date_time'] is not None:
                date_time = date_time + date_time_parts['utc_date_time']
        else:
            if date_time_parts.get('local_date_time') is not None:
                date_time = date_time + date_time_parts['local_date_time']

        if date_time_parts.get('fraction_of_second') is not None:
            date_time = date_time + '.' + date_time_parts['fraction_of_second']
        if date_time_parts.get('utc_offset') is not None:
            date_time = date_time + date_time_parts['utc_offset']
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
        hours, minutes = map(int, utc_offset(':'))
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

    def __enrichDateTime(self,date_time):
        date_time_parts = self.__splitDateTime(date_time)
        # Transfer missing date/time parts
        if date_time_parts['local_date_time'] and not self.date_time_parts['local_date_time']:
            self.date_time_parts['local_date_time'] = date_time_parts['local_date_time']
        if date_time_parts['utc_date_time'] and not self.date_time_parts['utc_date_time']:
            self.date_time_parts['utc_date_time'] = date_time_parts['utc_date_time']
        if date_time_parts['fraction_of_second'] and not self.date_time_parts['fraction_of_second']:
            self.date_time_parts['fraction_of_second'] = date_time_parts['fraction_of_second']
        if date_time_parts['utc_offset'] and not self.date_time_parts['utc_offset']:
            self.date_time_parts['utc_offset'] = date_time_parts['utc_offset']

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


    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        str_value = str(value)   # Converts SubSec from number to string. The rest is already string
        if len(str_value) > 6:    # Means that it is a data (Not offset, not subsec)
            number_value = ''.join([char for char in str_value if char.isdigit()])   #All number-characters in string
            zero_value = ''.join([char for char in str_value if char == '0'])       #All zero number-characters in string
            if number_value == zero_value:     # If value contains 0000:00:00 00:00:00 do nothing
                return

        # Local date-time with fraction and offset
        if exif_tag in ['XMP:Date','IPTC:DateCreated','QuickTime:CreationDate','RIFF:DateTimeOriginal','File:FileCreateDate']:   # 2024:10:15 14:00:00.123+02:00
            # Convert 2024:10:15 14:00:00.123+02:00 --> 2024-10-15T14:00:00.123+02:00
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')

        # Local date-time without fraction and offset
        elif exif_tag in ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'EXIF:ModifyDate']: # 2024:10:15 14:00:00
            # Convert 2024:10:15 14:00:00 --> 2024-10-15T14:00:00
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')

        # UTC date-time with fraction, without utc-offset
        elif exif_tag in ['QuickTime:MediaCreateDate', 'QuickTime:CreateDate', 'QuickTime:ModifyDate', 'QuickTime:MediaModifyDate', 'QuickTime:TrackCreateDate', 'QuickTime:TrackModifyDate']: # 2024:10:15 14:00:00.123
            # Convert 2024:10:15 14:00:00.123 --> 2024-10-15T14:00:00.123Z
            date_time = value
            date_time = self.__replaceChar(date_time,4,'-')
            date_time = self.__replaceChar(date_time,7,'-')
            date_time = self.__replaceChar(date_time,10,'T')
            date_time += 'Z'

        # utc-offset
        elif exif_tag in ['EXIF:OffsetTimeOriginal','EXIF:OffsetTimeDigitized','EXIF:OffsetTime']: # +02:00
            date_time = value

        elif exif_tag in ['EXIF:SubSecTimeOriginal','EXIF:SubSecTimeDigitized','EXIF:SubSecTime']: # 123
            date_time = str(value)

        self.__enrichDateTime(date_time)
        test_value = self.value

    def setValue(self,value):
        self.value = None
        self.date_time_parts = self.__splitDateTime()   # All parts set to None
        self.__enrichDateTime(value)

    def getExifValue(self,exif_tag):
        # Local date-time with fraction and offset
        if exif_tag in ['XMP:Date','IPTC:DateCreated','QuickTime:CreationDate','RIFF:DateTimeOriginal','File:FileCreateDate']:   # 2024:10:15 14:00:00.123+02:00
            date_time = self.value
            # 2024-15-15T14:00:00.123+02:00--> 2024:10:15 14:00:00.123+02:00
            date_time = self.__replaceChar(date_time,4,':')
            date_time = self.__replaceChar(date_time,7,':')
            date_time = self.__replaceChar(date_time,10,' ')
            return date_time

        # Local date-time without fraction and offset
        elif exif_tag in ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'EXIF:ModifyDate']:  # 2024:10:15 14:00:00
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
                    date_time = date_time + self.date_time_parts.get('fraction_of_second')
                date_time = self.__replaceChar(date_time,4,':')
                date_time = self.__replaceChar(date_time,7,':')
                date_time = self.__replaceChar(date_time,10,' ')
            return date_time

        # utc-offset
        elif exif_tag in ['EXIF:OffsetTimeOriginal', 'EXIF:OffsetTimeDigitized', 'EXIF:OffsetTime']:  # +02:00
            utc_offset = self.date_time_parts.get('utc_offset')
            if  utc_offset in ['Z',None]:
                return ''
            else:
                return utc_offset

        elif exif_tag in ['EXIF:SubSecTimeOriginal', 'EXIF:SubSecTimeDigitized', 'EXIF:SubSecTime']:  # 123
            fraction = self.date_time_parts.get('fraction_of_second')
            if fraction is None:
                return ''
            return fraction.replace(".", "")

    def getValue(self):
        return self.value

class GeoLocationValue():
    def __init__(self):
        self.value = None                # 37.7749,-122.4194

    def setValueFromExif(self, value,exif_tag):
        if value is None:
            return
        self.value = value.replace(' ', ',', 1)     # 37.7749 -122.4194 --> 37.7749,-122.4194 Bug in Exif causes space as delimiter, but exif requires comme as delimiter at updates

    def setValue(self, value):
      self.value = value

    def getExifValue(self,exif_tag):
        return self.value

    def getValue(self):
        return self.value









