#                                                                        -o--
"""
    mosRTcmix.py   (child of mosOSC.MOSOSC, with module support)


    Extend class mosOSC.MOSOSC and provide module support to enable
    real-time controls to trigger and parameterize sounds defined by RTcmix.

        * Share a common OSC message format between RTcmix and Python, 
            via MinC struct OSCData.

        * Define how score files engage OSCData.
            See demos/MOSOSC-with-RTcmix/soundsAndSequences.sco.

	* Trigger CMIX score performance from Python OSC server via OSC
	    message when CMIX build does NOT enable "CMIX-style" OSC.  
            See invokeCMIXWithOSCData() (below).

	* Trigger CMIX score performance from Python OSC client via OSC
	    message when CMIX build enables "CMIX-style" OSC.  
            See cmixMessage*() and send*ToCMIX() (below).

	* Send arbitrary OSC messages via message*() or send one or more
	    MinC OSCData objects via cmixMessage*() methods.

	    NOTE: Use of cmixMessge*() is NOT REQUIRED.  MOSOSC.message*() 
                  works just the same as with any other OSC server.


    For more details see code, video, score examples and README.md in
    demos/MOSOSC-with-RTcmix.  See also cmix/cmixHelper.sco.


    MODULE PUBLIC ATTRIBUTES--
        * cmixBuildEnablesOSC  

        * cmixHostname
        * cmixPort
        * cmixOSCPath          


    MODULE PROTECTED ATTRIBUTES--
        * _cmixHelperVersion1  
        * _lengthOfOSCDataCommonList  
        * _defaultCMIXUndefined  

    MODULE PROTECTED FUNCTIONS--
        * _createCommonList()
        * _createOSCDataObject()
        * _convertOSCInputToMinCList()
        * _mincFormatFromOSCArgs()


    MODULE TEST FUNCTIONS--
        * testSendNormalOSCMessagesToScoreEnabledWithOSCData()
        * testSendCMIXOSCMessagesToScoreEnabledWithOSCData()
        * testSendNormalAndCMIXMessages()


    ASSUME  CMIX executable is accessible to subprocess.Popen() and os.system().

    ASSUME  Running with a CMIX score that understands MinC struct OSCData.  
	      See cmix/cmixHelper.sco and cmix/template-for-scores-receiving-arbitrary-OSC.sco.


    See also:
      * mosOSC.MOSOSC
      * cmix/cmixHelper.sco
      * demos/MOSOSC-with-RTcmix/soundsAndSequences.sco

    Learn more about RTcmix...
        * http://rtcmix.org
        * http://rtcmix.org/links

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021-2022.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.2"   #RELEASE



#----------------------------------------- -o--
# Modules.

from subprocess import Popen
import subprocess
import sys
import time
from typing import Any, List, Tuple, Union


#
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_bundle_builder import OscBundleBuilder


#
import mosLog
log = mosLog.MOSLog()

import mosZ as z
#import mosDump as dump

import mosOSC




#----------------------------------------- -o--
# Module public attributes.

cmixBuildEnablesOSC  :bool  = True      #DEFAULT
    # ASSUME  CMIX score and OSC client set their respective
    #         cmixBuildEnablesOSC globals to the same value.


# The following cmix* attributes are REQUIRED when CMIX build enables OSC.
# These values are static CMIX system values.
#
cmixHostname    :str  = "127.0.0.1"             
cmixPort        :int  = 7777                      
cmixOSCPath     :str  = "/RTcmix/ScoreCommands"  




#----------------------------------------- -o--
# Module protected attributes.

_cmixHelperVersion1  :str  = "cmix1"    #XXX
        # Shared between OSC message creation and message conversion functions.

_lengthOfOSCDataCommonList  :int  = 5   #XXX

_defaultCMIXUndefined  :int  = -1       #XXX




#----------------------------------------------- -o--
class MOSRTcmix(mosOSC.MOSOSC):
    """
    CLASS PUBLIC METHODS--
        * cmixMessage()            -- For OSC client.  See also MOSOSC.message*()
        * cmixMessageAdd()
        * cmixMessageSend()    

        * send()

        * sendScoreToCMIX()        -- For OSC client when CMIX build does enable OSC.
        * sendMinCToCMIX()

        * invokeCMIXWithOSCData()  -- For OSC server when CMIX build does NOT enable OSC.


    CLASS PROTECTED METHODS--
        * _sendOSCArgsToCMIX()

    """



    #----------------------------------------------- -o--
    # Lifecycle.

    #                                                                    -o-
    def  __init__( self, 
                   hostname  :str=cmixHostname, 
                   port      :int=cmixPort
                 ):
        """
        hostname and port define server target.  
        Public attributes hostname and port shared between client and server. 
        Defaults set per requirements when CMIX build enables "CMIX-style" OSC.

	ASSUME  Each MOSRTcmix instance is used ONLY as client or as server.
        """
        #self._validateHostnameAndPort(cmixHostname, cmixPort)
        super().__init__(hostname, port)




    #----------------------------------------------- -o--
    # Class public methods.

    #                                                                    -o-
    def  cmixMessage(  self,
                       oscPath         :str,
                       freeListArgs    :Tuple[Any]  = None,
                       commonList      :dict        = None,
                       sendMessageNow  :bool        = False,
                    )  -> List[Any]:
        """
	oscPath is followed by a tuple or array (OSCData free list) then
	  followed by a dictionary (OSCData common parameters).
          Both may be empty.

        All inputs must be encapsulated within the tuple/array or the dictionary.

        NB  commonList must be named on invocation,
            because it follows variable arg freeListArgs.

        NB  commonListDict may be literal dictionary with a partial set of keys.
            Unmentioned keys will be sent as DEFAULTS.
        """
        oscData      :list  = None
        messageList  :List  = []


        self._validateClientSetup()
        self._validateOSCPath(oscPath)


        # NB  Seed first OSCData object with OSC path for entire message.
	# NB  _cmixHelperVersion1 token is captured by _mincFormatFromOSCArgs(), 
        #        in OSC server or OSC client, per setting of mosRTcmix.cmixBuildEnablesOSC.
        #
        oscData = _createOSCDataObject(oscPath, freeListArgs, commonListDict=commonList)

        messageList.append(oscPath)
        messageList.append(_cmixHelperVersion1)
        messageList.append(oscData)

        #
        if  sendMessageNow:
            self.send(messageList)

        return  messageList


    #                                                                    -o-
    def  cmixMessageAdd(  self,
                          messageList     :List[Any],
                          label           :str,
                         *freeListArgs    :Tuple[Any],
                          commonList      :dict        = None,
                       )  -> OscMessageBuilder:
        """
        (See description for cmixMessage().)
        """

        oscData  :list  = None

        self._validateClientSetup()

        #
        if      not isinstance(messageList, List)      \
            or  (len(messageList) <= 0):
            log.critical(f"messageList MUST be a List with AT LEAST ONE ITEM.  ({messageList})")

        #
        self._validateOSCPath(messageList[0])
        oscData  = _createOSCDataObject(label, *freeListArgs, commonListDict=commonList)
        messageList.append(oscData)

        #
        return  messageList


    #                                                                    -o-
    def  cmixMessageSend(  self,
                           oscPath         :str,
                           freeListArgs    :Tuple[Any]  = None,
                           commonList      :dict        = None,
                        )  -> List[Any]:
        """
        (See description for cmixMessage().)
        """
        return  self.cmixMessage(oscPath, freeListArgs, commonList, True)


    #                                                                    -o-
    def  send( self, 
               messageListOrBundleBuilder  :Union[List[Any], OscBundleBuilder],
             ) -> None:
        """
        RTcmix version of send() to handle two cases: whether or not CMIX build enables OSC.

	If mosRTcmix.cmixBuildEnablesOSC is False, then use MOSOSC.send().
          OSC args are converted to MinC format by the Python OSC Server,
          which in turn executes CMIX once per OSC message.

	Otherwise, if mosRTcmix.cmixBuildEnablesOSC is True, then use _sendOSCArgsToCMIX().  
          OSC args are converted locally to MinC before being sent to CMIX directly.

        NB  When mosRTcmix.cmixBuildEnablesOSC is True...
                . OSC bundles are not supported.
                . MUST USE designated CMIX port on localhost.
        """

        oscPath  :str  = None


        #
        self._validateClientSetup()

        if       isinstance(messageListOrBundleBuilder, List)   \
            and  (len(messageListOrBundleBuilder) <= 0):
            log.critical("messageListOrBundleBuilder contains messageList WHICH IS EMPTY.")


        #
        if  not cmixBuildEnablesOSC:              
            super().send(messageListOrBundleBuilder)
            return


        #
        if  isinstance(messageListOrBundleBuilder, OscBundleBuilder):
            log.error("CMIX-style OSC server DOES NOT SUPPORT BUNDLES.  DROPPING bundle message...")
            return


        #
        oscPath = messageListOrBundleBuilder[0]
        self._validateOSCPath(oscPath)
        self._sendOSCArgsToCMIX(oscPath, messageListOrBundleBuilder[1:])



    #                                                                    -o-
    def  sendScoreToCMIX( self,
                          cmixScore  :str
                        ) -> None:
        """
        Used by OSC client when CMIX build enables "CMIX-style" OSC.

        Load cmix score via sending OSC message to CMIX server.
        """

        msgToSend  :List  = []

        #
        if      not isinstance(cmixScore, str)  \
            or  (len(cmixScore) <= 0):
            log.critical("cmixScore is INVALID.")

        #
        miniScore   :str  = f"""
