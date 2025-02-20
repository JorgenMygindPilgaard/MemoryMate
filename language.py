import settings


def getText(key):
    text = ''
    texts = keys_texts.get(key)
    if texts:
        if settings.language is None:
            text = texts.get('EN')
        else:
            text = texts.get(settings.language)
    return text

keys_texts = {"tag_label_rating":
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
              "settings_labels_ui_mode":
                {"DA": "Applikations-udseende",
                 "EN": "Application-mode"},
              "settings_ui_mode.LIGHT":
                {"DA": "Lyst tema",
                 "EN": "Light Theme"},
              "settings_ui_mode.DARK":
                {"DA": "Mørkt tema",
                 "EN": "Dark Theme"},
              "settings_lr_integration_headline":
                  {"DA": "Lightroom-integration:",
                   "EN": "Lightroom-integration:"},
              "settings_labels_lr_integration_active":
                  {"DA": "Aktiver integration",
                   "EN": "Activate Integration"},
              "settings_lr_integration_disclaimer":
                  {"DA": "Lightroom integrationen opdaterer filnavnene i dit Lightroom Classic katalog\nnår du bruger \"Standardiser filnavne\"-funktionen i Memory Mate.\nOpdateringen af filnavne sker vha. en uofficiel API. Adobe stiller ikke nogen API til rådighed for opdatering af filnavne i kataloget.\n\nVær derfor opmærksom på flg: \n  1. Efter hver opdatering af Lightroom skal du tjekke og opdatere filnavn på katalog-filen i feltet herunder\n  2. Der er en (omend lille) risiko for at Lightroom-databasen bliver korumperet, da opdatering sker med en uofficiel API",
                   "EN": "The Lightroom Integration will update filenames in your Lightroom Classic Catalouge\n when you use the \"Standardise Filenames\"-functionality in Memory Mate.\nThe update of filenames is utilizing an unofficial API. Adobe does not offer an API for updating filenames in the catalouge.\n\nPlease be aware: \n  1. After each version-update of Lightroom you need to check and updatethe filename of the catalouge-file in the below field\n  2. There is a slight risk of corruption of your Lightroom catalouge as the update utilizes an unofficial API"},
              "settings_labels_lr_db_file":
                  {"DA": "Lightroom katalog-fil",
                   "EN": "Lightroom Catalog File"},
              "settings_lr_file_selector_placeholder_text":
                  {"DA": "Klik for at vælge Lightroom katalog-fil (.lrcat)",
                   "EN": "Click to select Lightroom Catalouge File (.lrcat)"},
              "settings_lr_file_selector_title":
                  {"DA": "Peg på .lrcat filen",
                   "EN": "Pick the .lrcat file"},
              "preview_menu_open_in_default_program":
                {"DA": "Åben",
                 "EN": "Open"},
              "preview_menu_open_in_browser":
                {"DA": "Åben i webbrowser",
                 "EN": "Open in Web Browser"},
              "lr_filename_update_error_title":
                  {"DA": "Filnavne kunne ikke opdateres i Lightroom",
                 "EN": "Error updating Filenames in Lightroom"},
              "lr_filename_update_error_msg":
                  {"DA": "Filnavne kan ikke opdateres i Lightroom når programmet kører. Luk Lightroom og prøv igen, eller prøv senere",
                   "EN": "Filenames in Lightroom can't be updated while program is running. Close Lightroom and retry, or try later"},
              "lr_filename_update_retry":
                  {"DA": "Prøv igen",
                   "EN": "Retry"},
              "lr_filename_update_later":
                  {"DA": "Senere",
                   "EN": "Later"},
              }
