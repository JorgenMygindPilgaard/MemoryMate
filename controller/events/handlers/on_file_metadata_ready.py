from configuration.settings import Settings
from services.metadata_services.metadata import FileMetadata
from services.queue_services.queue import Queue
from services.metadata_services.consolidate_metadata import ConsolidateMetadata
from controller.events.coordinators.coordinate_metadata_ready_preview_ready import Coordinator

def onFileMetadataReady(file_name):
    file_meta_data = FileMetadata.getInstance(file_name)

# Keep metadata consolidated automatically at read
    due_for_consolidation = False

    if Settings.get('auto_consolidate_active'):
        # Find out if changed by external program since last run
        tags_hash_tag = file_meta_data.getTagsHashTag()
        tags_hash = file_meta_data.getTagsHash()
        if tags_hash_tag != tags_hash:                      # External program changed tags in file
            due_for_consolidation = True

        # Skip consolidation if already in queue
        queue_entries=Queue.getInstance('metadata.write').entries()
        exists = any(queue_entry.get("file") == file_name for queue_entry in queue_entries)
        if exists:
            due_for_consolidation = False
        else:
        # Find out if file has unsaved logical tag values
            saved_logical_tag_values = file_meta_data.getSavedLogicalTagValues(filter_writable_only=True)
            logical_tag_values = file_meta_data.getLogicalTagValues(filter_writable_only=True)
            if saved_logical_tag_values != logical_tag_values:  # Will differ if Api or sidecar-file provided new values
                due_for_consolidation = True

        # Consolidate if needed
        if due_for_consolidation:
            ConsolidateMetadata(file_name)

# Find out and send signal when both metadata and preview is ready
    Coordinator.getInstance().metadataReady(file_name)