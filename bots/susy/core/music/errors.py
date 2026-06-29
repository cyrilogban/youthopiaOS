class DownloadFailedError(Exception):
    """Raised when a track source cannot be downloaded."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
