from PyQt6.QtCore import QObject, pyqtSignal

class GarminIntegrationEventEmitter(QObject):
    instance = None
    event_signal = pyqtSignal(str)  # running/done/no internet/not logged or start_request

    def __init__(self):
        super().__init__()

    @staticmethod
    def getInstance():
        if GarminIntegrationEventEmitter.instance is None:
            GarminIntegrationEventEmitter.instance = GarminIntegrationEventEmitter()
        return GarminIntegrationEventEmitter.instance
    def emit(self, event_name):
        self.event_signal.emit(event_name)