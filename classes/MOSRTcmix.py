#                                                                        -o--
"""
    MOSRTcmix.py   (module)


    Provide glue between MOSOSC and RTcmix score files.

        * Share a common OSC message format between RTcmix and Python, 
            via Minc struct OSCData.
            Defined in MOSToolKit/demos/MOSOSC-with-RTcmix/cmixHelper.sco.

        * Define how score files engage OSCData.
            See MOSToolKit/demos/MOSOSC-with-RTcmix/oscDrumMachineDemo.sco.

	* Trigger CMIX score performance from Python OSC server with
	    incoming OSC message.  See playScoreWithOSCData() below.

        * Simple generation of OSCData objects by MOSOSC client.
	    cmixMessage*() function suite modeled on MOSOSC.message*()
	    suite -- instead of sending a list of simple values, it
	    can send one or more OSCData objects via an intuitive API.

	    NOTE: Use of cmixMessge*() is NOT REQUIRED.
	    MOSOSC.message*() works just the same as with any other
	    OSC server.


    PUBLIC FUNCTIONS--
        * cmixMessage()
        * cmixMessageAdd()
        * cmixMessageSend()  (Cf. MOSOSC.message*())

        * createCommonList()

        * playScoreWithOSCData()


    PROTECTED FUNCTIONS--
        * _createOSCDataObject()
        * _convertOSCInputToMincList()


    TEST FUNCTIONS--
        * testSendingCMIXOSCMessagesToScoreEnabledWithMincOSCData()
        * testSendingRawOSCMessagesToScoreEnabledWithMincOSCData()


    ASSUME  CMIX executable is accessible to subprocess.Popen() and os.system().

    ASSUME  Running with a CMIX score that understands Minc struct OSCData 
            and is prepared to receive them.  See cmixHelper.sco.


    See also:
      * MOSOSC
      * MOSToolKit/demos/MOSOSC-with-RTcmix/cmixHelper.sco
      * MOSToolKit/demos/MOSOSC-with-RTcmix/oscDrumMachineDemo.sco

    Learn more about RTcmix...
        * http://rtcmix.org
        * http://rtcmix.org/links

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.1"   #RELEASE



#----------------------------------------- -o--
# Modules.

import os
from subprocess import Popen
import subprocess
import tempfile
from typing import Any, List, Tuple, Union


#
from pythonosc.osc_message_builder import OscMessageBuilder


#
import MOSLog
log = MOSLog.MOSLog()

import MOSZ as z
#import MOSDump as dump

import MOSOSC




#----------------------------------------- -o--
# Protected attributes.

_cmixHelperVersion1  :str  = "cmix1"    #XXX
        # Shared between OSC message creation and message conversion functions.

_lengthOfOSCDataCommonList  :int  = 5   #XXX

_defaultCMIXUndefined  :int  = -1       #XXX




#----------------------------------------------- -o--
# Public functions.

#                                                                    -o-
def  cmixMessage(  oscClient       :MOSOSC.MOSOSC, 
                   oscPath         :str,
                   freeListArgs    :Tuple[Any]   = None,
                   commonList      :dict        = None,
                   sendMessageNow  :bool        = False,
                )  -> OscMessageBuilder:
    """
    oscClient is same as used for sending other  message*() and
        bundle*() objects.  Created with MOSOSC.createClient().

    OSC Path is optionally followed by a tuple or array (free list) and/or followed by a dictionary (RTCmix common parameters).
    All inputs must be encapsulated within the tuple/array or the dictionary.

    NB  commonList must be named on invocation,
        because it follows variable arg freeListArgs.

    NB  commonListDict may be literal dictionary with a partial set of keys.
        Unmentioned keys will be sent as defaults.
    """
    oscData  :List  = None


    # NB  Seed first OSCData object with empty label.
    #     Will be replaced by OSC path.
    #
    oscData = _createOSCDataObject("", freeListArgs, commonListDict=commonList)

    messageBuilder = OscMessageBuilder(oscPath)
    messageBuilder.add_arg(_cmixHelperVersion1)
    messageBuilder.add_arg(oscData)


    #
    if  sendMessageNow:
        oscClient.send(messageBuilder)

    return  messageBuilder


#                                                                    -o-
def  cmixMessageAdd(  oscClient       :MOSOSC.MOSOSC, 
                      messageBuilder  :OscMessageBuilder,
                      label           :str,
                      *freeListArgs   :Tuple[Any],
                      commonList      :dict        = None,
                   )  -> OscMessageBuilder:
    """
    (See description for cmixMessage().)
    """
    oscData  :List  = None

    #
    if  not isinstance(messageBuilder, OscMessageBuilder):
        log.critical(f"messageBuilder must be of type OscMessageBuilder.  ({messageBuilder})")

    #
    oscData  = _createOSCDataObject(label, *freeListArgs, commonListDict=commonList)
    messageBuilder.add_arg(oscData)

    #
    return  messageBuilder


#                                                                    -o-
def  cmixMessageSend(  oscClient       :MOSOSC.MOSOSC, 
                       oscPath         :str,
                       freeListArgs   :Tuple[Any]   = None,
                       commonList      :dict        = None,
                    )  -> OscMessageBuilder:
    """
    (See description for cmixMessage().)
    """
    return  cmixMessage(oscClient, oscPath, freeListArgs, commonList, True)



#                                                                    -o-
def  createCommonList(  start  :float  = _defaultCMIXUndefined,
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
def  playScoreWithOSCData(  oscPath               :str, 
                            oscArgs               :List[Any],
                            cmixScore             :str, 
                            cmixOSCInputListName  :str         = "oscDataObjectsFromPython",
                            runInForeground       :bool        = False,
                         )  -> None:
    """
    Prepend OSC input to CMIX score enabled with Minc struct OSCData,
      then pipe to CMIX.

    Set runInForground=True to run CMIX to see the runtime output
      (including any OSCData debugging).  NOTE: This also interrupts
      program flow until the score file is finished.
    """

    mincFormat             :str  = None
    cmixOSCGlobalVariable  :str  = None

    cmixOSCInputFile  :tempfile.NamedTemporaryFile  = None

    catProcessArgs   :List  = ["cat"]
    cmixProcessArgs  :List  = ["CMIX"]

    catProcess   :Popen  = None
    cmixProcess  :Popen  = None

    cmixCommandlineForDebug  :str  = None


    #
    try:
        mincFormat  = _convertOSCInputToMincList(oscPath, oscArgs)
        #log.debug(mincFormat)   #DEBUG

    except Exception as e:
        log.error(e)
        return

    cmixOSCGlobalVariable  = f"\n{cmixOSCInputListName} = {mincFormat}\n\n"


    #
    cmixOSCInputFile  = tempfile.NamedTemporaryFile(mode="w+")
    cmixOSCInputFile.write(cmixOSCGlobalVariable)
    cmixOSCInputFile.seek(0)

    #log.debug(f"Contents of {cmixOSCInputFile.name}...")   #DEBUG
    #os.system(f"cat {cmixOSCInputFile.name}")              #DEBUG


    #
    catProcessArgs.append(cmixOSCInputFile.name)
    catProcessArgs.append(cmixScore)

    if  runInForeground:   #DEBUG
        cmixCommandlineForDebug  = " ".join(catProcessArgs) + " | " + " ".join(cmixProcessArgs)
        log.debug("CMD: " + cmixCommandlineForDebug)
        os.system(cmixCommandlineForDebug)
        cmixOSCInputFile.close()
        return


    # NB  Missing executable raises exception.  
    #     Missing files only noted on stderr, but dumped to console.
    #
    # Occasionaly temporary cmixOSCInputFile is named but does not exist.
    #   This also causes CMIX to abandon the score file.  Eg:
    #
    #       cat: /var/folders/fy/ysz2c_yx2zvb3nvq_zjsqtcc000crv/T/tmpnn2woszd: No such file or directory
    #       *** ERROR [parser]: 'oscDataObjectsFromPython' is not declared (near line 29)
    #       *** WARNING [parse_score]:  caught parse exception: Parser error
    #       *** WARNING [parse_score]:  Exit-on-error enabled - exiting
    #  
    try:
        catProcess   = Popen(catProcessArgs, stdout=subprocess.PIPE)
        cmixProcess  = Popen(cmixProcessArgs, stdin=catProcess.stdout, stdout=subprocess.PIPE)
        catProcess.stdout.close()

    except Exception as e:
        log.error(e)
        return 

    finally:
        cmixOSCInputFile.close()

#ENDDEF -- playScoreWithOSCData




#----------------------------------------------- -o--
# Protected functions.

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

    if  not isinstance(freeListArgs, (Tuple,List,list)):
        log.critical(f"freeListArgs IS NOT a Tuple or list.  ({freeListArgs})")


    #
    if  freeListArgs is not None:
        for arg in freeListArgs:
            if  None is arg:  continue 
            freeList.append(arg)

    oscData.append(freeList)

    if  commonListDict:
        completeList = createCommonList(**commonListDict)
        oscData.append( list(completeList.values()) )


    #
    return  oscData


#                                                                    -o-
def  _convertOSCInputToMincList(oscPath:str, oscArgs:List[Any])  -> str:
    """
    Convert incoming OSC message into a CMIX Minc list format that can
    be read by parseOSCData() and converted into A LIST OF Minc
    struct OSCData as defined by cmixHelper.sco, version 1.

    If the first token is "cmix1" (for cmixHelper, v1), then ASSUME
    each following list represents a candidate Minc struct OSCData
    object.  By design, the path token in the first object is left
    blank, then overwritten with the OSC path.  All list objects must
    have a form analogous to OSCData:

        [ "path-or-label", [free_list], [common_list] ]

    ...where the two lists are optional, per cmixHelper.sco.

    Otherwise, take all items and encapsulate them into a single Free
    List within a single Minc struct OSCData object.

    For either method, encapsulate the final result in one more list,
    delivering a single list to the score environment.

    Be flexible with processing errors by tossing smallest broken
    unit, in case adjacent elements can be salvaged.

    NB  Handles limited types, a common subset of both OSC and
          Minc types: float, string, list.  Lists may be nested.
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


    def  convertPythonOSCDataCandidate(pList:List)  -> Union[str,None]:
        mincList      :str   = ""
        commaSpace    :str   = ", "

        candidateCommonString  :str  = None


        #                                       
        if  not isinstance(pList, list):        # Candidate is not a list.
            log.error(f"Skipping candidate -- DOES NOT CONFORM to Minc struct OSCData.  ({pList})")
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

