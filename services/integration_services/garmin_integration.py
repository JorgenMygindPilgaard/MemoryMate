from view.windows.login_window import LoginWindow
from PyQt6.QtCore import QObject, QThread, QCoreApplication, QTimer, pyqtSignal
from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectAuthenticationError
from garth.exc import GarthException, GarthHTTPError
import requests
import keyring
from configuration.paths import Paths
from configuration.language import Texts
from repository.gps_location_repo.gps_location_api import GpsApi
from datetime import datetime, timezone
from controller.events.emitters.garmin_integration_event_emitter import GarminIntegrationEventEmitter
import os

class GarminIntegration(QObject):
    get_instance_active = False
    instance=None

    def __init__(self):
        super().__init__()
        self.garmin_api = None
        self.garmin_integration_worker = None
        self.status = 'not logged in'
        self.user_name = None
        # Check that getInstance was called
        if not GarminIntegration.get_instance_active:
            raise Exception('Please use getInstance method')

        # Set data for GarminIntegration
        GarminIntegration.instance = self

    @staticmethod
    def getInstance():
        if GarminIntegration.instance is None:
            GarminIntegration.get_instance_active = True
            Garmin.instance = GarminIntegration()
            GarminIntegration.get_instance_active = False
        return GarminIntegration.instance

    def garminApiLogin(self):
        while True:
            try:
                self.garmin_api = self.__garminApiTokenLogin()
            except Exception as e:
                if 'NameResolutionError' in str(e):
                    raise Exception('no internet')
                else:   # All other exceptions: Try password-login
                    self.garmin_api = self.__garminApiPasswordLogin()
            self.user_name = self.__getStoredEmail()
            return self.garmin_api

    def garminApiLogout(self):
        if self.garmin_api is not None:
            # Stop worker
            self.stop()

            # Logout
            self.garmin_api.logout()
            self.garmin_api = None
            GarminIntegrationEventEmitter.getInstance().emit("not logged in")

            # Delete token (Will enable login with new user afterwards)
            for filename in os.listdir(Paths.get("garmin_token")):
                file_path = os.path.join(Paths.get("garmin_token"), filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  # remove file or symlink
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)  # remove empty directory
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    def __garminApiTokenLogin(self):
        garmin_api = Garmin()
        garmin_api.login(Paths.get("garmin_token"))    # Raises exception if unsuccessful
        return garmin_api

    def __garminApiPasswordLogin(self):  # L
        # Loop for credential entry with retry on auth failure
        message=None
        while True:
            login_window = LoginWindow(title=Texts.get("garmin_login_window_title"),
                                       user=self.__getStoredEmail(),
                                       message=message)
            login_window.show()
            button, user, password, mfa_code = login_window.getInfo()
            if button == 'cancel':
                raise Exception('cancel')

            try:
                garmin_api = Garmin(email=user, password=password, is_cn=False, return_on_mfa=True)
                result1, result2 = garmin_api.login()
                if result1 == "needs_mfa":
                    login_window = LoginWindow(title=Texts.get("garmin_login_window_title"),
                                               user=user,
                                               protect_user_field=True,
                                               password=password,
                                               protect_password_field=True,
                                               request_mfa_code=True,
                                               message=message)
                    login_window.show()
                    button, user, password, mfa_code = login_window.getInfo()
                    if button == 'cancel':
                        raise Exception('cancel')
                    try:
                        garmin_api.resume_login(result2, mfa_code)
                    except GarthHTTPError as garth_error:
                        # Handle specific HTTP errors from MFA
                        error_str = str(garth_error)
                        if "429" in error_str and "Too Many Requests" in error_str:
                            message = Texts.get('login_window_message_too_many_attempts')
                            continue
                        elif "401" in error_str or "403" in error_str:
                            message = Texts.get('login_window_message_mfa_code_wrong')
                            continue
                        else:
                            message = 'login_window_message_mfa_authentication_failed'
                            continue
                    except GarthException:
                        message = 'login_window_message_mfa_authentication_failed'
                        continue

            except Exception as e:
                if '401 Client Error: Unauthorized' in str(e):
                    message = Texts.get('login_window_message_user_or_password_wrong')
                    continue
                elif 'NameResolutionError' in str(e):
                    message = Texts.get('login_window_message_connection_error')
                    continue
                else:
                    message = str(e)
                    continue

            garmin_api.garth.dump(Paths.get("garmin_token"))
            self.__storeEmail(user)
            return garmin_api

    def start(self):

        # Return if already running
        if self.garmin_integration_worker is not None:
            if self.garmin_integration_worker.isRunning():
                return   # Return if already running

        # Log in if not logged in already
        if self.garmin_api is None:
            try:
                self.garmin_api = self.garminApiLogin()
            except Exception as e:
                if str(e) == 'no internet':
                    GarminIntegrationEventEmitter.getInstance().emit("no internet")  # running/done/not logged in/no internet
                    QTimer.singleShot(5000, GarminIntegration.getInstance().start)
                    return
                elif str(e) == 'cancel':
                    GarminIntegrationEventEmitter.getInstance().emit("not logged in")  # running/done/not logged in/no internet

        # Start sync if logged in
        if self.garmin_api is not None:
            self.garmin_integration_worker = GarminIntegrationWorker(self.garmin_api)  #
            self.garmin_integration_worker.start()
            if QCoreApplication.instance() is not None:
                QCoreApplication.instance().aboutToQuit.connect(self.garmin_integration_worker.onAboutToQuit)

    def stop(self):
            if self.garmin_integration_worker is not None:
                self.garmin_integration_worker.stop()

    def __getStoredEmail(self):
        """Return last used email, or None if not stored."""
        return keyring.get_password('garmin_connect', "last-used-email")

    def __storeEmail(self,email):
        """Store email for future suggestion."""
        keyring.set_password('garmin_connect', "last-used-email", email)

