from .Giveable import Giveable
import json
from datetime import datetime, timezone, timedelta
from .timeoutException import timeOutException

class GivableWithTimeout(Giveable):
    def __init__(self, given: int = 0, recieved: int = 0, timeout: datetime = datetime.now(timezone.utc)):
        super().__init__(given, recieved)
        self.timeout = timeout
        
    
    async def toJson(self):
        myObj = await super().toJson()
        if self.timeout > datetime.now(tz = timezone.utc):
            myObj["timeout"] = self.timeout.timestamp()
        return myObj

    async def updateTimeout(self, timeoutDuration: timedelta = timedelta(seconds=30)):
        self.timeout = datetime.now(timezone.utc) + timeoutDuration

    async def give(self, reciever):
        if datetime.now(timezone.utc) < self.timeout:
            raise timeOutException(self.timeout)
        await super().give(reciever)
        await self.updateTimeout()
    
    @classmethod
    def fromJson(cls, obj: dict):
        
        returnedItem = cls()
        if "timeout" in obj:
            obj["timeout"] = datetime.fromtimestamp(obj["timeout"], timezone.utc)

        compObj = Giveable.getCompObj()
        compObj["timeout"] = datetime.now(timezone.utc)

        for key in obj:
            if key in compObj and obj[key] > compObj[key]:
                setattr(returnedItem, key, obj[key])
        return returnedItem