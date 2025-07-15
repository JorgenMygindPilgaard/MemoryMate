from configuration.settings import Settings
from services.metadata_services.metadata import FileMetadata
from services.metadata_services.consolidate_metadata import ConsolidateMetadata
from controller.events.coordinators.coordinate_metadata_ready_preview_ready import Coordinator


def onFileMetadataReady(file_name):
    file_meta_data = FileMetadata.getInstance(file_name)

# Keep metadata consolidated automatically at read
    if Settings.get('auto_consolidate_active'):
        memory_mate_save_version = file_meta_data.tag_values.get('XMP:MemoryMateSaveVersion')
        if memory_mate_save_version is None:
            memory_mate_save_version = ''
        else:
            memory_mate_save_version = memory_mate_save_version.replace('.','')
        if memory_mate_save_version < '350':
            ConsolidateMetadata(file_name)

# Find out and send signal when both metadata and preview is ready
    Coordinator.getInstance().metadataReady(file_name)
