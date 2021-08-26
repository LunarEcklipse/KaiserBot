import discord
import discord.ext.tasks
import json
import asyncio
from datetime import datetime, timedelta
import time
import random
import math
import os
import pytz
from fuzzywuzzy import fuzz
from pytz import timezone
import pytz
from dpyConsole import Console

version = "1.1.0-alpha"

absPath = os.path.abspath(__file__) # This little chunk makes sure the working directory is correct.
dname = os.path.dirname(absPath)
os.chdir(dname)
random.seed(round(time.time())) # Hopefully by putting this here, this will fix the bug which caused messages to constantly have the same factoid.

### TIMESTAMP STUFF ###

def AddZeroBelowTen(inNum): # This function is used for time-stamping as it adds a 0 before any number less than 10 to make it easier to read. It also converts the number to a string so that's cool.
    outStr = ""
    if inNum < 10:
        if inNum >= 0:
            outStr = "0"
        else:
            inNum = abs(inNum)
            outStr = "-0"
    outStr += str(inNum)
    return outStr

def CreateTimestamp():
    ts = time.localtime()
    utcHrs = AddZeroBelowTen(int(ts.tm_gmtoff / 3600))
    utcMin = AddZeroBelowTen(int(ts.tm_gmtoff % 60))
    convert = "[" + str(ts.tm_year) + "-" + AddZeroBelowTen(ts.tm_mon) + "-" + AddZeroBelowTen(ts.tm_mday) + " | " + AddZeroBelowTen(ts.tm_hour) + ":" + AddZeroBelowTen(ts.tm_min) + ":" + AddZeroBelowTen(ts.tm_sec) + " UTC " + utcHrs + ":" + utcMin + "]"
    return convert

### MESSAGE HANDLER ###

async def MessageHandler(client, message):

    file = open(".//data//blacklist.json", 'r')
    raw = file.read()
    file.close()
    blacklist = json.loads(raw)

    ResponseDict = {
        "Responses":
        [
            {
                "Keyword": "difference", # Difference between two time zones
                "RespID": 0
            },
            {
                "Keyword": "diff",
                "RespID": 0
            },
            {
                "Keyword": "time",
                "RespID": 1
            },
            {
                "Keyword": "blacklist",
                "RespID": 2
            },
            {
                "Keyword": "whitelist",
                "RespID": 3
            },
            {
                "Keyword": "register", # For registering people to the bot so their time zone can be tracked.
                "RespID": 4
            }
        ]
    }

    msg = message.content.lower()
    if msg.startswith("!kaiser"):
        print(CreateTimestamp(), " Command detected in:", message.channel)
        msgSplit = msg.split()
        length = 0
        for i in msgSplit:
            length += 1
        respID = 1
        for i in ResponseDict["Responses"]:
            try:
                if msgSplit[1] == i["Keyword"]:
                    respID = i["RespID"]
                    print(CreateTimestamp(), "Command response code found:", respID)
            except(IndexError) as exception:
                print("Fuck")
                respID = 1

        userIsBlacklisted = False
        channelIsBlacklisted = False

        print(respID)

        if respID != 3:
            for i in blacklist["Channels"]:
                if message.channel.id == i["ChannelID"]:
                    print(CreateTimestamp(), "Command detected in " + message.channel.name + ", but the channel is blacklisted.")
                    return
            for i in blacklist["Users"]:
                if message.author.id == i["UserID"]:
                    if i["GuildID"] == message.guild.id:
                        print(CreateTimestamp(), "Command detected from " + message.author.name + ", but the user is blacklisted from the bot in this guild.")
                    return
        else:
            for i in blacklist["Channels"]:
                if message.channel.id == i["ChannelID"]:
                    channelIsBlacklisted = True
            for i in blacklist["Users"]:
                if message.author.id == i["UserID"]:
                    userIsBlacklisted = True

        if respID == 0:
            await CommandDifference(message, msgSplit)
            return
        if respID == 1:
            await CommandTime(message, msgSplit)
            return
        if respID == 2:
            blacklistSuccess = CommandBlacklist(message, msgSplit)
            if blacklistSuccess == True:
                await message.add_reaction("❌")
            else:
                await message.channel.send("You do not have the required permissions to perform this action", reference = message)
            return
        if respID == 3:
            whitelistSuccess = CommandWhitelist(message, msgSplit, userIsBlacklisted, channelIsBlacklisted)
            return
        if respID == 4:
            CommandRegister(message, msgSplit)
            return
        return
    else:
        file = open(".\\data\\system\\response.json", 'r')
        raw = file.read()
        file.close()
        response = json.loads(raw)

        await ResponseHandler(client, message, msg, response)
        return

