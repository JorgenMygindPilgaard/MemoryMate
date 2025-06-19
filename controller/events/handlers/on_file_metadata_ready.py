from controller.events.coordinators.coordinate_metadata_ready_preview_ready import Coordinator
def onFileMetadataReady(file_name):
    Coordinator.getInstance().metadataReady(file_name)
