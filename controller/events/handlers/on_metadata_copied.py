from view.windows.file_panel import FilePanel


def onMetadataCopied(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.saveMetadata()   # .not to copy old data, save what is in screen