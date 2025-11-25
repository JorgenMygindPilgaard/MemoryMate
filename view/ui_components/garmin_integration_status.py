import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QMovie, QAction
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QMenu
import keyring
from configuration.language import Texts
from configuration.paths import Paths
from services.integration_services.garmin_integration import GarminIntegration

class GarminIntegrationStatusMonitor(QHBoxLayout):
    instance=None
    get_instance_active=False

    def __init__(self):
        if not GarminIntegrationStatusMonitor.get_instance_active:
            raise Exception('Please use getInstance method')
        super().__init__()
        self.init_ui()

    @staticmethod
    def getInstance():
        if GarminIntegrationStatusMonitor.instance is None:
            GarminIntegrationStatusMonitor.get_instance_active = True
            GarminIntegrationStatusMonitor.instance = GarminIntegrationStatusMonitor()
            GarminIntegrationStatusMonitor.get_instance_active = False
        return GarminIntegrationStatusMonitor.instance

    def init_ui(self):
        # Set initial statue
        self.status = None  # (running/done/no internet/not logged in)

        # Create a label for status (running/done/no internet/not logged in)
        self.garmin_status_label = QLabel()
        self.garmin_running_movie = QMovie(os.path.join(Paths.get('resources'), "garmin_running.gif"))
        self.garmin_running_movie.setScaledSize(QSize(90,18))
        self.garmin_done_pixmap = QPixmap(os.path.join(Paths.get('resources'), "garmin_done.png")).scaled(QSize(90,18))
        self.garmin_not_logged_in_pixmap = QPixmap(os.path.join(Paths.get('resources'), "garmin_not_logged_in.png")).scaled(QSize(90,18))
        self.garmin_no_internet_pixmap = QPixmap(os.path.join(Paths.get('resources'), "garmin_no_internet.png")).scaled(QSize(90,18))
    #    self.garmin_status_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Create a horizontal layout and add the widgets
        # Create an empty label to take up space
        self.space_label = QLabel()
        self.space_label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
        self.addWidget(self.space_label)
        self.addWidget(self.garmin_status_label)

        # Connect mouse events
        self.garmin_status_label.mousePressEvent = self.onGarminStatusLabelPress
        # self.garmin_status_label.enterEvent = self.onGarminStatusLabelEnter
        # self.garmin_status_label.leaveEvent = self.onGarminStatusLabelLeave
        self.garmin_status_label.contextMenuEvent = self.onGarminStatusLabelContextMenu

    def onGarminStatusLabelEnter(self,event):
        if self.status is not None:
            self.garmin_status_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def onGarminStatusLabelLeave(self,event):
        self.garmin_status_label.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

    def onGarminStatusLabelPress(self,event):
        return

    def onGarminStatusLabelContextMenu(self, event):
        menu = QMenu(self.garmin_status_label)
        login_action = QAction("Login", self.garmin_status_label)
        logout_action = QAction("Logout", self.garmin_status_label)
        sync_action = QAction("Synchronize", self.garmin_status_label)

        login_action.triggered.connect(self.login)
        if self.status in ('running','done'):
            login_action.setEnabled(False)
        logout_action.triggered.connect(self.logout)
        if self.status in ('no internet','not logged in'):
            logout_action.setEnabled(False)
        sync_action.triggered.connect(self.synchronize)
        if self.status != 'done':    # Only sync when logged in and not synchronizing
            sync_action.setEnabled(False)

        menu.addAction(login_action)
        menu.addAction(logout_action)
        menu.addAction(sync_action)

        menu.exec(event.globalPos())

    # === New methods for menu actions ===
    def login(self):
        GarminIntegration.getInstance().garminApiLogin()
        GarminIntegration.getInstance().start()

    def logout(self):
        GarminIntegration.getInstance().garminApiLogout()

    def synchronize(self):
        GarminIntegration.getInstance().start()


    def setStatus(self, event_name:str):
        if event_name == 'running':     # (running/done/no internet/not logged in)
            if self.status == 'running':
                return
            self.status = 'running'
            self.garmin_status_label.clear()
            self.garmin_status_label.setMovie(self.garmin_running_movie)
            self.garmin_running_movie.start()
            self.garmin_status_label.setToolTip(Texts.get("garmin_status_monitor_tool_tip_running").replace('{user}',keyring.get_password('garmin_connect', "last-used-email")))
        elif event_name == 'done':
            if self.status == 'done':
                return
            self.status = 'done'
            self.garmin_status_label.clear()
            self.garmin_status_label.setPixmap(self.garmin_done_pixmap)
            self.garmin_status_label.setToolTip(Texts.get("garmin_status_monitor_tool_tip_done").replace('{user}',keyring.get_password('garmin_connect', "last-used-email")))
        elif event_name == 'no internet':
            if self.status == 'no internet':
                return
            self.status = 'no internet'
            self.garmin_status_label.clear()
            self.garmin_status_label.setPixmap(self.garmin_no_internet_pixmap)
            self.garmin_status_label.setToolTip(Texts.get("garmin_status_monitor_tool_tip_running").replace('{user}',keyring.get_password('garmin_connect', "last-used-email")))
        elif event_name == 'not logged in':
            if self.status == 'not logged in':
                return
            self.status = 'not logged in'
            self.garmin_status_label.clear()
            self.garmin_status_label.setPixmap(self.garmin_not_logged_in_pixmap)
            self.garmin_status_label.setToolTip(Texts.get("garmin_status_monitor_tool_tip_no_internet").replace('{user}',keyring.get_password('garmin_connect', "last-used-email")))

