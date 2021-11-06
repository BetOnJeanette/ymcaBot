import asyncio
import json
import logging
import os
import random
import re
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

from classes.timeoutException import timeOutException
from classes.User import User as BotUser

PATH_NAME = os.path.dirname(__file__)

#Get the attribute forms from the json file
with open(PATH_NAME + "\\attributeForms.json") as file:
    ATTR_FORMS = json.loads(file.read())
statChoices = [create_choice(key,ATTR_FORMS[key]["display"]) for key in ATTR_FORMS]

#Set logging on the console
logging.basicConfig(level=logging.INFO)

async def getAudioFiles(folderName):
    return [PATH_NAME + "\\" + folderName + "\\" + file for file in os.listdir(PATH_NAME + "\\" + folderName)]

async def getServerFileName(guildID):
    return PATH_NAME + "/serverCounts/" + str(guildID) + ".json"

async def getFileStat(guildFile):
    #Get the info from the file
    fileStream = open(str(guildFile), "r")
    values = json.loads(fileStream.read())
    fileStream.close()
    for key in values:
        values[key] = BotUser(values[key])
    return values

async def playAudio(audio:list, connected:list, notInVC:list, couldNotConnect:list, ctx:SlashContext):
    author = ctx.author
    # If the request can't be associated with a voice channel, just do a lil joke response
    if isinstance(author, discord.user.User) or author.voice == None:
        await ctx.send(content=notInVC)
        return
        
    else:
        myAudio = random.choice(audio)
        voiceChannel = author.voice.channel
        await ctx.send(content=connected)
        # Create a voice stream
        audioStream = discord.FFmpegPCMAudio(myAudio, executable=config["ffmpegLoc"])
        VCs = [vc for vc in bot.voice_clients if vc.channel.id == voiceChannel.id]
        vc = None
        # If the bot is connected, don't try connecting
        if len(VCs) == 0:
            # Join the voice channel
            vc = await voiceChannel.connect() 
        else:
            vc = VCs[0]

        vc.play(audioStream)
        while vc.is_playing():
            await asyncio.sleep(5)
        await vc.disconnect()

async def ensureUsersAreAvailable(guildId: int, ids: list):
    guildFile = await getServerFileName(guildId)
    values = {}
    ids[:] = [str(item) for item in ids]
    # If there's not a file in there, make a new dict
    if not os.path.exists(guildFile):
        for item in ids:
            values[item] = BotUser()
    
    # If there is a file, get the numbers from it
    else:
        values = await getFileStat(guildFile)
        
        # If the current id is not in the dict, add it
        for item in ids:
            if item not in values:
                values[item] = BotUser()

    return values

async def saveFile(values: dict, guildFile: str):
    for user in values:
        values[user] = await values[user].toJson()

    # Update the file
    fileStream = open(guildFile, "w")
    fileStream.write(json.dumps(values))
    fileStream.close()

async def appendCountMessage(count: int, attributeName: str):
    message = "\nYou have now recieved {} ".format(count)
    if count == 1:
        message += ATTR_FORMS[attributeName]["singular"]
    else:
        message += ATTR_FORMS[attributeName]["plural"]
    return message

async def giveToOtherUser(giver: discord.Member, reciever: discord.Member, guildId: int, attribute: str):
    values = await ensureUsersAreAvailable(guildId, [giver.id, reciever.id])
    author = values[str(giver.id)]
    recieverVal = values[str(reciever.id)]

    # Try having the one person bonk the other
    await author.givesOtherUser(recieverVal, attribute)
    countMessage = await appendCountMessage(getattr(recieverVal, attribute).recieved, attribute)
    
    guildFile = await getServerFileName(guildId)
    await saveFile(values, guildFile)
    return countMessage
    
# Bot instance-specific details
config = json.loads(open("config.json").read())

#Set up the client and commands
bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.

# Entering the server
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@slash.slash(name = "YMCA", description = "Start blaring YMCA in the vc you are in!", \
    guild_ids=config["GUILD_IDS"])
async def playYMCA(ctx):
    notInVC = "I mean, this won't be *as* good... uh... \n \
            \U0001F3B6 YYY M C A, it's fun to stay at the YYY M C A-A \U0001F3B6"
    audio = await getAudioFiles("ymca")
    connected = "Now playing YMCA"
    couldNotConnect = "Cannot connect right now"
    await playAudio(audio, connected, notInVC, couldNotConnect, ctx)
    

@slash.slash(name="bonk", description="Send someone to horny jail", \
    guild_ids=config["GUILD_IDS"], options=[create_option("bonked", "Who you want to send to horny jail", 6, False),\
    create_option("reason", "Why are you bonking?", 3, False)])
async def bonk(ctx: SlashContext, bonked: discord.Member = None, reason: str = None):
    connected = random.choice(ATTR_FORMS["bonks"]["responses"])
    audio = await getAudioFiles("bonk")
    couldNotConnect = random.choice(["Cannot bonk right now", "Not within bonking range", "Bonking bat is in the shop"])

    # If someone is bonked, append a mention to the start of the response
    if bonked != None:
        # Try having the one person bonk the other
        try:
            countMessage = await giveToOtherUser(ctx.author, bonked, ctx.guild_id, "bonks")
        except timeOutException as ex:
            await ctx.send(ex.message)
            return
        # Tell them how many times they have been bonked
        connected = bonked.mention + connected + countMessage
        notInVc = connected
    else:
        # Lets pretend that we have other options for if the user who calls it is not in the vc
        notInVc = connected + ", but silently" 

    if reason != None:
        connected = connected + "\n\nThe bonk was because \"" + reason + "\""
        notInVc = connected + "\n\nThe bonk was because \"" + reason + "\"" 
    await playAudio(audio, connected, notInVc, couldNotConnect, ctx)
    
