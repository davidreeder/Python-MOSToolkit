#!/usr/bin/env python
"""                                     -o-
  rtcmixOSCServer.py

  Demonstrate simple "drum machine" interaction model by playing
  RTcmix sounds from a single score via incoming OSC messages.


  ASSUME  CMIX executable is accessible to subprocess.Popen() and os.system().

  ASSUME  Running with a CMIX score enabled with Minc struct OSCData.
          See cmixHelper.sco.
"""

version = "0.1"   #RELEASE



#----------------------------------- -o-
# Modules.

import MOSLog
log = MOSLog.MOSLog(logTime=True, logDate=False)

import MOSZ as z
#import MOSDump as dump

import MOSOSC
import MOSRTcmix




#----------------------------------- -o-
# OSC path handlers.

#                                                                    -o-
def handlerOSCMessagesForCMIX(*eventArgs):
  """
  Send OSC message to CMIX score enabled with Minc struct OSCData.
  """

  _, _, oscPath, oscArgs, _ = server.parseEventArgs(eventArgs)

  MOSRTcmix.playScoreWithOSCData(  oscPath, oscArgs, 
                                   cmdlineArgs.cmixScore, cmdlineArgs.cmixOSCInputListName, 
                                   #runInForeground=True   #DEBUG
                                )


#                                                                    -o-
def  handlerDestroyServer(*eventArgs):
  server.parseEventArgs(eventArgs)
  server.destroyServer()




#----------------------------------- -o-
# Main.

cmdlineArgs = None

if  "__main__" == __name__:

  cmdlineArgs = z.parseCommandlineArguments( [
      { "option_strings"  : "--cmixScore",
        "default"         : "oscDrumMachineDemo.sco",
        "help"            : "CMIX score enabled with Minc struct OSCData.",
      },                                                              

      { "option_strings"  : "--cmixOSCInputListName",
        "default"         : "oscDataObjectsFromPython",
        "help"            : "Name of global variable, prepended to cmixScore, that defines OSC input.",
      },                                                              


      { "option_strings"  : "--hostname",
        "default"         : "127.0.0.1",
        "help"            : "Hostname or IP upon which to listen.",
      },                                                              
                                                                     
      { "option_strings"  : "--port",                           
        "default"         : 50001,
        "type"            : int,                              
        "help"            : "Port upon which to listen.",    
      },                                                        
    ] )



  #
  # Create and configure server.
  #
  server = MOSOSC.MOSOSC()

  #server.enablePathLogging = False

  server.createServer(cmdlineArgs.hostname, cmdlineArgs.port)


  # OSC paths defined by OSC client and CMIX score.  
  #   See groovySequenceControl.py and oscDemo.sco.
  #
  server.addPathHandler("/lowSequence",      handlerOSCMessagesForCMIX)
  server.addPathHandler("/highSequence",     handlerOSCMessagesForCMIX)
  server.addPathHandler("/boom",             handlerOSCMessagesForCMIX)
  server.addPathHandler("/kapow",            handlerOSCMessagesForCMIX)
  server.addPathHandler("/clearDiskMemory",  handlerOSCMessagesForCMIX)

  server.addPathHandler("/quit", handlerDestroyServer)



  #
  # Start and stop server.
  #
  server.startServer()  


#ENDMAIN

