#                                                                        -o--
"""
    mosOSC.py   (class)

    Wrapper for https://pypi.org/project/python-osc, version 1.8.0.

    Provides control over creation and management of...
        * OSC client and server
        * incrementally aggregated messages and bundles
        * sending to OSC paths
        * receiving with custom OSC path handlers 
        * automated OSC path logging on send and receive
        * function hook for default path processing

    Choices for this initial API are in the service of a simple, unified
    interface to the larger offering of pythonosc.  MOSOSC does not
    comprehensively represent the whole of pythonosc.


    Resources:
        * https://en.wikipedia.org/wiki/Open_Sound_Control
        * opensoundcontrol.org
        * https://web.archive.org/web/20030914224904/http://cnmat.berkeley.edu/OSC/OSC-spec.html
        * https://www.linuxjournal.com/content/introduction-osc

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021-2022.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.3"   #RELEASE

USAGE  :str  = "[hostname:str], [port:int]"   



#----------------------------------------- -o--
# Modules.

from typing import Any, List, Tuple, Union
from types import FunctionType


#
from pythonosc import udp_client

from pythonosc import osc_server
from pythonosc import dispatcher

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_bundle_builder import OscBundleBuilder
from pythonosc import osc_message 
from pythonosc import osc_bundle 


#
import mosLog
log = mosLog.MOSLog(logTime=True, logDate=False)
    # NB  Suggested invocation of mosLog for logging MOSLog.osc().

import mosZ as z
import mosDump as dump




#----------------------------------------- -o--
class  MOSOSC:
    """
    SHARED ATTRIBUTES--
        * hostname
        * port

        * enablePathLogging 


    CLIENT METHODS--
        * createClient()
        * destroyClient()

        * message()
        * messageAdd()
        * messageSend()

        * bundle()
        * bundleAdd()
        * bundleSend()

        * send()

        * postOSCArgs()


    SERVER METHODS--
        * createServer()      
        * destroyServer()     

        * startServer()
        * stopServer()        

        * addPathHandler()
        * removePathHandler()
        * listPathHandlers() 

        * parseEventArgs()       

    SERVER ATTRIBUTES--
        * enablePathHandlerDefault
        * pathHandlerDefaultFunction 
        * enableSourceAddrLogging


    NB  All OSC paths must begin with slash and be at least 
        one character long.  ("/?")

    NB  Message and bundle creation is composable...
            message() + [messageAdd()] + send()
        ...or just one call: messageSend().  Bundles are similar.

    NB
      * Incoming OSC path will match all valid handlers.
      * Use globbing in OSC path names to match multiple incoming OSC paths.  
      * Optionally use default handler function to capture unmatched OSC paths.
          Redirect stderr to squelch DEBUG messages from default handler.

    ASSUME  Each MOSOSC instance is used ONLY as client or as server.

    See class header and pydoc for full details.
    """



    #=============================================== -o--
    # Shared public attributes.

    # NB  hostname and port are effectively read-only.
    #     Set them is via input to the class constructor,
    #       createServer() or createClient().
    #
    hostname  :str  = None
    port      :int  = None

    enablePathLogging  :bool  = True                    #DEFAULT
        # Log the oscPath and associated arguments with log.osc().
        # Use this attributes in custom oscPath handlers to unify logging
        #   control across all handlers.



    #----------------------------------------------- -o--
    # Shared protected attributes.
    #
    # NB  "localhost" != "127.0.0.1".  Both client and server must use same address format.
    #

    _hostnameDefault  :str  = "127.0.0.1"               #DEFAULT
    _portDefault      :int  = 50001                     #DEFAULT




    #----------------------------------------------- -o--
    # Lifecycle.

    #                                                                    -o-
    def  __init__(self, hostname:str=None, port:int=None):
        """
        hostname and port define server target.  
        Public attributes hostname and port shared between client and server. 
	ASSUME  Each MOSOSC instance is used ONLY as client or as server.
        """
        self._validateHostnameAndPort(hostname, port)



    #----------------------------------------------- -o--
    # Shared protected methods.

    #                                                                    -o-
    # NB  Checks for type and syntax.  
    # XXX  No checks for connectivity.
    #
    def  _validateHostnameAndPort(  self, 
                                    hostname    :str  = None, 
                                    port        :int  = None,
                                    exitValue   :int  = 1
                                 )  -> None:

        if  not hostname:   hostname  = self._hostnameDefault
        if  not port:       port      = self._portDefault

        #
        if  not isinstance(hostname, str)  or  not isinstance(port, int):
            z.postDefUsage(log.className(), USAGE)
            return

        if  (len(hostname) <= 0):
            z.postAndExit("%s(): hostname is EMPTY." % log.className(), exitValue=exitValue)
            return

        if  port < 1024:
            z.postAndExit( "%s(): port MUST BE GREATER than 1024. (%s)" % (log.className(), port),
                           exitValue=exitValue )
            return

        #
        self.hostname  = hostname
        self.port      = port

    #ENDDEF -- _validateHostnameAndPort()


    #                                                                    -o-
    # OSC paths must begin with slash ("/") and be at least two characters long.
    #
    def  _validateOSCPath(self, oscPath) -> bool:
        if  (len(oscPath) < 2)  or  ("/" != oscPath[0]):
            log.critical(f"OSC path is MALFORMED.  ({oscPath})")
            return  False
            
        return  True




    #=============================================== -o--
    # Client protected attributes.

    _client  :udp_client.UDPClient  = None




    #----------------------------------------------- -o--
    # Client public methods.

    #                                                                    -o-
    # Client runs as UDPClient.  pythonosc also offers SimpleUDPClient.
    #
    def  createClient(  self, 
                        hostname         :str   = None, 
                        port             :int   = None,
                        enableBroadcast  :bool  = False,
                     )  -> None:
        """
        One client per instance.  Client sends to server at hostname:port.
        """

        if  self._client:
            log.critical("Client is ALREADY CREATED.")

        self._validateHostnameAndPort(hostname, port)

        self._client = udp_client.UDPClient(self.hostname, self.port, enableBroadcast)

        #
        enableBroadcastString = ""
        if  enableBroadcast:
            enableBroadcastString = "  Broadcast IS ENABLED."

        log.info(f"Created client to {self.hostname}:{self.port}.{enableBroadcastString}")


    #                                                                    -o-
    def  destroyClient(self)  -> None:
        if  not self._client:
            log.warning("Client is already UNDEFINED.")
            return

        self._client = None
        log.info(f"Destroyed client to {self.hostname}:{self.port}.")



    #                                                                    -o-
    def  message(  self, 
                   oscPath         :str,
                  *messageArgs     :Tuple[Any],
                   sendMessageNow  :bool        = False,
                )  -> List[Any]:
        """
        NB  Removes instances of None from messageArgs.
        """

        messageList  :List[Any]  = []

        self._validateClientSetup()
        self._validateOSCPath(oscPath)

        #
        messageList.append(oscPath)

        for arg in messageArgs:
            if  None is arg:  continue 
            messageList.append(arg)

        if  sendMessageNow:
            self.send(messageList)

        #
        return  messageList


    #                                                                    -o-
    def  messageAdd(  self, 
                      messageList     :List[Any],
                     *messageArgs     :Tuple[Any],
                   )  -> List[Any]:
        """
        NB  Removes instances of None from messageArgs.
        """

        self._validateClientSetup()

        if      not isinstance(messageList, List)       \
            or  (len(messageList) <= 0)                 \
            or  (len(messageArgs) <= 0):
            log.critical("One or more input ARGUMENTS ARE INVALID.")

        #
        for arg in messageArgs:
            if  None is arg:  continue 
            messageList.append(arg)

        return  messageList


    #                                                                    -o-
    def  messageSend(self, oscPath:str, *messageArgs:Tuple[Any])  -> List[Any]:
        return  self.message(oscPath, *messageArgs, sendMessageNow=True)



    #                                                                    -o-
    def  bundle(  self, 
                 *messageListOrBundle   :Tuple[Union[ List[Any], OscBundleBuilder ]],
                  delayTimeInSeconds    :float  = 0,   #NB osc_bundle_builder.IMMEDIATELY, 
                  sendBundleNow         :bool   = False,
               )  -> OscBundleBuilder:
        """
        When delayTimeInSeconds is zero (0), the received OSC message
          is executed immediately.  Otherwise, delay execution for N seconds.
          Per OSC standard.

	NB  bundle*() methods take as input, and deliver as output,
	    "builders": OscBundleBuilder or List[Any] (aka "messageList"),
            the latter is lazily transformed into OscMessageBundle when needed.

	    OscBundle and OscMessge are fixed objects, whereas OscBundleBuilder 
            can continue to accept new inputs as a convenience to the enduser.
        """

        self._validateClientSetup()

        if       isinstance(messageListOrBundle, List)   \
            and  (len(messageListOrBundle) <= 0):
            log.critical("messageListOrBundle contains EMPTY messageList.")

        if  (delayTimeInSeconds < 0):
            log.critical(f"delayTimeInSeconds IS INVALID.  ({delayTimeInSeconds})")


        #
        timestamp = 0

        if  delayTimeInSeconds > 0:
            timestamp = z.timeNowInSeconds(delayTimeInSeconds)

        bundleBuilder = OscBundleBuilder(timestamp)


        #
        for obj in messageListOrBundle:
            objToBundle = obj

            if  isinstance(objToBundle, List):
                objToBundle = self._convertMessageListToMessageBuilder(objToBundle)

            bundleBuilder.add_content(objToBundle.build())

        if  sendBundleNow:
            if len(messageListOrBundle) <= 0:   # XXX  Never reached.
                log.critical("Cannot send BUNDLE WITH NO CONTENT.")
            self.send(bundleBuilder)

        #
        return  bundleBuilder


    #                                                                    -o-
    def  bundleAdd(  self, 
                     bundleBuilder               :OscBundleBuilder,
                    *messageListOrBundleBuilder  :Tuple[Union[ List[Any], OscBundleBuilder ]],
                  )  -> OscBundleBuilder:
        """
        (See description for bundle().)
        """

        self._validateClientSetup()

        #
        if        isinstance(messageListOrBundleBuilder, List)  \
             and  (len(messageListOrBundleBuilder) <= 0):
            log.critical("messageListOrBundleBuilder contains EMPTY messageList.")


        # OscBundleBuilder contains "built objects": OscMessage or OscBundle.
        #
        for obj in messageListOrBundleBuilder:
            objToBundle = obj

            if  isinstance(objToBundle, List):
                objToBundle = self._convertMessageListToMessageBuilder(objToBundle)
                
            bundleBuilder.add_content(objToBundle.build())

        #
        return  bundleBuilder


    #                                                                    -o-
    def  bundleSend(  self, 
                      messageListOrBundleBuilder  :Tuple[Union[ List, OscBundleBuilder ]],
                      delayTimeInSeconds          :float  = 0,    #NB osc_bundle_builder.IMMEDIATELY
                   )  -> OscBundleBuilder:
        """
        NB  bundleSend() with empty messageListOrBundle will fail.  
            Use send() directly if bundle content is already added.
        """
        return  self.bundle(messageListOrBundleBuilder, delayTimeInSeconds=delayTimeInSeconds, sendBundleNow=True)



    #                                                                    -o-
    def  send(  self, 
                messageListOrBundleBuilder  :Union[List[Any], OscBundleBuilder],
             )  -> None:

        objectToSend  :Union[OscMessageBuilder, OscBundleBuilder]  = None


        #
        self._validateClientSetup()

        if       isinstance(messageListOrBundleBuilder, List)   \
            and  (len(messageListOrBundleBuilder) <= 0):
            log.critical("messageListOrBundleBuilder IS INVALID.")


        #
        if  isinstance(messageListOrBundleBuilder, List):
            objectToSend = self._convertMessageListToMessageBuilder(messageListOrBundleBuilder)
        else:
            objectToSend = messageListOrBundleBuilder

        self._client.send(objectToSend.build())


        #
        if  self.enablePathLogging:
            self.postOSCArgs(objectToSend)


    #                                                                    -o-
    def  postOSCArgs(  self,
                       messageOrBundleBuilder  :Union[OscMessageBuilder, OscBundleBuilder],
                    )  -> None:
        """
        Post OSC args via log.osc() for any OscMessageBuilder or OscBundleBuilder.
        Occurs automatically when enablePathLogging is True.
        """

        def  postOSC(message:osc_message.OscMessage, atTimestamp:float=0) -> None:
            delayString  :str  = ""

            if  atTimestamp > 0:  
                delayRemaining  = atTimestamp - z.timeNowInSeconds()
                delayString     = f"  :: remaining delay {delayRemaining:.3f} @ time {atTimestamp:.3f}"

            log.osc(f"{message.address} {z.c2s(message._parameters)}{delayString}")

        #ENDDEF -- postOSC()


        #
        def  findMessageInBundle(  messageOrBundle  :Union[osc_message.OscMessage, osc_bundle.OscBundle], 
                                   atTimestamp      :float = 0,
                                 ) -> None:
            #
            if  isinstance(messageOrBundle, osc_message.OscMessage):
                postOSC(messageOrBundle, atTimestamp)

            # Unwrap bundle to find messages.
            # NB  Getter bug: OscBundle.timestamp()->int !
            #
            else:
                for _ in messageOrBundle._contents:  
                    if  isinstance(_, osc_message.OscMessage):
                        postOSC(_, messageOrBundle._timestamp)
                    else:
                        findMessageInBundle(_, _._timestamp)
                    
        #ENDDEF -- findMessageInBundle()


        #
        mob = messageOrBundleBuilder.build()
        findMessageInBundle(mob)

    #ENDDEF -- postOSCArgs()




    #----------------------------------------------- -o--
    # Client protected methods.

    #                                                                    -o-
    def  _validateClientSetup(self):
        if  not self._client:
            log.critical("Client is UNDEFINED.")


    #                                                                    -o-
    def  _convertMessageListToMessageBuilder(self, messageList:List[Any])  -> OscMessageBuilder:
        """
        NB  Remove elements set to None, but otherwise preserve order of MessageList.
        """

        oscPath         :str                = messageList[0]         
        messageBuilder  :OscMessageBuilder  = None

        self._validateOSCPath(oscPath)                  # Handle OSC path.
        messageBuilder  = OscMessageBuilder(oscPath)

        for arg in messageList[1:]:                     # Handle OSC arguments.
            if  None is arg:  continue 
            messageBuilder.add_arg(arg)   

        return  messageBuilder




    #=============================================== -o--
    # Server public attributes.

    enablePathHandlerDefault    :bool  = True           #DEFAULT
        # createServer() automatically defines a method to capture oscPaths
        #   that are not named by a custom handler.
        #
        # If False, the oscPath handler default returns before taking action.
        # If set False before calling createServer(), the oscPath handler
        #   default will not be created.

    pathHandlerDefaultFunction  :FunctionType  = None   #DEFAULT
        # Run a function for every oscPath captured by the default handler.
        # See _pathHandlerDefault() for function signature.

    enableSourceAddrLogging     :bool  = True           #DEFAULT
        # Log the source hostname and port.  In the oscPath default
        #   handler, this is logged with oscPath.



    #----------------------------------------------- -o--
    # Server protected attributes.

    _server      :osc_server.ThreadingOSCUDPServer  = None
    _dispatcher  :dispatcher.Dispatcher             = None


    #
    _pathHandlersReceiveSourceAddr  :bool  = True       #DEFAULT
        # NB  This value is used when the Dispatcher creates a handler.
        #     See createServer() and addPathHandler().
        #
        # By DEFAULT, all handlers receive the OSC path source address
        #   information.  To prevent the logging of source address, set
        #   enableSourceAddrLogging to False.

    _isServerRunning  :bool  = False
        # True if server is running.

    _willDestroyServer  :bool  = False
        # Indicate that server is schedule for destruction.
        #   In this state, it shall not be restarted.




    #----------------------------------------------- -o--
    # Server public methods.
    #
    # One server and one dispatcher per class instance.
    # Dispatcher can be updated, even after server is running.
    # 
    # Server instance runs as ThreadingOSCUDPServer.  
    # pythonosc also offers:
    #   . AsyncIOOSCUDPServer
    #   . BlockingOSCUDPServer
    #   . ForkingOSCUDPServer
    #

    #                                                                    -o-
    def  createServer(  self, 
                        hostname  :str   = None, 
                        port      :int   = None,
                     )  -> None:
        """
        Create server without starting it.  
        Server is always created with a dispatcher.  
        Dispatcher is created by DEFAULT and set to default oscPath
          handler, which user may choose to disable.
        """

        if  self._server:
            log.critical("Server is ALREADY CREATED.", exitValue=1)

        self._validateHostnameAndPort(hostname, port)


        #
        self._dispatcher = dispatcher.Dispatcher()

        if  self.enablePathHandlerDefault:
            self._dispatcher.set_default_handler(
                      self._pathHandlerDefault, 
                      needs_reply_address=self._pathHandlersReceiveSourceAddr )

        #
        try:
            self._server = osc_server.ThreadingOSCUDPServer( 
                                        (self.hostname, self.port), self._dispatcher )
        except  Exception as e:
            if  48 == e.errno:
                log.critical(  "Server ALREADY RUNNING on " +
                                  f"{self.hostname}:{self.port}.", 
                               exitValue=1 )
            else:
                log.critical(e, exitValue=1)

    #ENDDEF -- createServer()


    #                                                                    -o-
    def  destroyServer(self)  -> None: 
        """
        Destroy server, dispatcher, all oscPath handlers and default
          handler function.
        """

        self._validateServerSetup()

        self._willDestroyServer = True
        self.stopServer()
            
        self._dispatcher.set_default_handler(None)
        self._dispatcher = None

        self._server = None
        self._willDestroyServer = False


    #                                                                    -o-
    def  startServer(self)  -> None:
        self._validateServerSetup()

        #
        if  self._isServerRunning:
            log.warning("Server is ALREADY RUNNING at %s:%s..." % (self.hostname, self.port))
            return

        if  self._willDestroyServer:
            log.warning("Server at %s:%s is SCHEDULED FOR DESTRUCTION..." % (self.hostname, self.port))
            return

        #
        log.info("Server STARTING at %s:%s..." % (self.hostname, self.port))
        self._isServerRunning = True
        self._server.serve_forever()
        self._isServerRunning = False


    #                                                                    -o-
    def  stopServer(self)  -> None:
        self._validateServerSetup()

        if  self._isServerRunning:
            self._server.shutdown()
            self._isServerRunning = False
            log.info("...Server at %s:%s is STOPPED." % (self.hostname, self.port))
        else:
            log.info("Server at %s:%s is ALREADY STOPPED." % (self.hostname, self.port))



    #                                                                    -o-
    def  addPathHandler(  self, 
                          oscPath         :str, 
                          oscPathHandler  :FunctionType, 
                          *userArgs       :List[Any]
                       )  -> None:
        """
        Give OSC path handlers a simple signature, and use parseEventArgs()
          to resolve essential parameters:

              def  handlerFunction(*eventArgs): 
                  sourceHostname, sourcePort, oscPath, oscArgs, userArgs =  \\
                    self.parseEventArgs(eventArgs, postOSCPath=True)
                  ...

          userArgs -- Arbitrary parameters or (function) pointers defined by
                      addPathHandler() invocation.

        NB--
          * Incoming OSC path will match all valid handlers.
          * Use globbing in OSC path names to match multiple incoming OSC paths.  
          * Optionally use default handler function to capture unmatched OSC paths.
              Redirect stderr to squelch DEBUG messages from default handler.
        """

        self._validateServerSetup()
        self._validateOSCPath(oscPath)

        if  self._isServerRunning:
            log.error(f"CANNOT add or remove OSC path handlers while SERVER IS RUNNING.  ({oscPath})")
            return

        #
        self._dispatcher.map(  oscPath, 
                               oscPathHandler, 
                               userArgs, 
                               needs_reply_address=self._pathHandlersReceiveSourceAddr )

        log.info(f"Added OSC path handler \"{oscPath}\".")


    #                                                                    -o-
    def  removePathHandler(self, oscPath:str)  -> None:
        self._validateServerSetup()
        self._validateOSCPath(oscPath)

        if  self._isServerRunning:
            log.error(f"CANNOT add or remove OSC path handlers while SERVER IS RUNNING.  ({oscPath})")
            return

        #
        try:
            self._dispatcher._map.pop(oscPath)
            log.info(f"Removed OSC path handler \"{oscPath}\".")
        except  KeyError:
            log.error(f"oscPath DOES NOT EXIST.  ({oscPath})")
        except  Exception as e:
            log.critical(e, exitValue=1)


    #                                                                    -o-
    def  listPathHandlers(self)  -> None:
        self._validateServerSetup()

        registeredOSCPaths  :List[str]  = list(self._dispatcher._map.keys())

        log.info(dump.listo(registeredOSCPaths, title="OSC Path Handlers", sort=True))



    #                                                                    -o-
    def  parseEventArgs(  self,
                          eventArgs       :Tuple[Any], 
                          expectUserArgs  :bool         = True,
                          postOSCPath     :bool         = True,
                        ) -> Tuple[str, int, str, List[Any], List[Any]]:
        """
        RETURNS: Tuple[str, int, str, List[Any], List[Any]]
                   :: (sourceHostname, sourcePort, oscPath, oscArgs, userArgs)

        Optionally post oscPath via log.osc().  
        Returns components of OSC event in a tuple.

        expectUserArgs -- Then True (DEFAULT), expect additional arguments 
                          from custom OSC path handler.
        postOSCPath -- Local toggle, override global toggle, for posting OSC path.

        See also public attributes: enablePathLogging, enableSourceAddrLogging.

        NB  Whether MOSOSC returns source hostname/port to every handler
              is determined by MOSOSC._pathHandlersReceiveSourceAddr (DEFAULT:True).
        """

        sourceHostname  :str        = None
        sourcePort      :int        = None
        oscPath         :str        = None
        userArgs        :List[Any]  = []
        oscArgs         :List[Any]  = []

        eventList         :List[Any]  = list(eventArgs)
        sourceAddrString  :str        = ""


        # ASSUME eventArgs tuple is of the form...
        #
        #    ( [sourceAddrTuple], oscPath, [userArgsTuple], oscArgsTuple )
        #
        # ...where:
        #   * sourceAddrTuple exists if _pathHandlersReceiveSourceAddr is True;
        #   * userAgrs exists if called from a custom oscPath handler.
        #
        if  isinstance(eventList[0], tuple):
            sourceHostname, sourcePort = eventList.pop(0)
            if  self.enableSourceAddrLogging:
                sourceAddrString = f"  :: {sourceHostname}:{sourcePort}"

        oscPath = eventList.pop(0) + " "

        if  expectUserArgs:
            userArgs = list(eventList.pop(0)[0])

        oscArgs = eventList


        #
        if  self.enablePathLogging and postOSCPath:  # Global and local toggles.
            log.osc(f"{oscPath}{z.c2s(oscArgs)}{sourceAddrString}")

        return  (sourceHostname, sourcePort, oscPath.strip(), oscArgs, userArgs)



    #----------------------------------------------- -o--
    # Server protected methods.

    #                                                                    -o-
    # ASSUME  If Server is defined, then so also is all Server support, 
    #         including Dispatcher and default oscPath handler.
    #
    def  _validateServerSetup(self):
        if  not self._server:
            log.critical("Server is UNDEFINED.")


    #                                                                    -o-
    # NB  First argument represents working instance of this class, 
    #       passed in by calling environment.
    #
    def  _pathHandlerDefault(  mososc,
                               *eventArgs  :Tuple[Any]
                            )  -> None:
        """
        If pathHandlerDefaultFunction is defined as a function, it will be
          called if enablePathHandlerDefault is True.

        pathHandlerDefaultFunction() REQUIRES the following signature:

            pathHandlerDefaultFunction(  mososc, 
                                         sourceHostname  :str,
                                         sourcePort      :int,
                                         oscPath         :str,
                                         oscArgs         :List[Any],
                                       ) -> None

            mososc -- Same instance of MOSOSC as contains all other methods.

            sourceHostname / sourcePort -- Network origin of the oscPath sent
              to the server.  Available when _pathHandlersReceiveSourceAddr
              is True.

            oscPath / oscArgs -- OSC pathname and associated arguments.
              oscArgs is List of zero (0) or more elements.

        See also public attributes: enablePathHandlerDefault, pathHandlerDefaultFunction.
        """

        if  not mososc.enablePathHandlerDefault:  return

        sourceHostname, sourcePort, oscPath, oscArgs, _ =  \
                mososc.parseEventArgs(eventArgs, expectUserArgs=False)

        if  mososc.pathHandlerDefaultFunction:
            mososc.pathHandlerDefaultFunction(mososc, sourceHostname, sourcePort, oscPath, oscArgs)


#ENDCLASS -- MOSOSC()

