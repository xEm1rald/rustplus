from push_receiver import PushReceiver
from threading import Thread, Event


class FCMListener:
    def __init__(self, data: dict = None) -> None:
        self.thread = None
        self.data = data
        self._push_listener = PushReceiver(credentials=self.data["fcm_credentials"])

    def on_notification(self, obj, notification, data_message) -> None:
        pass

    def start(self, daemon=False, close_event: Event=None) -> None:
        self.thread = Thread(target=self.__fcm_listen, args=(close_event,), daemon=daemon).start()

    def __fcm_listen(self, close_event=None) -> None:
        if self.data is None:
            raise ValueError("Data is None")

        self._push_listener.listen(callback=self.on_notification, close_event=close_event)