### COMMANDS ###

def CommandBlacklist(message, msgSplit): # TODO: Update this to determine if it's a user or channel and fix it
    try:
        check = msgSplit[2]
    except(IndexError) as exception: # If this field is left blank, assume they are trying to blacklist the channel.
        permissions = message.author.permissions_in(message.channel)
        if permissions.manage_permissions == False and permissions.administrator == False:
            return False
        BlacklistChannel(message.channel.id)
        return True
    if check == "me" or check == "myself":
        BlacklistUser(message.author.id, message.guild.id, False)
        return True
    mentions = message.mentions
    blacklists = 0
    for i in mentions:
        if message.author.id == i.id:
            BlacklistUser(message.author.id, message.guild.id, False)
            blacklists += 1
        else:
            permissions = message.author.permissions_in(message.channel)
            if permissions.administrator == True or permissions.manage_roles == True:
                BlacklistUser(i.id, message.guild.id, True)
                blacklists += 1
    if blacklists != 0:
        return True
    else:
        return False

def CommandWhitelist(message, msgSplit, userBlacklisted, channelBlacklisted):
    try:
        check = msgSplit[2]
    except(IndexError) as exception: # If this field is left blank, assume they are trying to whitelist the channel.
        permissions = message.author.permissions_in(message.channel)
        if permissions.manage_permissions == False and permissions.administrator == False:
            return False
        WhitelistChannel(message.channel.id)
        return True
    if check == "me" or check == "myself":
        if channelBlacklisted == True:
            print(CreateTimestamp() + " User " + message.author.name + " tried to whitelist themself, but the channel is blacklisted.")
            return False
        permissions = message.author.permissions_in(message.channel)
        adminAttempt = False
        if permissions.manage_permissions == True or permissions.administrator == True:
            adminAttempt = True
        WhitelistUser(message.author.id, message.guild.id, adminAttempt)
        return True
    mentions = message.mentions
    whitelists = 0
    for i in mentions:
        if message.author.id == i.id:
            if channelBlacklisted == True:
                print(CreateTimestamp() + " User " + message.author.name + " tried to whitelist themself, but the channel is blacklisted.")
                return False
            adminAttempt = False
            permissions = message.author.permissions_in(message.channel)
            if permissions.manage_permissions == True or permissions.administrator == True:
                adminAttempt = True
            WhitelistUser(message.author.id, message.guild.id, adminAttempt)
            whitelists += 1
            continue
        else:
            if channelBlacklisted == True or userBlacklisted == True:
                 print(CreateTimestamp() + " User " + message.author.name + " tried to use a whitelist command, but they were stopped by the blacklist.")
                 continue
            permissions = message.author.permissions_in(message.channel)
            if permissions.administrator == True or permissions.manage_roles == True:
                WhitelistUser(i.id, message.guild.id, True)
                whitelists += 1
    if whitelists != 0:
        return True
    else:
        return False

### ### BLACKLIST / WHITELIST ### ###