class GarminIntegrationWorker(QThread):
    def __init__(self,garmin_api):
        # Check that instantiation is called from getInstance-method
        super().__init__()
        self.garmin_api=garmin_api
        self.service_id=None # Will be filled at start
        self.user_id=None # Will be filled at start
        self.local_gps_api = GpsApi.getInstance()
        self.stop_requested=False
        if QCoreApplication.instance() is not None:
            QCoreApplication.instance().aboutToQuit.connect(self.onAboutToQuit)

    def run(self):
        GarminIntegrationEventEmitter.getInstance().emit("running")   # running/done/no internet/not logged in
        self.service_id = self.__storeMissingService('garmin_connect')
        self.user_id = self.__storeMissingUser(email=self.__getStoredEmail())
        self.__storeMissingActivities()
        GarminIntegrationEventEmitter.getInstance().emit("done")   # running/done/no internet/not logged in

    def stop(self):
        self.stop_requested = True   #

    def __getStoredEmail(self):
        """Return last used email, or None if not stored."""
        return keyring.get_password('garmin_connect', "last-used-email")

    def __storeMissingService(self,service):
        # Find (or add) service_id in local gps db
        services = self.local_gps_api.get_services(name='garmin_connect')
        if services == []:  # Service not existing in local gps-db
            self.local_gps_api.create_service(name='garmin_connect')
            services = self.local_gps_api.get_services(name='garmin_connect')
        if services != []:
            return services[0].get('id')  # Return id in database of created service

    def __storeMissingUser(self,email):
        # Find (or add) user_id in local gps db
        user_id = self.local_gps_api.get_user_id('garmin_connect',email)
        if user_id is None:
            if self.service_id is None:
                self.service_id = self.__storeMissingService()
            self.local_gps_api.create_user(name=email, service_id=self.service_id)
            user_id = self.local_gps_api.get_user_id('garmin_connect',email)
        return user_id

    def __storeMissingActivities(self):
        def __formattedTime(time:str):
            __formattedTime=time

    # Add activities as tracks one by one local gps db, until an existing track is met
        current_activity_index=0 # 0 means most current activity
        batch_size=100
        while True:
            # Exit if stop requested
            if self.stop_requested:
                break
            activities=self.garmin_api.get_activities(start=current_activity_index,limit=batch_size)  # Get latest activity
            current_activity_index +=batch_size

            # Stop, if no activities found
            if activities==[]:
                break       # Stop searching, if no tracks found

            for activity in activities:
                # Exit if stop requested
                if self.stop_requested:
                    break

                # Skip activity, if it contains no gps-track
                if activity.get("hasPolyline") != True:
                    continue    # If no gps-track in activity, then continue to next activity
                # Stop, if activity already fully fetched, or clean up for new attempt if not fully fetched
                garmin_activity_id=activity.get("activityId")
                tracks=self.local_gps_api.get_tracks(user_id=self.user_id,external_id=garmin_activity_id)
                if tracks!=[]:   # Track already exist
                    track=tracks[0]
                    if track.get('point_count') != 0:
                        continue # Stop searching, if track already fully loaded
                    self.local_gps_api.delete_track(track_id=track.get('id')) # Delete track and it's points if not fully loaded

                # Create garmin-activity as track in local gps db
                start_time_utc=datetime.strptime(activity.get("startTimeGMT"), "%Y-%m-%d %H:%M:%S").isoformat()
                start_time_local=datetime.strptime(activity.get("startTimeLocal"), "%Y-%m-%d %H:%M:%S").isoformat()
                # print("startTimeLocal=" + activity.get("startTimeGMT")+"      "+"startTimeGMT="+activity.get("startTimeLocal")+"     "+"start_time_local="+start_time_local+"     "+"start_time_utc="+start_time_utc)
                if activity.get("endTimeGMT") is None:
                    continue
                end_time_utc =datetime.strptime(activity.get("endTimeGMT"), "%Y-%m-%d %H:%M:%S").isoformat()
                self.local_gps_api.create_track(external_id=garmin_activity_id,user_id=self.user_id,start_time_utc=start_time_utc,start_time_local=start_time_local,end_time_utc=end_time_utc,point_count=0)
                tracks = self.local_gps_api.get_tracks(user_id=self.user_id, external_id=garmin_activity_id)   # Fetch newly created track
                if tracks == []:  # It never is. Just safe coding
                    continue
                track = tracks[0]

                # Now track holds the track that needs points fetched. Fetch those
                activity_details = {}
                activity_details = self.garmin_api.get_activity_details(garmin_activity_id)
                activity_polyline = activity_details.get("geoPolylineDTO", {}).get("polyline")

                track_id = track.get('id')

                if activity_polyline:
                    points = []
                    for p in activity_polyline:
                        if p.get("valid"):
                            timestamp_ms = p.get("time")
                            if timestamp_ms is not None:
                                # Convert milliseconds → seconds → UTC ISO8601 string with "Z"
                                iso_time = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime(
                                    "%Y-%m-%dT%H:%M:%S")
                                points.append({
                                    "track_id": track_id,
                                    "time_utc": iso_time,
                                    "latitude": p.get("lat"),
                                    "longitude": p.get("lon")
                                })
                    if points != []:
                        self.local_gps_api.create_points(points)
                        self.local_gps_api.update_track(track_id=track_id,point_count=len(points))




    def onAboutToQuit(self):
        if self.isRunning():
            self.stop()
        self.quit()


