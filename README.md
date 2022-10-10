# HavocNotion
A simple ExternalC2 POC for Havoc C2. Communicates over Notion using a custom python agent, handler and extc2 channel.  
Not meant to be a usable agent, just a PoC to understand how Havoc C2's ExternalC2 interface works. Accompanying blogpost upcoming and will be linked here eventually.

## Limitations
Only supports 1 agent per notion key - was designed this way due to notion rate limiting

## Setup
Download https://github.com/HavocFramework/havoc-py and place in the same directory as the listener and handler scripts.

## Usage
1. start up the Havoc teamserver
2. create an external listener. Default endpoint name configured here is ExtEndpoint. If you change it be sure to change the code too.
3. Replace the notion tokenv2 and page url in listener.py and agent.py
4. run the handler.py script to register the agent
5. run the listener.py to start checking the notion
6. run the agent.py