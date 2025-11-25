from controller.events.emitters.current_file_changed_emitter import CurrentFileChangedEmitter
from controller.events.emitters.file_metadata_changed_emitter import FileMetadataChangedEmitter
from controller.events.emitters.file_metadata_pasted_emitter import FileMetadataPastedEmitter
from controller.events.emitters.file_metadata_ready_emitter import FileMetadataReadyEmitter
from controller.events.emitters.file_preview_ready_emitter import FilePreviewReadyEmitter
from controller.events.emitters.file_ready_emitter import FileReadyEmitter
from controller.events.emitters.files_rename_done_emitter import FileRenameDoneEmitter
from controller.events.emitters.image_rotated_emitter import ImageRotatedEmitter
from controller.events.emitters.garmin_integration_event_emitter import GarminIntegrationEventEmitter
from controller.events.handlers.on_current_file_changed import onCurrentFileChanged
from controller.events.handlers.on_file_metadata_ready import onFileMetadataReady
from controller.events.handlers.on_file_preview_ready import onFilePreviewReady
from controller.events.handlers.on_file_ready import onFileReady
from controller.events.handlers.on_files_rename_done import onFileRenameDone
from controller.events.handlers.on_image_rotated import onImageRotated
from controller.events.handlers.on_metadata_changed import onMetadataChanged
from controller.events.handlers.on_metadata_pasted import onMetadataPasted
from controller.events.handlers.on_garmin_integration_event import onGarminIntegrationEvent

def initializeConnections():
    FileMetadataChangedEmitter.getInstance().change_signal.connect(onMetadataChanged)
    FileRenameDoneEmitter.getInstance().done_signal.connect(onFileRenameDone)
    CurrentFileChangedEmitter.getInstance().change_signal.connect(onCurrentFileChanged)
    FileMetadataPastedEmitter.getInstance().paste_signal.connect(onMetadataPasted)
    ImageRotatedEmitter.getInstance().rotate_signal.connect(onImageRotated)
    FileMetadataReadyEmitter.getInstance().ready_signal.connect(onFileMetadataReady)
    FilePreviewReadyEmitter.getInstance().ready_signal.connect(onFilePreviewReady)
    FileReadyEmitter.getInstance().ready_signal.connect(onFileReady)
    GarminIntegrationEventEmitter.getInstance().event_signal.connect(onGarminIntegrationEvent)