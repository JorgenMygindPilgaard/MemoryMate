import re

from configuration.settings import Settings
from services.utility_services.rreplace import rreplace


def splitFileName(file_name,depad_base_name=False):
    def __escapeExceptDotStar(pattern):
        escaped_pattern = ''
        for char in pattern:
            if char == '.' or char == '*':
                escaped_pattern += char
            else:
                escaped_pattern += re.escape(char)
        return escaped_pattern

    def __depad(name):
        name_alone = name
        prefix = ""
        postfix = ""

        padding_patterns = Settings.get('file_name_padding')
        if padding_patterns:
            prefix_patterns = padding_patterns.get("file_name_prefix")
            if prefix_patterns:
                while True:
                    prefix_found = False
                    for prefix_pattern in prefix_patterns:
                        escaped_prefix_pattern = __escapeExceptDotStar(prefix_pattern)
                        match = re.search(escaped_prefix_pattern, name_alone)
                        if match:
                            prefix_found = True
                            if match.start() == 0:
                                found_prefix_pattern = match.group(0)
                                prefix = prefix + found_prefix_pattern
                                name_alone = name_alone.replace(found_prefix_pattern, '', 1)
                    if not prefix_found:
                        break

            postfix_patterns = padding_patterns.get("file_name_postfix")
            if postfix_patterns:
                while True:
                    postfix_found = False
                    for postfix_pattern in postfix_patterns:
                        escaped_postfix_pattern = __escapeExceptDotStar(postfix_pattern)
                        match = re.search(escaped_postfix_pattern,
                                          name_alone)  # ! added to make sure to find last occurrence postfix
                        if match:
                            end_pos = len(name_alone)
                            if match.end() == end_pos:
                                postfix_found = True
                                found_postfix_pattern = match.group(0)  # Remove ! from found_postfix
                                postfix = found_postfix_pattern + postfix
                                name_alone = rreplace(name_alone, found_postfix_pattern, '')
                    if not postfix_found:
                        break

        return [prefix, name_alone, postfix]

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
        if depad_base_name:
            [filename_prefix,filename_alone,filename_postfix] = __depad(filename)
            return [directory, filename, file_extension, filename_prefix, filename_alone, filename_postfix]
        else:
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


