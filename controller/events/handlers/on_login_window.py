from view.windows.login_window import LoginWindow
from controller.events.emitters.login_window_result_emitter import LoginWindowResultEmitter

def onLoginWindow(login_window:LoginWindow):
    login_window.show()
    LoginWindowResultEmitter.getInstance().emit(login_window)   # login_window instance contains credentials


