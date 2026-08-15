import inspect
import unittest
from unittest.mock import patch

from rustplus.remote.fcm import FCMListener


class FakeAsyncPushReceiver:
    def __init__(self, credentials):
        self.credentials = credentials
        self.is_running = False
        self.stopped = False

    async def listen(self, callback):
        self.is_running = True
        result = callback(None, {"channelId": "pairing"}, "message")
        if inspect.isawaitable(result):
            await result
        self.is_running = False

    async def stop(self):
        self.stopped = True


class AsyncFCMListenerTests(unittest.IsolatedAsyncioTestCase):
    DATA = {"fcm_credentials": {"gcm": {}}}

    def test_requires_fcm_credentials(self):
        with self.assertRaisesRegex(ValueError, "fcm_credentials"):
            FCMListener({})

    async def test_uses_async_push_receiver_and_awaits_callback(self):
        with patch(
            "rustplus.remote.fcm.fcm_listener.AsyncPushReceiver",
            FakeAsyncPushReceiver,
        ):
            class Listener(FCMListener):
                def __init__(self, data):
                    super().__init__(data)
                    self.notifications = []

                async def on_notification(self, obj, notification, data_message):
                    self.notifications.append((notification, data_message))
                    await self.stop()

            listener = Listener(self.DATA)
            await listener.start()

        self.assertEqual(
            listener.notifications,
            [({"channelId": "pairing"}, "message")],
        )
        self.assertTrue(listener._push_listener.stopped)
        self.assertFalse(listener.is_running)


if __name__ == "__main__":
    unittest.main()
