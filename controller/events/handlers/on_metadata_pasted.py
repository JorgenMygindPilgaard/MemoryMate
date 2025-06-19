from view.windows.file_panel import FilePanel


def onMetadataPasted(file_name):
    if file_name == FilePanel.file_name:
        FilePanel.getInstance(file_name)   #Triggers update of Filepanel