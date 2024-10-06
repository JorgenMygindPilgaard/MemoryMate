from datetime import datetime, timedelta

class StringValue():
    def __init__(self):
        self.value = None                # String

    def set_value_from_exif(self, value,exif_tag,):
        self.value = value

    def set_value_from_internal(self, value, value_name='value'):
        self.value = value

    def get_exif_value(self,exif_tag):
        return self.value

    def get_internal_value(self,value_name='value'):
        return self.value


class ListValue():
    def __init__(self):
        self.value = None                # List of strings

    def set_value_from_exif(self, value,exif_tag,):
        if isinstance(value, list):
            self.value = value
        else:
            self.value = [value]

    def set_value_from_internal(self, value, value_name='value'):
        if isinstance(value, list):
            self.value = value
        else:
            self.value = [value]

    def get_exif_value(self,exif_tag):
        return self.value

    def get_internal_value(self, value_name='value'):
        return self.value

class RotationValue():
    def __init__(self):
        self.value = None                # Rotation 0, 90, 180, 270
        self.orientation = None          # 0°:1, 90°:8, 180°:3, 270°:6

    def set_value_from_exif(self, value,exif_tag,):
        if exif_tag == 'EXIF:Orientation':     #Orientation id-number being set
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

    def set_value_from_internal(self, value, value_name='value'):
        self.value = value

    def get_exif_value(self,exif_tag):
        if exif_tag == 'EXIF:Orientation':     #Orientation id-number being read
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

    def get_internal_value(self, value_name='value'):
        return self.value


class RatingValue():
    def __init__(self):
        self.value = None                # Rating between 0 and 5

    def set_value_from_exif(self, value,exif_tag,):
        if exif_tag == 'XMP-microsoft:RatingPercent':
            if value == 0:                          # 0% --> Rating 0
                self.value = 0
            elif value == 1:                        # 1% --> Rating 1
                self.value = 1
            else:
                self.value = value / 25 + 1         # 25% --> Rating 2, 50% --> Rating 3, 75% -->Rating 4, 100% --> Rating 5
        else:
            self.value

    def set_value_from_internal(self, value, value_name='value'):
        self.value = value

    def get_exif_value(self, exif_tag):
        if exif_tag == 'XMP-microsoft:RatingPercent':
            if self.value == 0:
                return 0
            elif self.value == 1:
                return 1
            else:
                return ( self.value - 1 ) * 25
        else:
            return self.value

    def get_internal_value(self, value_name='value'):
        return self.value

class DateTimeValue():
    def __init__(self):
        self.value = None                # "2024-08-30T10:02:58.471+02:00"
                                         # "2024-08-30T10:02:58.471" if timezone unknown
                                         # "2024-08-30 if time is unknown
                                         # "10:02:58.471+02:00 if date is unknown
                                         # "10:02:58.4711" if date and timezone is unknown  (ISO 8601 timestamp)

        self.__local_date = None           # "2024-08-30"
        self.__local_time = None           # "10:02:58.471"
        self.__utc_offset = None           # "+02:00"
        self.__utc_date = None             # "2024-08-30"
        self.__utc_time = None             # "08:02:58.471"

    @staticmethod
    def __dateTimeGetUtcDateTime(date_time_str):    # 2024:12:15 15:22:16+02:00 --> 2024:12:15 13:22:16
        # Define the date/time format
        date_time_format = "%Y:%m:%d %H:%M:%S"

        # Isolate date_time
        local_date_time_str = date_time_str[:19]
        local_date_time = datetime.strptime(local_date_time_str, date_time_format)

        # Isolate utc_offset
        utc_offset_str = date_time_str[19:]
        utc_offset_hours, utc_offset_minutes = map(int, utc_offset_str[1:].split(':'))
        utc_offset_sign = utc_offset_str[0]
        utc_offset = timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
        if utc_offset_sign == '-':
            utc_offset = -utc_offset

        # Calculate utc_date_time
        utc_date_time = local_date_time - utc_offset

        # Convert utc_date_time to string
        utc_date_time_str = utc_date_time.strftime(date_time_format)

        return utc_date_time_str

    def set_value_from_exif(self, value,exif_tag,):
        if exif_tag == 'XMP:Date':
            if self.__local_date is None and value[:10]:      # Only read from first tag
                self.__local_date = value[:10].replace(":","-")                # 2024-08-30
            if self.__local_time is None and value[11:19]:
                self.__local_time = value[11:19] + '.000'
                if self.



    def set_value(self,value, value_name='value'):
        if value_name == 'value':
            self.value = value                                          # 2024:12:15 15:22:16+02:00
            self.local_date_time = value[:19]                           # 2024:12:15 15:22:16
            self.utc_offset = value[19:]                                # +02:00
            self.utc_date_time = self.__dateTimeGetUtcDateTime(value)   # 2024:12:15 13:22:16
        elif value_name == 'local_date_time':
            self.local_date_time = value
            if self.utc_offset is not None:
                self.value = value + self.utc_offset
                self.utc_date_time = self.__dateTimeGetUtcDateTime(self.value)  # Trust existing utc_offset and recalc utc_data_time
        elif value_name == 'utc_offset':
            self.utc_offset = value
            if self.local_date_time is not None:
                self.value = self.local_date_time + value
                self.utc_date_time = self.__dateTimeGetUtcDateTime(self.value)  # Trust existing local_date_time and recalc utc_data_time
            elif self.utc_date_time is not None:



            self.local_date_time = value
            self.utc_date_time = self.__dateTimeGetUtcDateTime(self.value)
        elif value_name == 'utc_offset':
            self.value = self.local_date_time + value
            self.utc_offset = value
            self.utc_date_time = self.__dateTimeGetUtcDateTime(self.value)
        elif value_name == 'local_date_time':
            return self.local_date_time
        elif value_name == 'utc_offset':
            return self.utc_date_time
        elif value_name == 'utc_date_time':
            return self.utc_date_time

    def get_value(self,value_name='value'):
        if value_name == 'value':
            return self.value
        elif value_name == 'local_date_time':
            return self.local_date_time
        elif value_name == 'utc_offset':
            return self.utc_date_time
        elif value_name == 'utc_date_time':
            return self.utc_date_time

class GeoLocationValue():
# This class compensates for a bug in ExifTool. It delivers Composite:GPSPosition# as "37.7749 -122.4194" (Space delimiter)
# But requires "37.7749,-122.4194" (Comma delimiter) at updates. The set-method adds comma-delimiter.
    def __init__(self):
        self.value = None                # 37.7749,-122.4194

    def set_value(self,value, value_name='value'):
      self.value = value.replace(' ', ',', 1)

    def get_value(self,value_name='value'):
        return self.value








