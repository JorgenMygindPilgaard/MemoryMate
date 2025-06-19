import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from configuration.paths import Paths
from view.windows.settings_window import SettingsWindow


class SettingsWheeel(QLabel):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap(os.path.join(Paths.get('resources'), 'settings.png')).scaled(20, 20)
        self.setPixmap(pixmap)
        self.mousePressEvent = self.onMousePress
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave
    def onEnter(self,event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def onLeave(self,event):
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

    def onMousePress(self,event):
        self.settings_window = SettingsWindow()
        self.settings_window.show()