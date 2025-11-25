from view.windows.login_window import LoginWindow
from controller.events.emitters.login_window_result_emitter import LoginWindowResultEmitter
from services.integration_services.garmin_integration import GarminIntegration
def onLoginWindowResult(login_window:LoginWindow):
    service,button,user,password,mfa_code = login_window.getInfo()
    if service=='garmin_connect' and button=='ok':
        garmin_integration = GarminIntegration.getInstance()
        garmin_integration.garminApiPasswordLogin(login_window)



