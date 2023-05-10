import json
import os
#
# Make location for Application, if missing
#
app_data_location = os.path.join(os.environ.get("ProgramData"),"Memory Mate")
if not os.path.isdir(app_data_location):
    os.mkdir(app_data_location)

settings_path = os.path.join(app_data_location,"settings.json")

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
    reference_tag_content = settings.get("reference_tag_content")
    logical_tag_descriptions = settings.get("logical_tag_descriptions")
    logical_tag_attributes = settings.get("logical_tag_attributes")
    tags = settings.get("tags")
    file_type_tags = settings.get("file_type_tags")
    file_context_menu_actions = settings.get("file_context_menu_actions")
    folder_context_menu_actions = settings.get("folder_context_menu_actions")

#
# Make settings-file, if it is missing
#
if not os.path.isfile(settings_path):
    file_types = ["jpg", "png", "cr3", "cr2", "dng", "arw", "heic", "tif", "gif", "mp4", "mov", "avi"]
    languages = {"DA": "Danish",
                 "EN": "English"}
    language = "EN"
    logical_tags = {"title":             "text_line",
                    "date":              "date_time",
                    "description_only":  "text",
                    "persons":           "text_set",
                    "photographer":      "text_line",
                    "source":            "text_line",
                    "original_filename": "text_line",
                    "description": "reference_tag"  # Always type text
                    }
    reference_tag_content = {"description": [{"type": "tag", "tag_name": "title", "tag_label": False},
                                             {"type": "tag", "tag_name": "description_only", "tag_label": False},
                                             {"type": "text_line", "text": ""},
                                             {"type": "tag", "tag_name": "persons", "tag_label": True},
                                             {"type": "tag", "tag_name": "source", "tag_label": True},
                                             {"type": "tag", "tag_name": "photographer", "tag_label": True},
                                             {"type": "tag", "tag_name": "original_filename", "tag_label": True}
                                             ]
                             }
    logical_tag_descriptions = {"title":             {"DA": "Titel",               "EN": "Title"},
                                "date":              {"DA": "Dato",                "EN": "Date"},
                                "description":       {"DA": "Fuld beskrivelse",    "EN": "Full Description"},
                                "description_only":  {"DA": "Beskrivelse",         "EN": "Description"},
                                "persons":           {"DA": "Personer",            "EN": "People"},
                                "photographer":      {"DA": "Fotograf",            "EN": "Photographer"},
                                "source":            {"DA": "Oprindelse",          "EN": "Source"},
                                "original_filename": {"DA": "Oprindeligt filnavn", "EN": "Original filename"}
                                }

    logical_tag_attributes = {"title": {},
                              "date": {},
                              "description": {"hide": False},  #As it is a ref-tag, it can be hidden. It is always write-protected

                              # The logical tag will be defaulted from fallback_tag if missing in image,
                              # but only until memory-mate saved metadata to image first time.
                              "description_only": {"fallback_tag": "description"},

                              "persons": {"Autocomplete": True},
                              "photographer": {"Autocomplete": True},
                              "source": {"Autocomplete": True},
                              "original_filename": {}
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
            "RIFF:DateTimeOriginal": {"type": "date_time", "access": "Read"}
            }
    file_type_tags = {
        "jpg": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"]
                },
        "png": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"]
                },
        "cr3": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription"]
                },

        "cr2": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription"]
                },
        "dng": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"]
                },
        "arw": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"]
                },
        "heic": {"title": ["XMP:Title", "EXIF:XPTitle"],
                 "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                 "description_only": ["XMP:DescriptionOnly"],
                 "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                             "EXIF:XPKeywords"],
                 "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                 "source": ["XMP:Source"],
                 "original_filename": ["XMP:PreservedFileName"],
                 "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription"]
                 },
        "tif": {"title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
                         "IPTC:DateCreated"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords", "IPTC:Keywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor", "IPTC:By-line"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription",
                                "IPTC:Caption-Abstract"]
                },
        "gif": {"title": ["XMP:Title", "EXIF:XPTitle"],
                "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                            "EXIF:XPKeywords"],
                "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "EXIF:XPComment", "EXIF:ImageDescription"]
                },
        "mp4": {"title": ["XMP:Title", "Quicktime:Title"],
                "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                         "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                         "Quicktime:TrackModifyDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP:Subject", "Quicktime:Category"],
                "photographer": ["XMP:Creator", "Quicktime:Artist"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "Quicktime:Comment"]
                },
        "mov": {"title": ["XMP:Title", "Quicktime:Title"],
                "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                         "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                         "Quicktime:TrackModifyDate"],
                "description_only": ["XMP:DescriptionOnly"],
                "persons": ["XMP:Subject", "Quicktime:Category"],
                "photographer": ["XMP:Creator", "Quicktime:Artist"],
                "source": ["XMP:Source"],
                "original_filename": ["XMP:PreservedFileName"],
                "description": ["XMP:Description", "Quicktime:Comment"]
                },
        "avi": {"date": ["RIFF:DateTimeOriginal"]
                }
    }
    file_context_menu_actions = {"consolidate_metadata": {"DA": "Konsolider metadata", "EN": "Consolidate Metadata"},
                                 "copy_metadata": {"DA": "Kopier metadata", "EN": "Copy Metadata"},
                                 "paste_metadata": {"DA": "Indsæt metadata", "EN": "Paste Metadata"},
                                 "patch_metadata": {"DA": "Udfyld metadata", "EN": "Patch Metadata"},
                                 "paste_by_filename": {"DA": "Indsæt metadata efter filnavn", "EN": "Paste Metadata by filename"},
                                 "patch_by_filename": {"DA": "Udfyld metadata efter filnavn", "EN": "Patch Metadata by filename"},
                                 "choose_tags_to_paste": {"DA": "Vælg hvad du vil overføre:",
                                                          "EN": "Choose what to transfer:"}
                                 }

    folder_context_menu_actions = {"standardize_filenames": {"DA": "Standardiser filnavne", "EN": "Standardize Filenames"},
                                   "consolidate_metadata": {"DA": "Konsolider metadata", "EN": "Consolidate Metadata"}
                                  }


    settings = {"file_types": file_types,
                "languages": languages,
                "language": language,
                "logical_tags": logical_tags,
                "reference_tag_content": reference_tag_content,
                "logical_tag_descriptions": logical_tag_descriptions,
                "logical_tag_attributes": logical_tag_attributes,
                "tags": tags,
                "file_type_tags": file_type_tags,
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