include  {cmixScore}
                            """

        #
        msgToSend = [cmixOSCPath, miniScore]
        super().send(msgToSend)


    #                                                                    -o-
    def  sendMinCToCMIX( self,
                         mincCode   :str
                       ) -> None:
        """
        Used by OSC client when CMIX build enables "CMIX-style" OSC.

        Send arbitrary MinC code to CMIX server.
        """

        msgToSend  :List  = []

        #
        if      not isinstance(mincCode, str)   \
            or  (len(mincCode) <= 0):
            log.critical("mincCode is INVALID.")

        #
        msgToSend = [cmixOSCPath, mincCode]
        super().send(msgToSend)



    #                                                                    -o-
    def  invokeCMIXWithOSCData( self,
                                oscPath               :str, 
                                oscArgs               :List[Any],
                                cmixScore             :str
                             )  -> None:
        """
        Used by OSC server to support CMIX when CMIX is NOT built to support CMIX-style OSC.

        Each incoming OSC message triggers a new process that receives MinC directives on stdin
        instructing CMIX to read the score (via include) then execute score template main() which,
        in turn, passes OSC arguments to CMIX in format defined by MinC OSCData struct.
        
        NB  Missing executable raises exception.  
        """

        mincFormat         :str  = None
        miniScore          :str  = None
        miniScoreInBinary  :str  = None

        cmixProcessArgs  :List   = ["CMIX"]
        cmixProcess      :Popen  = None


        #
        if      not isinstance(oscPath, str)        \
            or  not isinstance(oscArgs, List)       \
            or  not isinstance(cmixScore, str):
            log.critical("One or more input args INCORRECT.")


        # Create MinC version of OSC args.
        # Create a string to invoke score and send OSC args via main().
        #
        mincFormat = _mincFormatFromOSCArgs(oscPath, oscArgs)

        miniScore =         f"""