def BlacklistChannel(ChannelID):
    try:
        file = open(".//data//blacklist.json", 'r')
    except(FileNotFoundError) as exception:
        print(CreateTimestamp(), "blacklist.json not found! Making a new one.")
        file = open(".//data//blacklist.json", 'x')
        file.close()
        file = open(".//data//blacklist.json", 'w')
        file.write("{\"Channels\": [], \"Users\": []}")
        file.close()
        file = open(".//data//blacklist.json", 'r')
    raw = file.read()
    blacklist = json.loads(raw)
    file.close()
    for i in blacklist["Channels"]:
        if i["ChannelID"] == ChannelID:
            print(CreateTimestamp(), "This channel is already blacklisted.")
            return
    blacklist["Channels"].append({"ChannelID": ChannelID})
    raw = json.dumps(blacklist)
    file = open(".//data//blacklist.json", 'w')
    file.write(raw)
    file.close()
    print(CreateTimestamp(), "Channel with ID", ChannelID, "blacklisted.")
    return

def BlacklistUser(UserID, GuildID, AdminBlacklist): # Admin blacklist means the user was blacklisted by someone with privileges and they cannot whitelist themselves if they do not have the same perms.
    try:
        file = open(".//data//blacklist.json", 'r')
    except(FileNotFoundError) as exception:
        print(CreateTimestamp(), "blacklist.json not found! Making a new one.")
        file = open(".//data//blacklist.json", 'x')
        file.close()
        file = open(".//data//blacklist.json", 'w')
        file.write("{\"Channels\": [], \"Users\": []}")
        file.close()
        file = open(".//data//blacklist.json", 'r')
    raw = file.read()
    blacklist = json.loads(raw)
    file.close()
    for i in blacklist["Users"]:
        if i["UserID"] == UserID:
            print(CreateTimestamp(), "This user is already blacklisted.")
            return
    blacklist["Users"].append({"GuildID": GuildID, "UserID": UserID, "AdminBlacklisted": AdminBlacklist})
    raw = json.dumps(blacklist)
    file = open(".//data//blacklist.json", 'w')
    file.write(raw)
    file.close()
    print(CreateTimestamp(), "User with ID: " + str(UserID) + " blacklisted in guild with ID: " + str(GuildID) + ".")
    return

def WhitelistUser(UserID, GuildID, AdminWhitelist):
    try:
        file = open(".//data//blacklist.json", 'r')
    except(FileNotFoundError) as exception:
        print(CreateTimestamp(), "blacklist.json not found! Making a new one.")
        file = open(".//data//blacklist.json", 'x')
        file.close()
        return
    raw = file.read()
    blacklist = json.loads(raw)
    for i in blacklist["Users"]:
        if i["UserID"] == UserID:
            if i["AdminBlacklisted"] == True:
                if AdminWhitelist == False:
                    print(CreateTimestamp(), "This user needs to be whitelisted by an admin.")
                    return False
            indexPos = blacklist["Users"].index(i)
            del blacklist["Users"][indexPos]
            print(CreateTimestamp(), "This user has been whitelisted.")
            break
    raw = json.dumps(blacklist)
    file = open(".//data//blacklist.json", 'w')
    file.write(raw)
    file.close()
    return

def WhitelistChannel(ChannelID):
    try:
        file = open(".//data//blacklist.json", 'r')
    except(FileNotFoundError) as exception:
        print(CreateTimestamp(), "blacklist.json not found! Making a new one.")
        file = open(".//data//blacklist.json", 'x')
        file.close()
        return
    raw = file.read()
    blacklist = json.loads(raw)
    for i in blacklist["Channels"]:
        if i["ChannelID"] == ChannelID:
            indexPos = blacklist["Channels"].index(i)
            del blacklist["Channels"][indexPos]
            print(CreateTimestamp(), "This channel has been whitelisted.")
            break
    raw = json.dumps(blacklist)
    file = open(".//data//blacklist.json", 'w')
    file.write(raw)
    file.close()
    return

### GET DICTS ###

