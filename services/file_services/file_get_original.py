import os

from configuration.language import Texts
from configuration.settings import Settings
from services.file_services.file_split_name import splitFileName
from services.file_services.file_get_list import getFileList

def fileGetOriginal(file):
    split_file_name = splitFileName(file)
    originals_path = split_file_name[0] + '/' + Texts.get('originals_folder_name')
    if not os.path.isdir(originals_path):  # Nothing to do if originals does not exist
        return None

    # Get file from originals folder
    file_name_pattern = [split_file_name[1] + "." + filetype for filetype in Settings.get('file_types')]
    original_files = getFileList(originals_path,pattern=file_name_pattern)  # Original files for file. Should only be one
    if len(original_files)!=0:
        return original_files[0]
    else:
        return None
