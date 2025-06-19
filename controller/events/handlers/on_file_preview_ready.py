from controller.events.coordinators.coordinate_metadata_ready_preview_ready import Coordinator
def onFilePreviewReady(file_name):
    Coordinator.getInstance().filePreviewReady(file_name)

