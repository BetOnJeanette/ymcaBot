import json
from os import path

#Load in the attribute forms file
FILE_DIR = path.dirname(__file__) + "\\..\\attributeForms.json"

with open(FILE_DIR) as file:
    ATTR_FORMS = json.loads(file.read())


class Giveable:
    def __init__(self, given: int = 0, recieved: int = 0):
        self.given = given
        self.recieved = recieved
    
    async def toJson(self):
        outObj = {}

        compObj = Giveable.getCompObj()
        for key in compObj:
            if getattr(self, key) > compObj[key]:
                outObj[key] = getattr(self, key)
        
        return outObj
    
    async def __str__(self):
        return await json.dumps(self.toJson())

    async def incrementRecieved(self, count: int = 1):
        self.recieved += count

    async def give(self, reciever):
        self.given += 1
        await reciever.incrementRecieved()
    
    @staticmethod
    def getCompObj():
        return {
            "given": 0,
            "recieved": 0
        }

    @classmethod
    def fromJson(cls, obj: dict):
        # Generate a new form of the class
        returnedItem = cls()
        # Go through all of the attributes that are in the file
        for key in obj:
            # If it's a vaild key, add it to the atts
            compObj = Giveable.getCompObj()
            if key in compObj:
                setattr(returnedItem, key, obj[key])

        return returnedItem
    
    async def individualStatEmbed(self, displayName: str, attributeName):
        respEmbed = {
            "title": ATTR_FORMS[attributeName]["singular"].title() + " Stats for " + displayName,
            "description": displayName
        }
        
        if self.recieved == 0:
            respEmbed["description"] += " has not not recieved any " + ATTR_FORMS[attributeName]["plural"]
        elif self.recieved == 1:
            respEmbed["description"] += " has  recieved 1 " + ATTR_FORMS[attributeName]["singular"]
        else:
            respEmbed["description"] += " has recieved " + str(self.recieved) + " " + ATTR_FORMS[attributeName]["plural"]
        

        respEmbed["description"] += "!\n\n"
        if self.given == 0:
            respEmbed["description"] += "They have not " + ATTR_FORMS[attributeName]["past"] + " anyone yet"
        elif self.given == 1:
            respEmbed["description"] += "They have " + ATTR_FORMS[attributeName]["past"] + " a member of this server once"
        else:
            respEmbed["description"] += "They have " + ATTR_FORMS[attributeName]["past"] + " members of this server " + str(self.given) + " times"
        respEmbed["description"] += "!"

        return respEmbed