def GetReactionDict():
    reactionDict = { # I had to do it this way because json encodes shit out
        "Reactions":
        [
            {
                "ReactID": 0,
                "Reaction": "❤️"
            },
            {
                "ReactID": 1,
                "Reaction": "🔥"
            },
            {
                "ReactID": 2,
                "Reaction": "❓"
            }
        ]
    }
    return reactionDict


async def ResponseHandler(client, message, msg, response):
    messageContainsPing = False
    if client.user.mentioned_in(message):
        messageContainsPing = True
    for i in response:
        for j in i["contains"]:
            if msg.find(j["text"]) != -1:
                if i["contains_ping"] == True and messageContainsPing == False: # return if the message needs a ping but has none
                    return
                if i["send_message"] == True:
                    count = -1
                    for k in i["text_response"]:
                        count += 1
                        if count == -1:
                            return
                    randNum = random.randint(0, count)
                    replyMsgUnformatted = i["text_response"][randNum]["text"]
                    replyMsg = replyMsgUnformatted.format(message_author = message.author.mention)
                    if i["reply"] == True:
                        await message.channel.send(replyMsg, reference = message)
                    else:
                        await message.channel.send(replyMsg)
                    return
                else:
                    if i["react_to_message"] == True:
                        reactionDict = GetReactionDict()
                        reaction = "❓"
                        for k in reactionDict["Reactions"]:
                            if i["reaction"] == k["ReactID"]:
                                reaction = k["Reaction"]
                        await message.add_reaction(reaction)
        for j in i["message_compare_full"]:
            if msg == j["text"]:
                if i["contains_ping"] == True and messageContainsPing == False: # return if the message needs a ping but has none
                    return
                if i["send_message"] == True:
                    for k in i["text_response"]:
                        count += 1
                    if count == -1:
                        return
                    randNum = random.randint(0, count)
                    replyMsgUnformatted = i["text_response"][randNum]["text"]
                    replyMsg = replyMsgUnformatted.format(message_author = message.author.mention)
                    if i["reply"] == True:
                        await message.channel.send(replyMsg, reference = message)
                    else:
                        await message.channel.send(replyMsg)
                    return
                else:
                    if i["react_to_message"] == True:
                        reactionDict = GetReactionDict()
                        reaction = "❓"
                        for k in reactionDict["Reactions"]:
                            if i["reaction"] == k["ReactID"]:
                                reaction = k["Reaction"]
                        await message.add_reaction(reaction)

def GetBlankEmbed():
    embed = {
        "title": "",
        "description": "",
        "url": "",
        "color": 14010210,
        "thumbnail":
        {
            "url": "https://cdn.discordapp.com/app-icons/863516627739738123/d2904b46279d7e669ee95789c3b87241.png?size=256"
        },
        "footer":
        {
            "text": ""
        },
        "author": 
        {
        },
        "fields":
        [
            {
                "name": "Did you know?",
                "value": ""
            }
        ]
    }
    return embed

def GetMonthConversion():
    monthDict = {
        "Months":
        [
            {
                "mon": 1,
                "name": "January",
                "short": "Jan"
            },
            {
                "mon": 2,
                "name": "February",
                "short": "Feb"
            },
            {
                "mon": 3,
                "name": "March",
                "short": "Mar"
            },
            {
                "mon": 4,
                "name": "April",
                "short": "Apr"
            },
            {
                "mon": 5,
                "name": "May",
                "short": "May"
            },
            {
                "mon": 6,
                "name": "June",
                "short": "Jun"
            },
            {
                "mon": 7,
                "name": "July",
                "short": "Jul"
            },
            {
                "mon": 8,
                "name": "August",
                "short": "Aug"
            },
            {
                "mon": 9,
                "name": "September",
                "short": "Sept"
            },
            {
                "mon": 10,
                "name": "October",
                "short": "Oct"
            },
            {
                "mon": 11,
                "name": "November",
                "short": "Nov"
            },
            {
                "mon": 12,
                "name": "December",
                "short": "Dec"
            }
        ]
    }
    return monthDict

