from view.ui_components.garmin_integration_status import GarminIntegrationStatusMonitor
from services.integration_services.garmin_integration import GarminIntegration

def onGarminIntegrationEvent(event_name:str):
    GarminIntegrationStatusMonitor.getInstance().setStatus(event_name) # Possible values: running/done/no internet/not logged in

