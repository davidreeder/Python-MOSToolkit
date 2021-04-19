#!/usr/bin/env python
"""                                     -o-
  OSCServer.py

  OSC server example.  
  MOSOSC is wrapper for https://pypi.org/project/python-osc .

  Demonstrates...
    * Creating and destroying the server
    * Starting and stopping the server
    * Adding, removing, listing OSC path handlers
    * Passing user arguments to handlers
    * Convenience method for parsing and logging handler inputs
    * Default handler and optional default handler function
    * Multiple matching handlers
    * OSC event logging optionally with millisecond timestamps or client source
    * Attributes to configure OSC path logging, default handler, and more
    * Managing server control via OSC


  NB  Ports under 1024 are reserved by the system.  
      See /etc/services for a list of which ports are already in use.

  See MOSOSC header and pydoc for more details.
"""

version = "0.1"   #RELEASE



#----------------------------------- -o-
# Modules.

import math
import time


#
import MOSLog
log = MOSLog.MOSLog(logTime=True, logDate=False)

import MOSZ as z
import MOSDump as dump

import MOSOSC




#----------------------------------- -o-
# OSC path handlers.

#
# Handlers with and without user defined arguments.
#
def  handlerVolume(*eventArgs):
  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \
            server.parseEventArgs(  eventArgs, 
                                    expectUserArgs  = True, 
                                    postOSCPath     = False )

  title = userArgs[0]
  value = "N/A"

  if  len(oscArgs) > 0:  
    value = oscArgs[0]

  print(f"[{title}] {value}")
  

def  handlerVolumeCompute(*eventArgs):
  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \
            server.parseEventArgs(  eventArgs, 
                                    expectUserArgs  = True, 
                                    postOSCPath     = False )

  title        = userArgs[0]
  logFunction  = userArgs[1]
  value        = "N/A"

  if  (len(oscArgs) > 0)  and  isinstance(oscArgs[0], float):
    value = logFunction(oscArgs[0])

  print(f"[{title}] {value} (logarithmic)")
    


#
# Handlers that affect the behavior of the server.
#
def  handlerStopServer(*eventArgs):
  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \
            server.parseEventArgs(eventArgs)

  server.stopServer()


def  handlerDestroyServer(*eventArgs):
  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \
            server.parseEventArgs(eventArgs)

  server.destroyServer()



#
# Custom default handler.  
# Compare to the built-in default handler + handler function.
#
def  handlerAnyOtherMessage(*eventArgs):
  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \
            server.parseEventArgs(eventArgs, postOSCPath=False)

  log.warning(f"Handler NOT IMPLEMENTED.  ({oscPath})")




#----------------------------------- -o-
# Main.

if  "__main__" == __name__:

  cmdlineArgs = z.parseCommandlineArguments( [
      { "option_strings"  : "--hostname",
        "default"         : "127.0.0.1",
        "help"            : "Hostname or IP upon which to listen.",
      },                                                              
                                                                     
      { "option_strings"  : "--port",                           
        "default"         : 5005,
        "type"            : int,                              
        "help"            : "Port upon which to listen.",    
      },                                                        
    ] )



  #
  # Create and configure server.
  #
  server = MOSOSC.MOSOSC()

  def defaultFunction(  mososc, 
                        sourceHostname, sourcePort,
                        oscPath, oscArgs ):
    log.info(dump.selectVars(locals(), ["oscPath", "oscArgs"]))
    if  mososc.enableSourceAddrLogging:
      log.info(f"{sourceHostname}:{sourcePort}")


  #server.enablePathHandlerDefault    = False
  #server.pathHandlerDefaultFunction  = defaultFunction

  #server.enablePathLogging        = False
  #server.enableSourceAddrLogging  = False

  server.createServer(cmdlineArgs.hostname, cmdlineArgs.port)


  #
  # Add, remove, list OSC path handlers.
  # 
  # Observations--
  #   * An incoming OSC path will match all valid handlers.
  #   * Use globbing in the path names to match multiple incoming OSC paths.
  #   * Optionally use default handler function to capture unmatched OSC paths.
  #
  # Redirect stderr to squelch DEBUG messages created by default handler, 
  #   and any MOSLog below level INFO.  Eg:
  #
  #   ./OSCServer.py  2>/dev/null
  #
  server.addPathHandler( "/filter", print)

  server.addPathHandler( "/volume",    handlerVolume,        "Volume")
  server.addPathHandler( "/logvolume", handlerVolumeCompute, "Log volume", math.log)
 
  server.addPathHandler( "/stopserver",    handlerStopServer)
  server.addPathHandler( "/destroyserver", handlerDestroyServer)

  server.addPathHandler( "/*volume", handlerAnyOtherMessage)


  server.removePathHandler("/flambé")   # Demonstrate FAIL.
  server.removePathHandler("/logvolume")

  server.listPathHandlers()


  #
  # Start and stop server.
  #
  server.startServer()  # NB  Blocks until stopped or destroyed.
  log.info("AFTER FIRST INVOCATION of server.startServer()")

  server.stopServer()   # Demonstrate FAIL.
  time.sleep(3)

  server.removePathHandler("/volume")
  server.addPathHandler("/logvolume", handlerVolumeCompute, "Log volume (added)", math.log)
  server.listPathHandlers()

  server.startServer()   # Restart server, once.


#ENDMAIN

