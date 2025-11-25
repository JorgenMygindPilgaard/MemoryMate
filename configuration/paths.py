import os
import sys


class Paths:
    paths = {}

    @staticmethod
    def get(path_id):
        return Paths.paths.get(path_id)

    @staticmethod
    def _initialize():
        Paths.paths['exe'] = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.exists(os.path.join(Paths.paths['exe'],"_distributable.txt")):  # existence of distributable.txt indicates that the program is in a distributable folder (with subfolder for data)
            Paths.paths['data'] = os.path.join(Paths.paths['exe'], "Data")
        else:
            Paths.paths['data'] = os.path.join(os.environ.get("ProgramData"), "Memory Mate")
        if not os.path.isdir(Paths.paths['data']):
            os.mkdir(Paths.paths['data'])

        if hasattr(sys, '_MEIPASS'):     # Execute an installed version
            Paths.paths['resources']=os.path.join(sys._MEIPASS, 'resources')
        else:                           # Execute in debugging
            Paths.paths['resources']='resources'





        Paths.paths['settings']=os.path.join(Paths.paths['data'], "settings.json")  # Path to settings-file
        Paths.paths['queue']=os.path.join(Paths.paths['data'], "queue.json")         # Path to settings-file
        Paths.paths['lr_queue']=os.path.join(Paths.paths['data'], "lr_queue.json")   # Path to settings-file
        Paths.paths['ui_status']=os.path.join(Paths.paths['data'], "ui_status.json")
        Paths.paths['current_image']=os.path.join(Paths.paths['data'], "current_image.html")
        Paths.paths['gps_location_db']=os.path.join(Paths.paths['data'], "gps_location.db")
        Paths.paths['garmin_token']=os.path.join(os.path.expanduser("~"),"memorymate_garmin_token")


Paths._initialize()






