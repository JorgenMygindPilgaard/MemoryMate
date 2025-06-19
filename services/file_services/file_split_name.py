def splitFileName(file_name):
    if '.' in file_name:
        dir_end_pos = file_name.rfind('/')
        if dir_end_pos != -1:
            directory = file_name[:dir_end_pos+1]
            full_filename = file_name[dir_end_pos + 1:]
        else:
            directory = ''
            full_filename = file_name

        ext_start_pos = full_filename.rfind('.')
        filename = full_filename[:ext_start_pos]
        file_extension = full_filename[ext_start_pos+1:]
        return [directory, filename, file_extension]
    else:
        if file_name != '':
            if file_name.endswith('/'):
                directory = file_name
            else:
                directory = file_name + '/'
        else:
            directory = ''
        return [directory, '', '']