def GetWeekdayDict():
    WeekdayDict = {
        "Weekdays":
        [
            {
                "wday": 0,
                "name": "Monday",
                "short": "Mon"
            },
            {
                "wday": 1,
                "name": "Tuesday",
                "short": "Tues"
            },
            {
                "wday": 2,
                "name": "Wednesday",
                "short": "Wed"
            },
            {
                "wday": 3,
                "name": "Thursday",
                "short": "Thurs"
            },
            {
                "wday": 4,
                "name": "Friday",
                "short": "Fri"
            },
            {
                "wday": 5,
                "name": "Saturday",
                "short": "Sat"
            },
            {
                "wday": 6,
                "name": "Sunday",
                "short": "Sun"
            }
        ]
    }
    return WeekdayDict

async def CommandDifference(message, msgSplit, timezone):
    try:
        tzOne = msgSplit[2]
    except(IndexError) as exception: # If this fails, the command fails.
        message.channel.send()

    tlocal = time.localtime()
    tgmt = time.gmtime()

async def CommandTimeTZ(message, msgSplit):

    try:
        testopen = open(".\\data\\system\\timezones.json", 'r')
        testopen.close()
    except (FileNotFoundError) as exception:
        print(CreateTimestamp(), "timezones.json is missing! This command won't work until it's restored!")
        return
    file = open(".\\data\\system\\timezones.json", 'r')
    raw = file.read()
    file.close()
    timezones = json.loads(raw)

    try:
        timezoneSpec = msgSplit[2].lower()
    except(IndexError) as exception:
        timezoneSpec = msgSplit[1].lower()
    timezonePossibilities = []
    timezoneCount = 0
    for i in timezones["dst"]:
        for j in i["keywords"]:
            if j["value"] == timezoneSpec:
                timezonePossibilities.append(i["name"])
                timezoneCount += 1
    for i in timezones["nodst"]:
        for j in i["timezones"]:
            for k in j["keywords"]:
                if k["value"] == timezoneSpec:
                    timezonePossibilities.append(j["name"])
                    timezoneCount += 1
    if timezoneCount == 0:
        await message.channel.send(message.author.mention + " 'Tis not a timezone by my recollection, I fear.")
        return
    if timezoneCount > 1:
        await message.channel.send(message.author.mention + " 'Tis " + str(timezoneCount) + " timezones by that abbreviation in my recollection.")
    for i in timezonePossibilities:
        for j in timezones["dst"]:
            if j["name"] == i:
                tzname = j["name"]
                tzabbrev = j["abbrev"]
                tzdatabase = pytz.timezone(j["tzdatabase"])
                await CommandTimezoneSendMsg(message, tzname, tzabbrev, tzdatabase, 0)

        for j in timezones["nodst"]:
            for k in j["timezones"]:
                if k["name"] == i:
                    tzname = k["name"]
                    tzabbrev = k["abbrev"]
                    offset = j["offset"]
                    await CommandTimezoneSendMsg(message, tzname, tzabbrev, None, offset)
    return

