import discord
import discord.ext.tasks
import json
import asyncio
import time
import random
import math
import os
from dpyConsole import Console

### TIMESTAMP STUFF ###

absPath = os.path.abspath(__file__)
dname = os.path.dirname(absPath)
os.chdir(dname)

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

### TIME ZONE SHIT ###

### MESSAGE HANDLER ###

async def MessageHandler(client, message, timezones):
    ResponseDict = {
        "Responses":
        [
            {
                "Keyword": "difference",
                "RespID": 0
            },
            {
                "Keyword": "diff",
                "RespID": 0
            },
            {
                "Keyword": "time",
                "RespID": 1
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
                    respID = i["ResponseID"]
                    print(CreateTimestamp(), "Command response code found:", respID)
            except(IndexError) as exception:
                respID = 1
            if respID == 0:
                await CommandDifference(message, msgSplit, timezones)
                return
            if respID == 1:
                await CommandTime(message, msgSplit, timezones)
                return
            return
    else:
        file = open("response.json", 'r')
        raw = file.read()
        file.close()
        response = json.loads(raw)

        await ResponseHandler(client, message, msg, response)
        return

### COMMANDS ###

def GetReactionDict():
    reactionDict = { # I had to do it this way because json encodes shit out
        "Reactions":
        [
            {
                "ReactID": 0,
                "Reaction": "❤️"
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
        "author": 
        {
            "name": "Kaiser",
            "url": "",
            "icon_url": "https://cdn.discordapp.com/app-icons/863516627739738123/d2904b46279d7e669ee95789c3b87241.png?size=256"
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

async def CommandTimeTZ(message, msgSplit, timezones):
    try:
        timezoneSpec = msgSplit[2].upper()
    except(IndexError) as exception:
        timezoneSpec = msgSplit[1].upper()
    timezonePossibilities = []
    timezoneCount = 0
    for i in timezones:
        if i["abbr"] == timezoneSpec:
            timezonePossibilities.append(i["value"])
            timezoneCount += 1
    if timezoneCount == 0:
        await message.channel.send(message.author.mention + " 'Tis not a timezone by my recollection, I fear.")
        return
    if timezoneCount > 1:
        await message.channel.send(message.author.mention + " 'Tis " + str(timezoneCount) + " timezones by that abbreviation in my recollection.")
    for i in timezonePossibilities:
        for j in timezones:
            if j["value"] == i:
                value = j["value"]
                abbrev = j["abbr"]
                offset = j["offset"]
                text = j["text"]

                timeNowEpoch = time.time()
                offsetSec = offset * 3600 # converts the offset to seconds to add to epoch
                timeNowEpoch += offsetSec
                timenow = time.gmtime(timeNowEpoch)

                tzYear = timenow.tm_year
                tzMonth = timenow.tm_mon
                tzDay = timenow.tm_mday
                tzHour = timenow.tm_hour
                tzMin = timenow.tm_min
                tzWday = timenow.tm_wday
                
                msgEmbed = GetBlankEmbed()
                WeekdayDict = GetWeekdayDict()
                MonthDict = GetMonthConversion()

                if tzHour > 12:
                    tzHour = tzHour - 12
                    AMPM = "PM"
                else:
                    AMPM = "AM"
                if tzHour == 0:
                    tzHour = 12
                hour = AddZeroBelowTen(tzHour)
                min = AddZeroBelowTen(tzMin)
                titleString = "In " + abbrev + ", 'tis currently " + hour + ":" + min + " " + AMPM + "."

                currMonth = ""
                for i in MonthDict["Months"]:
                    if tzMonth == i["mon"]:
                        currMonth = i["name"]
                        break

                currWkday = ""
                for i in WeekdayDict["Weekdays"]:
                    if tzWday == i["wday"]:
                        currWkday = i["name"]
                        break

                dateSuffix = "th"
                if tzDay == 1 or tzDay == 21 or tzDay == 31:
                    dateSuffix = "st"
                elif tzDay == 2 or tzDay == 22:
                    dateSuffix = "nd"
                elif tzDay == 3 or tzDay == 23:
                    dateSuffix == "rd"

                descString = "There, the date is currently " + currWkday + ", the " + str(tzDay) + dateSuffix + " of " + currMonth + ", " + str(tzYear) + ".\nI better recall this time zone as " + value + "."
                funFactString = FunFactGenerator()

                msgEmbed = GetBlankEmbed()
                msgEmbed["title"] = titleString
                msgEmbed["description"] = descString
                msgEmbed["fields"][0]["value"] = funFactString

                msgEmbedReady = discord.Embed.from_dict(msgEmbed)

                await message.channel.send(embed=msgEmbedReady)


async def CommandTime(message, msgSplit, timezones):
    noTimezone = False
    try:
        testGet = msgSplit[1]
        if testGet == "time":
            noTimezone = True
    except(IndexError) as exception:
        noTimezone = True
    if noTimezone == False:
        await CommandTimeTZ(message, msgSplit, timezones)
        return
    noTimezone = False
    try:
        testGet = msgSplit[2]
    except(IndexError) as exception: # This chunk tests if there is a second time zone, in which case a different command needs to be run.
        noTimezone = True
    if noTimezone == False:
        await CommandTimeTZ(message, msgSplit, timezones)
        return
    ts = time.localtime()
    hourInt = ts.tm_hour
    if hourInt > 12:
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
    msgEmbed["fields"][0]["value"] = funFactString

    msgEmbedReady = discord.Embed.from_dict(msgEmbed)

    await message.channel.send(embed=msgEmbedReady)


### FUN FACT SHIT ###

def FunFactGenerator():
    random.seed(round(time.time()))
    try:
        file = open("generalfacts.json", 'r')
        raw = file.read()
        file.close()
        generalfacts = json.loads(raw)
    except(FileNotFoundError) as exception:
        return "Error: generalfacts.json is missing!"
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

print("Kaiserbot v1.0.0")
print(CreateTimestamp(), "Awake!")
print(CreateTimestamp(), "Current Working Directory:", os.getcwd())
client = discord.Client()
console = Console(client)

@client.event
async def on_ready(): 
    print(CreateTimestamp(), "Kaiser is now ready!")
    
@client.event
async def on_message(message):
    if message.author == client.user: # Don't answer messages from yourself.
        return
    cwd = os.getcwd()
    file = open("Timezones.json", 'r')
    raw = file.read()
    timezones = json.loads(raw)
    file.close()
    await MessageHandler(client, message, timezones)

file = open("BotToken.key", 'r')
token = file.read()
file.close()

if token == "":
    print(CreateTimestamp(), "Bot token is empty! Make sure that your bot token is in your BotToken.key file!")
    input("Press enter to continue...")
    sys.exit()

console.start()
client.run(token)