import json
import os
import copy
from util import insertDictionary


def readSettingsFile():
    global settings_path, settings
    if os.path.isfile(settings_path):
        with open(settings_path, 'r') as settings_file:
            settings = json.load(settings_file)
    else:
        settings = {}

def patchDefaultValues():
    global settings
    # Set default-values for missing settings
    if settings.get("version") is None:
        settings["version"] = "0.0.0"  # Initial installation
    if settings.get("file_types") is None:
        settings["file_types"] = ["jpg", "jpeg", "png", "bmp", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "tiff", "gif",
                                  "mp4", "m4v", "mov", "avi", "m2t", "m2ts","mts"]
    if settings.get("languages") is None:
        settings["languages"] = {"DA": "Danish",
                                 "EN": "English"}
    if settings.get("language") is None:
        settings["language"] = "EN"
    if settings.get("logical_tags") is None:
        settings["logical_tags"] = {
            "orientation": {"widget": "orientation",
                            "data_type": "number"},
            "rotation": {"widget": "rotation",
                         "data_type": "number"},
            "rating": {"widget": "rating",
                       "data_type": "number",
                       "label_text_key": "tag_label_rating"},
            "title": {"widget": "text_line",
                      "data_type": "string",
                      "label_text_key": "tag_label_title"},
            "date": {"widget": "date_time",
                     "data_type": "string",
                     "label_text_key": "tag_label_date",
                     "default_paste_select": False},
            "description_only": {"widget": "text",
                                 "data_type": "string",
                                 "label_text_key": "tag_label_description_only",
                                 "fallback_tag": "description"},
            # If description_only is blank in metadata, it is populated from description
            "persons": {"widget": "text_set",
                        "data_type": "list",
                        "label_text_key": "tag_label_persons",
                        "Autocomplete": True},
            "photographer": {"widget": "text_line",
                             "data_type": "string",
                             "label_text_key": "tag_label_photographer",
                             "Autocomplete": True},
            "source": {"widget": "text_line",
                       "data_type": "string",
                       "label_text_key": "tag_label_source",
                       "Autocomplete": True},
            "original_filename": {"widget": "text_line",
                                  "data_type": "string",
                                  "label_text_key": "tag_label_original_filename"},
            "geo_location": {"widget": "geo_location",
                             "data_type": "string",
                             "label_text_key": "tag_label_geo_location",
                             "default_paste_select": False},
            "description": {"widget": "text",
                            "data_type": "string",
                            "label_text_key": "tag_label_description",
                            "reference_tag": True,
                            "reference_tag_content": [{"type": "tag", "tag_name": "title", "tag_label": False},
                                                      {"type": "tag", "tag_name": "description_only",
                                                       "tag_label": False},
                                                      {"type": "text_line", "text": ""},
                                                      {"type": "tag", "tag_name": "persons", "tag_label": True},
                                                      {"type": "tag", "tag_name": "source", "tag_label": True},
                                                      {"type": "tag", "tag_name": "photographer", "tag_label": True},
                                                      {"type": "tag", "tag_name": "original_filename",
                                                       "tag_label": True}
                                                      ]}
        }
    if settings.get("tags") is None:
        settings["tags"] = {"XMP:Title": {"access": "Read/Write"},
                            "EXIF:XPTitle": {"access": "Read/Write"},
                            "IPTC:ObjectName": {"access": "Read/Write"},
                            "XMP:Date": {"access": "Read/Write"},
                            "EXIF:DateTimeOriginal": {"access": "Read/Write}"},
                            "EXIF:CreateDate": {"access": "Read/Write}"},
                            "EXIF:ModifyDate": {"access": "Read/Write}"},
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
                            "QuickTime:ModifyDate": {"access": "Read/Write"},
                            "QuickTime:MediaModifyDate": {"access": "Read/Write"},
                            "QuickTime:TrackCreateDate": {"access": "Read/Write"},
                            "QuickTime:TrackModifyDate": {"access": "Read/Write"},
                            "QuickTime:Comment": {"type": "text", "access": "Read/Write"},
                            "QuickTime:Category": {"type": "text_set", "access": "Read/Write"},
                            "QuickTime:Artist": {"access": "Read/Write"},
                            "RIFF:DateTimeOriginal": {"access": "Read"},
                            "File:FileCreateDate": {"access": "Read"},
                            "Composite:GPSPosition#": {"access": "Read/Write"},
                            "EXIF:Orientation#:": {"access": "Read/Write"},
                            "QuickTime:Rotation#": {"access": "Read/Write"},
                            "XMP:Rating": {"access": "Read/Write"},
                            "XMP-microsoft:RatingPercent": {"access": "Read/Write"}
                            }
    if settings.get("file_type_tags") is None:
        settings["file_type_tags"] = {
            "jpg": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },
            "jpeg": {"rotation": ["EXIF:Orientation#"],
                     "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                     "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                     "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                              "IPTC:DateCreated", "File:FileCreateDate"],
                     "description_only": ["XMP:DescriptionOnly"],
                     "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                 "EXIF:XPKeywords", "IPTC:Keywords"],
                     "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                     "geo_location": ["Composite:GPSPosition#"],
                     "source": ["XMP:Source"],
                     "original_filename": ["XMP:PreservedFileName"],
                     "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                     "IPTC:Caption-Abstract"]
                     },
            "png": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },
            "bmp": {},
            "cr3": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                    },

            "cr2": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                    },
            "nef": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                    },
            "dng": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },
            "arw": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },
            "heic": {"rotation": ["QuickTime:Rotation#"],
                     "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                     "title": ["XMP:Title", "EXIF:XPTitle"],
                     "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                              "File:FileCreateDate"],
                     "description_only": ["XMP:DescriptionOnly"],
                     "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                 "EXIF:XPKeywords"],
                     "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                     "geo_location": ["Composite:GPSPosition#"],
                     "source": ["XMP:Source"],
                     "original_filename": ["XMP:PreservedFileName"],
                     "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                     },
            "tif": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },
            "tiff": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                    },

            "gif": {"rotation": ["EXIF:Orientation#"],
                    "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "EXIF:XPTitle"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                    "description_only": ["XMP:DescriptionOnly", "File:FileCreateDate"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                    },
            "mp4": {"rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["XMP:Date", "QuickTime:MediaCreateDate", "QuickTime:CreateDate", "QuickTime:ModifyDate",
                             "QuickTime:MediaModifyDate", "QuickTime:TrackCreateDate",
                             "QuickTime:TrackModifyDate", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment"]
                    },
            "m4v": {"rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["XMP:Date", "QuickTime:MediaCreateDate", "QuickTime:CreateDate", "QuickTime:ModifyDate",
                             "QuickTime:MediaModifyDate", "QuickTime:TrackCreateDate",
                             "QuickTime:TrackModifyDate", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment"]
                    },
            "mov": {"rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["XMP:Date", "QuickTime:MediaCreateDate", "QuickTime:CreateDate", "QuickTime:ModifyDate",
                             "QuickTime:MediaModifyDate", "QuickTime:TrackCreateDate",
                             "QuickTime:TrackModifyDate", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment"]
                    },
            "avi": {"date": ["RIFF:DateTimeOriginal", "File:FileCreateDate"]
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
                                     {"DA": "Dato",
                                      "EN": "Date"},
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
        settings["file_name_padding"] = {"file_name_postfix": ["-Enhanced-NR",              # Added by lightroom AI-enhancement
                                                               "-gigapixel-*x",             # Added by Topaz gigapixel
                                                               "-SAI",                      # Added by Topaz sharpen AI
                                                                "-DeNoiseAI",               # Added by Topaz Denoise AI
                                                                " - Copy",                  # Added by Windows when copying to place where target exist
                                                                " - Copy (.)",              #                    "
                                                                " - Copy (..)"              #                    "
                                                               ],
                                          "file_name_prefix": ["copy_of_"]}

def migrateVersion():
    global version, settings
    def versionNumber(ver):
        ver_num = 0
        parts = ver.split(".")
        if len(parts) == 3:
            try:
                part1, part2, part3 = map(int, parts)
                ver_num = part1 * 10000 + part2 * 100 + part3
            except ValueError:
                pass
        return ver_num

    def rule01():  # Add logical tag and physical tags for rating
        global settings
        if old_ver_num <= 10199 and new_ver_num >= 10200:  # rating-tag added in version 1.2
            if settings["logical_tags"].get("rating") is None:  # Add rating in logical tags
                insertDictionary(settings["logical_tags"], "rating",
                                 {"widget": "rating", "data_type": "number", "label_text_key": "tag_label_rating"},
                                 2)  # Insert rating as third logical tag
            if settings["tags"].get("XMP:Rating") is None:  # Add rating in logical tags
                settings["tags"]["XMP:Rating"] = {"access": "Read/Write"}
            if settings["tags"].get("XMP-microsoft:RatingPercent") is None:  # Add rating in logical tags
                settings["tags"]["XMP-microsoft:RatingPercent"] = {"access": "Read/Write"}
            for migration_file_type in ["jpg", "jpeg", "png", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "gif",
                                        "mp4", "mov"]:
                if settings["file_type_tags"][migration_file_type].get("rating") is None:
                    if migration_file_type == "mp4" or migration_file_type == "mov":  # Here rating is first logical tag
                        insertDictionary(settings["file_type_tags"][migration_file_type], "rating",
                                         ["XMP:Rating", "XMP-microsoft:RatingPercent"], 0)
                    else:
                        insertDictionary(settings["file_type_tags"][migration_file_type], "rating",
                                         ["XMP:Rating", "XMP-microsoft:RatingPercent"], 1)
            if settings["text_keys"].get("tag_label_rating") is None:
                settings["text_keys"]["tag_label_rating"] = {"DA": "Bedømmelse", "EN": "Rating"}

    def rule02():  # Add text_keys for file-preview context menu
        global settings
        if old_ver_num <= 10399 and new_ver_num >= 10400:  # Tiff-support added in version 1.4.0
            def rule02():  # Add text_keys for file-preview context menu
                global settings
                if old_ver_num <= 10299 and new_ver_num >= 10300:  # Context-menu for file-preview added in version 01.03.00
                    if settings["text_keys"].get("preview_menu_open_in_default_program") is None:
                        settings["text_keys"]["preview_menu_open_in_default_program"] = {"DA": "Åben",
                                                                                         "EN": "Open"}
                    if settings["text_keys"].get("preview_menu_open_in_browser") is None:
                        settings["text_keys"]["preview_menu_open_in_browser"] = {"DA": "Åben i webbrowser",
                                                                                 "EN": "Open in Web Browser"}

            if settings["text_keys"].get("preview_menu_open_in_default_program") is None:
                settings["text_keys"]["preview_menu_open_in_default_program"] = {"DA": "Åben",
                                                                                 "EN": "Open"}
            if settings["text_keys"].get("preview_menu_open_in_browser") is None:
                settings["text_keys"]["preview_menu_open_in_browser"] = {"DA": "Åben i webbrowser",
                                                                         "EN": "Open in Web Browser"}

    def rule03():  # Add support for .tiff files to be the same as .tif files, as both extensions are used
        global settings
        if old_ver_num <= 10399 and new_ver_num >= 10400:  # Tiff-file support added in version 1.4.0
            if not "tiff" in settings["file_types"]:
                settings["file_types"].append("tiff")
            settings["file_type_tags"]["tiff"] = {"rotation": ["EXIF:Orientation#"],
                "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                    "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                             "IPTC:DateCreated", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                "EXIF:XPKeywords", "IPTC:Keywords"],
                    "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                    "IPTC:Caption-Abstract"]
                }


    def rule04():  # By defaule, date and geolocation should not be selected for pasting
        if old_ver_num <= 10399 and new_ver_num >= 10400:  # Date and geolocation not pasted by default
            date_logical_tag = settings["logical_tags"].get("date")
            if date_logical_tag != None:
                if date_logical_tag.get("default_paste_select") == None:
                    date_logical_tag["default_paste_select"] = False
            geo_location_logical_tag = settings["logical_tags"].get("geo_location")
            if geo_location_logical_tag != None:
                if geo_location_logical_tag.get("default_paste_select") == None:
                    geo_location_logical_tag["default_paste_select"] = False

    def rule05():   # Add support for mt2- and m2ts-files
        global settings
        if old_ver_num <= 10401 and new_ver_num >= 10500:  # mt2- and m2ts-file support added in 1.5.0
            if not "m2t" in settings["file_types"]:
                settings["file_types"].append("m2t")
                settings["file_type_tags"]["m2t"] = {}
            if not "m2ts" in settings["file_types"]:
                settings["file_types"].append("m2ts")
                settings["file_type_tags"]["m2ts"] =  {}
            if not "mts" in settings["file_types"]:
                settings["file_types"].append("mts")
                settings["file_type_tags"]["mts"] = {}
    def rule06():   # Add support for m4vgit-files
        global settings
        if old_ver_num <= 10600 and new_ver_num >= 10700:  # m4v added in version 1.7.0
            if not "m4v" in settings["file_types"]:
                settings["file_types"].append("m4v")
                settings["file_type_tags"]["m4v"] = {"rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                    "title": ["XMP:Title", "QuickTime:Title"],
                    "date": ["XMP:Date", "QuickTime:CreateDate", "QuickTime:ModifyDate",
                             "QuickTime:MediaModifyDate", "QuickTime:TrackCreateDate",
                             "QuickTime:TrackModifyDate", "File:FileCreateDate"],
                    "description_only": ["XMP:DescriptionOnly"],
                    "persons": ["XMP:Subject", "QuickTime:Category"],
                    "photographer": ["XMP:Creator", "QuickTime:Artist"],
                    "geo_location": ["Composite:GPSPosition#"],
                    "source": ["XMP:Source"],
                    "original_filename": ["XMP:PreservedFileName"],
                    "description": ["XMP:Description", "QuickTime:Comment"]
                    }
    def rule07():   # Replace Quicktime with QuickTime in settings, and add QuickTime:MediaCreateDate as first quicktim-tag for date
        global settings
        if old_ver_num <= 10700 and new_ver_num >= 10701:
            # Replace Quicktime with QuickTime in keys of tags-dictionary
            old_tags = settings.get("tags").copy()
            for tag in old_tags:     # Quicktime corrected to QuickTime in 1.7.1
                if isinstance(tag, str):
                    new_tag = tag.replace("Quicktime", "QuickTime")
                    if new_tag != tag:
                        settings["tags"][new_tag] = settings["tags"].pop(tag)
            # Replace Quicktime with QuickTime in values of logical_tag_tags-list
            for file_type in settings["file_type_tags"]:
                for logical_tag in settings["file_type_tags"][file_type]:
                    tags = settings["file_type_tags"][file_type][logical_tag]
                    new_tags = [tag.replace("Quicktime", "QuickTime") for tag in tags]
                    if new_tags != tags:
                        settings["file_type_tags"][file_type][logical_tag] = new_tags
            # Add QuickTime:MediaCreateDate in mp4, m4v and mov files
            if settings["tags"].get("QuickTime:MediaCreateDate") is None:
                settings["tags"]["QuickTime:MediaCreateDate"] = {"access": "Read/Write"}
                for file_type in ["mp4","m4v","mov"]:
                    if not settings["file_type_tags"].get(file_type) is None:
                        if not settings["file_type_tags"][file_type].get("date") is None:
                            pos = 0
                            if len(settings["file_type_tags"][file_type]["date"]) > 0:
                                if settings["file_type_tags"][file_type]["date"][0] == "XMP:Date":
                                    pos = 1
                            settings["file_type_tags"][file_type]["date"].insert(pos, "QuickTime:MediaCreateDate")

            # use rotation and remove orientation logical tag
            if 'orientation' in settings["logical_tags"]:
                dummy = settings["logical_tags"].pop('orientation')

            new_file_type_tags = {}
            for file_type in settings["file_type_tags"]:
                new_file_type_tags[file_type] = {}
                for logical_tag in settings["file_type_tags"][file_type]:
                    if logical_tag == 'orientation':
                        new_logical_tag = 'rotation'
                    else:
                        new_logical_tag = logical_tag
                    new_file_type_tags[file_type][new_logical_tag] = settings["file_type_tags"][file_type][logical_tag]
            settings['file_type_tags'] = new_file_type_tags


    old_ver_num = versionNumber(settings.get("version"))
    new_ver_num = versionNumber(version)

    settings["version"] = version

    if old_ver_num == 0:
        return
    else:
        rule01()  # Add rating in settings
        rule02()  # Add context menu to preview
        rule03()  # Add support for tiff-files
        rule04()  # Don't select date and geo-location for pasting by default
        rule05()  # Add support for m2t- and m2ts-files
        rule06()  # Add support for m4v-files
        rule07()  # Change Quicktime to QuickTime, and add tag QuickTime:MediaCreateDate

def writeSettingsFile():
    global settings, settings_path
    settings_json_object = json.dumps(settings, indent=4)
    with open(settings_path, "w") as outfile:
        outfile.write(settings_json_object)


version = "1.7.1"   # Quicktime replaced with QuickTime in settings

# Make location for Application, if missing
app_data_location = os.path.join(os.environ.get("ProgramData"),"Memory Mate")
if not os.path.isdir(app_data_location):
    os.mkdir(app_data_location)

# Define global variable for settings
settings = {}

# Set path to settings
settings_path = os.path.join(app_data_location,"settings.json")

# Set path to queue-file
queue_file_path = os.path.join(app_data_location,"queue.json")

# Read settings-file, patch it and upgrade
readSettingsFile()
old_settings = copy.deepcopy(settings)
patchDefaultValues()
migrateVersion()

# Write settings to file if new or upgraded
if old_settings != settings:          # Write to file and update settings variables in case of change
    writeSettingsFile()

# Set all variables from data in settingsfile
version = settings.get("version")            # Actually this is the version already assigned in top of settings
file_types = settings.get("file_types")
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