async def CommandTimezoneSendMsg(message, tzname, tzabbrev, tzdatabase, offset):
    utc = datetime.utcnow() # Gets our current UTC time. Now we can either do this the easy way, or the hard way.
    if tzdatabase != None: # The easy way
        timelocalized = utc.astimezone(tzdatabase) # TO FIX: tzinfo argument must be a None or of a tzinfo subclass, not type 'str'
    else: # The hard way
        isNegative = False
        if offset < 0:
            isNegative = True
        offsethrs = abs(math.floor(offset))
        offsetmins = abs(60 * (offset % 1))
        if isNegative:
            timelocalized = utc - timedelta(minutes=offsetmins, hours=offsethrs)
        else:
            timelocalized = utc + timedelta(minutes=offsetmins, hours=offsethrs)

    timeyear = int(timelocalized.strftime("%Y"))
    timemonth = int(timelocalized.strftime("%m"))
    timedate = int(timelocalized.strftime("%d"))
    timehour = int(timelocalized.strftime("%H"))
    timemin = int(timelocalized.strftime("%M"))
    weekday = timelocalized.weekday()

    AMPM = "AM"
    if timehour > 11: # Update this later to support preferences for 12 or 24 hour time.
        AMPM = "PM"
        if timehour != 12:
            timehour -= 12
    if timehour == 0:
        timehour = 12
    
    timehourstr = AddZeroBelowTen(timehour)
    timeminstr = AddZeroBelowTen(timemin)

    titleString = "In " + tzabbrev + ", 'tis currently " + timehourstr + ":" + timeminstr + " " + AMPM + "."

    currMonth = ""
    MonthDict = GetMonthConversion()
    for i in MonthDict["Months"]:
        if timemonth == i["mon"]:
            currMonth = i["name"]
            break
    
    WeekdayDict = GetWeekdayDict()
    currWkday = ""
    for i in WeekdayDict["Weekdays"]:
        if weekday == i["wday"]:
            currWkday = i["name"]
            break
    
    dateSuffix = "th"
    if (timedate % 10) == 1 and timedate != 11:
        dateSuffix = "st"
    elif (timedate % 10) == 2 and timedate != 12:
        dateSuffix = "nd"
    elif (timedate % 10) == 3 and timedate != 13: ## CONTINUE HERE
        dateSuffix = "rd"

    descString = "There, the date is currently " + currWkday + ", the " + str(timedate) + dateSuffix + " of " + currMonth + ", " + str(timeyear) + ".\nI better recall this time zone as " + tzname + "."
    funFactString = FunFactGenerator()
    
    if tzdatabase != None:
        tzname += " − " + tzdatabase.zone
    tzname += " − Data from IANA Timezone Database"

    msgEmbed = GetBlankEmbed()
    msgEmbed["title"] = titleString
    msgEmbed["description"] = descString
    msgEmbed["footer"]["text"] = tzname
    msgEmbed["fields"][0]["value"] = funFactString

    msgEmbedReady = discord.Embed.from_dict(msgEmbed)

    await message.channel.send(embed=msgEmbedReady)
    return


async def CommandTime(message, msgSplit):
    noTimezone = False
    try:
        testGet = msgSplit[1]
        if testGet == "time":
            noTimezone = True
    except(IndexError) as exception:
        noTimezone = True
    if noTimezone == False:
        await CommandTimeTZ(message, msgSplit)
        return
    noTimezone = False
    try:
        testGet = msgSplit[2]
    except(IndexError) as exception: # This chunk tests if there is a second time zone, in which case a different command needs to be run.
        noTimezone = True
    if noTimezone == False:
        await CommandTimeTZ(message, msgSplit)
        return

    pytz.timezone("Etc/GMT")
    await CommandTimezoneSendMsg(message, "Coordinated Universal Time", "UTC", pytz.timezone("Etc/GMT"), 0) # For the time being, a regular time command returns UTC. Make this a preference thing later.
    return

    hourInt = ts.tm_hour
    if hourInt > 1:
        if hourInt != 12:
            hourInt = hourInt - 12
        AMPM = "PM"
    else:
        AMPM = "AM"
    if hourInt == 0:
        hourInt = 12
    hour = AddZeroBelowTen(hourInt)
    min = AddZeroBelowTen(ts.tm_min)

    timeStamp = hour + ":" + min
    titleString = "\'Tis currently: " + timeStamp + " " + AMPM + "."
    dateSuffix = "th"
    if ts.tm_mday == 1 or ts.tm_mday == 21 or ts.tm_mday == 31:
        dateSuffix = "st"
    elif ts.tm_mday == 2 or ts.tm_mday == 22:
        dateSuffix = "nd"
    elif ts.tm_mday == 3 or ts.tm_mday == 23:
        dateSuffix == "rd"
    
    monthDict = GetMonthConversion()
    currMonth = ""
    for i in monthDict["Months"]:
        if ts.tm_mon == i["mon"]:
            currMonth = i["name"]
            break
    WeekDayDict = GetWeekdayDict()

    currWkday = ""
    for i in WeekDayDict["Weekdays"]:
        if ts.tm_wday == i["wday"]:
            currWkday = i["name"]

    descString = "Today is " + currWkday + ", the " + str(ts.tm_mday) + dateSuffix + " of " + currMonth + ", " + str(ts.tm_year) + ".\nMine current time zone is " + ts.tm_zone + "."
    funFactString = FunFactGenerator()

    msgEmbed = GetBlankEmbed()
    msgEmbed["title"] = titleString
    msgEmbed["description"] = descString
    msgEmbed["footer"]["text"] = ts.tm_zone
    msgEmbed["fields"][0]["value"] = funFactString

    msgEmbedReady = discord.Embed.from_dict(msgEmbed)

    await message.channel.send(embed=msgEmbedReady)