# app=QApplication(sys.argv)

# Login to garmin and get garmin
# garmin=garminLoginWithPopups()


# Login to garmin and get garmin
# garmin=garminLoginWithPopups()
# if garmin:
#     activities=garmin.get_activities(0, 100)
    # "activityId": 20395420917
    # "beginTimestamp": 1757956567000
    # "endLatitude": 55.66555394791067,
    # "endLongitude": 9.66876570135355,
    # "endTimeGMT": "2025-09-15 17:33:15",
    # "hasPolyline": true,
    # "startLatitude": 55.65751017071307,
    # "startLongitude": 9.67002491466701,
    # "startTimeGMT": "2025-09-15 17:16:07",
    # "startTimeLocal": "2025-09-15 19:16:07",


#   'activityId': 20395420917
#   'hasPolyline': True
#   'beginTimestamp': 1757956567000
#   'endLatitude': 55.66555394791067,
#   'endLongitude': 9.66876570135355,
#   'endTimeGMT': '2025-09-15 17:33:15'
#   'startLatitude': 55.65751017071307,
#   'startLongitude': 9.67002491466701,
#   'startTimeGMT': '2025-09-15 17:16:07',
#   'startTimeLocal': '2025-09-15 19:16:07'
#     activity_id=activities[0]["activityId"]



# List activities (first 1 for example)
# if garmin:
#     activities=garmin.get_activities(0, 1)
#     activity_id=activities[0]["activityId"]
#
#     # Download GPX data
#     details=garmin.get_activity_details(activity_id)
#
#     # Print data
#     print(json.dumps(details, indent=2))




# #****************************
# email="jorgen.pilgaard@gmail.com"
# password="ioNjL6Ptexz#7z9N"
#
# try:
#     # Create Garmin garmin
#     garmin=Garmin(email, password,prompt_mfa=True)
#     garmin.login()
#
#     # List activities (first 1 for example)
#     activities=garmin.get_activities(0, 1)
#     activity_id=activities[0]["activityId"]
#
#     # Download GPX data
#     details=garmin.get_activity_details(activity_id)
#     #
#     # with open(f"activity_{activity_id}.gpx", "wb") as f:
#     #     f.write(gpx_data)
#     #
#     # print("GPX file downloaded!")
#     print('done')
# except (GarminConnectConnectionError, GarminConnectAuthenticationError, GarminConnectTooManyRequestsError) as e:
#     print(f"Error: {e}")
#
# # Get detailed data as JSON
# details=garmin.get_activity_details(activity_id)
#
# # Print or process the JSON data
#
#
# print(json.dumps(details, indent=2))
#
