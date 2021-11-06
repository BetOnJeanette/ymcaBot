from .Giveable import Giveable
from .GivableWithTimeout import GivableWithTimeout
import json

class User:
    # Use an object to initialize them
    def __init__(self, obj: dict = None):
        if obj != None:
            if "bonks" in obj:
                self.bonks = GivableWithTimeout.fromJson(obj["bonks"])
            else:
                self.bonks = GivableWithTimeout()
            if "boops" in obj:
                self.boops = Giveable.fromJson(obj["boops"])
            else:
                self.boops = Giveable()
            if "face palms" in obj:
                self.facePalms = obj["face palms"]
            else:
                self.facePalms = 0
        else:
            self.bonks = GivableWithTimeout()
            self.boops = Giveable()
            self.facePalms = 0
        
    
    async def toJson(self):
        returnedObj = {}
        bonks = await self.bonks.toJson()
        if len(bonks) > 0:
            returnedObj["bonks"] = bonks
        boops = await self.boops.toJson()
        if len(boops) > 0:
            returnedObj["boops"] = boops
        if self.facePalms > 0:
            returnedObj["face palms"] = self.facePalms
        return returnedObj

    @staticmethod
    def isGiveable(att):
        return not att == "facePalms"

    async def givesOtherUser(self, reciever, attribute):
        await getattr(self, attribute).give(getattr(reciever, attribute))