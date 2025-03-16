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

keys_texts = {
    "general_ok": {
        "DA": "OK",
        "EN": "OK",
        "FR": "OK",
        "ES": "OK",
        "DE": "OK"
    },
    "general_cancel": {
        "DA": "Annuller",
        "EN": "Cancel",
        "FR": "Annuler",
        "ES": "Cancelar",
        "DE": "Abbrechen"
    },
    "tag_label_rating": {
        "DA": "Bedømmelse",
	    "EN": "Rating",
	    "FR": "Évaluation",
	    "ES": "Clasificación",
	    "DE": "Bewertung"
    },
    "tag_label_title": {
        "DA": "Titel",
	    "EN": "Title",
	    "FR": "Titre",
	    "ES": "Título",
	    "DE": "Titel"
    },
    "tag_label_date": {
        "DA": "Dato/tid",
    	"EN": "Date/time",
	    "FR": "Date/heure",
    	"ES": "Fecha/hora",
	    "DE": "Datum/Uhrzeit"
    },
    "tag_label_date.local_date_time": {
        "DA": "Lokal dato/tid",
	    "EN": "Local date/time",
    	"FR": "Date/heure locale",
    	"ES": "Fecha/hora local",
    	"DE": "Lokales Datum/Uhrzeit"
    },
    "tag_label_date.utc_offset": {
        "DA": "Dato/tid utc-offset",
	    "EN": "Date/time UTC offset",
	    "FR": "Décalage UTC date/heure",
	    "ES": "Desplazamiento UTC fecha/hora",
	    "DE": "Datum/Uhrzeit UTC-Versatz"
    },
    "tag_label_date.latest_change": {
        "DA": "Seneste dato/tid ændring",
	    "EN": "Latest date/time change",
	    "FR": "Dernier changement de date/heure",
	    "ES": "Último cambio de fecha/hora",
	    "DE": "Letzte Änderung Datum/Uhrzeit"
    },
    "tag_label_description_only": {
        "DA": "Beskrivelse",
	    "EN": "Description",
	    "FR": "Description",
	    "ES": "Descripción",
	    "DE": "Beschreibung"
    },
    "tag_label_persons": {
        "DA": "Personer",
	    "EN": "People",
	    "FR": "Personnes",
	    "ES": "Personas",
	    "DE": "Personen"
    },
    "tag_label_photographer": {
        "DA": "Fotograf",
	    "EN": "Photographer",
	    "FR": "Photographe",
	    "ES": "Fotógrafo",
	    "DE": "Fotograf"
    },
    "tag_label_source": {
        "DA": "Oprindelse",
	    "EN": "Source",
	    "FR": "Source",
	    "ES": "Fuente",
	    "DE": "Quelle"
    },
    "tag_label_original_filename": {
        "DA": "Oprindeligt filnavn",
	    "EN": "Original Filename",
	    "FR": "Nom de fichier original",
	    "ES": "Nombre de archivo original",
	    "DE": "Originaldateiname"
    },
    "tag_label_geo_location": {
        "DA": "Geo-lokation",
	    "EN": "Geo-location",
	    "FR": "Géolocalisation",
	    "ES": "Geolocalización",
	    "DE": "Geostandort"
    },
    "tag_label_description": {
        "DA": "Fuld beskrivelse",
	    "EN": "Full Description",
	    "FR": "Description complète",
	    "ES": "Descripción completa",
	    "DE": "Vollständige Beschreibung"
    },
    "file_menu_file_management": {
        "DA": "Fil styring",
	    "EN": "File Management",
	    "FR": "Gestion des fichiers",
	    "ES": "Gestión de archivos",
	    "DE": "Dateiverwaltung"
    },
    "file_menu_consolidate": {
        "DA": "Konsolider metadata",
	    "EN": "Consolidate Metadata",
	    "FR": "Consolider les métadonnées",
	    "ES": "Consolidar metadatos",
	    "DE": "Metadaten konsolidieren"
    },
    "file_menu_copy": {
        "DA": "Kopier metadata",
	    "EN": "Copy Metadata",
	    "FR": "Copier les métadonnées",
	    "ES": "Copiar metadatos",
	    "DE": "Metadaten kopieren"
    },
    "file_menu_paste": {
        "DA": "Indsæt metadata",
	    "EN": "Paste Metadata",
	    "FR": "Coller les métadonnées",
	    "ES": "Pegar metadatos",
	    "DE": "Metadaten einfügen"
    },
    "file_menu_patch": {
        "DA": "Udfyld metadata",
	    "EN": "Patch Metadata",
	    "FR": "Corriger les métadonnées",
	    "ES": "Parchear metadatos",
	    "DE": "Metadaten patchen"
    },
    "file_menu_standardize": {
        "DA": "Standardiser filnavne",
	    "EN": "Standardize Filenames",
	    "FR": "Standardiser les noms de fichiers",
	    "ES": "Estandarizar nombres de archivos",
	    "DE": "Dateinamen standardisieren"
    },
    "file_menu_preserve_originals": {
        "DA": "Gem originaler",
	    "EN": "Preserve Originals",
	    "FR": "Préserver les originaux",
	    "ES": "Preservar originales",
	    "DE": "Originale bewahren"
    },
    "file_menu_delete_unused_originals": {
        "DA": "Slet ubrugte originaler",
	    "EN": "Delete unused Originals",
	    "FR": "Supprimer les originaux inutilisés",
	    "ES": "Eliminar originales no utilizados",
	    "DE": "Unbenutzte Originale löschen"
    },
    "file_menu_paste_by_filename": {
        "DA": "Indsæt metadata efter filnavn",
        "EN": "Paste Metadata by Filename",
        "FR": "Coller les métadonnées par nom de fichier",
        "ES": "Pegar metadatos por nombre de archivo",
        "DE": "Metadaten nach Dateiname einfügen"
    },
    "file_menu_patch_by_filename": {
        "DA": "Udfyld metadata efter filnavn",
        "EN": "Patch Metadata by Filename",
        "FR": "Corriger les métadonnées par nom de fichier",
        "ES": "Parchear metadatos por nombre de archivo",
        "DE": "Metadaten nach Dateiname korrigieren"
    },
    "file_menu_chose_tags_to_paste": {
        "DA": "Vælg hvad du vil overføre:",
        "EN": "Choose what to transfer:",
        "FR": "Choisissez quoi transférer :",
        "ES": "Elige qué transferir:",
        "DE": "Wählen Sie, was übertragen werden soll:"
    },
    "file_menu_fetch_originals": {
        "DA": "Hent originaler",
        "EN": "Fetch Originals",
        "FR": "Récupérer les originaux",
        "ES": "Obtener originales",
        "DE": "Originale abrufen"
    },
    "fetch_originals_dialog_label": {
        "DA": "Vælg mappe",
        "EN": "Select Folder",
        "FR": "Sélectionner un dossier",
        "ES": "Seleccionar carpeta",
        "DE": "Ordner auswählen"
    },
    "fetch_originals_dialog_placeholder_text": {
        "DA": "Klik for at vælge mappe",
        "EN": "Click to Select Folder",
        "FR": "Cliquez pour sélectionner un dossier",
        "ES": "Haga clic para seleccionar una carpeta",
        "DE": "Klicken Sie, um einen Ordner auszuwählen"
    },
    "fetch_originals_dialog_selector_title": {
        "DA": "Vælg hvor du vil hente originaler fra",
        "EN": "Choose from where you want to fetch Originals",
        "FR": "Choisissez d'où récupérer les originaux",
        "ES": "Elige de dónde obtener los originales",
        "DE": "Wählen Sie, woher Sie die Originale abrufen möchten"
    },
    "progress_bar_title_consolidate_metadata": {
        "DA": "Konsoliderer metadata",
        "EN": "Consolidating Metadata",
        "FR": "Consolidation des métadonnées",
        "ES": "Consolidando metadatos",
        "DE": "Metadaten konsolidieren"
    },
    "progress_bar_title_standardize_filenames": {
        "DA": "Standardiserer filnavne",
        "EN": "Standardizing Filenames",
        "FR": "Standardisation des noms de fichiers",
        "ES": "Estandarizando nombres de archivos",
        "DE": "Dateinamen standardisieren"
    },
    "progress_bar_title_paste_metadata": {
        "DA": "Indsætter metadata",
        "EN": "Pasting Metadata",
        "FR": "Collage des métadonnées",
        "ES": "Pegando metadatos",
        "DE": "Metadaten einfügen"
    },
    "progress_bar_title_preserve_originals": {
        "DA": "Gemmer originaler",
        "EN": "Preserving Originals",
        "FR": "Préservation des originaux",
        "ES": "Preservando originales",
        "DE": "Originale bewahren"
    },
    "progress_bar_title_delete_unused_originals": {
        "DA": "Sletter ubrugte originaler",
        "EN": "Deleting unused Originals",
        "FR": "Suppression des originaux inutilisés",
        "ES": "Eliminando originales no utilizados",
        "DE": "Unbenutzte Originale löschen"
    },
    "progress_bar_title_fetch_originals": {
        "DA": "Henter originaler",
        "EN": "Fetching Originals",
        "FR": "Récupération des originaux",
        "ES": "Obteniendo originales",
        "DE": "Originale abrufen"
    },
    "originals_folder_name": {
        "DA": "Originaler",
        "EN": "Originals",
        "FR": "Originaux",
        "ES": "Originales",
        "DE": "Originale"
    },
    "settings_window_title": {
        "DA": "Indstillinger",
        "EN": "Settings",
        "FR": "Paramètres",
        "ES": "Configuración",
        "DE": "Einstellungen"
    },
    "settings_labels_application_language": {
        "DA": "Sprog",
        "EN": "Language",
        "FR": "Langue",
        "ES": "Idioma",
        "DE": "Sprache"
    },
    "settings_labels_ui_mode": {
        "DA": "Applikations-udseende",
        "EN": "Application-mode",
        "FR": "Mode d'application",
        "ES": "Modo de aplicación",
        "DE": "Anwendungsmodus"
    },
    "settings_ui_mode.LIGHT": {
        "DA": "Lyst tema",
        "EN": "Light Theme",
        "FR": "Thème clair",
        "ES": "Tema claro",
        "DE": "Helles Thema"
    },
    "settings_ui_mode.DARK": {
        "DA": "Mørkt tema",
        "EN": "Dark Theme",
        "FR": "Thème sombre",
        "ES": "Tema oscuro",
        "DE": "Dunkles Thema"
    },
    "settings_lr_integration_headline": {
        "DA": "Lightroom-integration:",
        "EN": "Lightroom-integration:",
        "FR": "Intégration Lightroom:",
        "ES": "Integración con Lightroom:",
        "DE": "Lightroom-Integration:"
    },
    "settings_labels_lr_integration_active": {
        "DA": "Aktiver integration",
        "EN": "Activate Integration",
        "FR": "Activer l'intégration",
        "ES": "Activar integración",
        "DE": "Integration aktivieren"
    },
    "settings_lr_integration_disclaimer": {
        "DA": "Lightroom integrationen opdaterer filnavnene i dit Lightroom Classic katalog\nnår du bruger \"Standardiser filnavne\"-funktionen i Memory Mate.\nOpdateringen af filnavne sker vha. en uofficiel API. Adobe stiller ikke nogen API til rådighed for opdatering af filnavne i kataloget.\n\nVær derfor opmærksom på flg: \n  1. Efter hver opdatering af Lightroom skal du tjekke og opdatere filnavn på katalog-filen i feltet herunder\n  2. Der er en (omend lille) risiko for at Lightroom-databasen bliver korumperet, da opdatering sker med en uofficiel API",
        "EN": "The Lightroom Integration will update filenames in your Lightroom Classic Catalogue\nwhen you use the \"Standardise Filenames\"-functionality in Memory Mate.\nThe update of filenames is utilizing an unofficial API. Adobe does not offer an API for updating filenames in the catalogue.\n\nPlease be aware:\n  1. After each version-update of Lightroom you need to check and update the filename of the catalogue-file in the below field\n  2. There is a slight risk of corruption of your Lightroom catalogue as the update utilizes an unofficial API",
        "FR": "L'intégration de Lightroom mettra à jour les noms de fichiers dans votre catalogue Lightroom Classic\nlorsque vous utilisez la fonctionnalité \"Standardiser les noms de fichiers\" dans Memory Mate.\nLa mise à jour des noms de fichiers utilise une API non officielle. Adobe ne propose pas d'API pour mettre à jour les noms de fichiers dans le catalogue.\n\nVeuillez noter:\n  1. Après chaque mise à jour de Lightroom, vous devez vérifier et mettre à jour le nom du fichier de catalogue dans le champ ci-dessous\n  2. Il existe un léger risque de corruption de votre catalogue Lightroom, car la mise à jour utilise une API non officielle",
        "ES": "La integración con Lightroom actualizará los nombres de archivo en su catálogo de Lightroom Classic\ncuando utilice la función \"Estandarizar nombres de archivos\" en Memory Mate.\nLa actualización de nombres de archivo utiliza una API no oficial. Adobe no proporciona una API para actualizar nombres de archivo en el catálogo.\n\nTenga en cuenta:\n  1. Después de cada actualización de Lightroom, debe verificar y actualizar el nombre del archivo de catálogo en el campo a continuación\n  2. Existe un pequeño riesgo de corrupción de su catálogo de Lightroom, ya que la actualización utiliza una API no oficial",
        "DE": "Die Lightroom-Integration aktualisiert Dateinamen in Ihrem Lightroom Classic-Katalog,\nwenn Sie die Funktion \"Dateinamen standardisieren\" in Memory Mate verwenden.\nDie Aktualisierung der Dateinamen erfolgt über eine inoffizielle API. Adobe stellt keine API zur Aktualisierung von Dateinamen im Katalog bereit.\n\nBitte beachten Sie:\n  1. Nach jeder Version von Lightroom müssen Sie den Dateinamen der Katalogdatei im untenstehenden Feld überprüfen und aktualisieren\n  2. Es besteht ein geringes Risiko, dass Ihre Lightroom-Datenbank beschädigt wird, da die Aktualisierung über eine inoffizielle API erfolgt"
    },
    "settings_labels_lr_db_file": {
        "DA": "Lightroom katalog-fil",
        "EN": "Lightroom Catalog File",
        "FR": "Fichier de catalogue Lightroom",
        "ES": "Archivo de catálogo de Lightroom",
        "DE": "Lightroom-Katalogdatei"
    },
    "settings_lr_file_selector_placeholder_text": {
        "DA": "Klik for at vælge Lightroom katalog-fil (.lrcat)",
        "EN": "Click to select Lightroom Catalogue File (.lrcat)",
        "FR": "Cliquez pour sélectionner le fichier de catalogue Lightroom (.lrcat)",
        "ES": "Haga clic para seleccionar el archivo de catálogo de Lightroom (.lrcat)",
        "DE": "Klicken Sie, um die Lightroom-Katalogdatei (.lrcat) auszuwählen"
    },
    "settings_lr_file_selector_title": {
        "DA": "Peg på .lrcat filen",
        "EN": "Pick the .lrcat file",
        "FR": "Sélectionnez le fichier .lrcat",
        "ES": "Seleccione el archivo .lrcat",
        "DE": "Wählen Sie die .lrcat-Datei"
    },
    "preview_menu_open_in_default_program": {
        "DA": "Åben",
        "EN": "Open",
        "FR": "Ouvrir",
        "ES": "Abrir",
        "DE": "Öffnen"
    },
    "preview_menu_open_in_browser": {
        "DA": "Åben i webbrowser",
        "EN": "Open in Web Browser",
        "FR": "Ouvrir dans le navigateur Web",
        "ES": "Abrir en el navegador web",
        "DE": "Im Webbrowser öffnen"
    },
    "lr_filename_update_error_title": {
        "DA": "Filnavne kunne ikke opdateres i Lightroom",
        "EN": "Error updating Filenames in Lightroom",
        "FR": "Erreur lors de la mise à jour des noms de fichiers dans Lightroom",
        "ES": "Error al actualizar los nombres de archivo en Lightroom",
        "DE": "Fehler beim Aktualisieren der Dateinamen in Lightroom"
    },
    "lr_filename_update_error_msg": {
        "DA": "Filnavne kan ikke opdateres i Lightroom når programmet kører. Luk Lightroom og prøv igen, eller prøv senere",
        "EN": "Filenames in Lightroom can't be updated while the program is running. Close Lightroom and retry, or try later",
        "FR": "Les noms de fichiers dans Lightroom ne peuvent pas être mis à jour lorsque le programme est en cours d'exécution. Fermez Lightroom et réessayez, ou essayez plus tard",
        "ES": "Los nombres de archivo en Lightroom no se pueden actualizar mientras el programa se está ejecutando. Cierre Lightroom y vuelva a intentarlo más tarde",
        "DE": "Dateinamen in Lightroom können nicht aktualisiert werden, während das Programm läuft. Schließen Sie Lightroom und versuchen Sie es erneut oder später"
    },
    "lr_filename_update_retry": {
	    "DA": "Prøv igen",
     	"EN": "Retry",
     	"FR": "Réessayer",
     	"ES": "Reintentar",
     	"DE": "Erneut versuchen"
    },
    "lr_filename_update_later": {
	    "DA": "Senere",
     	"EN": "Later",
     	"FR": "Plus tard",
     	"ES": "Más tarde",
     	"DE": "Später"
    },
    "standardize_dialog_title": {
        "DA": "Standardiser filnavne",
        "EN": "Standardize Filenames",
        "FR": "Standardiser les noms de fichiers",
        "ES": "Estandarizar nombres de archivos",
        "DE": "Dateinamen standardisieren"
    },
    "standardize_dialog_prefix_label": {
        "DA": "Præfiks",
        "EN": "Prefix",
        "FR": "Préfixe",
        "ES": "Prefijo",
        "DE": "Präfix"
    },
    "standardize_dialog_number_pattern_label": {
        "DA": "Talmønster",
        "EN": "Number Pattern",
        "FR": "Modèle numérique",
        "ES": "Patrón numérico",
        "DE": "Zahlenmuster"
    },
    "standardize_dialog_postfix_label": {
        "DA": "Suffiks",
        "EN": "Postfix",
        "FR": "Suffixe",
        "ES": "Sufijo",
        "DE": "Suffix"
    }
}
