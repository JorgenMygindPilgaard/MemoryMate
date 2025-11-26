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
            "login_window_title": {
                "DA": "Log ind",
                "EN": "Login",
                "FR": "Connexion",
                "ES": "Iniciar sesión",
                "DE": "Anmelden",
                "FI": "Kirjaudu sisään",
                "SV": "Logga in",
                "IT": "Accesso"
            },
            "login_window_user_label": {
                "DA": "Bruger",
                "EN": "User",
                "FR": "Utilisateur",
                "ES": "Usuario",
                "DE": "Benutzer",
                "FI": "Käyttäjä",
                "SV": "Användare",
                "IT": "Utente"
            },
            "login_window_password_label": {
                "DA": "Adgangskode",
                "EN": "Password",
                "FR": "Mot de passe",
                "ES": "Contraseña",
                "DE": "Passwort",
                "FI": "Salasana",
                "SV": "Lösenord",
                "IT": "Password"
            },
            "login_window_mfa_code_label": {
                "DA": "MFA-kode",
                "EN": "MFA-code",
                "FR": "Code MFA",
                "ES": "Código MFA",
                "DE": "MFA-Code",
                "FI": "MFA-koodi",
                "SV": "MFA-kod",
                "IT": "Codice MFA"
            },
            "login_window_message_user_missing": {
                "DA": "Indtast Bruger",
                "EN": "Enter user",
                "FR": "Saisir l’utilisateur",
                "ES": "Ingrese usuario",
                "DE": "Benutzer eingeben",
                "FI": "Syötä käyttäjä",
                "SV": "Ange användare",
                "IT": "Inserisci utente"
            },
            "login_window_message_password_missing": {
                "DA": "Indtast adgangskode",
                "EN": "Enter password",
                "FR": "Saisir le mot de passe",
                "ES": "Ingrese contraseña",
                "DE": "Passwort eingeben",
                "FI": "Syötä salasana",
                "SV": "Ange lösenord",
                "IT": "Inserisci password"
            },
            "login_window_message_mfa_code_missing": {
                "DA": "Indtast MFA-kode",
                "EN": "Enter MFA code",
                "FR": "Saisir le code MFA",
                "ES": "Ingrese código MFA",
                "DE": "MFA-Code eingeben",
                "FI": "Syötä MFA-koodi",
                "SV": "Ange MFA-kod",
                "IT": "Inserisci codice MFA"
            },
            "login_window_message_user_or_password_wrong": {
                "DA": "Bruger eller adgangskode er forkert. Prøv igen",
                "EN": "User or password incorrect. Please try again",
                "FR": "Nom d’utilisateur ou mot de passe incorrect. Veuillez réessayer",
                "ES": "Usuario o contraseña incorrectos. Inténtalo de nuevo",
                "DE": "Benutzer oder Passwort ist falsch. Bitte erneut versuchen",
                "FI": "Käyttäjätunnus tai salasana on virheellinen. Yritä uudelleen",
                "SV": "Användarnamn eller lösenord är felaktigt. Försök igen",
                "IT": "Nome utente o password errati. Riprova"
            },
            "login_window_message_too_many_attempts": {
                "DA": "For mange forsøg. Prøv igen om 30 minutter",
                "EN": "Too many attempts. Try again in 30 minutes",
                "FR": "Trop de tentatives. Réessayez dans 30 minutes",
                "ES": "Demasiados intentos. Inténtalo de nuevo en 30 minutos",
                "DE": "Zu viele Versuche. Bitte versuchen Sie es in 30 Minuten erneut",
                "FI": "Liian monta yritystä. Yritä uudelleen 30 minuutin kuluttua",
                "SV": "För många försök. Försök igen om 30 minuter",
                "IT": "Troppi tentativi. Riprova tra 30 minuti"
            },
            "login_window_message_mfa_code_wrong": {
                "DA": "Forkert MFA-kode. Prøv igen",
                "EN": "MFA code is incorrect. Please try again",
                "FR": "Le code MFA est incorrect. Veuillez réessayer",
                "ES": "El código MFA es incorrecto. Inténtalo de nuevo",
                "DE": "Der MFA-Code ist falsch. Bitte versuchen Sie es erneut",
                "FI": "MFA-koodi on virheellinen. Yritä uudelleen",
                "SV": "MFA-koden är felaktig. Försök igen",
                "IT": "Il codice MFA non è corretto. Riprova"
            },

            "login_window_message_mfa_authentication_failed": {
                "DA": "Multifaktor-godkendelse (MFA) mislykkedes",
                "EN": "Multi-factor authentication (MFA) failed",
                "FR": "Échec de l’authentification multifacteur (MFA)",
                "ES": "Error en la autenticación multifactor (MFA)",
                "DE": "Mehrfaktor-Authentifizierung (MFA) fehlgeschlagen",
                "FI": "Monivaiheinen todennus (MFA) epäonnistui",
                "SV": "Multifaktorautentisering (MFA) misslyckades",
                "IT": "Autenticazione a più fattori (MFA) non riuscita"
            },

            "login_window_message_connection_error": {
                "DA": "Forbindelsesfejl. Kontroller din internetforbindelse, og prøv igen",
                "EN": "Connection error. Please check your internet connection and try again",
                "FR": "Erreur de connexion. Veuillez vérifier votre connexion Internet et réessayer",
                "ES": "Error de conexión. Por favor, compruebe su conexión a Internet y vuelva a intentarlo",
                "DE": "Verbindungsfehler. Bitte überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut",
                "FI": "Yhteysvirhe. Tarkista internetyhteytesi ja yritä uudelleen",
                "SV": "Anslutningsfel. Kontrollera din internetanslutning och försök igen",
                "IT": "Errore di connessione. Controlla la tua connessione Internet e riprova"
            },
            "garmin_login_window_title": {
                "DA": "Garmin-login",
                "EN": "Garmin Login",
                "FR": "Connexion Garmin",
                "ES": "Inicio de sesión Garmin",
                "DE": "Garmin-Anmeldung",
                "FI": "Garmin-kirjautuminen",
                "SV": "Garmin-inloggning",
                "IT": "Accesso Garmin"
            },
            "garmin_status_monitor_tool_tip_running": {
                "DA": "Logget ind som {user}. \nSynkroniserer i øjeblikket. \nHøjreklik for valgmuligheder",
                "EN": "Logged in as {user}. \nCurrently synchronizing. \nRight-click for options",
                "FR": "Connecté en tant que {user}. \nSynchronisation en cours. \nCliquez avec le bouton droit pour les options",
                "ES": "Conectado como {user}. \nSincronizando actualmente. \nHaz clic derecho para ver las opciones",
                "DE": "Angemeldet als {user}. \nWird derzeit synchronisiert. \nRechtsklick für Optionen",
                "FI": "Kirjautunut käyttäjänä {user}. \nSynkronoidaan parhaillaan. \nNapsauta hiiren oikealla painikkeella nähdäksesi vaihtoehdot",
                "SV": "Inloggad som {user}. \nSynkroniserar just nu. \nHögerklicka för alternativ",
                "IT": "Accesso effettuato come {user}. \nSincronizzazione in corso. \nFai clic con il tasto destro per le opzioni"
            },
            "garmin_status_monitor_tool_tip_done": {
                "DA": "Logget ind som {user}. \nSynkronisering fuldført. \nHøjreklik for valgmuligheder",
                "EN": "Logged in as {user}. \nSynchronization done. \nRight-click for options",
                "FR": "Connecté en tant que {user}. \nSynchronisation terminée. \nCliquez avec le bouton droit pour les options",
                "ES": "Conectado como {user}. \nSincronización completada. \nHaz clic derecho para ver las opciones",
                "DE": "Angemeldet als {user}. \nSynchronisierung abgeschlossen. \nRechtsklick für Optionen",
                "FI": "Kirjautunut käyttäjänä {user}. \nSynkronointi valmis. \nNapsauta hiiren oikealla painikkeella nähdäksesi vaihtoehdot",
                "SV": "Inloggad som {user}. \nSynkronisering klar. \nHögerklicka för alternativ",
                "IT": "Accesso effettuato come {user}. \nSincronizzazione completata. \nFai clic con il tasto destro per le opzioni"
            },
            "garmin_status_monitor_tool_tip_not_logged_in": {
                "DA": "Ikke logget ind. \nHøjreklik for valgmuligheder",
                "EN": "Not logged in. \nRight-click for options",
                "FR": "Non connecté. \nCliquez avec le bouton droit pour les options",
                "ES": "No has iniciado sesión. \nHaz clic derecho para ver las opciones",
                "DE": "Nicht angemeldet. \nRechtsklick für Optionen",
                "FI": "Ei kirjautunut sisään. \nNapsauta hiiren oikealla painikkeella nähdäksesi vaihtoehdot",
                "SV": "Inte inloggad. \nHögerklicka för alternativ",
                "IT": "Non connesso. \nFai clic con il tasto destro per le opzioni"
            },
            "garmin_status_monitor_tool_tip_no_internet": {
                "DA": "Ingen internetforbindelse. Kontroller din forbindelse. \nHøjreklik for valgmuligheder",
                "EN": "No internet. Check your connection. \nRight-click for options",
                "FR": "Pas d’internet. Vérifiez votre connexion. \nCliquez avec le bouton droit pour les options",
                "ES": "Sin conexión a internet. Verifica tu conexión. \nHaz clic derecho para ver las opciones",
                "DE": "Keine Internetverbindung. Überprüfen Sie Ihre Verbindung. \nRechtsklick für Optionen",
                "FI": "Ei internetyhteyttä. Tarkista yhteytesi. \nNapsauta hiiren oikealla painikkeella nähdäksesi vaihtoehdot",
                "SV": "Ingen internetanslutning. Kontrollera din anslutning. \nHögerklicka för alternativ",
                "IT": "Nessuna connessione a Internet. Controlla la tua connessione. \nFai clic con il tasto destro per le opzioni"
            },
            "file_preview_file_corrupted": {
                "DA": "Beklager. Memory Mate kan ikke åbne filen da filformatet ikke understøttes, eller filen er beskadiget",
                "EN": "Sorry. Memory Mate can't open the file because the format is unsupported, or the file is corrupted",
                "FR": "Désolé. Memory Mate ne peut pas ouvrir le fichier car le format n'est pas pris en charge ou le fichier est endommagé",
                "ES": "Lo sentimos. Memory Mate no puede abrir el archivo porque el formato no es compatible o el archivo está dañado",
                "DE": "Entschuldigung. Memory Mate kann die Datei nicht öffnen, da das Format nicht unterstützt wird oder die Datei beschädigt ist",
                "FI": "Pahoittelut. Memory Mate ei voi avata tiedostoa, koska tiedostomuotoa ei tueta tai tiedosto on vioittunut",
                "SV": "Tyvärr. Memory Mate kan inte öppna filen eftersom formatet inte stöds eller filen är skadad",
                "IT": "Spiacenti. Memory Mate non può aprire il file perché il formato non è supportato o il file è danneggiato"
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
                "DA": "Indsæt..",
                "EN": "Paste..",
                "FR": "Coller..",
                "ES": "Pegar..",
                "DE": "Einfügen..",
                "FI": "Liitä..",
                "SV": "Klistra in..",
                "IT": "Incolla.."
            },
            "file_menu_patch": {
                "DA": "Udfyld manglende..",
                "EN": "Fill missing..",
                "FR": "Remplir les éléments manquants..",
                "ES": "Rellenar faltantes..",
                "DE": "Fehlendes ausfüllen..",
                "FI": "Täytä puuttuvat..",
                "SV": "Fyll i saknade..",
                "IT": "Compila i mancanti.."
            },
            "file_menu_delete": {
                "DA": "Slet..",
                "EN": "Delete..",
                "FR": "Supprimer..",
                "ES": "Eliminar..",
                "DE": "Löschen..",
                "FI": "Poista..",
                "SV": "Radera..",
                "IT": "Elimina.."
            },
            "file_menu_empty_clipboard": {
                "DA": "Tøm udklipsholder",
                "EN": "Empty Clipboard",
                "FR": "Vider le presse-papiers",
                "ES": "Vaciar el portapapeles",
                "DE": "Zwischenablage leeren",
                "FI": "Tyhjennä leikepöytä",
                "SV": "Töm urklippshanteraren",
                "IT": "Svuota gli appunti"
            },
            "file_menu_paste_metadata": {
                "DA": "Indsæt",
                "EN": "Paste",
                "FR": "Coller",
                "ES": "Pegar",
                "DE": "Einfügen",
                "FI": "Liitä",
                "SV": "Klistra in",
                "IT": "Incolla"
            },
            "file_menu_patch_metadata": {
                "DA": "Udfyld",
                "EN": "Fill",
                "FR": "Remplir",
                "ES": "Rellenar",
                "DE": "Ausfüllen..",
                "FI": "Täytä",
                "SV": "Fyll",
                "IT": "Compila"
            },
            "file_menu_delete_metadata": {
                "DA": "Slet",
                "EN": "Delete",
                "FR": "Supprimer",
                "ES": "Eliminar",
                "DE": "Löschen",
                "FI": "Poista",
                "SV": "Radera",
                "IT": "Elimina"
            },
            "file_menu_paste_geo_location_from_garmin": {
                "DA": "Geo-lokation fra Garmin",
                "EN": "Geo-location from Garmin",
                "FR": "Géo-localisation depuis Garmin",
                "ES": "Geolocalización desde Garmin",
                "DE": "Geoposition von Garmin",
                "FI": "Sijaintitiedot Garminista",
                "SV": "Geoposition från Garmin",
                "IT": "Geolocalizzazione da Garmin"
            },
            "file_menu_patch_geo_location_from_garmin": {
                "DA": "Geo-lokation fra Garmin",
                "EN": "Geo-location from Garmin",
                "FR": "Géo-localisation depuis Garmin",
                "ES": "Geolocalización desde Garmin",
                "DE": "Geoposition von Garmin",
                "FI": "Sijaintitiedot Garminista",
                "SV": "Geoposition från Garmin",
                "IT": "Geolocalizzazione da Garmin"
            },
            "file_menu_paste_original_filename_from_filename": {
                "DA": "Oprindeligt filnavn fra filnavn",
                "EN": "Original Filename from Filename",
                "FR": "Nom de fichier original depuis le nom de fichier",
                "ES": "Nombre de archivo original desde el nombre de archivo",
                "DE": "Ursprünglicher Dateiname aus Dateiname",
                "FI": "Alkuperäinen tiedostonimi tiedostonimestä",
                "SV": "Ursprungligt filnamn från filnamn",
                "IT": "Nome file originale dal nome file"
            },
            "file_menu_patch_original_filename_from_filename": {
                "DA": "Oprindeligt filnavn fra filnavn",
                "EN": "Original Filename from Filename",
                "FR": "Nom de fichier original depuis le nom de fichier",
                "ES": "Nombre de archivo original desde el nombre de archivo",
                "DE": "Ursprünglicher Dateiname aus Dateiname",
                "FI": "Alkuperäinen tiedostonimi tiedostonimestä",
                "SV": "Ursprungligt filnamn från filnamn",
                "IT": "Nome file originale dal nome file"
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
            "file_menu_chose_tags_to_patch": {
                "DA": "Vælg hvad du vil overføre:",
                "EN": "Choose what to transfer:",
                "FR": "Choisissez quoi transférer :",
                "ES": "Elige qué transferir:",
                "DE": "Wählen Sie, was übertragen werden soll:",
                "FI": "Valitse mitä siirretään:",
                "SV": "Välj vad du vill överföra:",
                "IT": "Scegli cosa trasferire:"
            },
            "file_menu_chose_tags_to_delete": {
                "DA": "Vælg hvad du vil slette:",
                "EN": "Choose what to delete:",
                "FR": "Choisissez ce que vous souhaitez supprimer :",
                "ES": "Elige qué quieres eliminar:",
                "DE": "Wählen Sie aus, was Sie löschen möchten:",
                "FI": "Valitse, mitä haluat poistaa:",
                "SV": "Välj vad du vill radera:",
                "IT": "Scegli cosa eliminare:"
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
            "settings_general_tab_title": {
                "DA": "Generelt",
                "EN": "General",
                "FR": "Général",
                "ES": "General",
                "DE": "Allgemein",
                "FI": "Yleiset",
                "SV": "Allmänt",
                "IT": "Generale"
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
            "settings_consolidate_tab_title": {
                "DA": "Konsolidering",
                "EN": "Consolidation",
                "FR": "Consolidation",
                "ES": "Consolidación",
                "DE": "Konsolidierung",
                "FI": "Yhdistäminen",
                "SV": "Konsolidering",
                "IT": "Consolidamento"
            },
            "settings_labels_auto_consolidate_active": {
                "DA": "Automatisk konsolidering af metadata i valgte mapper",
                "EN": "Automatic consolidation of metadata in selected folders",
                "FR": "Consolidation automatique des métadonnées dans les dossiers sélectionnés",
                "ES": "Consolidación automática de metadatos en las carpetas seleccionadas",
                "DE": "Automatische Konsolidierung von Metadaten in ausgewählten Ordnern",
                "FI": "Metatietojen automaattinen yhdistäminen valituissa kansioissa",
                "SV": "Automatisk konsolidering av metadata i valda mappar",
                "IT": "Consolidamento automatico dei metadati nelle cartelle selezionate"
            },
            "settings_auto_consolidate_explanation": {
                "DA": "Første gang Memory Mate skriver metadata til en fil, konsolideres metadata,\n så alle data står i de rette metadata-tags.\nDu kan få Memory Mate til automatisk at konsolidere metadata på billeder i mapper\n i samme øjeblik du vælger mappen i Memory Mates fil-navigatoren (venstre del af vinduet).\n Memory Mate har styr på om metadata i en fil allerede er konsolideret, så det sker kun en gang.",
                "EN": "The first time Memory Mate writes metadata to a file, the metadata is consolidated\n so that all information is placed in the correct metadata tags.\nYou can have Memory Mate automatically consolidate metadata on images in folders\n the moment you select the folder in Memory Mate's file navigator (the left part of the window).\nMemory Mate keeps track of whether the metadata in a file has already been consolidated, so it only happens once.",
                "FR": "La première fois que Memory Mate écrit des métadonnées dans un fichier, les métadonnées sont consolidées\n afin que toutes les informations soient placées dans les bons champs de métadonnées.\nVous pouvez demander à Memory Mate de consolider automatiquement les métadonnées des images dans les dossiers\n dès que vous sélectionnez le dossier dans le navigateur de fichiers de Memory Mate (partie gauche de la fenêtre).\nMemory Mate vérifie si les métadonnées d’un fichier ont déjà été consolidées, donc cela ne se produit qu’une seule fois.",
                "ES": "La primera vez que Memory Mate escribe metadatos en un archivo, los metadatos se consolidan\n de modo que toda la información quede en las etiquetas de metadatos correctas.\nPuedes hacer que Memory Mate consolide automáticamente los metadatos de las imágenes en las carpetas\n en el mismo momento en que selecciones la carpeta en el navegador de archivos de Memory Mate (parte izquierda de la ventana).\nMemory Mate controla si los metadatos de un archivo ya se han consolidado, por lo que solo ocurre una vez.",
                "DE": "Wenn Memory Mate zum ersten Mal Metadaten in eine Datei schreibt, werden die Metadaten konsolidiert,\n sodass alle Informationen in den richtigen Metadaten-Tags stehen.\nSie können Memory Mate so einstellen, dass Metadaten in Bildern in Ordnern automatisch konsolidiert werden,\n sobald Sie den Ordner im Dateinavigator von Memory Mate auswählen (linker Teil des Fensters).\nMemory Mate behält den Überblick, ob die Metadaten einer Datei bereits konsolidiert wurden, sodass dies nur einmal geschieht.",
                "FI": "Kun Memory Mate kirjoittaa ensimmäisen kerran metatietoja tiedostoon, metatiedot konsolidoidaan\n niin, että kaikki tiedot sijoitetaan oikeisiin metatietotunnisteisiin.\nVoit antaa Memory Maten konsolidoida automaattisesti kansioiden kuvien metatiedot\n heti, kun valitset kansion Memory Maten tiedostoselaimessa (ikkunan vasemmassa osassa).\nMemory Mate seuraa, onko tiedoston metatiedot jo konsolidoitu, joten se tapahtuu vain kerran.",
                "SV": "Första gången Memory Mate skriver metadata till en fil konsolideras metadata\n så att all information hamnar i rätt metadata-taggar.\nDu kan låta Memory Mate automatiskt konsolidera metadata för bilder i mappar\n i samma ögonblick som du väljer mappen i Memory Mates filnavigator (vänstra delen av fönstret).\nMemory Mate håller reda på om metadatan i en fil redan har konsoliderats, så det sker bara en gång.",
                "IT": "La prima volta che Memory Mate scrive metadati in un file, i metadati vengono consolidati\n in modo che tutte le informazioni siano inserite nei tag di metadati corretti.\nPuoi fare in modo che Memory Mate consolidi automaticamente i metadati delle immagini nelle cartelle\n non appena selezioni la cartella nel navigatore di file di Memory Mate (parte sinistra della finestra).\nMemory Mate tiene traccia se i metadati in un file sono già stati consolidati, quindi questo avviene solo una volta."
            },
            "settings_lightroom_tab_title": {
                "DA": "Lightroom",
                "EN": "Lightroom",
                "FR": "Lightroom",
                "ES": "Lightroom",
                "DE": "Lightroom",
                "FI": "Lightroom",
                "SV": "Lightroom",
                "IT": "Lightroom"
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
            "settings_lr_integration_explanation": {
                "DA": "Lightroom integrationen opdaterer filnavnene i dit Lightroom Classic katalog\nnår du bruger \"Standardiser filnavne\"-funktionen i Memory Mate.",
                "EN": "The Lightroom Integration will update filenames in your Lightroom Classic Catalogue\nwhen you use the \"Standardise Filenames\"-functionality in Memory Mate.",
                "FR": "L'intégration de Lightroom mettra à jour les noms de fichiers dans votre catalogue Lightroom Classic\nlorsque vous utilisez la fonctionnalité \"Standardiser les noms de fichiers\" dans Memory Mate.",
                "ES": "La integración con Lightroom actualizará los nombres de archivo en su catálogo de Lightroom Classic\ncuando utilice la función \"Estandarizar nombres de archivos\" en Memory Mate.",
                "DE": "Die Lightroom-Integration aktualisiert Dateinamen in Ihrem Lightroom Classic-Katalog,\nwenn Sie die Funktion \"Dateinamen standardisieren\" in Memory Mate verwenden.",
                "FI": "Lightroom-integraatio päivittää tiedostonimet Lightroom Classic -luettelossasi,\nkun käytät Memory Maten \"Vakiinnuta tiedostonimet\" -toimintoa.",
                "SV": "Lightroom-integrationen uppdaterar filnamnen i din Lightroom Classic-katalog\nnär du använder funktionen \"Standardisera filnamn\" i Memory Mate.",
                "IT": "L'integrazione con Lightroom aggiornerà i nomi dei file nel tuo catalogo Lightroom Classic\nquando utilizzi la funzione \"Standardizza nomi file\" in Memory Mate."
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
            "settings_garmin_tab_title": {
                "DA": "Garmin",
                "EN": "Garmin",
                "FR": "Garmin",
                "ES": "Garmin",
                "DE": "Garmin",
                "FI": "Garmin",
                "SV": "Garmin",
                "IT": "Garmin"
            },
            "settings_garmin_integration_headline": {
                "DA": "Garmin-integration:",
                "EN": "Garmin-integration:",
                "FR": "Intégration Garmin:",
                "ES": "Integración con Garmin:",
                "DE": "Garmin-Integration:",
                "FI": "Garmin-integraatio:",
                "SV": "Garmin-integration:",
                "IT": "Integrazione Garmin:"
            },
            "settings_labels_garmin_integration_active": {
                "DA": "Aktiver integration",
                "EN": "Activate Integration",
                "FR": "Activer l'intégration",
                "ES": "Activar integración",
                "DE": "Integration aktivieren",
                "FI": "Aktivoi integraatio",
                "SV": "Aktivera integration",
                "IT": "Attiva integrazione"
            },
            "settings_garmin_integration_explanation": {
                "DA": "Hvis du tracker dine vandreture i Garmin Connect, kan du bruge dataene til at skrive geo-lokation til billeder.\nAktivér blot integrationen.\nAlle billeder taget i tidsrummet for en aktivitet vil få geo-lokationen sat,\nhvis placeringen mangler i billedet (..ingen overskrivning).",
                "EN": "If you track your hikes in Garmin Connect, you can use the data to write geo-location to images.\n Simply switch on the integration.\nAll images taken in the timespan of an activity will get the geolocation set\n in case the location is missing in the image (..no overwriting)",
                "FR": "Si vous enregistrez vos randonnées dans Garmin Connect, vous pouvez utiliser les données pour écrire la géolocalisation dans les images.\nIl suffit d’activer l’intégration.\nToutes les images prises pendant la durée d’une activité recevront la géolocalisation\nsi celle-ci est absente de l’image (..aucun écrasement).",
                "ES": "Si registras tus excursiones en Garmin Connect, puedes usar los datos para escribir la geolocalización en las imágenes.\nSimplemente activa la integración.\nTodas las imágenes tomadas durante el período de una actividad recibirán la geolocalización\nsi falta en la imagen (..sin sobrescribir).",
                "DE": "Wenn Sie Ihre Wanderungen in Garmin Connect aufzeichnen, können Sie die Daten verwenden, um die Geoposition in die Bilder zu schreiben.\nAktivieren Sie einfach die Integration.\nAlle Bilder, die im Zeitraum einer Aktivität aufgenommen wurden, erhalten die Geoposition,\nfalls im Bild keine vorhanden ist (..kein Überschreiben).",
                "FI": "Jos tallennat vaelluksesi Garmin Connectiin, voit käyttää tietoja kirjoittamaan sijaintitiedon kuviin.\nAktivoi vain integrointi.\nKaikki aktiviteetin aikana otetut kuvat saavat sijainnin,\njos sijainti puuttuu kuvasta (..ei ylikirjoitusta).",
                "SV": "Om du registrerar dina vandringar i Garmin Connect kan du använda data för att skriva in geolokalisering i bilder.\nSlå bara på integrationen.\nAlla bilder som tas under en aktivitets tidsperiod får geolokaliseringen\nom platsen saknas i bilden (..ingen överskrivning).",
                "IT": "Se registri le tue escursioni in Garmin Connect, puoi utilizzare i dati per scrivere la geolocalizzazione nelle immagini.\nBasta attivare l’integrazione.\nTutte le immagini scattate durante il periodo di un’attività riceveranno la geolocalizzazione\nse manca nell’immagine (..nessuna sovrascrittura)."
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
