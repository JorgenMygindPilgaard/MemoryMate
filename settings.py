import json
import os
import copy
from util import insertDictionary

version = "1.2.0"   # Version with rating added

# Make location for Application, if missing
app_data_location = os.path.join(os.environ.get("ProgramData"),"Memory Mate")
if not os.path.isdir(app_data_location):
    os.mkdir(app_data_location)

# Set path to settings
settings_path = os.path.join(app_data_location,"settings.json")

# Set path to queue-file
queue_file_path = os.path.join(app_data_location,"queue.json")

def readSettingsFile():
    if os.path.isfile(settings_path):
        with open(settings_path, 'r') as settings_file:
            settings = json.load(settings_file)
    else:
        settings = {}
    return settings
def writeSettingsFile():
    settings_json_object = json.dumps(settings, indent=4)
    with open(settings_path, "w") as outfile:
        outfile.write(settings_json_object)
def migrateVersion(version,settings):
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
        if old_ver_num <= 10199 and new_ver_num >= 10200:  # rating-tag added in version 1.2
            if settings["logical_tags"].get("rating") is None:                 # Add rating in logical tags
                insertDictionary(settings["logical_tags"],"rating",{"widget": "rating", "data_type": "number","label_text_key": "tag_label_rating"},2)  # Insert rating as third logical tag
            if settings["tags"].get("XMP:Rating") is None:                 # Add rating in logical tags
                settings["tags"]["XMP:Rating"] = {"access": "Read/Write"}
            if settings["tags"].get("XMP-microsoft:RatingPercent") is None:                 # Add rating in logical tags
                settings["tags"]["XMP-microsoft:RatingPercent"] = {"access": "Read/Write"}
            for migration_file_type in ["jpg", "jpeg", "png", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "gif", "mp4", "mov"]:
                if settings["file_type_tags"][migration_file_type].get("rating") is None:
                    if migration_file_type == "mp4" or migration_file_type == "mov":               # Here rating is first logical tag
                        insertDictionary(settings["file_type_tags"][migration_file_type],"rating",["XMP:Rating", "XMP-microsoft:RatingPercent"],0)
                    else:
                        insertDictionary(settings["file_type_tags"][migration_file_type], "rating",["XMP:Rating", "XMP-microsoft:RatingPercent"], 1)
            if settings["text_keys"].get("tag_label_rating") is None:
                settings["text_keys"]["tag_label_rating"] = {"DA": "Bedømmelse", "EN": "Rating"}


    old_ver_num = versionNumber(settings.get("version"))
    new_ver_num = versionNumber(version)

    settings["version"] = version
        
    if old_ver_num == 0:
        return
    else:
        rule01()    # Add rating

# Read settings-file, if it is there
settings = readSettingsFile()
old_settings = copy.deepcopy(settings)

# Set default-values for missing settings
if settings.get("version") is None:
    settings["version"] = "0.0.0"       # Initial installation
if settings.get("file_types") is None:
    settings["file_types"] = ["jpg", "jpeg", "png", "bmp", "cr3", "cr2", "dng", "arw", "nef", "heic", "tif", "gif", "mp4", "mov", "avi"]
if settings.get("languages") is None:
    settings["languages"] = {"DA": "Danish",
                             "EN": "English"}
if settings.get("language") is None:
    settings["language"] = "EN"