#ENDDEF -- convertOSCInputToMincList




#----------------------------------------------- -o--
# Test functions.

#                                                                    -o-
def  testSendingCMIXOSCMessagesToScoreEnabledWithMincOSCData(oscClient:MOSOSC.MOSOSC)  -> None:
    """
    Test how a list of OSC messages is handled by Minc struct OSCData shared conventions.

    /clearDiskMemory is a useful OSC path for test because it provides access to the score, makes no sound and performs a simple atomic action.
    """

    commonListOdd   = createCommonList(start=1, amp=3, pan=5)
    commonListEven  = createCommonList(dur=20, freq=30)


    # Successful CMIX OSC messages.
    #
    msg1 = cmixMessage(oscClient, "/clearDiskMemory", [1,2,3], commonList=commonListOdd)
    oscClient.send(msg1)

    #cmixMessageSend(oscClient, "/clearDiskMemory", 5,6,7, commonList=commonListEven)                   #NOWORKIE.
    cmixMessageSend(oscClient, "/clearDiskMemory", [5,6,7], commonList=commonListEven)

    cmixMessageSend(oscClient, "/clearDiskMemory", commonList=commonListEven)

    cmixMessageSend(oscClient, "/clearDiskMemory")

    #cmixMessageSend(oscClient, "/clearDiskMemory", 108, 42, [1,2,3], ['a','b','c', [55,66,77,88]])     #NOWORKIE.
    #cmixMessageSend(oscClient, "/clearDiskMemory", [1,2,3], ['a','b','c', [55,66,77,88]])              #NOWORKIE.
    cmixMessageSend(oscClient, "/clearDiskMemory", ['a','b','c', [55,66,77,88]])

    msg2 = cmixMessage(oscClient, "/clearDiskMemory", [1,2,3], commonList=commonListOdd)
    #msg2 = cmixMessageAdd(oscClient, msg2, "garage", 31,32,33, commonList={"start":50,"freq":40})      #NOWORKIE.
    msg2 = cmixMessageAdd(oscClient, msg2, "garage", [31,32,33], commonList={"start":50,"freq":40})
    oscClient.send(msg2)


    # Bundling CMIX messages.
    #

    bundle1     = oscClient.bundle(msg1, delayTimeInSeconds=3)
    bundle2     = oscClient.bundle(msg2)
    bundleBoth  = oscClient.bundle(bundle1, bundle2)

    oscClient.send(bundleBoth)