include  {cmixScore}
main( {mincFormat} )    
                            """

        miniScoreInBinary = miniScore.encode('ascii')


        # Invoke CMIX passing miniScore directives on stdin.
        #
        try:
            #log.debug(f"miniScore = {miniScore}")                           #DEBUG
            #cmixProcess  = Popen(cmixProcessArgs, stdin=subprocess.PIPE)    #DEBUG

            cmixProcess  = Popen(cmixProcessArgs, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmixProcess.communicate(input=miniScoreInBinary)

        except Exception as e:
            log.error(e)
            return 


    #ENDDEF -- invokeCMIXWithOSCData




    #----------------------------------------------- -o--
    # Class protected methods.

    #                                                                    -o-
    def  _sendOSCArgsToCMIX( self,
                            oscPath    :str, 
                            oscArgs    :List[Any]
                          ) -> None:
        """
        Used by OSC client when CMIX build enables "CMIX-style" OSC.

        Send OSC args to CMIX server.

        ASSUME  Loaded score supports OSCData struct and OSC intake via main().
        """

        msgToSend  :List  = []

        #
        if      not isinstance(oscPath, str)            \
            or  not self._validateOSCPath(oscPath)      \
            or  not isinstance(oscArgs, List):
            log.critical("One or more input args INVALID.")


        #
        mincFormat  :str  = _mincFormatFromOSCArgs(oscPath, oscArgs)

        miniScore   :str  = f"""
