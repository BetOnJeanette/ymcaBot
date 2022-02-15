from .Giveable import Giveable
from .GivableWithTimeout import GivableWithTimeout
import json

class User:
    # Use an object to initialize them
    def __init__(self, obj: dict = None):
        self.bonks = GivableWithTimeout()
        self.boops = Giveable()
        self.facePalms = 0
        if obj != None:
            for item in ["bonks", "boops", "face palms"]:
                if item in obj:
                    # Convert from the obj formating to the class formating
                    selfItem = item.split(" ")
                    for i in range(1, len(selfItem)):
                        selfItem[i] = selfItem[i].title()
                    selfItem = "".join(selfItem)

                    # Set the item to the listed item
                    # If it isn't a givable, just set it
                    if isinstance(self.__getattribute__(selfItem), int):
                        self.__setattr__(selfItem, obj[item])
                    # If it is a givable, use fromJson
                    else:    
                        self.__setattr__(selfItem, self.__getattribute__(selfItem).__class__.fromJson(obj[item]))

    def toJson(self):
        returnedObj = {}
        bonks = self.bonks.toJson()
        if len(bonks) > 0:
            returnedObj["bonks"] = bonks
        boops = self.boops.toJson()
        if len(boops) > 0:
            returnedObj["boops"] = boops
        if self.facePalms > 0:
            returnedObj["face palms"] = self.facePalms
        return returnedObj

    @staticmethod
    def isGiveable(att):
        return not att == "facePalms"

    def givesOtherUser(self, reciever, attribute):
        getattr(self, attribute).give(getattr(reciever, attribute))