#ENDDEF -- testSendingCMIXOSCMessagesToScoreEnabledWithMincOSCData


#                                                                    -o-
def  testSendingRawOSCMessagesToScoreEnabledWithMincOSCData(oscClient:MOSOSC.MOSOSC)  -> None:
    """
    Test how a list of OSC messages is handled by Minc struct OSCData shared conventions.

    /clearDiskMemory is a useful OSC path for test because it provides access to the score, makes no sound and performs a simple atomic action.
    """
    
    # Simple messages.
    #
    oscClient.messageSend("/clearDiskMemory")


    oscClient.messageSend("/clearDiskMemory", "two", 1, 2, 3)


    msg = oscClient.message("/clearDiskMemory")
    msg = oscClient.messageAdd(msg, "two2", 1, 2, 3)
    oscClient.send(msg)
                #NB  Same as previous message.



    # Free list with nesting.
    #
    three = ['a', 'b', [1,2,3], 'c']
    oscClient.messageSend("/clearDiskMemory", "three", three)


    four = ['a', 'b', [[42,108,7], 1,2,3, []], 'c']
    oscClient.messageSend("/clearDiskMemory", "four", four)



    # OSCData messages that are correct.
    #
    pathOnly = ["/usr/home/somewhere/"]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, pathOnly)
        #NB  Same as without using any arguments -- path is overwritten in first OSCData object.


    freeList = ["", [ 1,2,3, ['a', 'b', 'c']]]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, freeList)


    freeAndCommonLists = ["", [ 1,2,3, ['a', 'b', 'c']], [50,40,30,20,10]]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, freeAndCommonLists)


    commonListOnly = ["", [], [50,40,30,20,10]]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, commonListOnly)


    twoDataObjects = [
                        ["", [1,2,3, ['a', 'b', 'c']]],
                        ["lounge", [], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *twoDataObjects)


    msg  = oscClient.message("/clearDiskMemory", _cmixHelperVersion1, twoDataObjects[0])
    msg  = oscClient.messageAdd(msg, twoDataObjects[1])
    oscClient.send(msg)
                #NB  Same as previous message.



    # OSCData messages with (fixable) errors.
    #
    badCommonList1 = [
                        [""],
                        ["commonListWrongLength", [], [40,30,20,10]] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *badCommonList1)

    badCommonList2 = [
                        [""],
                        ["commonListBadTypes", ['x','y','z'], [50,"bogus",30,20,10]] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *badCommonList2)


    corruptOSCData1 = [
                        42,
                        ["hi there", ['x','y','z'], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *corruptOSCData1)

    corruptOSCData2 = [
                        [['i','j', [1,2,3]], [43,123,31,349,2]],
                        [[1000000]],
                        ["hi there", ['x','y','z'], [50,40,30,20,10]] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *corruptOSCData2)


    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, [])


    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, [[]])


    corruptOSCDataCandidate = [
                        ["", [1,2,3]],
                        [42, [43,123,31,349,2]],
                        [[1000000], 42],
                        [],
                        ["hi there", ['x','y','z'], [50,40,30,20,10], ['look', 108], ['at', 'all', 'this', 'fun']] 
                      ]
    oscClient.messageSend("/clearDiskMemory", _cmixHelperVersion1, *corruptOSCDataCandidate)

#ENDDEF -- testSendingRawOSCMessagesToScoreEnabledWithMincOSCData

