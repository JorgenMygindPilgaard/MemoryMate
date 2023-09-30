import os
import json

class UiStatusManager():
    __instance = None
    __status_file_name = ""
    def __init__(self,status_file_name: str=""):
        UiStatusManager.__status_file_name = status_file_name
        self.status_parameters = {}
        if os.path.exists(UiStatusManager.__status_file_name):
            with open(UiStatusManager.__status_file_name, 'r') as infile:
                self.status_parameters = json.load(infile)
    @staticmethod
    def getInstance(status_file_name: str=""):
        if UiStatusManager.__instance == None or status_file_name != "" and status_file_name != UiStatusManager.__status_file_name:
            UiStatusManager.__instance = UiStatusManager(status_file_name)
        return UiStatusManager.__instance

    def setUiStatusParameters(self,status_parameters={}):
        # Add or replace status-parameters
        for parameter_name in status_parameters:
            self.status_parameters[parameter_name]=status_parameters[parameter_name]

    def getStatusParameters(self):
        return self.status_parameters
    def getStatusParameter(self, parameter_name: str):
        return self.status_parameters.get(parameter_name)

    def save(self):
        # Save status-parameters in file
        status_parameters_json_object = json.dumps(self.status_parameters, indent=4)
        with open(UiStatusManager.__status_file_name, "w") as outfile:
            outfile.write(status_parameters_json_object)

