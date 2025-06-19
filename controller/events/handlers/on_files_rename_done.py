from configuration.settings import Settings
from controller.events.emitters.file_metadata_pasted_emitter import FileMetadataPastedEmitter
from services.integration_services import lightroom_integration
from view.ui_components.file_preview import FilePreview
from services.file_services.file_split_name import splitFileName
from services.queue_services.json_queue_file import JsonQueueFile
from services.metadata_services.metadata import FileMetadata


def onFileRenameDone(files,update_original_filename_tag=False):
# Update filenames in Lightroom Classic Catalog
    if Settings.get('lr_integration_active'):
        lightroom_integration.appendLightroomQueue(Settings.get('lr_queue_file_path'), files)
        lightroom_integration.processLightroomQueue(Settings.get('lr_db_path'), Settings.get('lr_queue_file_path'))

# Update file-names in queue
    queue_changes = []
    for file in files:
        queue_changes.append({'find': {'file': file.get('old_name')},'change': {'file': file.get('new_name')}})
    json_queue_file = JsonQueueFile.getInstance(Settings.get('queue_file_path'))
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

# Set original filename tag in all files
    if update_original_filename_tag==True and Settings.get('logical_tags').get('original_filename') is not None:
        for file in files:
            new_file_name = file.get('new_name')
            if 'tmp' in new_file_name:
                continue
            file_metadata = FileMetadata.getInstance(new_file_name)
            new_name_alone = splitFileName(new_file_name)[1]
            if new_name_alone != '' and new_name_alone is not None:
                logical_tags = {'original_filename': new_name_alone}
                file_metadata.setLogicalTagValues(logical_tags)
                file_metadata_pasted_emitter = FileMetadataPastedEmitter.getInstance()
                file_metadata_pasted_emitter.emit(new_file_name)