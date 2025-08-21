import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy
from configuration.paths import Paths

from configuration.settings import Settings


class QueueStatusMonitor(QHBoxLayout):
    def __init__(self, queue=None):
        super().__init__()
        self.queue = queue
        self.queue.queue_size_changed.connect(self.onQueueSizeChanged)
        if queue is not None:
            self.queue_size = queue.size()
        else:
            self.queue_size = 0
        self.init_ui()

    def init_ui(self):
        # Create a label for pause/play
        self.play_pause_label = QLabel()
        self.play_pixmap = QPixmap(os.path.join(Paths.get('resources'), "play.png")).scaled(12, 12)
        self.pause_pixmap = QPixmap(os.path.join(Paths.get('resources'), "pause.png")).scaled(12, 12)
        self.play_pause_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        if self.queue.queue_worker_paused:
            self.play_pause_label.setPixmap(self.play_pixmap)
        else:
            self.play_pause_label.setPixmap((self.pause_pixmap))
        self.play_pause_label.mousePressEvent = self.onPlayPausePress
        self.play_pause_label.enterEvent = self.onPlayPauseEnter
        self.play_pause_label.leaveEvent = self.onPlayPauseLeave

        # Create a label for displaying the queue size

        self.queue_size_label = QLabel("")
        if self.queue_size != 0:
            self.queue_size_label.setText(str(self.queue_size))
        self.queue_size_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Load the processing.gif and display it using a QMovie
        self.movie = QMovie(os.path.join(Paths.get('resources'), "processing.gif"))
        self.movie.setScaledSize(QSize(25,18))

        # Set the maximum height for the gif label to match the queue size label
        self.gif_label = QLabel()
#        self.gif_label.setMaximumHeight(self.queue_size_label.sizeHint().height())
        self.gif_label.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)  # Set size policy
        if self.queue_size > 0 and not self.queue.queue_worker_paused:
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        # Create an empty label to take up space
        self.space_label = QLabel()
        self.space_label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

        # Create a horizontal layout and add the widgets
        self.addWidget(self.play_pause_label)
        self.addWidget(self.gif_label)
        self.addWidget(self.queue_size_label)
        self.addWidget(self.space_label)

    def onPlayPauseEnter(self,event):
        self.play_pause_label.setCursor(Qt.CursorShape.PointingHandCursor)  # Change cursor to pointing hand when mouse enters

    def onPlayPauseLeave(self,event):
        self.play_pause_label.setCursor(Qt.CursorShape.ArrowCursor)  # Change cursor back tor arrow

    def onPlayPausePress(self,event):
        if self.queue.queue_worker_paused:   # Toggle to playing if paused
            self.play_pause_label.setPixmap(self.pause_pixmap)
            if self.queue_size > 0:
                self.gif_label.setMovie(self.movie)
                self.movie.start()
            self.queue.resume()
        else:                                     # Toggle to paused if playing
            self.play_pause_label.setPixmap(self.play_pixmap)
            self.gif_label.clear()
            self.movie.stop()
            self.queue.pause()

    def onQueueSizeChanged(self, size):
        self.queue_size = size
        if size > 0:
            self.queue_size_label.setText(str(size))
        else:
            self.queue_size_label.clear()
        if size > 0 and not self.queue.queue_worker_paused:
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.gif_label.clear()
            self.movie.stop()
