import sys
import qdarkstyle
from configuration.paths import Paths

from PyQt6.QtWidgets import QDialog, QApplication

from controller.events.connections import initializeConnections
from configuration.settings import Settings
from view.ui_components.file_preview import FilePreview
from services.integration_services.lightroom_integration import processLightroomQueue
from services.metadata_services.metadata import FileMetadata
from services.queue_services.queue import Queue
from services.stack_services.stack import Stack
from view.windows.initial_settings_window import InitialSettingsWindow
from view.windows.main_window import MainWindow

# Prepare application
app = QApplication(sys.argv)

# Check if language is set, if not, show the selection dialog
if Settings.get('language') is None:
    dialog = InitialSettingsWindow()
    if dialog.exec() == QDialog.DialogCode.Rejected:  # If user closes the dialog, exit app
        sys.exit()


# Set app UI-mode
if Settings.get('ui_mode') == 'LIGHT':
    app.setStyle("Fusion")
elif Settings.get('ui_mode') == 'DARK':
    app.setStyleSheet(qdarkstyle.load_stylesheet())
else:
    app.setStyle("Fusion")

# Set up connections (events to event-handlers)
initializeConnections()

# Prepare queues and stacks
Queue.getInstance('metadata.write',FileMetadata,'processWriteQueueEntry',Paths.get('queue')).start()
Stack.getInstance('metadata.read',FileMetadata,'processReadStackEntry').start()
Stack.getInstance('preview.read',FilePreview,'processReadStackEntry').start()

# Rename files in Lightroom if anything in queue
if Settings.get('lr_integration_active') is True:
    processLightroomQueue(Settings.get('lr_db_path'), Paths.get('lr_queue'), True)

window = MainWindow()
window.show()
app.exec()

