import discord
import json
import asyncio
import time
from dpyConsole import Console

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

### TIME ZONE SHIT ###

### MESSAGE HANDLER ###

def MessageHandler(message):



### ACTUAL SHIT ###

print("Kaiserbot v1.0.0")
print(CreateTimestamp(), "Awake!")

file = open("Timezones.json", 'r')
raw = file.read()
timezones = json.loads(raw)
file.close()
print(CreateTimestamp(), "Timezones loaded.")
client = discord.Client()
console = Console(client)

@client.event
async def on_ready(): 
    print(CreateTimestamp(), "Kaiser is now ready!")
    
@client.event
async def on_message(message):
    if message.author == client.user: # Don't answer messages from yourself.
        return

    MessageHandler(message)



console.start()
client.run("ODYzNTE2NjI3NzM5NzM4MTIz.YOoChw.YnxdmspRUcNR86vvCkH7lgHT3xc")

# Bot Token: ODYzNTE2NjI3NzM5NzM4MTIz.YOoChw.YnxdmspRUcNR86vvCkH7lgHT3xc