if settings.get("logical_tags") is None:
    settings["logical_tags"] = {
                                "orientation":       {"widget":                "orientation",
                                                      "data_type":             "number"},
                                "rotation":          {"widget":                "rotation",
                                                      "data_type":             "number"},
                                "rating":            {"widget":                "rating",
                                                      "data_type":             "number",
                                                      "label_text_key":        "tag_label_rating"},
                                "title":             {"widget":                "text_line",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_title"},
                                "date":              {"widget":                "date_time",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_date"},
                                "description_only":  {"widget":                "text",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_description_only",
                                                      "fallback_tag":          "description"},    #If description_only is blank in metadata, it is populated from description
                                "persons":           {"widget":                "text_set",
                                                      "data_type":             "list",
                                                      "label_text_key":        "tag_label_persons",
                                                      "Autocomplete":          True},
                                "photographer":      {"widget":                "text_line",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_photographer",
                                                      "Autocomplete":          True},
                                "source":            {"widget":                "text_line",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_source",
                                                      "Autocomplete":          True},
                                "original_filename": {"widget":                "text_line",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_original_filename"},
                                "geo_location":      {"widget":                "geo_location",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_geo_location"},
                                "description":       {"widget":                "text",
                                                      "data_type":             "string",
                                                      "label_text_key":        "tag_label_description",
                                                      "reference_tag":         True,
                                                      "reference_tag_content": [{"type": "tag", "tag_name": "title", "tag_label": False},
                                                                                {"type": "tag", "tag_name": "description_only", "tag_label": False},
                                                                                {"type": "text_line", "text": ""},
                                                                                {"type": "tag", "tag_name": "persons", "tag_label": True},
                                                                                {"type": "tag", "tag_name": "source", "tag_label": True},
                                                                                {"type": "tag", "tag_name": "photographer", "tag_label": True},
                                                                                {"type": "tag", "tag_name": "original_filename", "tag_label": True}
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
                        "Quicktime:Title": {"access": "Read/Write"},
                        "Quicktime:CreateDate": {"access": "Read/Write"},
                        "Quicktime:ModifyDate": {"access": "Read/Write"},
                        "Quicktime:MediaModifyDate": {"access": "Read/Write"},
                        "Quicktime:TrackCreateDate": {"access": "Read/Write"},
                        "Quicktime:TrackModifyDate": {"access": "Read/Write"},
                        "Quicktime:Comment": {"type": "text", "access": "Read/Write"},
                        "Quicktime:Category": {"type": "text_set", "access": "Read/Write"},
                        "Quicktime:Artist": {"access": "Read/Write"},
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
                                    "jpg":  {"orientation": ["EXIF:Orientation#"],
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
                                    "jpeg": {"orientation": ["EXIF:Orientation#"],
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
                                    "png": {"orientation": ["EXIF:Orientation#"],
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
                                    "cr3": {"orientation": ["EXIF:Orientation#"],
                                            "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                                            "title": ["XMP:Title", "EXIF:XPTitle"],
                                            "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                                            "description_only": ["XMP:DescriptionOnly"],
                                            "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                                        "EXIF:XPKeywords"],
                                            "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                                            "geo_location": ["Composite:GPSPosition#"],
                                            "source": ["XMP:Source"],
                                            "original_filename": ["XMP:PreservedFileName"],
                                            "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                                            },

                                    "cr2": {"orientation": ["EXIF:Orientation#"],
                                            "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                                            "title": ["XMP:Title", "EXIF:XPTitle"],
                                            "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                                            "description_only": ["XMP:DescriptionOnly"],
                                            "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                                        "EXIF:XPKeywords"],
                                            "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                                            "geo_location": ["Composite:GPSPosition#"],
                                            "source": ["XMP:Source"],
                                            "original_filename": ["XMP:PreservedFileName"],
                                            "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                                            },
                                    "nef": {"orientation": ["EXIF:Orientation#"],
                                            "rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                                            "title": ["XMP:Title", "EXIF:XPTitle"],
                                            "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                                            "description_only": ["XMP:DescriptionOnly"],
                                            "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                                        "EXIF:XPKeywords"],
                                            "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                                            "geo_location": ["Composite:GPSPosition#"],
                                            "source": ["XMP:Source"],
                                            "original_filename": ["XMP:PreservedFileName"],
                                            "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                                            },
                                    "dng": {"orientation": ["EXIF:Orientation#"],
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
                                    "arw": {"orientation": ["EXIF:Orientation#"],
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
                                             "date": ["XMP:Date", "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate", "File:FileCreateDate"],
                                             "description_only": ["XMP:DescriptionOnly"],
                                             "persons": ["XMP-iptcExt:PersonInImage", "XMP-MP:RegionPersonDisplayName", "XMP:Subject",
                                                         "EXIF:XPKeywords"],
                                             "photographer": ["XMP:Creator", "EXIF:Artist", "EXIF:XPAuthor"],
                                             "geo_location": ["Composite:GPSPosition#"],
                                             "source": ["XMP:Source"],
                                             "original_filename": ["XMP:PreservedFileName"],
                                             "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment", "EXIF:ImageDescription"]
                                            },
                                    "tif": {"orientation": ["EXIF:Orientation#"],
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
                                    "gif": {"orientation": ["EXIF:Orientation#"],
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
                                            "title": ["XMP:Title", "Quicktime:Title"],
                                            "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                                                     "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                                                     "Quicktime:TrackModifyDate", "File:FileCreateDate"],
                                            "description_only": ["XMP:DescriptionOnly"],
                                            "persons": ["XMP:Subject", "Quicktime:Category"],
                                            "photographer": ["XMP:Creator", "Quicktime:Artist"],
                                            "geo_location": ["Composite:GPSPosition#"],
                                            "source": ["XMP:Source"],
                                            "original_filename": ["XMP:PreservedFileName"],
                                            "description": ["XMP:Description", "Quicktime:Comment"]
                                            },
                                    "mov": {"rating": ["XMP:Rating", "XMP-microsoft:RatingPercent"],
                                            "title": ["XMP:Title", "Quicktime:Title"],
                                            "date": ["XMP:Date", "Quicktime:CreateDate", "Quicktime:ModifyDate",
                                                     "Quicktime:MediaModifyDate", "Quicktime:TrackCreateDate",
                                                     "Quicktime:TrackModifyDate", "File:FileCreateDate"],
                                            "description_only": ["XMP:DescriptionOnly"],
                                            "persons": ["XMP:Subject", "Quicktime:Category"],
                                            "photographer": ["XMP:Creator", "Quicktime:Artist"],
                                            "geo_location": ["Composite:GPSPosition#"],
                                            "source": ["XMP:Source"],
                                            "original_filename": ["XMP:PreservedFileName"],
                                            "description": ["XMP:Description", "Quicktime:Comment"]
                                            },
                                    "avi": {"date": ["RIFF:DateTimeOriginal", "File:FileCreateDate"]
                                           }
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
                                 {"DA": "Konsolider metadata",
                                  "EN": "Consolidate Metadata"},
                             "settings_window_title":
                                 {"DA": "Indstillinger",
                                  "EN": "Settings"},
                             "settings_labels_application_language":
                                 {"DA": "Sprog",
                                  "EN": "Language"}
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

# Migrate settings at upgrade
migrateVersion(version,settings)

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





