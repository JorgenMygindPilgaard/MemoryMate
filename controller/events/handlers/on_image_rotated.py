from view.ui_components.file_preview import FilePreview
from view.windows.file_panel import FilePanel


def onImageRotated(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()
        file_preview = FilePreview.instance_index.get(file_name)  # Get existing preview, if exist
        if file_preview:
            file_preview.updatePixmap()
            FilePanel.preview_widget.setPixmap(file_preview.getPixmap(FilePreview.latest_panel_width))