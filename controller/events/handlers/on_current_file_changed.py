from services.stack_services.stack_coordinator import StackCoordinator
from view.windows.file_panel import FilePanel
from services.metadata_services.metadata import FileMetadata
from view.ui_components.file_preview import FilePreview

def onCurrentFileChanged(new_file_name):
    if new_file_name != FilePanel.file_name:
        FilePanel.saveMetadata()  # Saves metadata for file currently in file-panel (if any)
        FileMetadata.getInstance(new_file_name).readLogicalTagValues()
        FilePreview.getInstance(new_file_name).readImage()
        FilePanel.getInstance(new_file_name)  # Puts new file in file-panel
        StackCoordinator.getInstance().doStacking(new_file_name)
