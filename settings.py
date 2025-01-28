import json
import os
import sys
import copy


def readSettingsFile():
    global settings_path, settings
    if os.path.isfile(settings_path):
        with open(settings_path, 'r') as settings_file:
            settings = json.load(settings_file)
    else:
        settings = {}

def patchDefaultValues():
    global settings

    if settings.get("resource_path") is None:
        if hasattr(sys, '_MEIPASS'):
            settings['resource_path'] = sys._MEIPASS
        else:
            settings['resource_path'] = ''

    if settings.get("file_types") is None:
        settings["file_types"] = ["jpg", "jpeg", "png", "bmp", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "tiff", "gif","mp4", "m4v", "mov", "avi", "m2t", "m2ts","mts"]
    if settings.get("sidecar_tag_groups") is None:
        settings["sidecar_tag_groups"] = {"JSON": {"file_name_pattern": "<file_name>.<ext>.json"} }
    if settings.get("languages") is None:
        settings["languages"] = {"DA": "Danish",
                                 "EN": "English"}
    if settings.get("logical_tags") is None:
        settings["logical_tags"] = {
            "make": {"value_class": "StringValue"},
            "model": {"value_class": "StringValue"},
            "lens_model": {"value_class": "StringValue"},
            "focal_length": {"value_class": "StringValue"},
            "aperture": {"value_class": "StringValue"},
            "shutter_speed": {"value_class": "StringValue"},
            "iso": {"value_class": "StringValue"},
            "rotation": {"widget": "Rotation",
                         "value_class": "RotationValue"},
            "rating": {"widget": "Rating",
                       "value_class": "RatingValue",
                       "label_text_key": "tag_label_rating"},
            "title": {"widget": "TextLine",
                      "value_class": "StringValue",
                      "label_text_key": "tag_label_title"},
            "date": {"widget": "DateTime",
                     "value_class": "DateTimeValue",
                     "value_parts": {"utc_offset":    {"label_text_key": "tag_label_date.utc_offset", # Value-parts addressable by setValue and getValue
                                                       "default_paste_select": False},                # ..and added in context-menu in addition
                                     "latest_change": {"label_text_key": "tag_label_date.latest_change",
                                                       "default_paste_select": False},
                                     "old_value":     {"disable_in_context_menu":True}
                                     },
                     "label_text_key": "tag_label_date",
                     "default_paste_select": False},
            "description_only": {"widget": "Text",
                                 "value_class": "StringValue",
                                 "label_text_key": "tag_label_description_only",
                                 "fallback_tag": "description"},
            # If description_only is blank in metadata, it is populated from description
            "persons": {"widget": "TextSet",
                        "value_class": "ListValue",
                        "label_text_key": "tag_label_persons",
                        "Autocomplete": True},
            "photographer": {"widget": "TextLine",
                             "value_class": "StringValue",
                             "label_text_key": "tag_label_photographer",
                             "Autocomplete": True},
            "source": {"widget": "TextLine",
                       "value_class": "StringValue",
                       "label_text_key": "tag_label_source",
                       "Autocomplete": True},
            "original_filename": {"widget": "TextLine",
                                  "value_class": "StringValue",
                                  "label_text_key": "tag_label_original_filename"},
            "geo_location": {"widget": "GeoLocation",
                             "value_class": "GeoLocationValue",
                             "label_text_key": "tag_label_geo_location",
                             "default_paste_select": False},
            "description": {"widget": "Text",
                            "value_class": "StringValue",
                            "label_text_key": "tag_label_description",
                            "reference_tag": True,
                            "reference_tag_content": [{"type": "tag", "tag_name": "title", "new_line": True},
                                                      {"type": "tag", "tag_name": "description_only","new_line": True},
                                                      {"type": "text_line", "text": "", "new_line": True},
                                                      {"type": "tag", "tag_name": "persons", "tag_label": True, "new_line": True},
                                                      {"type": "tag", "tag_name": "source", "tag_label": True, "new_line": True},
                                                      {"type": "tag", "tag_name": "photographer", "tag_label": True, "new_line": True},
                                                      {"type": "tag", "tag_name": "original_filename","tag_label": True, "new_line": True}
                                                      ]},
            "camera_settings": {"widget": "TextLine",
                                "value_class": "StringValue",
                                "reference_tag": True,
                                "reference_tag_separator": ", ",
                                "reference_tag_content": [{"type": "tag", "tag_name": "make"},
                                                          {"type": "tag", "tag_name": "model"},
                                                          {"type": "tag", "tag_name": "lens_model"},
                                                          {"type": "tag", "tag_name": "focal_length"},
                                                          {"type": "tag", "tag_name": "aperture", "prefix": "f/"},
                                                          {"type": "tag", "tag_name": "shutter_speed", "postfix": "s"},
                                                          {"type": "tag", "tag_name": "iso","prefix": "ISO "}
                                                      ]}
        }
    if settings.get("tags") is None:
        settings["tags"] = {"XMP:Title": {"access": "Read/Write"},
                            "EXIF:XPTitle": {"access": "Read/Write"},
                            "IPTC:ObjectName": {"access": "Read/Write"},
                            "XMP:Date": {"access": "Read/Write"},
                            "XMP:DateCreated": {"access": "Read/Write"},
                            "EXIF:DateTimeOriginal": {"access": "Read/Write}"},
                            "EXIF:OffsetTimeOriginal": {"access": "Read/Write}"},
                            "EXIF:SubSecTimeOriginal":{"access": "Read/Write}"},
                            "EXIF:CreateDate": {"access": "Read/Write}"},
                            "EXIF:OffsetTimeDigitized": {"access": "Read/Write}"},
                            "EXIF:SubSecTimeDigitized": {"access": "Read/Write}"},
                            "EXIF:ModifyDate": {"access": "Read/Write}"},
                            "EXIF:OffsetTime": {"access": "Read/Write}"},
                            "EXIF:SubSecTime": {"access": "Read/Write}"},
                            "IPTC:DateCreated": {"access": "Read/Write}"},
                            "XMP:Description": {"type": "text", "access": "Read/Write}"},
                            "EXIF:XPComment": {"type": "text", "access": "Read/Write"},
                            "EXIF:UserComment": {"type": "text", "access": "Read/Write"},
                            "EXIF:ImageDescription": {"type": "text", "access": "Read/Write"},
                            "IPTC:Caption-Abstract": {"type": "text", "access": "Read/Write"},
                            "XMP:DescriptionOnly": {"type": "text", "access": "Read/Write}"},
                            "XMP-iptcExt:PersonInImage": {"type": "text_set", "access": "Read"},
                            "XMP-MP:RegionPersonDisplayName": {"type": "text_set", "access": "Read"},
                            "XMP:Subject": {"type": "text_set", "access": "Read/Write"},
                            "EXIF:XPKeywords": {"type": "text_set", "access": "Read/Write"},
                            "IPTC:Keywords": {"type": "text_set", "access": "Read/Write"},
                            "XMP:Creator": {"access": "Read/Write"},
                            "EXIF:Artist": {"access": "Read/Write"},
                            "EXIF:XPAuthor": {"access": "Read/Write"},
                            "IPTC:By-line": {"access": "Read/Write"},
                            "XMP:Source": {"access": "Read/Write"},
                            "XMP:PreservedFileName": {"access": "Read/Write"},
                            "QuickTime:Title": {"access": "Read/Write"},
                            "QuickTime:MediaCreateDate": {"access": "Read/Write"},
                            "QuickTime:CreateDate": {"access": "Read/Write"},
                            "QuickTime:TrackCreateDate": {"access": "Read/Write"},
                            "QuickTime:Comment": {"type": "text", "access": "Read/Write"},
                            "QuickTime:Category": {"type": "text_set", "access": "Read/Write"},
                            "QuickTime:Artist": {"access": "Read/Write"},
                            "QuickTime:CreationDate": {"access":"Read/Write"},
                            "RIFF:DateTimeOriginal": {"access": "Read"},
                            "Composite:GPSPosition#": {"access": "Read/Write"},
                            "EXIF:Orientation#": {"access": "Read/Write"},
                            "QuickTime:Rotation#": {"access": "Read/Write"},
                            "Composite:Rotation": {"access": "Read/Write"},
                            "XMP:Rating": {"access": "Read/Write"},
                            "XMP-microsoft:RatingPercent": {"access": "Read/Write"},
                            "EXIF:Make": {"access": "Read"},
                            "QuickTime:Make": {"access": "Read"},
                            "EXIF:Model": {"access": "Read"},
                            "QuickTime:Model": {"access": "Read"},
                            "EXIF:LensModel": {"access": "Read"},
                            "MakerNotes:LensModel": {"access": "Read"},
                            "EXIF:FocalLength": {"access": "Read"},
                            "MakerNotes:FocalLength": {"access": "Read"},
                            "Composite:Aperture": {"access": "Read"},
                            "Composite:ShutterSpeed": {"access": "Read"},
                            "EXIF:ISO": {"access": "Read"},
                            "Composite:ISO": {"access": "Read"},
                            "JSON:GeoDataExifLatitude": {"access": "Read", "sidecar_tag_group": "JSON"},
                            "JSON:GeoDataExifLongitude": {"access": "Read", "sidecar_tag_group": "JSON"},
                            "JSON:GeoDataLatitude": {"access": "Read", "sidecar_tag_group": "JSON"},
                            "JSON:GeoDataLongitude": {"access": "Read", "sidecar_tag_group": "JSON"},
                            "JSON:PhotoTakenTimeTimestamp": {"access": "Read", "sidecar_tag_group": "JSON"},
                            "JSON:description": {"access": "Read", "sidecar_tag_group": "JSON"},
                            }
    if settings.get("file_type_tags") is None:
        settings["file_type_tags"] = {
            "jpg": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },

            "jpeg": {"rotation": ["EXIF:Orientation#"],
                     "camera_settings": [],
                     "make": ["EXIF:Make"],
                     "model": ["EXIF:Model"],
                     "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                     "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                     "aperture": ["Composite:Aperture"],
                     "shutter_speed": ["Composite:ShutterSpeed"],
                     "iso": ["Composite:ISO", "EXIF:ISO"],
                     "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                     "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                     "date": ["EXIF:DateTimeOriginal", "EXIF:OffsetTimeOriginal", "EXIF:SubSecTimeOriginal",
                              "XMP:Date","XMP:DateCreated",
                              "EXIF:CreateDate", "EXIF:OffsetTimeDigitized", "EXIF:SubSecTimeDigitized",
                              "EXIF:ModifyDate", "EXIF:OffsetTime", "EXIF:SubSecTime",
                              "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                     "description_only": ["XMP:DescriptionOnly"],
                     "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                 "EXIF:XPKeywords", "IPTC:Keywords"],
                     "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                     "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                     "source": ["XMP:Source"],
                     "original_filename": ["XMP:PreservedFileName"],
                     "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                     "IPTC:Caption-Abstract", "JSON:description"]
                     },
            "png": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },
            "bmp": {},
            "cr3": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                    "EXIF:ImageDescription", "JSON:description"]
                    },

            "cr2": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                    "EXIF:ImageDescription", "JSON:description"]
                    },
            "nef": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                    "EXIF:ImageDescription", "JSON:description"]
                    },
            "dng": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },
            "arw": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },
            "heic": {"rotation": ["QuickTime:Rotation#"],
                     "camera_settings": [],
                     "make": ["EXIF:Make"],
                     "model": ["EXIF:Model"],
                     "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                     "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                     "aperture": ["Composite:Aperture"],
                     "shutter_speed": ["Composite:ShutterSpeed"],
                     "iso": ["Composite:ISO", "EXIF:ISO"],
                     "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                     "title": ["XMP:Title", "EXIF:XPTitle"],
                     "date": ["EXIF:DateTimeOriginal", "EXIF:OffsetTimeOriginal", "EXIF:SubSecTimeOriginal",
                              "XMP:Date","XMP:DateCreated",
                              "EXIF:CreateDate", "EXIF:OffsetTimeDigitized", "EXIF:SubSecTimeDigitized",
                              "EXIF:ModifyDate", "EXIF:OffsetTime", "EXIF:SubSecTime",
                              "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                     "description_only": ["XMP:DescriptionOnly"],
                     "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                 "EXIF:XPKeywords"],
                     "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                     "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                     "source": ["XMP:Source"],
                     "original_filename": ["XMP:PreservedFileName"],
                     "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                     "EXIF:ImageDescription", "JSON:description"]
                     },
            "tif": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },
            "tiff": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract", "JSON:description"]
                    },

            "gif": {"rotation": ["EXIF:Orientation#"],
                    "camera_settings": [],
                    "make": ["EXIF:Make"],
                    "model": ["EXIF:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["EXIF:DateTimeOriginal","EXIF:OffsetTimeOriginal","EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate","EXIF:OffsetTimeDigitized","EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate","EXIF:OffsetTime","EXIF:SubSecTime",
                             "IPTC:DateCreated","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                    "EXIF:ImageDescription", "JSON:description"]
                    },
            "mp4": {"rotation": ["Composite:Rotation"],
                    "camera_settings": [],
                    "make": ["EXIF:Make", "QuickTime:Make"],
                    "model": ["EXIF:Model", "QuickTime:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["QuickTime:CreationDate",
                             "EXIF:DateTimeOriginal", "EXIF:OffsetTimeOriginal", "EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate", "EXIF:OffsetTimeDigitized", "EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate", "EXIF:OffsetTime", "EXIF:SubSecTime",
                             "QuickTime:CreateDate", "QuickTime:TrackCreateDate","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment", "JSON:description"]
                    },
            "m4v": {"rotation": ["Composite:Rotation"],
                    "camera_settings": [],
                    "make": ["EXIF:Make", "QuickTime:Make"],
                    "model": ["EXIF:Model", "QuickTime:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["QuickTime:CreationDate",
                             "EXIF:DateTimeOriginal", "EXIF:OffsetTimeOriginal", "EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate", "EXIF:OffsetTimeDigitized", "EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate", "EXIF:OffsetTime", "EXIF:SubSecTime",
                             "QuickTime:CreateDate", "QuickTime:TrackCreateDate","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment", "JSON:description"]
                    },
            "mov": {"rotation": ["Composite:Rotation"],
                    "camera_settings": [],
                    "make": ["EXIF:Make", "QuickTime:Make"],
                    "model": ["EXIF:Model", "QuickTime:Model"],
                    "lens_model": ["EXIF:LensModel", "MakerNotes:LensModel"],
                    "focal_length": ["EXIF:FocalLength", "MakerNotes:FocalLength"],
                    "aperture": ["Composite:Aperture"],
                    "shutter_speed": ["Composite:ShutterSpeed"],
                    "iso": ["Composite:ISO", "EXIF:ISO"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["QuickTime:CreationDate",
                             "EXIF:DateTimeOriginal", "EXIF:OffsetTimeOriginal", "EXIF:SubSecTimeOriginal",
                             "XMP:Date","XMP:DateCreated",
                             "EXIF:CreateDate", "EXIF:OffsetTimeDigitized", "EXIF:SubSecTimeDigitized",
                             "EXIF:ModifyDate", "EXIF:OffsetTime", "EXIF:SubSecTime",
                             "QuickTime:CreateDate", "QuickTime:TrackCreateDate","JSON:PhotoTakenTimeTimestamp"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#",
                                     "JSON:GeoDataExifLatitude", "JSON:GeoDataExifLongitude",
                                     "JSON:GeoDataLatitude", "JSON:GeoDataLongitude"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment", "JSON:description"]
                    },
            "avi": {"date": ["JSON:PhotoTakenTimeTimestamp","RIFF:DateTimeOriginal"]
                    },
            "m2t": {},
            "m2ts": {},
            "mts": {},
        }
    if settings.get("text_keys") is None:
        settings["text_keys"] = {"tag_label_rating":
                                     {"DA": "Bedømmelse",
                                      "EN": "Rating"},
                                 "tag_label_title":
                                     {"DA": "Titel",
                                      "EN": "Title"},
                                 "tag_label_date":
                                     {"DA": "Dato/tid",
                                      "EN": "Date/time"},
                                 "tag_label_date.local_date_time":
                                     {"DA": "Lokal dato/tid",
                                      "EN": "Local date/time"},
                                 "tag_label_date.utc_offset":
                                     {"DA": "Dato/tid utc-offset",
                                      "EN": "Date/time utc-offset"},
                                 "tag_label_date.latest_change":
                                     {"DA": "Seneste dato/tid ændring",
                                      "EN": "Latest date/time change"},
                                 "tag_label_description_only":
                                     {"DA": "Beskrivelse",
                                      "EN": "Description"},
                                 "tag_label_persons":
                                     {"DA": "Personer",
                                      "EN": "People"},
                                 "tag_label_photographer":
                                     {"DA": "Fotograf",
                                      "EN": "Photographer"},
                                 "tag_label_source":
                                     {"DA": "Oprindelse",
                                      "EN": "Source"},
                                 "tag_label_original_filename":
                                     {"DA": "Oprindeligt filnavn",
                                      "EN": "Original Filename"},
                                 "tag_label_geo_location":
                                     {"DA": "Geo-lokation",
                                      "EN": "Geo-location"},
                                 "tag_label_description":
                                     {"DA": "Fuld beskrivelse",
                                      "EN": "Full Description"},
                                 "file_menu_consolidate":
                                     {"DA": "Konsolider metadata",
                                      "EN": "Consolidate Metadata"},
                                 "file_menu_copy":
                                     {"DA": "Kopier metadata",
                                      "EN": "Copy Metadata"},
                                 "file_menu_paste":
                                     {"DA": "Indsæt metadata",
                                      "EN": "Paste Metadata"},
                                 "file_menu_patch":
                                     {"DA": "Udfyld metadata",
                                      "EN": "Patch Metadata"},
                                 "file_menu_paste_by_filename":
                                     {"DA": "Indsæt metadata efter filnavn",
                                      "EN": "Paste Metadata by Filename"},
                                 "file_menu_patch_by_filename":
                                     {"DA": "Udfyld metadata efter filnavn",
                                      "EN": "Patch Metadata by Filename"},
                                 "file_menu_chose_tags_to_paste":
                                     {"DA": "Vælg hvad du vil overføre:",
                                      "EN": "Choose what to transfer:"},
                                 "folder_menu_standardize":
                                     {"DA": "Standardiser filnavne",
                                      "EN": "Standardize Filenames"},
                                 "folder_menu_consolidate":
                                     {"DA": "Konsolider metadata",
                                      "EN": "Consolidate Metadata"},
                                 "settings_window_title":
                                     {"DA": "Indstillinger",
                                      "EN": "Settings"},
                                 "settings_labels_application_language":
                                     {"DA": "Sprog",
                                      "EN": "Language"},
                                 "preview_menu_open_in_default_program":
                                     {"DA": "Åben",
                                      "EN": "Open"},
                                 "preview_menu_open_in_browser":
                                     {"DA": "Åben i webbrowser",
                                      "EN": "Open in Web Browser"},
                                 }
    if settings.get("file_context_menu_actions") is None:
        settings["file_context_menu_actions"] = {"consolidate_metadata":
                                                     {"text_key": "file_menu_consolidate"},
                                                 "copy_metadata":
                                                     {"text_key": "file_menu_copy"},
                                                 "paste_metadata":
                                                     {"text_key": "file_menu_paste"},
                                                 "patch_metadata":
                                                     {"text_key": "file_menu_patch"},
                                                 "paste_by_filename":
                                                     {"text_key": "file_menu_paste_by_filename"},
                                                 "patch_by_filename":
                                                     {"text_key": "file_menu_patch_by_filename"},
                                                 "choose_tags_to_paste":
                                                     {"text_key": "file_menu_chose_tags_to_paste"}
                                                 }
    if settings.get("folder_context_menu_actions") is None:
        settings["folder_context_menu_actions"] = {"standardize_filenames":
                                                       {"text_key": "folder_menu_standardize"},
                                                   "consolidate_metadata":
                                                       {"text_key": "floder_menu_consolidate"}
                                                   }
    if settings.get("settings_labels") is None:
        settings["settings_labels"] = {"application_language":
                                           {"text_key": "settings_labels_application_language"}
                                       }
    # A file padded with one of the paddings are still considered coming from same source-file during standardization of filenames.
    # Example: IMG_0920.jpg and IMG_0920-Enhanced-NR.jpg will end up being e.t 2024-F005-007.jpg and 2024-F005-007-Enhanced-NR.jpg.
    #          The original filename tag will, however, hold 2024-F005-007 in both cases.
    if settings.get("file_name_padding") is None:
        settings["file_name_padding"] = {"file_name_postfix": ["-Enhanced-NR",             # Added by lightroom AI-enhancement
                                                               "-gigapixel-*x",            # Added by Topaz gigapixel
                                                               "-SAI",                     # Added by Topaz sharpen AI
                                                               "-DeNoiseAI",               # Added by Topaz Denoise AI
                                                               "-redigeret",               # Added by Google Takeout for photos edited in Google Photos, if your account is set to danish language
                                                               "-edited",                  # Added by Google Takeout for photos edited in Google Photos, if your account is set to english language
                                                               " - Copy",                  # Added by Windows when copying to place where target exist
                                                               " - Copy (.)",              #                    "
                                                               " - Copy (..)"              #                    "
                                                               ],
                                          "file_name_prefix": ["copy_of_"]}

def writeSettingsFile():
    global settings, settings_path
    file_settings = {}
    file_settings['version']=settings.get('version')
    file_settings['language']=settings.get('language')
    settings_json_object = json.dumps(file_settings, indent=4)
    with open(settings_path, "w") as outfile:
        outfile.write(settings_json_object)

version = "2.1.0"   # Rotation of videos

# Make location for Application, if missing
app_data_location = os.path.join(os.environ.get("ProgramData"),"Memory Mate")
if not os.path.isdir(app_data_location):
    os.mkdir(app_data_location)

# Define global variable for settings
settings = {}
old_settings = {}

# Set path to settings
settings_path = os.path.join(app_data_location,"settings.json")

# Set path to queue-file
queue_file_path = os.path.join(app_data_location,"queue.json")

# Read settings-file, patch it and upgrade
readSettingsFile()                       # Holds version and Language only, so settings now holds these two

# Read settings-file with language and version-number
old_settings['version']=settings.get('version')
old_settings['language']=settings.get('language')
settings = copy.deepcopy(old_settings)   # Now settings only holds old version and language
settings['version']=version   # Settings now holds new version (from line 526)
if settings.get('language') is None:
    settings['language']='EN'

# Write settings to file if new or upgraded
if old_settings != settings:          # Write to file and update settings variables in case of change
    writeSettingsFile()

patchDefaultValues()                  # Settings now holds all (Tags, translations etc. are added)

# Set all variables from data in settings-file and defaultdata
version = settings.get("version")            # Actually this is the version already assigned in top of settings
file_types = settings.get("file_types")
sidecar_tag_groups=settings.get("sidecar_tag_groups")
languages = settings.get("languages")
language = settings.get("language")
logical_tags = settings.get("logical_tags")
tags = settings.get("tags")
file_type_tags = settings.get("file_type_tags")
text_keys = settings.get("text_keys")
file_context_menu_actions = settings.get("file_context_menu_actions")
folder_context_menu_actions = settings.get("folder_context_menu_actions")
settings_labels = settings.get("settings_labels")
file_name_padding = settings.get("file_name_padding")
resource_path = settings.get('resource_path')
print('path: '+ resource_path )