### FUN FACT SHIT ###

def FunFactGenerator():
    random.seed(round(time.time()))
    try:
        file = open(".\\data\\system\\generalfacts.json", 'r')
        raw = file.read()
        file.close()
        generalfacts = json.loads(raw)
    except(FileNotFoundError) as exception:
        print(CreateTimestamp(), "Error: generalfacts.json is missing!")
        return
    count = -1 # starting at -1 since the first position is 0 in an array
    for i in generalfacts:
        count +=1
    randNum = 0
    if count == -1:
        return "null"
    else:
        randNum = random.randint(0, count)
        
        randFactUnformatted = generalfacts[randNum]["text"]
        tz = time.localtime()
        tzOff = tz.tm_gmtoff
        timeEpoch = math.floor(time.time() + tzOff)
        daysBirthdayEpoch = math.floor(timeEpoch / 86400)
        yearsBirthdayEpoch = math.floor(daysBirthdayEpoch / 365.25) # .25 accounts for leap years
        daysBirthday = daysBirthdayEpoch + 203004
        yearsBirthday = yearsBirthdayEpoch + 556
        dateOfYear = tz.tm_yday

        dateOfYearCut = dateOfYear % 100
        dateOfYearCutCut = dateOfYearCut % 10
        dateOfYearSuffix = "th"

        if dateOfYearCutCut == 1 and dateOfYearCut != 11:
            dateOfYearSuffix = "st"
        elif dateOfYearCutCut == 2 and dateOfYearCut != 12:
            dateOfYearSuffix = "nd"
        elif dateOfYearCutCut == 3 and dateOfYearCut != 13:
            dateOfYearSuffix = "rd"

        randFactFormatted = randFactUnformatted.format(daysSinceBirthday = daysBirthday, yearsSinceBirthday = yearsBirthday, daysYear = dateOfYear, dateSuffix = dateOfYearSuffix)
        return randFactFormatted

### ACTUAL SHIT ###

print("Kaiserbot v." + version)
print(CreateTimestamp(), "Awake!")
print(CreateTimestamp(), "Current Working Directory:", os.getcwd())
client = discord.Client()
console = Console(client)

intents = discord.Intents.default() # You may need to access member intents later. Make sure to enable that on the developer portal if that's the case.

@client.event
async def on_ready(): 
    print(CreateTimestamp(), "Kaiser is now ready!")
    
@client.event
async def on_message(message):
    if message.author == client.user: # Don't answer messages from yourself.
        return
    cwd = os.getcwd()
    await MessageHandler(client, message)

file = open(".\\data\\BotToken.key", 'r')
token = file.read()
file.close()

if token == "":
    print(CreateTimestamp(), "Bot token is empty! Make sure that your bot token is in your BotToken.key file!")
    input("Press enter to continue...")
    sys.exit()

console.start()
try:
    client.run(token) # Make sure this is always at the bottom!
except(discord.errors.LoginFailure) as exception:
    print(CreateTimestamp(), "Error: Failed to log in. Make sure that the token in BotToken.key is correct!")
