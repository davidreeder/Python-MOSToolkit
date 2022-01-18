#!/usr/bin/env python
"""                                     -o-
  soundsAndSequences_oscServer.py


  Demonstrate how OSC can effect real-time controls to trigger and
  parameterize sounds defined by RTcmix in the case where CMIX build does
  NOT enable "CMIX-style" OSC.

  Tradeoffs--
    * PRO: Using a separate OSC server provides allows the use of OSC
        bundles and allows the server and client to exist on different machines.
    * CON: Audio quality may be degraded when frequency of incoming OSC messages is high.

  See README.md for more full details.

  Demo uses an event loop to manage threads that send MIDI sequences and
  other data via well-defined OSC paths.  One thread tracks the others and
  posts state to stdout.


  ASSUME  CMIX executable is accessible to subprocess.Popen() and os.system().

  ASSUME  Running with a CMIX score enabled with MinC struct OSCData.
          See demos/MOSOSC-with-RTcmix/cmixHelper.sco.
"""

version = "0.2"   #RELEASE



#----------------------------------- -o-
# Modules.

#import mosLog
#log = mosLog.MOSLog(logTime=True, logDate=False)

#import mosDump as dump
import mosZ as z

import mosRTcmix   # NB  Inherits from mosOSC.MOSOSC.




#----------------------------------- -o-
# OSC path handlers.

#                                                                    -o-
def handlerOSCMessagesForCMIX(*eventArgs):
  """
  Send OSC message to CMIX score enabled with MinC struct OSCData.
  """

  _, _, oscPath, oscArgs, _ = server.parseEventArgs(eventArgs)
  server.invokeCMIXWithOSCData(oscPath, oscArgs, cmdlineArgs.pathToCMIXScore)


#                                                                    -o-
def  handlerDestroyServer(*eventArgs):
  server.destroyServer()




#----------------------------------- -o-
# Main.

if  "__main__" == __name__:

  # Commandline args.
  #
  cmdlineArgs = z.parseCommandlineArguments( [
      { "option_strings"  : "--hostname",
        "default"         : mosRTcmix.cmixHostname,
        "help"            : "Hostname or IP upon which to listen.",
      },                                                              
                                                                     
      { "option_strings"  : "--port",                           
        "default"         : mosRTcmix.cmixPort,
        "type"            : int,                              
        "help"            : "Port upon which to listen.",    
      },                                                        

      { "option_strings"  : "--pathToCMIXScore",                           
        "default"         : "soundsAndSequences.sco",
        "help"            : "Score to load into CMIX.  (When CMIX build DOES NOT enable OSC.)",    
      },                                                        

    ] )



  #----------------------------------- -o-
  # Create and configure server.

  server = mosRTcmix.MOSRTcmix()

  #server.enablePathLogging = False

  server.createServer(cmdlineArgs.hostname, cmdlineArgs.port)


  # OSC paths defined by OSC client and CMIX score.  
  #   See soundsAndSequences_OSCClient.py and soundsAndSequences.sco.
  #
  server.addPathHandler("/lowSequence",   handlerOSCMessagesForCMIX)
  server.addPathHandler("/highSequence",  handlerOSCMessagesForCMIX)
  server.addPathHandler("/boom",          handlerOSCMessagesForCMIX)
  server.addPathHandler("/kapow",         handlerOSCMessagesForCMIX)
  server.addPathHandler("/resetScore",    handlerOSCMessagesForCMIX)

  server.addPathHandler("/quit", handlerDestroyServer)



  #----------------------------------- -o-
  # Start server.

  server.startServer()  


#ENDMAIN

