import os
import json

class UiStatusManager():
    def __init__(self,status_file_name: str=""):
        self.status_file_name = status_file_name
        self.status_parameters = {}
        if os.path.exists(self.status_file_name):
            with open(self.status_file_name, 'r') as infile:
                self.status_parameters = json.load(infile)

    def setUiStatusParameters(self,status_parameters={}):
        # Write or replace status-parameters in status file
        for parameter_name in status_parameters:
            self.status_parameters[parameter_name]=status_parameters[parameter_name]
        status_parameters_json_object = json.dumps(status_parameters, indent=4)
        with open(self.status_file_name, "w") as outfile:
            outfile.write(status_parameters_json_object)

    def getStatusParameters(self):
        return self.status_parameters
    def getStatusParameter(self, parameter_name: str):
        return self.status_parameters.get(parameter_name)
