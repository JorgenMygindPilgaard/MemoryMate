from configuration.settings import Settings

class Texts:
    keys_texts = {}

    @staticmethod
    def get(key):
        text = ''
        texts = Texts.keys_texts.get(key)
        if texts:
            if Settings.get('language') is None:
                text = texts.get('EN')
            else:
                text = texts.get(Settings.get('language'))
        return text

    @staticmethod
    def _initialize():
        Texts.keys_texts = {
            "general_ok": {
                "DA": "OK",
                "EN": "OK",
                "FR": "OK",
                "ES": "OK",
                "DE": "OK",
                "FI": "OK",
                "SV": "OK",
                "IT": "OK"
            },
            "general_cancel": {
                "DA": "Annuller",
                "EN": "Cancel",
                "FR": "Annuler",
                "ES": "Cancelar",
                "DE": "Abbrechen",
                "FI": "Peruuta",
                "SV": "Avbryt",
                "IT": "Annulla"
            },
            "tag_label_rating": {
                "DA": "Bedømmelse",
                "EN": "Rating",
                "FR": "Évaluation",
                "ES": "Clasificación",
                "DE": "Bewertung",
                "FI": "Arvostelu",
                "SV": "Betyg",
                "IT": "Valutazione"
            },
            "tag_label_title": {
                "DA": "Titel",
                "EN": "Title",
                "FR": "Titre",
                "ES": "Título",
                "DE": "Titel",
                "FI": "Otsikko",
                "SV": "Titel",
                "IT": "Titolo"
            },
            "tag_label_date": {
                "DA": "Dato/tid",
                "EN": "Date/time",
                "FR": "Date/heure",
                "ES": "Fecha/hora",
                "DE": "Datum/Uhrzeit",
                "FI": "Päivämäärä/aika",
                "SV": "Datum/tid",
                "IT": "Data/ora"
            },
            "tag_label_date.local_date_time": {
                "DA": "Lokal dato/tid",
                "EN": "Local date/time",
                "FR": "Date/heure locale",
                "ES": "Fecha/hora local",
                "DE": "Lokales Datum/Uhrzeit",
                "FI": "Paikallinen päivämäärä/aika",
                "SV": "Lokalt datum/tid",
                "IT": "Data/ora locale"
            },
            "tag_label_date.utc_offset": {
                "DA": "Dato/tid utc-offset",
                "EN": "Date/time UTC offset",
                "FR": "Décalage UTC date/heure",
                "ES": "Desplazamiento UTC fecha/hora",
                "DE": "Datum/Uhrzeit UTC-Versatz",
                "FI": "Päivämäärä/aika UTC-siirtymä",
                "SV": "Datum/tid UTC-förskjutning",
                "IT": "Offset UTC data/ora"
            },
            "tag_label_date.latest_change": {
                "DA": "Seneste dato/tid ændring",
                "EN": "Latest date/time change",
                "FR": "Dernier changement de date/heure",
                "ES": "Último cambio de fecha/hora",
                "DE": "Letzte Änderung Datum/Uhrzeit",
                "FI": "Viimeisin päivämäärä/aika muutos",
                "SV": "Senaste datum/tid ändring",
                "IT": "Ultima modifica data/ora"
            },
            "tag_label_description_only": {
                "DA": "Beskrivelse",
                "EN": "Description",
                "FR": "Description",
                "ES": "Descripción",
                "DE": "Beschreibung",
                "FI": "Kuvaus",
                "SV": "Beskrivning",
                "IT": "Descrizione"
            },
            "tag_label_persons": {
                "DA": "Personer",
                "EN": "People",
                "FR": "Personnes",
                "ES": "Personas",
                "DE": "Personen",
                "FI": "Henkilöt",
                "SV": "Personer",
                "IT": "Persone"
            },
            "tag_label_photographer": {
                "DA": "Fotograf",
                "EN": "Photographer",
                "FR": "Photographe",
                "ES": "Fotógrafo",
                "DE": "Fotograf",
                "FI": "Valokuvaaja",
                "SV": "Fotograf",
                "IT": "Fotografo"
            },
            "tag_label_source": {
                "DA": "Oprindelse",
                "EN": "Source",
                "FR": "Source",
                "ES": "Fuente",
                "DE": "Quelle",
                "FI": "Lähde",
                "SV": "Källa",
                "IT": "Fonte"
            },
            "tag_label_original_filename": {
                "DA": "Oprindeligt filnavn",
                "EN": "Original Filename",
                "FR": "Nom de fichier original",
                "ES": "Nombre de archivo original",
                "DE": "Originaldateiname",
                "FI": "Alkuperäinen tiedostonimi",
                "SV": "Originalfilnamn",
                "IT": "Nome file originale"
            },
            "tag_label_geo_location": {
                "DA": "Geo-lokation",
                "EN": "Geo-location",
                "FR": "Géolocalisation",
                "ES": "Geolocalización",
                "DE": "Geostandort",
                "FI": "Maantieteellinen sijainti",
                "SV": "Geografisk plats",
                "IT": "Posizione geografica"
            },
            "tag_label_description": {
                "DA": "Fuld beskrivelse",
                "EN": "Full Description",
                "FR": "Description complète",
                "ES": "Descripción completa",
                "DE": "Vollständige Beschreibung",
                "FI": "Täysi kuvaus",
                "SV": "Fullständig beskrivning",
                "IT": "Descrizione completa"
            },
            "file_menu_file_management": {
                "DA": "Fil styring",
                "EN": "File Management",
                "FR": "Gestion des fichiers",
                "ES": "Gestión de archivos",
                "DE": "Dateiverwaltung",
                "FI": "Tiedostonhallinta",
                "SV": "Filhantering",
                "IT": "Gestione file"
            },
            "file_menu_consolidate": {
                "DA": "Konsolider metadata",
                "EN": "Consolidate Metadata",
                "FR": "Consolider les métadonnées",
                "ES": "Consolidar metadatos",
                "DE": "Metadaten konsolidieren",
                "FI": "Yhdistä metatiedot",
                "SV": "Konsolidera metadata",
                "IT": "Consolida metadati"
            },
            "file_menu_copy": {
                "DA": "Kopier metadata",
                "EN": "Copy Metadata",
                "FR": "Copier les métadonnées",
                "ES": "Copiar metadatos",
                "DE": "Metadaten kopieren",
                "FI": "Kopioi metatiedot",
                "SV": "Kopiera metadata",
                "IT": "Copia metadati"
            },
            "file_menu_paste": {
                "DA": "Indsæt metadata",
                "EN": "Paste Metadata",
                "FR": "Coller les métadonnées",
                "ES": "Pegar metadatos",
                "DE": "Metadaten einfügen",
                "FI": "Liitä metatiedot",
                "SV": "Klistra in metadata",
                "IT": "Incolla metadati"
            },
            "file_menu_patch": {
                "DA": "Udfyld metadata",
                "EN": "Patch Metadata",
                "FR": "Corriger les métadonnées",
                "ES": "Parchear metadatos",
                "DE": "Metadaten patchen",
                "FI": "Paikkaa metatiedot",
                "SV": "Patcha metadata",
                "IT": "Applica patch ai metadati"
            },
          "file_menu_standardize": {
            "DA": "Standardiser filnavne",
            "EN": "Standardize Filenames",
            "FR": "Standardiser les noms de fichiers",
            "ES": "Estandarizar nombres de archivos",
            "DE": "Dateinamen standardisieren",
            "FI": "Vakioi tiedostonimet",
            "SV": "Standardisera filnamn",
            "IT": "Standardizza i nomi dei file"
          },
          "file_menu_preserve_originals": {
            "DA": "Gem originaler",
            "EN": "Preserve Originals",
            "FR": "Préserver les originaux",
            "ES": "Preservar originales",
            "DE": "Originale bewahren",
            "FI": "Säilytä alkuperäiset",
            "SV": "Bevara original",
            "IT": "Conserva gli originali"
          },
          "file_menu_delete_unused_originals": {
            "DA": "Slet ubrugte originaler",
            "EN": "Delete unused Originals",
            "FR": "Supprimer les originaux inutilisés",
            "ES": "Eliminar originales no utilizados",
            "DE": "Unbenutzte Originale löschen",
            "FI": "Poista käyttämättömät alkuperäiset",
            "SV": "Ta bort oanvända original",
            "IT": "Elimina gli originali inutilizzati"
          },
          "file_menu_paste_by_filename": {
            "DA": "Indsæt metadata efter filnavn",
            "EN": "Paste Metadata by Filename",
            "FR": "Coller les métadonnées par nom de fichier",
            "ES": "Pegar metadatos por nombre de archivo",
            "DE": "Metadaten nach Dateiname einfügen",
            "FI": "Liitä metatiedot tiedostonimen perusteella",
            "SV": "Klistra in metadata efter filnamn",
            "IT": "Incolla i metadati per nome file"
          },
          "file_menu_patch_by_filename": {
            "DA": "Udfyld metadata efter filnavn",
            "EN": "Patch Metadata by Filename",
            "FR": "Corriger les métadonnées par nom de fichier",
            "ES": "Parchear metadatos por nombre de archivo",
            "DE": "Metadaten nach Dateiname korrigieren",
            "FI": "Paikkaa metatiedot tiedostonimen perusteella",
            "SV": "Korrigera metadata efter filnamn",
            "IT": "Correggi i metadati per nome file"
          },
          "file_menu_chose_tags_to_paste": {
            "DA": "Vælg hvad du vil overføre:",
            "EN": "Choose what to transfer:",
            "FR": "Choisissez quoi transférer :",
            "ES": "Elige qué transferir:",
            "DE": "Wählen Sie, was übertragen werden soll:",
            "FI": "Valitse mitä siirretään:",
            "SV": "Välj vad du vill överföra:",
            "IT": "Scegli cosa trasferire:"
          },
          "file_menu_fetch_originals": {
            "DA": "Hent originaler",
            "EN": "Fetch Originals",
            "FR": "Récupérer les originaux",
            "ES": "Obtener originales",
            "DE": "Originale abrufen",
            "FI": "Hae alkuperäiset",
            "SV": "Hämta original",
            "IT": "Recupera gli originali"
          },
          "fetch_originals_dialog_label": {
            "DA": "Vælg mappe",
            "EN": "Select Folder",
            "FR": "Sélectionner un dossier",
            "ES": "Seleccionar carpeta",
            "DE": "Ordner auswählen",
            "FI": "Valitse kansio",
            "SV": "Välj mapp",
            "IT": "Seleziona cartella"
          },
          "fetch_originals_dialog_placeholder_text": {
            "DA": "Klik for at vælge mappe",
            "EN": "Click to Select Folder",
            "FR": "Cliquez pour sélectionner un dossier",
            "ES": "Haga clic para seleccionar una carpeta",
            "DE": "Klicken Sie, um einen Ordner auszuwählen",
            "FI": "Napsauta valitaksesi kansion",
            "SV": "Klicka för att välja mapp",
            "IT": "Clicca per selezionare la cartella"
          },
          "fetch_originals_dialog_selector_title": {
            "DA": "Vælg hvor du vil hente originaler fra",
            "EN": "Choose from where you want to fetch Originals",
            "FR": "Choisissez d'où récupérer les originaux",
            "ES": "Elige de dónde obtener los originales",
            "DE": "Wählen Sie, woher Sie die Originale abrufen möchten",
            "FI": "Valitse mistä haluat hakea alkuperäiset",
            "SV": "Välj varifrån du vill hämta original",
            "IT": "Scegli da dove vuoi recuperare gli originali"
          },
          "progress_bar_title_consolidate_metadata": {
            "DA": "Konsoliderer metadata",
            "EN": "Consolidating Metadata",
            "FR": "Consolidation des métadonnées",
            "ES": "Consolidando metadatos",
            "DE": "Metadaten konsolidieren",
            "FI": "Yhdistetään metatiedot",
            "SV": "Konsoliderar metadata",
            "IT": "Consolidamento dei metadati"
          },
          "progress_bar_title_standardize_filenames": {
            "DA": "Standardiserer filnavne",
            "EN": "Standardizing Filenames",
            "FR": "Standardisation des noms de fichiers",
            "ES": "Estandarizando nombres de archivos",
            "DE": "Dateinamen standardisieren",
            "FI": "Vakioidaan tiedostonimet",
            "SV": "Standardiserar filnamn",
            "IT": "Standardizzazione dei nomi dei file"
          },
          "progress_bar_title_paste_metadata": {
            "DA": "Indsætter metadata",
            "EN": "Pasting Metadata",
            "FR": "Collage des métadonnées",
            "ES": "Pegando metadatos",
            "DE": "Metadaten einfügen",
            "FI": "Liitetään metatiedot",
            "SV": "Klistrar in metadata",
            "IT": "Incollando i metadati"
          },
          "progress_bar_title_preserve_originals": {
            "DA": "Gemmer originaler",
            "EN": "Preserving Originals",
            "FR": "Préservation des originaux",
            "ES": "Preservando originales",
            "DE": "Originale bewahren",
            "FI": "Tallennetaan alkuperäiset",
            "SV": "Bevarar original",
            "IT": "Conservando gli originali"
          },
          "progress_bar_title_delete_unused_originals": {
            "DA": "Sletter ubrugte originaler",
            "EN": "Deleting unused Originals",
            "FR": "Suppression des originaux inutilisés",
            "ES": "Eliminando originales no utilizados",
            "DE": "Unbenutzte Originale löschen",
            "FI": "Poistetaan käyttämättömät alkuperäiset",
            "SV": "Tar bort oanvända original",
            "IT": "Eliminazione degli originali inutilizzati"
          },
          "progress_bar_title_fetch_originals": {
            "DA": "Henter originaler",
            "EN": "Fetching Originals",
            "FR": "Récupération des originaux",
            "ES": "Obteniendo originales",
            "DE": "Originale abrufen",
            "FI": "Haetaan alkuperäiset",
            "SV": "Hämtar original",
            "IT": "Recupero degli originali"
          },
          "originals_folder_name": {
            "DA": "Originaler",
            "EN": "Originals",
            "FR": "Originaux",
            "ES": "Originales",
            "DE": "Originale",
            "FI": "Alkuperäiset",
            "SV": "Original",
            "IT": "Originali"
          },
          "settings_window_title": {
            "DA": "Indstillinger",
            "EN": "Settings",
            "FR": "Paramètres",
            "ES": "Configuración",
            "DE": "Einstellungen",
            "FI": "Asetukset",
            "SV": "Inställningar",
            "IT": "Impostazioni"
          },
          "settings_labels_application_language": {
            "DA": "Sprog",
            "EN": "Language",
            "FR": "Langue",
            "ES": "Idioma",
            "DE": "Sprache",
            "FI": "Kieli",
            "SV": "Språk",
            "IT": "Lingua"
          },
          "settings_labels_ui_mode": {
            "DA": "Applikations-udseende",
            "EN": "Application-mode",
            "FR": "Mode d'application",
            "ES": "Modo de aplicación",
            "DE": "Anwendungsmodus",
            "FI": "Sovellustila",
            "SV": "Applikationsläge",
            "IT": "Modalità applicazione"
          },
          "settings_ui_mode.LIGHT": {
            "DA": "Lyst tema",
            "EN": "Light Theme",
            "FR": "Thème clair",
            "ES": "Tema claro",
            "DE": "Helles Thema",
            "FI": "Vaalea teema",
            "SV": "Ljust tema",
            "IT": "Tema chiaro"
          },
          "settings_ui_mode.DARK": {
            "DA": "Mørkt tema",
            "EN": "Dark Theme",
            "FR": "Thème sombre",
            "ES": "Tema oscuro",
            "DE": "Dunkles Thema",
            "FI": "Tumma teema",
            "SV": "Mörkt tema",
            "IT": "Tema scuro"
          },
          "settings_lr_integration_headline": {
            "DA": "Lightroom-integration:",
            "EN": "Lightroom-integration:",
            "FR": "Intégration Lightroom:",
            "ES": "Integración con Lightroom:",
            "DE": "Lightroom-Integration:",
            "FI": "Lightroom-integraatio:",
            "SV": "Lightroom-integration:",
            "IT": "Integrazione Lightroom:"
          },
          "settings_labels_lr_integration_active": {
            "DA": "Aktiver integration",
            "EN": "Activate Integration",
            "FR": "Activer l'intégration",
            "ES": "Activar integración",
            "DE": "Integration aktivieren",
            "FI": "Aktivoi integraatio",
            "SV": "Aktivera integration",
            "IT": "Attiva integrazione"
          },
          "settings_lr_integration_disclaimer": {
            "DA": "Lightroom integrationen opdaterer filnavnene i dit Lightroom Classic katalog\nnår du bruger \"Standardiser filnavne\"-funktionen i Memory Mate.\nOpdateringen af filnavne sker vha. en uofficiel API. Adobe stiller ikke nogen API til rådighed for opdatering af filnavne i kataloget.\n\nVær derfor opmærksom på flg: \n  1. Efter hver opdatering af Lightroom skal du tjekke og opdatere filnavn på katalog-filen i feltet herunder\n  2. Der er en (omend lille) risiko for at Lightroom-databasen bliver korumperet, da opdatering sker med en uofficiel API",
            "EN": "The Lightroom Integration will update filenames in your Lightroom Classic Catalogue\nwhen you use the \"Standardise Filenames\"-functionality in Memory Mate.\nThe update of filenames is utilizing an unofficial API. Adobe does not offer an API for updating filenames in the catalogue.\n\nPlease be aware:\n  1. After each version-update of Lightroom you need to check and update the filename of the catalogue-file in the below field\n  2. There is a slight risk of corruption of your Lightroom catalogue as the update utilizes an unofficial API",
            "FR": "L'intégration de Lightroom mettra à jour les noms de fichiers dans votre catalogue Lightroom Classic\nlorsque vous utilisez la fonctionnalité \"Standardiser les noms de fichiers\" dans Memory Mate.\nLa mise à jour des noms de fichiers utilise une API non officielle. Adobe ne propose pas d'API pour mettre à jour les noms de fichiers dans le catalogue.\n\nVeuillez noter:\n  1. Après chaque mise à jour de Lightroom, vous devez vérifier et mettre à jour le nom du fichier de catalogue dans le champ ci-dessous\n  2. Il existe un léger risque de corruption de votre catalogue Lightroom, car la mise à jour utilise une API non officielle",
            "ES": "La integración con Lightroom actualizará los nombres de archivo en su catálogo de Lightroom Classic\ncuando utilice la función \"Estandarizar nombres de archivos\" en Memory Mate.\nLa actualización de nombres de archivo utiliza una API no oficial. Adobe no proporciona una API para actualizar nombres de archivo en el catálogo.\n\nTenga en cuenta:\n  1. Después de cada actualización de Lightroom, debe verificar y actualizar el nombre del archivo de catálogo en el campo a continuación\n  2. Existe un pequeño riesgo de corrupción de su catálogo de Lightroom, ya que la actualización utiliza una API no oficial",
            "DE": "Die Lightroom-Integration aktualisiert Dateinamen in Ihrem Lightroom Classic-Katalog,\nwenn Sie die Funktion \"Dateinamen standardisieren\" in Memory Mate verwenden.\nDie Aktualisierung der Dateinamen erfolgt über eine inoffizielle API. Adobe stellt keine API zur Aktualisierung von Dateinamen im Katalog bereit.\n\nBitte beachten Sie:\n  1. Nach jeder Version von Lightroom müssen Sie den Dateinamen der Katalogdatei im untenstehenden Feld überprüfen und aktualisieren\n  2. Es besteht ein geringes Risiko, dass Ihre Lightroom-Datenbank beschädigt wird, da die Aktualisierung über eine inoffizielle API erfolgt",
            "FI": "Lightroom-integraatio päivittää tiedostonimet Lightroom Classic -luettelossasi,\nkun käytät Memory Maten \"Vakiinnuta tiedostonimet\" -toimintoa.\nTiedostonimien päivitys tapahtuu epävirallisen API:n avulla. Adobe ei tarjoa API:a tiedostonimien päivittämiseen luettelossa.\n\nHuomioi seuraavat:\n  1. Jokaisen Lightroom-päivityksen jälkeen sinun on tarkistettava ja päivitettävä luettelotiedoston nimi alla olevassa kentässä\n  2. Lightroom-tietokannan vioittumisriski on pieni, koska päivitys tapahtuu epävirallisen API:n avulla",
            "SV": "Lightroom-integrationen uppdaterar filnamnen i din Lightroom Classic-katalog\nnär du använder funktionen \"Standardisera filnamn\" i Memory Mate.\nUppdateringen av filnamnen sker med hjälp av ett inofficiellt API. Adobe erbjuder inte ett API för att uppdatera filnamn i katalogen.\n\nVar vänlig uppmärksamma:\n  1. Efter varje versionuppdatering av Lightroom måste du kontrollera och uppdatera filnamnet på katalogfilen i fältet nedan\n  2. Det finns en liten risk för korruption av din Lightroom-katalog eftersom uppdateringen använder ett inofficiellt API",
            "IT": "L'integrazione con Lightroom aggiornerà i nomi dei file nel tuo catalogo Lightroom Classic\nquando utilizzi la funzione \"Standardizza nomi file\" in Memory Mate.\nL'aggiornamento dei nomi file utilizza un'API non ufficiale. Adobe non offre un'API per aggiornare i nomi file nel catalogo.\n\nNota bene:\n  1. Dopo ogni aggiornamento di versione di Lightroom, è necessario controllare e aggiornare il nome del file di catalogo nel campo sottostante\n  2. Esiste un leggero rischio di danneggiamento del catalogo Lightroom poiché l'aggiornamento utilizza un'API non ufficiale"
          },
          "settings_labels_lr_db_file": {
            "DA": "Lightroom katalog-fil",
            "EN": "Lightroom Catalog File",
            "FR": "Fichier de catalogue Lightroom",
            "ES": "Archivo de catálogo de Lightroom",
            "DE": "Lightroom-Katalogdatei",
            "SV": "Lightroom-katalogfil",
            "FI": "Lightroom-katalogitiedosto",
            "IT": "File catalogo di Lightroom"
          },
          "settings_lr_file_selector_placeholder_text": {
            "DA": "Klik for at vælge Lightroom katalog-fil (.lrcat)",
            "EN": "Click to select Lightroom Catalogue File (.lrcat)",
            "FR": "Cliquez pour sélectionner le fichier de catalogue Lightroom (.lrcat)",
            "ES": "Haga clic para seleccionar el archivo de catálogo de Lightroom (.lrcat)",
            "DE": "Klicken Sie, um die Lightroom-Katalogdatei (.lrcat) auszuwählen",
            "SV": "Klicka för att välja Lightroom-katalogfil (.lrcat)",
            "FI": "Napsauta valitaksesi Lightroom-katalogitiedoston (.lrcat)",
            "IT": "Fai clic per selezionare il file catalogo di Lightroom (.lrcat)"
          },
          "settings_lr_file_selector_title": {
            "DA": "Peg på .lrcat filen",
            "EN": "Pick the .lrcat file",
            "FR": "Sélectionnez le fichier .lrcat",
            "ES": "Seleccione el archivo .lrcat",
            "DE": "Wählen Sie die .lrcat-Datei",
            "SV": "Välj .lrcat-filen",
            "FI": "Valitse .lrcat-tiedosto",
            "IT": "Seleziona il file .lrcat"
          },
          "preview_menu_open_in_default_program": {
            "DA": "Åben",
            "EN": "Open",
            "FR": "Ouvrir",
            "ES": "Abrir",
            "DE": "Öffnen",
            "SV": "Öppna",
            "FI": "Avaa",
            "IT": "Apri"
          },
          "preview_menu_open_in_browser": {
            "DA": "Åben i webbrowser",
            "EN": "Open in Web Browser",
            "FR": "Ouvrir dans le navigateur Web",
            "ES": "Abrir en el navegador web",
            "DE": "Im Webbrowser öffnen",
            "SV": "Öppna i webbläsare",
            "FI": "Avaa verkkoselaimessa",
            "IT": "Apri nel browser web"
          },
          "lr_filename_update_error_title": {
            "DA": "Filnavne kunne ikke opdateres i Lightroom",
            "EN": "Error updating Filenames in Lightroom",
            "FR": "Erreur lors de la mise à jour des noms de fichiers dans Lightroom",
            "ES": "Error al actualizar los nombres de archivo en Lightroom",
            "DE": "Fehler beim Aktualisieren der Dateinamen in Lightroom",
            "SV": "Fel vid uppdatering av filnamn i Lightroom",
            "FI": "Virhe päivitettäessä tiedostonimiä Lightroomissa",
            "IT": "Errore durante l'aggiornamento dei nomi file in Lightroom"
          },
          "lr_filename_update_error_msg": {
            "DA": "Filnavne kan ikke opdateres i Lightroom når programmet kører. Luk Lightroom og prøv igen, eller prøv senere",
            "EN": "Filenames in Lightroom can't be updated while the program is running. Close Lightroom and retry, or try later",
            "FR": "Les noms de fichiers dans Lightroom ne peuvent pas être mis à jour lorsque le programme est en cours d'exécution. Fermez Lightroom et réessayez, ou essayez plus tard",
            "ES": "Los nombres de archivo en Lightroom no se pueden actualizar mientras el programa se está ejecutando. Cierre Lightroom y vuelva a intentarlo más tarde",
            "DE": "Dateinamen in Lightroom können nicht aktualisiert werden, während das Programm läuft. Schließen Sie Lightroom und versuchen Sie es erneut oder später",
            "SV": "Filnamn i Lightroom kan inte uppdateras medan programmet körs. Stäng Lightroom och försök igen, eller försök senare",
            "FI": "Tiedostonimiä ei voi päivittää Lightroomissa ohjelman käydessä. Sulje Lightroom ja yritä uudelleen tai myöhemmin",
            "IT": "I nomi dei file in Lightroom non possono essere aggiornati mentre il programma è in esecuzione. Chiudi Lightroom e riprova, oppure riprova più tardi"
          },

          "lr_filename_update_retry": {
            "DA": "Prøv igen",
            "EN": "Retry",
            "FR": "Réessayer",
            "ES": "Reintentar",
            "DE": "Erneut versuchen",
            "FI": "Yritä uudelleen",
            "SV": "Försök igen",
            "IT": "Riprova"
          },
          "lr_filename_update_later": {
            "DA": "Senere",
            "EN": "Later",
            "FR": "Plus tard",
            "ES": "Más tarde",
            "DE": "Später",
            "FI": "Myöhemmin",
            "SV": "Senare",
            "IT": "Più tardi"
          },
          "standardize_dialog_title": {
            "DA": "Standardiser filnavne",
            "EN": "Standardize Filenames",
            "FR": "Standardiser les noms de fichiers",
            "ES": "Estandarizar nombres de archivos",
            "DE": "Dateinamen standardisieren",
            "FI": "Vakioi tiedostonimet",
            "SV": "Standardisera filnamn",
            "IT": "Standardizza nomi file"
          },
          "standardize_dialog_prefix_label": {
            "DA": "Præfiks",
            "EN": "Prefix",
            "FR": "Préfixe",
            "ES": "Prefijo",
            "DE": "Präfix",
            "FI": "Etuliite",
            "SV": "Prefix",
            "IT": "Prefisso"
          },
          "standardize_dialog_number_pattern_label": {
            "DA": "Talmønster",
            "EN": "Number Pattern",
            "FR": "Modèle numérique",
            "ES": "Patrón numérico",
            "DE": "Zahlenmuster",
            "FI": "Numeromalli",
            "SV": "Nummermönster",
            "IT": "Schema numerico"
          },
          "standardize_dialog_postfix_label": {
            "DA": "Suffiks",
            "EN": "Postfix",
            "FR": "Suffixe",
            "ES": "Sufijo",
            "DE": "Suffix",
            "FI": "Jälkiliite",
            "SV": "Suffix",
            "IT": "Suffisso"
          }
        }

Texts._initialize()
