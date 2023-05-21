import subprocess
import os
import json
import locale
import unicodedata
from datetime import datetime
import settings

class ExifTool(object):
    read_process=None    # Two exiftool-processes runs in memory, one for read and one for write.
    write_process=None   # ..that way user does not have to wait for background processor to finalize writes from queue
    configuration=''
    executable=None
    sentinel = "{ready}\r\n"
    sys_encoding = locale.getpreferredencoding()
    # when wrapper calls exiftool, it does so throug windows cmp (command prompt). At the same time parameters are
    # passed through cmd to exiftool (like tag-names, filenames etc).
    # cmd grabs parameters from wrapper (e.g. coded as utf-8). cmd translates parameters into windows system-encoding
    # (e.g. cp1252) before passing them to Exiftool.Exiftool needs to be told what encoding is used for parameters.
    # To tell exiftool what encoding was used, we pass parameter -charset <sys_encoding> (e.g. -charset cp1252) to
    # Exiftool along with the other parameters. (see below in execute-method).

    def __init__(self,executable='exiftool', configuration='' ):
        ExifTool.executable = executable
        ExifTool.configuration = configuration

    def __enter__(self):
        # Prepare read-process of exiftool.exe
        if ExifTool.read_process!=None:               #Process created
            if ExifTool.read_process.poll()!=None:    #Process not running
                ExifTool.read_process=None
        if ExifTool.read_process==None:
            if ExifTool.configuration!='':
                ExifTool.read_process = subprocess.Popen([ExifTool.executable, "-config", ExifTool.configuration, "-stay_open", "True", "-@", "-"],
                                                      universal_newlines=True,
                                                      stdin=subprocess.PIPE,
                                                      stdout=subprocess.PIPE,
                                                      creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                ExifTool.read_process = subprocess.Popen([ExifTool.executable, "-stay_open", "True",  "-@", "-"],
                                                      universal_newlines=True,
                                                      stdin=subprocess.PIPE,
                                                      stdout=subprocess.PIPE,
                                                      creationflags=subprocess.CREATE_NO_WINDOW)

#      Prepare write-process of exiftool.exe
        if ExifTool.write_process!=None:               #Process created
            if ExifTool.write_process.poll()!=None:    #Process not running
                ExifTool.write_process=None
        if ExifTool.write_process==None:
            if ExifTool.configuration!='':
                ExifTool.write_process = subprocess.Popen([ExifTool.executable, "-config", ExifTool.configuration, "-stay_open", "True", "-@", "-"],
                                                      universal_newlines=True,
                                                      stdin=subprocess.PIPE,
                                                      stdout=subprocess.PIPE,
                                                      creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                ExifTool.write_process = subprocess.Popen([ExifTool.executable, "-stay_open", "True",  "-@", "-"],
                                                      universal_newlines=True,
                                                      stdin=subprocess.PIPE,
                                                      stdout=subprocess.PIPE,
                                                      creationflags=subprocess.CREATE_NO_WINDOW)
        return self

    def  __exit__(self, exc_type, exc_value, traceback):
        ExifTool.read_process.stdin.flush()
        ExifTool.write_process.stdin.flush()

    @staticmethod
    def close():
        if ExifTool.read_process!=None:                 # Process exist
            if ExifTool.read_process.poll() == None:    # Proceass is running
                ExifTool.read_process.stdin.write("-stay_open\nFalse\n")    #Close process
                ExifTool.read_process.stdin.flush()
        if ExifTool.write_process!=None:                 # Process exist
            if ExifTool.write_process.poll() == None:    # Proceass is running
                ExifTool.write_process.stdin.write("-stay_open\nFalse\n")    #Close process
                ExifTool.write_process.stdin.flush()

    def execute(self, args,process):
        args.append('-charset')                        # This and the next line tells exiftool which encoding to expect
        args.append('filename='+self.sys_encoding)     # in tags. Windows cmd recodes everything to sys-encoding before passing to exiftool.
        args.append('-charset')
        args.append('exif=UTF8')
        args.append('-charset')
        args.append('iptc=UTF8')
        args.append('-charset')
        args.append('id3=UTF8')
        args.append('-charset')
        args.append('photoshop=UTF8')
        args.append('-charset')
        args.append('quicktime=UTF8')
        args.append('-charset')
        args.append('riff=UTF8')
        args.append('-charset')
        args.append(self.sys_encoding)
        args.append('-overwrite_original')
        args.append('-api')
        args.append('-LargeFileSupport=1')
        args.append("-execute\n")
        args_tuple = tuple(args)
        file_args = str.join("\n", args_tuple)

        #---------------------------------------------------
        # This will remove combining "ring above a" characters with pre-composed å character in UTF.
        # Python translates to system-encoding (CP1252) before passing string to system. Python can't
        # translate the combining characters to system-encoding (CP1252). It needs to be normalized.
        # All combined characters will be replaced with pre-composed characters that can be translated.
        file_args = unicodedata.normalize("NFC", file_args)
        #-----------------------------------------------------

        process.stdin.write(file_args)
        process.stdin.flush()
        output = ""
        fd = process.stdout.fileno()
        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8', errors='replace')
        return output[:-len(self.sentinel)]

    def getTags(self, filenames, tags=[]):           #Gets all metadata of files if tags is empty or not supplied
        args = []
        tags.append('XMP:MemoryMateSaveDateTime')
        for tag in tags:
            if tag[0]!='-':
                tag='-'+tag
            args.append(tag)
        args.append('-G')
        args.append('-j')
        args.append('-n')
        if type(filenames)==str:
            args.append(filenames)
            file_to_return=filenames
        else:
            for filename in filenames:
                args.append(filename)
        tags_to_return = self.execute((args),ExifTool.read_process)
        return json.loads(tags_to_return)

    def setTags(self, filenames, tag_values={}):
        if tag_values=={}:
            pass                                    #Quick return if no tags to set
        tag_values['XMP:MemoryMateSaveDateTime']=datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        args = []
        for tag in tag_values:
            if isinstance(tag_values[tag],str):
                if '\n' in tag_values[tag]:                                      # Text contains lineshift
                    tag_value = tag_values[tag].replace('\n', '\\n')             # Hex 0A (newline) replaced by Hex 5C 6E (Characters \n )
                    args.append('#[CSTR]' + '-' + tag + '=' + tag_value)         # #[CSTR] tells exiftool to accept escape-caracter sequence in argument
                else:
                    args.append('-' + tag + '=' + tag_values[tag])
            else:                                                               # assuming tag_value is a list (eg. persons in image)
                if tag_values[tag] == []:
                    args.append('-' + tag + '=')
                else:
                    for tag_value_item in tag_values[tag]:
                        args.append('-' + tag + '=' + tag_value_item)               # adds tag_value_items one at the time (e.g. persons)


        if type(filenames)==str:
            args.append(filenames)
        else:
            for filename in filenames:
                args.append(filename)
        return self.execute(args,ExifTool.write_process)





