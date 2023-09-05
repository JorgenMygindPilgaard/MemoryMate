import json
import os
from file_util import JsonQueue
#
# Make location for Application, if missing
#
app_data_location = os.path.join(os.environ.get("ProgramData"),"Memory Mate")
if not os.path.isdir(app_data_location):
    os.mkdir(app_data_location)

settings_path = os.path.join(app_data_location,"settings.json")
queue_file_path = os.path.join(app_data_location,"queue.json")

#
# Read settings-file, if it is there
#
if os.path.isfile(settings_path):
    with open(settings_path, 'r') as infile:
        settings = json.load(infile)

    file_types = settings.get("file_types")
    languages = settings.get("languages")
    language = settings.get("language")
    logical_tags = settings.get("logical_tags")
    tags = settings.get("tags")
    file_type_tags = settings.get("file_type_tags")
    text_keys = settings.get("text_keys")
    file_context_menu_actions = settings.get("file_context_menu_actions")
    folder_context_menu_actions = settings.get("folder_context_menu_actions")

#
# Make settings-file, if it is missing
#
if not os.path.isfile(settings_path):
    file_types = ["jpg", "jpeg", "png", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "gif", "mp4", "mov", "avi"]
    languages = {"DA": "Danish",
                 "EN": "English"}
    language = "DA"

    logical_tags = {"title":             {"widget":                "text_line",
                                          "label_text_key":        "tag_label_title"},
                    "date":              {"widget":                "date_time",
                                          "label_text_key":        "tag_label_date"},
                    "description_only":  {"widget":                "text",
                                          "label_text_key":        "tag_label_description_only",
                                          "fallback_tag":          "description"},    #If description_only is blank in metadata, it is populated from description
                    "persons":           {"widget":                "text_set",
                                          "label_text_key":        "tag_label_persons",
                                          "Autocomplete":          True},
                    "photographer":      {"widget":                "text_line",
                                          "label_text_key":        "tag_label_photographer",
                                          "Autocomplete":          True},
                    "source":            {"widget":                "text_line",
                                          "label_text_key":        "tag_label_source",
                                          "Autocomplete":          True},
                    "original_filename": {"widget":                "text_line",
                                          "label_text_key":        "tag_label_original_filename"},
                    "geo_location":      {"widget":                "geo_location",
                                          "label_text_key":        "tag_label_geo_location"},
                    "description":       {"widget":                "text",
                                          "label_text_key":        "tag_label_description",
                                          "reference_tag":         True,
                                          "reference_tag_content": [{"type": "tag", "tag_name": "title", "tag_label": False},
                                                                    {"type": "tag", "tag_name": "description_only", "tag_label": False},
                                                                    {"type": "text_line", "text": ""},
                                                                    {"type": "tag", "tag_name": "persons", "tag_label": True},
                                                                    {"type": "tag", "tag_name": "source", "tag_label": True},
                                                                    {"type": "tag", "tag_name": "photographer", "tag_label": True},
                                                                    {"type": "tag", "tag_name": "original_filename", "tag_label": True}
                                                                   ]},
                    "orientation":       {"widget":        None}
                   }

    tags = {"XMP:Title": {"type": "text_line", "access": "Read/Write"},
            "EXIF:XPTitle": {"type": "text_line", "access": "Read/Write"},
            "IPTC:ObjectName": {"type": "text_line", "access": "Read/Write"},
            "XMP:Date": {"type": "date_time", "access": "Read/Write"},
            "EXIF:DateTimeOriginal": {"type": "date_time", "access": "Read/Write}"},
            "EXIF:CreateDate": {"type": "date_time", "access": "Read/Write}"},
            "EXIF:ModifyDate": {"type": "date_time", "access": "Read/Write}"},
            "IPTC:DateCreated": {"type": "date_time", "access": "Read/Write}"},
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
            "XMP:Creator": {"type": "text_line", "access": "Read/Write"},
            "EXIF:Artist": {"type": "text_line", "access": "Read/Write"},
            "EXIF:XPAuthor": {"type": "text_line", "access": "Read/Write"},
            "IPTC:By-line": {"type": "text_line", "access": "Read/Write"},
            "XMP:Source": {"type": "text_line", "access": "Read/Write"},
            "XMP:PreservedFileName": {"type": "text_line", "access": "Read/Write"},
            "Quicktime:Title": {"type": "text_line", "access": "Read/Write"},
            "Quicktime:CreateDate": {"type": "date_time", "access": "Read/Write"},
            "Quicktime:ModifyDate": {"type": "date_time", "access": "Read/Write"},
            "Quicktime:MediaModifyDate": {"type": "date_time", "access": "Read/Write"},
            "Quicktime:TrackCreateDate": {"type": "date_time", "access": "Read/Write"},
            "Quicktime:TrackModifyDate": {"type": "date_time", "access": "Read/Write"},
            "Quicktime:Comment": {"type": "text", "access": "Read/Write"},
            "Quicktime:Category": {"type": "text_set", "access": "Read/Write"},
            "Quicktime:Artist": {"type": "text_line", "access": "Read/Write"},
            "RIFF:DateTimeOriginal": {"type": "date_time", "access": "Read"},
            "File:FileCreateDate": {"type": "date_time", "access": "Read"},
            "Composite:GPSPosition": {"type": "geo_location", "access": "Read/Write"}
            }

    file_type_tags = {
        "jpg": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
               },
        "jpeg": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
                },
        "png": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
                },
        "cr3": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"],
                "orientation": ["EXIF:Orientation"]
                },

        "cr2": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"],
                "orientation": ["EXIF:Orientation"]
                },
        "nef": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"],
                "orientation": ["EXIF:Orientation"]
                },
        "dng": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
                },
        "arw": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
               },
        "heic": {"title": ["XMP:Title", "EXIF:XPTitle"],
                 "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                 "description_only": ["XMP:DescriptionOnly"],
                 "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                             "EXIF:XPKeywords"],
                 "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                 "geo_location": ["Composite:GPSPosition"],
                 "source": ["XMP:Source"],
                 "original_filename": ["XMP:PreservedFileName"],
                 "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                },
        "tif": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"],
                "orientation": ["EXIF:Orientation"]
               },
        "gif": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                "description_only": ["XMP:DescriptionOnly", "File:FileCreateDate"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"],
                "orientation": ["EXIF:Orientation"]
               },
        "mp4": {"title": ["XMP:Title", "Quicktime:Title"],
                "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                         "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                         "Quicktime:TrackModifyDate", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP:Subject", "Quicktime:Category"],
                "photographer": ["XMP:Creator", "Quicktime:Artist"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "Quicktime:Comment"]
                },
        "mov": {"title": ["XMP:Title", "Quicktime:Title"],
                "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                         "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                         "Quicktime:TrackModifyDate", "File:FileCreateDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP:Subject", "Quicktime:Category"],
                "photographer": ["XMP:Creator", "Quicktime:Artist"],
                "geo_location": ["Composite:GPSPosition"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "Quicktime:Comment"]
                },
        "avi": {"date": ["RIFF:DateTimeOriginal", "File:FileCreateDate"]
                }
    }

    text_keys = {"tag_label_title":
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
                      "EN": "Original filename"},
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
                      "EN": "Paste Metadata by filename"},
                 "file_menu_patch_by_filename":
                     {"DA": "Udfyld metadata efter filnavn",
                      "EN": "Patch Metadata by filename"},
                 "file_menu_chose_tags_to_paste":
                     {"DA": "Vælg hvad du vil overføre:",
                      "EN": "Choose what to transfer:"},
                 "folder_menu_standardize":
                     {"DA": "Standardiser filnavne",
                      "EN": "Standardize Filenames"},
                 "folder_menu_consolidate":
                     {"DA": "Konsolider metadata", "EN": "Consolidate Metadata"}
                }

    file_context_menu_actions = {"consolidate_metadata":
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

    folder_context_menu_actions = {"standardize_filenames":
                                       {"text_key": "folder_menu_standardize"},
                                   "consolidate_metadata":
                                       {"text_key": "floder_menu_consolidate"}
                                  }


    settings = {"file_types": file_types,
                "languages": languages,
                "language": language,
                "logical_tags": logical_tags,
                "tags": tags,
                "file_type_tags": file_type_tags,
                "text_keys": text_keys,
                "file_context_menu_actions": file_context_menu_actions,
                "folder_context_menu_actions": folder_context_menu_actions}

    settings_json_object = json.dumps(settings, indent=4)
    with open(settings_path, "w") as outfile:
        outfile.write(settings_json_object)

# Make exiftool.cfg file if it is missing
exiftool_cfg_path = os.path.join(app_data_location,"exiftool.cfg")
if not os.path.isfile(exiftool_cfg_path):
    exiftool_cfg = ["# A new XMP-namespace (jmp_mde) is added to Main XMP-table:",
                    "%Image::ExifTool::UserDefined = (",
                    "    'Image::ExifTool::XMP::Main' => {",
                    "        jmp_mde => {",
                    "            SubDirectory => {",
                    "                TagTable => 'Image::ExifTool::UserDefined::jmp_mde',",
                    "            },",
                    "        },",
                    "    },",
                    ");",
                    "",
                    "# New tags are added to XMP-jmp_mde namespace:",
                    "%Image::ExifTool::UserDefined::jmp_mde = (",
                    "    GROUPS => { 0 => 'XMP', 1 => 'XMP-jmp_mde', 2 => 'Image' },",
                    "    NAMESPACE => { 'jmp_mde' => 'https://jorgenpilgaard.dk/namespace/jmp_mde/' },",
                    "    WRITABLE => 'string', # (default to string-type tags)",
                    "    DescriptionOnly => { Writable => 'lang-alt' },",
                    "    MemoryMateSaveDateTime => { Writable => 'lang-alt' },",
                    "    #AnotherTag => { Writable => 'lang-alt' },",
                    ");"]

    with open(exiftool_cfg_path, "w") as outfile:
        # Loop through the list and write each string to a new line in the file
        for item in exiftool_cfg:
            outfile.write(item + "\n")
