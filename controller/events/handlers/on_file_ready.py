from view.windows.file_panel import FilePanel

def onFileReady(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.instance.prepareFilePanel()