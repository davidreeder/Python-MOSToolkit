#!/usr/bin/env python
"""                             -o-
  OSCClient.py

  OSC client example.
  MOSOSC is wrapper for https://pypi.org/project/python-osc .

  Demonstrates...
    * Create and destroy client
    * Send messages and bundles
    * Send nested bundles, bundles with delays
    * Composable message and bundle content creation
    * Optional automatic OSC path logging per send, including delay status


  See MOSOSC header and pydoc for more details.
"""

version = "0.1"   #RELEASE



#----------------------------------- -o-
# Modules.

import os
import random
import time


#
import MOSLog
log = MOSLog.MOSLog(logTime=True, logDate=False)

import MOSZ as z

import MOSOSC 




#----------------------------------- -o-
# Global parameters.

# NB  Use fully qualified domain name (FQDN) to guarantee 
#     uniqueness of your message across all possible OSC programs.
#
USER = os.getenv("USER")


# NB  Use comment to prevent any OSC path from being sent.
#
messagePathList = [
        "/filter",
        "/volume",
        "/logvolume",

        "/edu/school/" + USER + "/your/unique/namespace",   
        "/whatevs",

        "/stopserver",
        "/destroyserver",
  ]




#----------------------------------- -o-
# Main.

if "__main__" == __name__:
  
  cmdlineArgs = z.parseCommandlineArguments( [
      { "option_strings"  : "--hostname",
        "default"         : "127.0.0.1",
        "help"            : "Hostname or IP to receive OSC messages.",
      },                                                              
                                                                     
      { "option_strings"  : "--port",                           
        "default"         : 5005,                              
        "type"            : int,                              
        "help"            : "Port to receive OSC messages.",    
      },                                                        
    ] )



  # Create client.
  # Optionally change globals parameters.
  #
  client = MOSOSC.MOSOSC()

  client.createClient(cmdlineArgs.hostname, cmdlineArgs.port)
  #client.createClient()

  #client.destroyClient()
  #client.createClient(cmdlineArgs.hostname, cmdlineArgs.port, True)


  #client.enablePathLogging = False


  # Send messages.
  # Random series of messages with random OSC args.
  #
  stopserverWasInvoked     = False
  destroyserverWasInvoked  = False

  for _ in range(25):
  #for _ in range(1):                                   #DEBUG
    messagePath     = random.choice(messagePathList)
    messageContent  = None
    extraContent    = ""
    msg             = None


    # Limit use and order of messages that change server behavior.
    #
    if  "/stopserver" == messagePath:
        if  stopserverWasInvoked:
            continue
        stopserverWasInvoked = True
        client.messageSend(messagePath)
        continue

    if  "/destroyserver" == messagePath:
        if  destroyserverWasInvoked  or  not stopserverWasInvoked:
            continue
        destroyserverWasInvoked = True
        client.messageSend(messagePath)
        continue

    #
    msg = client.message(messagePath)

    if  "/whatevs" == messagePath:
        messageContent = [ "abc", 25, [] ]
        msg = client.messageAdd(msg, messageContent)

    else:
        r = random.random()

        if  r < 0.75:
            messageContent = random.choice([ random.random(), [random.random(), 42] ])
            msg = client.messageAdd(msg, messageContent)

            if  r < 0.25:
                extraContent = "108"
                msg = client.messageAdd(msg, extraContent)

    #
    #client.postOSCArgs(msg)

    client.send(msg)
    time.sleep(1)

  #ENDFOR -- in range()



  # Send a bundle.  (That contains a bundle.)
  #
  msg   = client.message("/bundle/SYNC", [1,2,3], 9999999)
  msg   = client.messageAdd(msg, 4.0, 2)

  msg2  = client.message("/bundle/SWAN")
  msg2  = client.messageAdd(msg2, "value")
  msg2  = client.messageAdd(msg2, b"\xfa\xb1\xed")

  #
  delayTime = 3

  bundle2 = client.bundle(msg2, delayTimeInSeconds=delayTime)
  #bundle2 = client.bundleSend(msg2, delayTimeInSeconds=delayTime)
  #client.postOSCArgs(bundle2)

  #bundle  = client.bundle(msg, bundle2)
  bundle  = client.bundle(bundle2, msg)

  #
  #time.sleep(2)
  client.send(bundle)


#ENDMAIN