@slash.slash(name="uwu-ify", description="turn a message into UwU speak", \
    guild_ids=config["GUILD_IDS"], options=[create_option("message", "The message you want to UwU-ify", 3, True)])
async def uwuify(ctx: SlashContext, message: str):
    EYES = "[ou]{2}"
    MOUTH = "w"
    message = message.lower()
    message = re.sub("[rl]", "w", message)
    message = re.sub("[RL]", "W", message)

    # message = re.sub("th", "ff", message)
    for character in "aeiou":
        message = re.sub("n" + character, "ny" + character, message)
    message = re.sub("ove", "uv", message)

    eyesInMessage = re.compile(EYES).search(message)
    while eyesInMessage:
        message = message[:eyesInMessage.span()[0] + 1] + MOUTH + message[eyesInMessage.span()[0] + 1:]
        eyesInMessage = re.compile(EYES).search(message)
    
    await ctx.send(message)

@slash.slash(name= "boop", description= "boop a snoot", guild_ids=config["GUILD_IDS"], \
    options=[create_option("booped", "Whoever you want to boop", 6, False), create_option("reason", "Why are you booping?", 3, False)])
async def boop(ctx: SlashContext, booped: discord.Member = None, reason: str = None):
    response = random.choice(ATTR_FORMS["boops"]["responses"])
    
    if booped != None:
        countMessage = await giveToOtherUser(ctx.author, booped, ctx.guild_id, "boops")

        response = booped.mention + ", " + ctx.author.mention + " booped you! " + response 
        response += countMessage
    if reason:
        response += "\n\nThe boop was because \""+ reason +"\""
    await ctx.send(response)

@slash.slash(name="stats", description = "See the stats for all of the given items in the server",\
    guild_ids= config["GUILD_IDS"], options = [create_option("attribute", "The attribute you want to see stats of", 3, True, statChoices),\
    create_option("user", "The member you want to see stats of", 6, False)])
async def boopStats(ctx: SlashContext, attribute: str, user: discord.Member = None):

    respEmbed = {
        "title": ATTR_FORMS[attribute]["singular"].title() + " stats",
        "description": "Currently, nobody has been " + ATTR_FORMS[attribute]["past"]
    }

    guildFile = await getServerFileName(ctx.guild_id)
    
    # If a user was requested, change the default message
    if user != None:
        respEmbed["title"] += " for {}".format(user.display_name)
        respEmbed["description"] = "{0} has not been {1} yet! \n\nThey have not {1} anyone yet!".format(user.display_name, ATTR_FORMS[attribute]["past"])

    # If the file doesn't exist, say nobody has been bonked
    if os.path.exists(guildFile):
        stats = await getFileStat(guildFile)
        # If there was no user requested, give the full list
        if user == None:
            # Fetch the guild 
            guild = await bot.fetch_guild(ctx.guild_id)
            if BotUser.isGiveable(attribute):
                stats = [ (await guild.fetch_member(int(key))).display_name + ": " + \
                    str(getattr(val, attribute).recieved) for (key, val) in sorted(stats.items(), \
                    key = lambda x: getattr(x[1], attribute).recieved, reverse= True) \
                    if getattr(val, attribute).recieved != 0]
            else:
                stats = [ (await guild.fetch_member(int(key))).display_name + ": " + \
                    str(getattr(val, attribute)) for (key, val) in sorted(stats.items(), \
                    key = lambda x: getattr(x[1], attribute), reverse= True) \
                    if getattr(val, attribute) != 0]
            respEmbed["description"] = "\n".join(stats) + "\n\n" + ATTR_FORMS[attribute]["end message"]
        # If there was a user requested, give their count
        else:
            userId = str(user.id)
            # If they're in the dict, show how many times they've been bonked
            if userId in stats:
                inQuestion = stats[userId]
                respEmbed = await getattr(inQuestion, attribute).individualStatEmbed(user.display_name, attribute)
                
            #Set the embed color to the user's color
            respEmbed["color"] = user.color.value
    await ctx.send(embed=discord.Embed.from_dict(respEmbed))

@slash.slash(name = "facePalm", description = "show your dissapointment with a facepalm",\
    guild_ids = config["GUILD_IDS"], options = [create_option("reason", "Why are you facepalming?", 3, False)])
async def facePalm(ctx: SlashContext, reason: str = None):
    values = await ensureUsersAreAvailable(ctx.guild_id, [ctx.author_id])
    values[str(ctx.author_id)].facePalms += 1

    await ctx.send(random.choice(ATTR_FORMS["facePalms"]["responses"]))
    secondMessage = ""
    if reason != None:
        secondMessage = "Facepalming because \"" + reason + "\"\n"
    
    secondMessage += "You have facepalmed {} time".format(values[str(ctx.author_id)].facePalms)
    if values[str(ctx.author_id)].facePalms > 1:
        secondMessage += "s"
    guildFile = await getServerFileName(ctx.guild_id)
    await saveFile(values, guildFile)
    await ctx.channel.send(secondMessage)
bot.run(config["BOT_TOKEN"])
