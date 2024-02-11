import signal
import subprocess
import os
import json
import locale
import unicodedata
from datetime import datetime
import time

class ExifTool(object):
    processes = {}
    read_process=None    # Two exiftool-processes runs in memory, one for read and one for write.
    write_process=None   # ..that way user does not have to wait for background processor to finalize writes from queue
    configuration=''
    executable=None
    sentinel = "{ready}\r\n"
    sys_encoding = locale.getpreferredencoding()
    last_written_filenames = []    #To be able to clean up temp-files at process closure

    # when wrapper calls exiftool, it does so throug windows cmp (command prompt). At the same time parameters are
    # passed through cmd to exiftool (like tag-names, filenames etc).
    # cmd grabs parameters from wrapper (e.g. coded as utf-8). cmd translates parameters into windows system-encoding
    # (e.g. cp1252) before passing them to Exiftool.Exiftool needs to be told what encoding is used for parameters.
    # To tell exiftool what encoding was used, we pass parameter -charset <sys_encoding> (e.g. -charset cp1252) to
    # Exiftool along with the other parameters. (see below in execute-method).

    def __init__(self,executable='exiftool', configuration=''):
        ExifTool.executable = executable
        ExifTool.configuration = configuration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    @staticmethod
    def getProcess(process_id):
        if ExifTool.processes.get(process_id)!=None:                      #Process created
            if ExifTool.processes.get(process_id).poll()!=None:           #Process not running
                del ExifTool.processes[process_id]
        if ExifTool.processes.get(process_id)==None:
            if ExifTool.configuration!='':
                ExifTool.processes[process_id] = subprocess.Popen([ExifTool.executable, "-config", ExifTool.configuration, "-stay_open", "True", "-@", "-"],
                                                                  universal_newlines=True,
                                                                  stdin=subprocess.PIPE,
                                                                  stdout=subprocess.PIPE,
                                                                  creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                ExifTool.processes[process_id] = subprocess.Popen([ExifTool.executable, "-stay_open", "True",  "-@", "-"],
                                                                   universal_newlines=True,
                                                                   stdin=subprocess.PIPE,
                                                                   stdout=subprocess.PIPE,
                                                                   creationflags=subprocess.CREATE_NO_WINDOW)
        return ExifTool.processes.get(process_id)

    @staticmethod
    def closeProcess(process_id='$all'):
        closed_processes = []
        for id, process in ExifTool.processes.items():
            if process_id == '$all' or id == process_id:
                if process!=None:
                    # ExifTool.read_process.send_signal(signal.CTRL_C_EVENT)                    # Terminate whatever process is currently doing
                    # ExifTool.read_process.stdin.flush()                                       # Send termination at once
                    #
                    # ExifTool.read_process.stdin.write("-ver\n -execute\n")                    # Make sure that exiftool is done with terminating process
                    # ExifTool.read_process.stdin.flush()                                       # by asking for version and waiting for answer back
                    # fd = ExifTool.read_process.stdout.fileno()
                    # output = ""
                    # while not output.endswith(ExifTool.sentinel):
                    #     output += os.read(fd, 4096).decode('utf-8', errors='replace')
                    process.stdin.write("-stay_open\nFalse\n -execute\n")  # Set process to terminate when done with last command
                    process.stdin.flush()
                    process.wait()
                    closed_processes.append(id)
        for id in closed_processes:
            del ExifTool.processes[id]


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
        args.append('largefilesupport=1')
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
        message = ""
        fd = process.stdout.fileno()

        message_started = False
        # while True:
        #     chunk = os.read(fd, 4096).decode('utf-8', errors='replace')
        #     if not chunk:
        #         break
        #     if message_started:
        #         message += chunk
        #     else:
        #         if chunk.endswith(self.sentinel):
        #             chunk = chunk[:-len(self.sentinel)]
        #             message_started = True
        #         output += chunk
        # return output, message

        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8', errors='replace')

        process.stdin.flush()    #Don't know if it is needed
        return output[:-len(self.sentinel)]

    def getTags(self, filenames, tags=[],process_id='READ'):           #Gets all metadata of files if tags is empty or not supplied
        args = []
        tags.append('XMP:MemoryMateSaveDateTime')
        for tag in tags:
            if tag[0]!='-':
                tag='-'+tag
            args.append(tag)
        args.append('-G')
        args.append('-j')
#        args.append('-n')
        if type(filenames)==str:
            args.append(filenames)
            file_to_return=filenames
        else:
            for filename in filenames:
                args.append(filename)
        output = self.execute((args),ExifTool.getProcess(process_id))
        return json.loads(output)


    def setTags(self, filenames, tag_values={},process_id='WRITE'):
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
            elif isinstance(tag_values[tag], list):
                if tag_values[tag] == []:
                    args.append('-' + tag + '=')
                else:
                    for tag_value_item in tag_values[tag]:
                        args.append('-' + tag + '=' + str(tag_value_item))      # adds tag_value_items one at the time (e.g. persons)
            elif tag_values[tag] == None:
                args.append('-' + tag + '=')
            else:                                                               # assuming tag_value is a number
                args.append('-' + tag + '=' + str(tag_values[tag]))

        if type(filenames)==str:
            filename = filenames
            args.append(filename)
            ExifTool.last_written_filenames = [filename]
        else:
            ExifTool.last_written_filenames = filenames
            for filename in filenames:
                args.append(filename)

        for filename in ExifTool.last_written_filenames:
            try:
                os.remove(filename + '_exiftool_tmp')  # Remove temporary files, if hanging from an earlier terminated process
            except OSError as e:
                pass

        output = self.execute(args,ExifTool.getProcess(process_id))
        return output






