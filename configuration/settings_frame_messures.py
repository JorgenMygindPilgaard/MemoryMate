import json
import os
from configuration.paths import Paths

class Settings():
    settings = {}

    @staticmethod
    def get(setting_id):
        return Settings.settings.get(setting_id)

    @staticmethod
    def set(setting_id,setting_value):
        Settings.settings[setting_id]=setting_value

    @staticmethod
    def _readSettingsFile():
        if os.path.isfile(Paths.get('settings')):
            with open(Paths.get('settings'), 'r') as settings_file:
                Settings.settings = json.load(settings_file)

    @staticmethod
    def _patchDefaultValues():
        if Settings.get("languages") is None:
            Settings.set("languages",
                         {"DA": "Danish",
                                     "EN": "English",
                                     "FR": "French",
                                     "ES": "Spanish",
                                     "DE": "German",
                                     "SV": "Swedish",
                                     "FI": "Finish",
                                     "IT": "Italian"})
        if Settings.get("ui_modes") is None:
            Settings.set("ui_modes",["LIGHT","DARK"])
        if Settings.get("ui_mode") is None:
            Settings.set("ui_mode","LIGHT")
        if Settings.get("auto_consolidate_active") is None:
            Settings.set("auto_consolidate_active",False)
        if Settings.get("lr_integration_active") is None:
            Settings.set("lr_integration_active",False)
        if Settings.get("lr_db_path") is None:
            Settings.set("lr_db_path",'')
        if Settings.get("garmin_integration_active") is None:
            Settings.set("garmin_integration_active",False)
        if Settings.get("file_types") is None:
            Settings.set("file_types", ["jpg", "jpeg", "png", "bmp", "cr3", "cr2", "dng", "arw", "nef", "heic","tif", "tiff", "gif", "mp4", "m4v", "mov", "avi", "m2t", "m2ts", "mts"])
        if Settings.get("raw_file_types") is None:
            Settings.set("raw_file_types", ["cr3", "cr2", "arw", "nef", "dng"])
        if Settings.get("sidecar_file_source_ids") is None:
            Settings.set("sidecar_file_source_ids",{"JSON": {"file_name_pattern": "<file_name>.<ext>.json"}})
        if Settings.get("logical_tags") is None:
            Settings.set("logical_tags",{
                "rotation": {"widget": "Rotation",
                             "value_class": "RotationValue",
                             "access": "Read/Write"},
                "title": {"widget": "TextLine",
                          "value_class": "StringValue",
                          "label_text_key": "tag_label_title",
                          "access": "Read/Write"},
                "description_only": {"widget": "Text",
                                     "value_class": "StringValue",
                                     "label_text_key": "tag_label_description_only",
                                     "fallback_tag": "description",
                                     "access": "Read/Write"},
                "insert_x": {"widget": "TextLine",
                          "value_class": "StringValue",
                          "label_text_key": "tag_label_insert_y",
                          "access": "Read/Write"},
                "insert_y": {"widget": "TextLine",
                             "value_class": "StringValue",
                             "label_text_key": "tag_label_insert_x",
                             "access": "Read/Write"},
                "insert_width": {"widget": "TextLine",
                             "value_class": "StringValue",
                             "label_text_key": "tag_label_insert_width",
                             "access": "Read/Write"},
                "insert_height": {"widget": "TextLine",
                             "value_class": "StringValue",
                             "label_text_key": "tag_label_insert_height",
                             "access": "Read/Write"},
                "insert_unit": {"widget": "TextLine",
                             "value_class": "StringValue",
                             "label_text_key": "tag_label_insert_unit",
                             "access": "Read/Write"},
                "insert_origin": {"widget": "TextLine",
                                  "value_class": "StringValue",
                                  "label_text_key": "tag_label_insert_origin",
                                  "access": "Read/Write"},
                "description": {"widget": "Text",
                                "value_class": "StringValue",
                                "label_text_key": "tag_label_description",
                                "reference_tag": True,
                                "access": "Read/Write",
                                "reference_tag_content": [{"type": "tag", "tag_name": "title", "new_line": True},
                                                          {"type": "tag", "tag_name": "description_only",
                                                           "new_line": True},
                                                          {"type": "text_line", "text": "", "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_x", "tag_label": True,
                                                           "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_y", "tag_label": True,
                                                           "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_width", "tag_label": True,
                                                           "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_height", "tag_label": True,
                                                           "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_unit", "tag_label": True,
                                                           "new_line": True},
                                                          {"type": "tag", "tag_name": "insert_origin", "tag_label": True,
                                                           "new_line": True}
                                                          ]}
            })

        if Settings.get("tags") is None:
            Settings.set("tags",{
                "XMP:InsertX": {"access": "Read/Write"},
                "XMP:InsertY": {"access": "Read/Write"},
                "XMP:InsertWidth": {"access": "Read/Write"},
                "XMP:InsertHeight": {"access": "Read/Write"},
                "XMP:InsertUnit": {"access": "Read/Write"},
                "XMP:InsertOrigin": {"access": "Read/Write"},
                "XMP:Title": {"access": "Read/Write"},
                "EXIF:XPTitle": {"access": "Read/Write"},
                "IPTC:ObjectName": {"access": "Read/Write"},
                "XMP:Date": {"access": "Read/Write"},
                "XMP:DateCreated": {"access": "Read/Write"},
                "EXIF:DateTimeOriginal": {"access": "Read/Write"},
                "EXIF:OffsetTimeOriginal": {"access": "Read/Write"},
                "EXIF:SubSecTimeOriginal": {"access": "Read/Write"},
                "EXIF:CreateDate": {"access": "Read/Write"},
                "EXIF:OffsetTimeDigitized": {"access": "Read/Write"},
                "EXIF:SubSecTimeDigitized": {"access": "Read/Write"},
                "IPTC:DateCreated": {"access": "Read/Write"},
                "XMP:Description": {"type": "text", "access": "Read/Write"},
                "EXIF:XPComment": {"type": "text", "access": "Read/Write"},
                "EXIF:UserComment": {"type": "text", "access": "Read/Write"},
                "EXIF:ImageDescription": {"type": "text", "access": "Read/Write"},
                "IPTC:Caption-Abstract": {"type": "text", "access": "Read/Write"},
                "XMP:DescriptionOnly": {"type": "text", "access": "Read/Write"},
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
                "QuickTime:CreationDate": {"access": "Read/Write"},
                "RIFF:DateTimeOriginal": {"access": "Read"},
                "Composite:GPSPosition": {"access": "Read/Write"},
                "Garmin:GPSPosition": {"access": "Read", "active_switch": "garmin_integration_active","source_type": "api", "source_id": "GpsApi","source_parameters":{"service_name":"garmin_connect"} },  # Standard-source for tags is files own metadata. In this case , source is the GpsApi
                "EXIF:Orientation#": {"access": "Read/Write"},
                "QuickTime:Rotation#": {"access": "Read/Write"},
                "Composite:Rotation": {"access": "Read/Write"},
                "XMP:Rating": {"access": "Read/Write"},
                "XMP:RatingPercent": {"access": "Read/Write"},
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
                "JSON:GeoDataExifLatitude": {"access": "Read", "source_type": "sidecar_file","source_id": "JSON"},
                "JSON:GeoDataExifLongitude": {"access": "Read", "source_type": "sidecar_file","source_id": "JSON"},
                "JSON:GeoDataLatitude": {"access": "Read", "source_type": "sidecar_file","source_id": "JSON"},
                "JSON:GeoDataLongitude": {"access": "Read", "source_type": "sidecar_file","source_id": "JSON"},
                "JSON:PhotoTakenTimeTimestamp": {"access": "Read","source_type": "sidecar_file","source_id": "JSON"},
                "JSON:description": {"access": "Read", "source_type": "sidecar_file","source_id": "JSON"},
                                         })
        if Settings.get("file_type_tags") is None:
            Settings.set("file_type_tags",{
                "jpg": {"rotation": ["EXIF:Orientation#"],
                        "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                        "description_only": ["XMP:DescriptionOnly"],
                        "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                        "EXIF:ImageDescription",
                                        "IPTC:Caption-Abstract", "JSON:description"],
                        },
                "jpeg": {"rotation": ["EXIF:Orientation#"],
                        "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                        "description_only": ["XMP:DescriptionOnly"],
                        "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                        "EXIF:ImageDescription",
                                        "IPTC:Caption-Abstract", "JSON:description"],
                        },
                "png": {"rotation": ["EXIF:Orientation#"],
                        "title": ["XMP:Title", "EXIF:XPTitle", "IPTC:ObjectName"],
                        "description_only": ["XMP:DescriptionOnly"],
                        "description": ["XMP:Description", "EXIF:XPComment", "EXIF:UserComment",
                                        "EXIF:ImageDescription",
                                        "IPTC:Caption-Abstract", "JSON:description"],
                        },
            })

        if Settings.get("file_context_menu") is None:
            Settings.set("file_context_menu",[
                {"id": "file_management", "parent_id": "file_context_menu", "type": "menu","text_key": "file_menu_file_management"},
                {"id": "consolidate_metadata", "parent_id": "file_context_menu", "type": "action","text_key": "file_menu_consolidate"},
                {"id": "copy_metadata", "parent_id": "file_context_menu", "type": "action","text_key": "file_menu_copy"},
                {"id": "paste", "parent_id": "file_context_menu", "type": "menu","text_key": "file_menu_paste"},
                {"id": "patch", "parent_id": "file_context_menu", "type": "menu","text_key": "file_menu_patch"},
                {"id": "delete", "parent_id": "file_context_menu", "type": "menu","text_key": "file_menu_delete"},
                {"id": "empty_clipboard", "parent_id": "file_context_menu", "type": "action","text_key": "file_menu_empty_clipboard"},
                {"id": "paste_metadata", "parent_id": "paste", "type": "action","text_key": "file_menu_paste_metadata"},
                {"id": "patch_metadata", "parent_id": "patch", "type": "action","text_key": "file_menu_patch_metadata"},
                {"id": "delete_metadata", "parent_id": "delete", "type": "action","text_key": "file_menu_delete_metadata"},
                {"id": "paste_by_filename", "parent_id": "paste", "type": "action","text_key": "file_menu_paste_by_filename"},
                {"id": "patch_by_filename", "parent_id": "patch", "type": "action","text_key": "file_menu_patch_by_filename"},
                {"id": "paste_geo_location_from_garmin", "active_switch": "garmin_integration_active","parent_id": "paste", "type": "action","text_key": "file_menu_paste_geo_location_from_garmin"},
                {"id": "patch_geo_location_from_garmin", "active_switch": "garmin_integration_active","parent_id": "patch", "type": "action","text_key": "file_menu_patch_geo_location_from_garmin"},
                {"id": "paste_original_filename_from_filename", "parent_id": "paste", "type": "action","text_key": "file_menu_paste_original_filename_from_filename"},
                {"id": "patch_original_filename_from_filename", "parent_id": "patch", "type": "action","text_key": "file_menu_patch_original_filename_from_filename"},
                {"id": "choose_tags_to_paste", "parent_id": "paste", "type": "text","text_key": "file_menu_chose_tags_to_paste"},
                {"id": "separator", "parent_id": "paste", "type": "separator"},
                {"id": "choose_tags_to_patch", "parent_id": "patch", "type": "text","text_key": "file_menu_chose_tags_to_patch"},
                {"id": "separator", "parent_id": "patch", "type": "separator"},
                {"id": "choose_tags_to_delete", "parent_id": "delete", "type": "text","text_key": "file_menu_chose_tags_to_delete"},
                {"id": "separator", "parent_id": "delete", "type": "separator"},
                {"id": "standardize_filenames", "parent_id": "file_management", "type": "action","text_key": "file_menu_standardize"},
                {"id": "fetch_originals", "parent_id": "file_management", "type": "action","text_key": "file_menu_fetch_originals"},
                {"id": "preserve_originals", "parent_id": "file_management", "type": "action","text_key": "file_menu_preserve_originals"},
                {"id": "delete_unused_originals", "parent_id": "file_management", "type": "action","text_key": "file_menu_delete_unused_originals"}
                ])
        if Settings.get("settings_labels") is None:
            Settings.set("settings_labels",{
                "application_language": {"text_key": "settings_labels_application_language"},
                "ui_mode": {"text_key": "settings_labels_ui_mode"}
                                                    })
        if Settings.get("settings_labels") is None:
            Settings.set("settings_labels",{
                "application_language": {"text_key": "settings_labels_application_language"}
                                                    })
        # A file padded with one of the paddings are still considered coming from same source-file during standardization of filenames.
        # Example: IMG_0920.jpg and IMG_0920-Enhanced-NR.jpg will end up being e.t 2024-F005-007.jpg and 2024-F005-007-Enhanced-NR.jpg.
        #          The original filename tag will, however, hold 2024-F005-007 in both cases.
        if Settings.get("file_name_padding") is None:
            Settings.set("file_name_padding", {
                "file_name_postfix": ["-Enhanced-NR",  # Added by lightroom AI-enhancement
                                      "-gigapixel-*x",  # Added by Topaz gigapixel
                                      "-SAI",  # Added by Topaz sharpen AI
                                      "-DeNoiseAI",  # Added by Topaz Denoise AI
                                      "-redigeret",
                                      # Added by Google Takeout for photos edited in Google Photos, if your account is set to danish language
                                      "-edited",
                                      # Added by Google Takeout for photos edited in Google Photos, if your account is set to english language
                                      " - Copy",  # Added by Windows when copying to place where target exist
                                      " - Copy (.)",  # "
                                      " - Copy (..)"  # "
                                      ],
                "file_name_prefix": ["copy_of_"]})

    @staticmethod
    def writeSettingsFile():
        file_settings = {}
        file_settings['version'] = Settings.get('version')
        file_settings['language'] = Settings.get('language')
        file_settings['ui_mode'] = Settings.get('ui_mode')
        file_settings['auto_consolidate_active'] = Settings.get('auto_consolidate_active')
        file_settings['lr_integration_active'] = Settings.get('lr_integration_active')
        file_settings['lr_db_path'] = Settings.get('lr_db_path')
        file_settings['garmin_integration_active'] = Settings.get('garmin_integration_active')
        settings_json_object = json.dumps(file_settings, indent=4)
        with open(Paths.get('settings'), "w") as outfile:
            outfile.write(settings_json_object)

    @staticmethod
    def _initialize():
        Settings._readSettingsFile()
        Settings._patchDefaultValues()
        Settings.set('old_version',Settings.get('version'))  # Old version from file. (might come in handy to know that version has changed)

#---------------------------Correct version here when deploying a new version of Memory Mate----------------------------
        Settings.set('version','4.0.0')
# ----------------------------------------------------------------------------------------------------------------------

        Settings.writeSettingsFile()

Settings._initialize()
