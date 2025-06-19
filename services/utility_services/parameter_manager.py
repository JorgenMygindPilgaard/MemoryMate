import os
import json

class ParameterManager():
    instance_index = {}
    get_instance_active = False

    def __init__(self,file_name: str=""):
#       Check that getInstance was used
        if not ParameterManager.get_instance_active:
            raise Exception('Please use getInstance method')
#       Create new instance
        self.parameter_file_name = file_name
        ParameterManager.instance_index[file_name] = self

#       Initialize parameters and read from file, if exists
        self.parameters = {}
        if os.path.exists(self.parameter_file_name):
            with open(self.parameter_file_name, 'r') as infile:
                self.parameters = json.load(infile)
                
    @staticmethod
    def getInstance(file_name: str=""):
        parameter_manager = ParameterManager.instance_index.get(file_name)
        if parameter_manager is None:
            ParameterManager.get_instance_active = True
            parameter_manager = ParameterManager(file_name)
            ParameterManager.get_instance_active = False
        return parameter_manager

    def setParameters(self,parameters={}):
        # Add or replace status-parameters
        for parameter_name in parameters:
            self.parameters[parameter_name]=parameters[parameter_name]

    def getParameters(self):
        return self.parameters
    def getParameter(self, parameter_name: str):
        return self.parameters.get(parameter_name)

    def save(self):
        # Save status-parameters in file
        parameters_json_object = json.dumps(self.parameters, indent=4)
        with open(self.parameter_file_name, "w") as outfile:
            outfile.write(parameters_json_object)