main( {mincFormat} )
                            """

        #
        msgToSend = [cmixOSCPath, miniScore]
        super().send(msgToSend)


#ENDCLASS -- MOSRTcmix()




#----------------------------------------------- -o--
# Module protected functions.

#                                                                    -o-
def  _createCommonList(  start  :float  = _defaultCMIXUndefined,
                         dur    :float  = _defaultCMIXUndefined,
                         amp    :float  = _defaultCMIXUndefined,
                         freq   :float  = _defaultCMIXUndefined,
                         pan    :float  = _defaultCMIXUndefined,
                      )  -> dict:
    commonList  :dict  = { "start"  : start,
                           "dur"    : dur,
                           "amp"    : amp,
                           "freq"   : freq,
                           "pan"    : pan,
                        }
    return  commonList


#                                                                    -o-
def  _createOSCDataObject(  label           :str,
                            freeListArgs    :Tuple[Any],
                            commonListDict  :dict         = None,
                         )  -> list:
    """
    NB  Removes instances of None from freeListArgs.

    NB  commonListDict may be literal dictionary with a partial set of keys.
        Unmentioned keys will be sent as defaults.
    """

    freeList    = []
    oscData     = [ label ]

    #
    if  not isinstance(label, str):
        log.critical(f"label IS NOT a String.  ({label})")

    if       not isinstance(freeListArgs, (Tuple,List))   \
        and  freeListArgs is not None:
        log.critical(f"freeListArgs IS NOT a Tuple or List.  ({freeListArgs})")


    #
    if  freeListArgs is not None:
        for arg in freeListArgs:
            if  None is arg:  continue 
            freeList.append(arg)

    oscData.append(freeList)

    if  commonListDict:
        completeList = _createCommonList(**commonListDict)
        oscData.append( list(completeList.values()) )


    #
    return  oscData


#                                                                    -o-
def  _convertOSCInputToMinCList(oscPath:str, oscArgs:List[Any])  -> str:
    """
    Convert incoming OSC message into CMIX MinC list format which is then
    read (in CMIX) by parseOSCData() which, in turn, creates a list of
    struct OSCData objects as defined by cmix/cmixHelper.sco.

    If the first token is "cmix1" (for cmixHelper, v1), then ASSUME
    each following list represents a candidate MinC struct OSCData
    object.  By design, the path token in the first object is left
    blank, then overwritten with the OSC path.  All list objects must
    have a form analogous to OSCData:

        [ "path-or-label", [free_list], [common_list] ]

    ...where the two lists are optional, per cmix/cmixHelper.sco.  If
    free_list is empty, but common_list is not, then free_list must still
    be given as an empty list to mark its place.

    Otherwise, when cmixHelper token is not used, all items are
    encapsulated into a single Free List within a single MinC struct
    OSCData object.

    For either method, encapsulate the final result in one more list,
    delivering a single list to the score environment.

    Be flexible with processing errors by tossing smallest broken
    unit, in case adjacent elements can be salvaged.

    NB  Handles limited types, a common subset of both OSC and
          MinC types: float, string, list.  Lists may be nested.
    """

    # Internal functions.
    #   * convertPythonFreeList()
    #   * convertPythonCommonList()
    #   * convertPythonOSCDataCandidate()
    #

    def  convertPythonFreeList(pList:List)  -> str:
        mincList      :str   = ""
        commaSpace    :str   = ""
        isFirstToken  :bool  = True

        for  elem  in pList:
            if  isinstance(elem, list):
                mincList += commaSpace + convertPythonFreeList(elem)

            elif  isinstance(elem, str):
                mincList += commaSpace + f"\'{elem}\'" 

            else:
                mincList += commaSpace + f"{elem}"   #XXX
            
            if  isFirstToken:
                commaSpace = ", "
                isFirstToken = False

        return  "{" + mincList + "}"
    #ENDDEF -- convertPythonFreeList


    def  convertPythonCommonList(pList:List)  -> Union[str,None]:
        mincList      :str   = ""
        commaSpace    :str   = ""
        isFirstToken  :bool  = True

        #
        if      not isinstance(pList, list)   \
            or  len(pList) != _lengthOfOSCDataCommonList:

            log.error(f"Common list candidate DOES NOT EXIST or IS WRONG LENGTH.  ({pList})")
            return  None

        for  elem  in pList:
            if  not z.isNumber(elem):
                log.error(f"Common list candidate contains non-numeric values.  ({pList})")
                return  None

            mincList += commaSpace + f"{elem}"

            if  isFirstToken:
                commaSpace = ", "
                isFirstToken = False

        #
        return  "{" + mincList + "}"
    #ENDDEF -- convertPythonCommonList


    def  convertPythonOSCDataCandidate(pList:list)  -> Union[str,None]:
        mincList      :str   = ""
        commaSpace    :str   = ", "

        candidateCommonString  :str  = None


        #                                       
        if  not isinstance(pList, list):        # Candidate is not a list.
            log.error(f"Skipping candidate -- DOES NOT CONFORM to MinC struct OSCData.  ({pList})")
            return  None

        if  len(pList) <= 0:                    # Candidate is empty list.
            log.error("Skipping EMPTY LIST.")
            return  None


        #
        if  not isinstance(pList[0], str):      # Required element: path or label.
            log.error(f"Candidate DOES NOT LEAD with string.  Inserting empty string.  ({pList[0]})")
            mincList += "\'\'"
        else: 
            mincList += f"\'{pList[0]}\'"
            pList.pop(0)


        #                                       # First optional element is missing or is not a list.
        if      (len(pList) <= 0)   \
            or  not isinstance(pList[0], list):     

            if  len(pList) > 0:
                log.error(f"Candidate DOES NOT CONTAIN Free List.  Ignore remaining elements.  ({pList})")

            return "{" + mincList + "}"

                                                # First optional element: Free list.
        mincList += commaSpace + convertPythonFreeList(pList[0])
        pList.pop(0)


        #                                       # Second optional element is missing or is not a list.
        if      (len(pList) <= 0)   \
            or  not isinstance(pList[0], list):     

            if  len(pList) > 0:
                log.error(f"Candidate DOES NOT CONTAIN Common List.  Ignore remaining elements.  ({pList})")

            return "{" + mincList + "}"

                                                # Second optional element: Common list.
        candidateCommonString  = convertPythonCommonList(pList[0])
        if  candidateCommonString:
            mincList += commaSpace + candidateCommonString
        pList.pop(0)

        if  len(pList) > 0:
            log.error(f"Candidate CONTAINS EXTRA DATA.  Ignore remaining elements.  ({pList})")

        return "{" + mincList + "}"
    #ENDDEF -- convertPythonOSCDataCandidate



    # Parse OSC input.
    #
    mincList         :str   = ""
    commaSpace       :str   = ", "
    isOSCDataFormat  :bool  = False

    if  len(oscArgs) > 0:
        isOSCDataFormat  = (_cmixHelperVersion1 == oscArgs[0])

        if  isOSCDataFormat:
            oscArgs.pop(0)


    #
    mincList += "{" + f"\'{oscPath}\'"

    if  len(oscArgs) <= 0:              # Partial OSCData -- path only.
        mincList += "}"

    elif  not isOSCDataFormat:          # Partial OSCData -- path + Free list.
        mincList += ", " + convertPythonFreeList(oscArgs)
        mincList += "}"

    else:                               # Candidates for list of OSCData objects.
        # Assign oscPath to leading string value of first OSCData candidate.
        # (By hook or by crook.)
        #
        if  not isinstance(oscArgs[0], list):
            log.error(f"First candidate is not a list.  Prepending new list with OSC Path only.  ({oscArgs[0]})")
            oscArgs.insert(0, [ oscPath ])

        else:
            if  len(oscArgs[0]) <= 0:
                log.error(f"First candidate is empty list.  Inserting OSC Path.  ({oscArgs[0]})")
                oscArgs[0].insert(0, oscPath)

            elif  not isinstance(oscArgs[0][0], str):
                log.error(f"First candidate is missing path placeholder.  Inserting OSC Path.  ({oscArgs[0]})")
                oscArgs[0].insert(0, oscPath)

            else:
                oscArgs[0][0] = oscPath

        # Convert list of candidates.
        #
        isFirstToken  :bool  = True

        mincList    = ""
        commaSpace  = ""

        for  oscDataCandidate  in oscArgs:
            candidateString  :str  = None

            candidateString  = convertPythonOSCDataCandidate(oscDataCandidate)
            if  candidateString:
                mincList += commaSpace + candidateString

            if  isFirstToken:
                commaSpace = ", "
                isFirstToken = False

    #ENDIF -- Conversions to (list of) OSCData inputs


    #
    return  "{ " + mincList + " }"

#ENDDEF -- _convertOSCInputToMinCList


#                                                                    -o-
def  _mincFormatFromOSCArgs( oscPath  :str, 
                             oscArgs  :List[Any]
                          )  -> str:
    """
    Generate MinC version of OSC args per CMIX struct OSCData.  
      (See cmix/cmixHelper.sco.)
    """

    mincFormat  :str  = None

    #
    try:
        mincFormat  = _convertOSCInputToMinCList(oscPath, oscArgs)
        #log.debug(mincFormat)   #DEBUG

    except Exception as e:
        log.error(e)
        return  None

    return  mincFormat




#----------------------------------------------- -o--
# Testing.

#                                                                    -o-
def  testSendNormalOSCMessagesToScoreEnabledWithOSCData(oscClient:MOSRTcmix)  -> None:
    """
    Test how a list of OSC messages is handled by MinC struct OSCData shared conventions.
    Test range of MOSOSC message, excluding bundles.

    /resetScore is a useful OSC path for test because it provides access to
      the score, makes no sound and performs a simple atomic action.

    NB  mosRTcmix.cmixBuildEnablesOSC MUST be False.
    """
    log.mark()

    
    # Simple messages.
    #
    oscClient.messageSend("/resetScore")

    oscClient.messageSend("/resetScore", "two", 1, 2, 3)

    msg = oscClient.message("/resetScore")
    msg = oscClient.messageAdd(msg, "two2", 1, 2, 3)
    oscClient.send(msg)
                #NB  Same as previous message.



    # Free list with nesting.
    #
    three = ['a', 'b', [1,2,3], 'c']
    oscClient.messageSend("/resetScore", "three", three)


    four = ['a', 'b', [[42,108,7], 1,2,3, []], 'c']
    oscClient.messageSend("/resetScore", "four", four)



    # OSCData messages that are correct.
    #
    pathOnly = ["/usr/home/somewhere/"]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, pathOnly)
        #NB  Same as without using any arguments -- path is overwritten in first OSCData object.


    freeList = ["", [ 1,2,3, ['a', 'b', 'c']]]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, freeList)


    freeAndCommonLists = ["", [ 1,2,3, ['a', 'b', 'c']], [50,40,30,20,10]]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, freeAndCommonLists)


    commonListOnly = ["", [], [50,40,30,20,10]]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, commonListOnly)


    twoDataObjects = [
                        ["", [1,2,3, ['a', 'b', 'c']]],
                        ["lounge", [], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *twoDataObjects)


    msg  = oscClient.message("/resetScore", _cmixHelperVersion1, twoDataObjects[0])
    msg  = oscClient.messageAdd(msg, twoDataObjects[1])
    oscClient.send(msg)
                #NB  Same as previous message.



    # OSCData messages with (fixable) errors.
    #
    badCommonList1 = [
                        [""],
                        ["commonListWrongLength", [], [40,30,20,10]] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *badCommonList1)

    badCommonList2 = [
                        [""],
                        ["commonListBadTypes", ['x','y','z'], [50,"bogus",30,20,10]] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *badCommonList2)


    corruptOSCData1 = [
                        42,
                        ["hi there", ['x','y','z'], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *corruptOSCData1)

    corruptOSCData2 = [
                        [['i','j', [1,2,3]], [43,123,31,349,2]],
                        [[1000000]],
                        ["hi there", ['x','y','z'], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *corruptOSCData2)


    oscClient.messageSend("/resetScore", _cmixHelperVersion1, [])


    oscClient.messageSend("/resetScore", _cmixHelperVersion1, [[]])


    corruptOSCDataCandidate = [
                        ["", [1,2,3]],
                        [42, [43,123,31,349,2]],
                        [[1000000], 42],
                        [],
                        ["hi there", ['x','y','z'], [50,40,30,20,10], ['look', 108], ['at', 'all', 'this', 'fun']] 
                      ]
    oscClient.messageSend("/resetScore", _cmixHelperVersion1, *corruptOSCDataCandidate)

#ENDDEF -- testSendNormalOSCMessagesToScoreEnabledWithOSCData


#                                                                    -o-
def  testSendCMIXOSCMessagesToScoreEnabledWithOSCData(oscClient:MOSRTcmix)  -> None:
    """
    Test how a list of OSC messages is handled by MinC struct OSCData shared conventions.
    Test range of MOSRTcmix message, including bundles.

    /resetScore is a useful OSC path for test because it provides access to the score, makes no sound and performs a simple atomic action.

    NB  mosRTcmix.cmixBuildEnablesOSC MUST be False.
    """
    log.mark()

    commonListOdd   = _createCommonList(start=1, amp=3, pan=5)
    commonListEven  = _createCommonList(dur=20, freq=30)


    # Successful CMIX OSC messages.
    #
    msg1 = oscClient.cmixMessage("/resetScore", [1,2,3], commonList=commonListOdd)
    oscClient.send(msg1)

    #oscClient.cmixMessageSend("/resetScore", 5,6,7, commonList=commonListEven)
    oscClient.cmixMessageSend("/resetScore", [5,6,7], commonList=commonListEven)

    oscClient.cmixMessageSend("/resetScore", commonList=commonListEven)

    oscClient.cmixMessageSend("/resetScore")

    #oscClient.cmixMessageSend("/resetScore", 108, 42, [1,2,3], ['a','b','c', [55,66,77,88]])
    #oscClient.cmixMessageSend("/resetScore", [1,2,3], ['a','b','c', [55,66,77,88]])
    oscClient.cmixMessageSend("/resetScore", ['a','b','c', [55,66,77,88]])

    msg2 = oscClient.cmixMessage("/resetScore", [1,2,3], commonList=commonListOdd)
    #msg2 = oscClient.cmixMessageAdd(msg2, "garage", 31,32,33, commonList={"start":50,"freq":40})
    msg2 = oscClient.cmixMessageAdd(msg2, "garage", [31,32,33], commonList={"start":50,"freq":40})
    oscClient.send(msg2)


    # Bundling CMIX messages.
    #
    
    #log.debug(f"type(msg1) = {type(msg1)} -- {msg1}")
    #log.debug(f"type(msg2) = {type(msg2)} -- {msg2}")

    bundle1     = oscClient.bundle(msg1, delayTimeInSeconds=3)
    bundle2     = oscClient.bundle(msg2)

    #log.debug(f"type(bundle1) = {type(bundle1)}")
    #log.debug(f"type(bundle2) = {type(bundle2)}")
    #oscClient.send(bundle1)
    #oscClient.send(bundle2)

    bundleBoth  = oscClient.bundle(bundle1, bundle2)

    #log.debug(f"type(bundleBoth) = {type(bundleBoth)}")

    oscClient.send(bundleBoth)

#ENDDEF -- testSendCMIXOSCMessagesToScoreEnabledWithOSCData



#                                               -o-
def  testSendNormalAndCMIXMessages()  -> None:
    """
    Test with Python OSC server.

    NB  REQUIRES QUALIFIED REFERENCE to (mosRTcmix.)cmixBuildEnablesOSC in MOSRTcmix.send().
        This is different than when send is used by scripts outside this module.
    """

    global cmixBuildEnablesOSC 

    #
    client = MOSRTcmix()
    client.createClient(port=cmixPort)

    cmixBuildEnablesOSC = False

    #
    print()
    testSendNormalOSCMessagesToScoreEnabledWithOSCData(client)
    time.sleep(1)

    print()
    testSendCMIXOSCMessagesToScoreEnabledWithOSCData(client)

    print()
    z.postAndExit("DONE.")




#-------------------------------------- -o--
# Main, for testing.


if  "__main__" == __name__:
    testSendNormalAndCMIXMessages()

    sys.exit(0)


