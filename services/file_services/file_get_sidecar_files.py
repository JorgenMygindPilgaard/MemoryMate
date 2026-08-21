from configuration.settings import Settings
from services.file_services.file_split_name import splitFileName
import os

def fileGetSidecarFiles(file_name,filename_only=False):
    split_file_name = splitFileName(file_name, depad_base_name=True)

    path = split_file_name[0]
    name = split_file_name[1]
    extension = split_file_name[2].rstrip('_backup')
    name_alone = split_file_name[4]

    sidecar_file_source_ids = Settings.get('sidecar_file_source_ids')
    sidecar_files = {}

    for sidecar_file_source_id_key, sidecar_file_source_id_value in sidecar_file_source_ids.items():
        sidecar_file_name_pattern = sidecar_file_source_id_value['file_name_pattern']

        candidate_names = [name]
        if name_alone != name:
            candidate_names.append(name_alone)

        existing_files = []
        for candidate_name in candidate_names:
            sidecar_file_name_only = sidecar_file_name_pattern.replace(
                '<file_name>', candidate_name).replace('<ext>', extension)
            sidecar_file_name = path + sidecar_file_name_only

            if os.path.isfile(sidecar_file_name) and sidecar_file_name not in existing_files:
                if filename_only:
                    existing_files.append(sidecar_file_name_only)
                else:
                    existing_files.append(sidecar_file_name)


        if existing_files:
            sidecar_files[sidecar_file_source_id_key] = existing_files

    return sidecar_files