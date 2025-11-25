from configuration.settings import Settings
from configuration.paths import Paths
from controller.events.emitters.file_metadata_pasted_emitter import FileMetadataPastedEmitter
from services.integration_services import lightroom_integration
from view.ui_components.file_preview import FilePreview
from services.file_services.file_split_name import splitFileName
from services.queue_services.json_queue_file import JsonQueueFile
from services.metadata_services.metadata import FileMetadata


def onFileRenameDone(files,update_original_filename_tag=False):
# Update filenames in Lightroom Classic Catalog
    if Settings.get('lr_integration_active'):
        lightroom_integration.appendLightroomQueue(Paths.get('lr_queue'), files)
        lightroom_integration.processLightroomQueue(Settings.get('lr_db_path'), Paths.get('lr_queue'))

# Update file-names in queue
    queue_changes = []
    for file in files:
        queue_changes.append({'find': {'file': file.get('old_name')},'change': {'file': file.get('new_name')}})
    json_queue_file = JsonQueueFile.getInstance(Paths.get('queue'))
    json_queue_file.change_queue(queue_changes)

# Update filename in preview-instance
    for file in files:
        file_preview = FilePreview.instance_index.get(file.get('old_name'))
        if file_preview is not None:
            file_preview.updateFilename(file.get('new_name'))

# Update filename in metadata-instance
    for file in files:
        file_metadata = FileMetadata.instance_index.get(file.get('old_name'))
        if file_metadata is not None:
            file_metadata.updateFilename(file.get('new_name'))

