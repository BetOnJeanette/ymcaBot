from datetime import datetime, timezone

class timeOutException(Exception):
    def __init__(self, timeout: datetime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = "You still have to wait {} seconds before you bonk again"\
                .format((timeout - datetime.now(timezone.utc)).seconds)