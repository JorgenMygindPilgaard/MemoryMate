from configuration.settings import Settings
from services.metadata_services.metadata import FileMetadata
from services.metadata_services.consolidate_metadata import ConsolidateMetadata
from controller.events.coordinators.coordinate_metadata_ready_preview_ready import Coordinator

def onFileMetadataReady(file_name):
    file_meta_data = FileMetadata.getInstance(file_name)

# Keep metadata consolidated automatically at read
    if Settings.get('auto_consolidate_active'):
        tags_hash_tag = file_meta_data.getTagsHashTag()
        tags_hash = file_meta_data.getTagsHash()
        if tags_hash_tag != tags_hash: # Some tags managed by MemoryMate changed by another program
            ConsolidateMetadata(file_name)

# Find out and send signal when both metadata and preview is ready
    Coordinator.getInstance().metadataReady(file_name)