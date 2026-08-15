from typing import Any, Mapping

from push_receiver import AsyncPushReceiver


class FCMListener:
    """An async Rust+ FCM notification listener.

    Subclasses may implement ``on_notification`` as either a regular function
    or an ``async def`` coroutine.  ``start`` runs until ``stop`` is called.
    """

    def __init__(self, data: Mapping[str, Any]) -> None:
        if data is None:
            raise ValueError("data must not be None")
        if "fcm_credentials" not in data:
            raise ValueError("data must contain fcm_credentials")

        self.data = data
        self._push_listener = AsyncPushReceiver(
            credentials=self.data["fcm_credentials"]
        )

    def on_notification(self, obj, notification, data_message) -> None:
        """Handle a received FCM notification.

        Override this method in a subclass.  The async receiver also accepts
        coroutine overrides of this method.
        """

    async def __aenter__(self) -> "FCMListener":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.stop()

    @property
    def is_running(self) -> bool:
        return self._push_listener.is_running

    async def start(self) -> None:
        """Listen for FCM messages until :meth:`stop` is awaited."""
        await self._push_listener.listen(callback=self.on_notification)

    async def stop(self) -> None:
        """Stop listening without waiting for the socket read timeout."""
        await self._push_listener.stop()
