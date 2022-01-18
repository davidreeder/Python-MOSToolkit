#!/usr/bin/env python
#                                       -o--
"""
  soundsAndSequences_oscClient.py


  Demonstrate how...
    * OSC can manage sound objects defined by RTcmix
    * OSC can be used with RTcmix whether or not the CMIX build supports OSC.

  This OSC server sends OSC messages to a Python OSC client or directly to CMIX
  depending on how mosRTcmix.cmixBuildEnablesOSC is set.  Although there are
  tradeoffs between functionality of the two servers, the result is roughly the same:
  the OSC client effects real-time controls to trigger and parameterize sounds 
  defined by RTcmix.  See README.md for more full details.


  Demo uses an event loop to manage threads that send MIDI sequences and
  other data via well-defined OSC paths.  One thread tracks the others and
  posts state to stdout.

"""

version  :str  = "0.2"   #RELEASE

USAGE  :str  = "USAGE: soundsAndSequences_client.py [--help] [--hostname HOSTNAME][--port PORT][--pathToCMIXScore PATH_TO_CMIX_SCORE]"



#-------------------------------------- -o--
# Modules.

from threading import Thread
import time


#
import mosLog
log = mosLog.MOSLog(logTime=True, logDate=False)

#import mosDump as dump
import mosZ as z

import mosMusic as music

import mosRTcmix        # NB  Inherits from mosOSC.MOSOSC.




#-------------------------------------- -o--
# Globals.

bpm  :float  = 25   #DEFAULT


#
lowThreadEnabled             :bool   = True
lowSequenceEnabled           :bool   = False
lowCount                     :float  = -1.0          #NB Initial value out of range.
lowCountPrev                 :float  = lowCount
lowSequenceSubdivision       :float  = 2.0
lowSequenceOrnamentsEnabled  :bool   = False
lowOrnament                  :str    = ""

highThreadEnabled        :bool   = True
highSequenceEnabled      :bool   = False
highCount                :float  = -1.0              #NB Initial value out of range.
highCountPrev            :float  = highCount
highSequenceSubdivision  :float  = 7.0

boomString   :str  = ""
kapowString  :str  = ""


#
postThreadEnabled  :bool  = True
postEventsEnabled  :bool  = True

commonSequenceSubdivision  :float  = lowSequenceSubdivision * highSequenceSubdivision




#-------------------------------------- -o--
# Functions.

#                                               -o-
def  lowSequence(**kwargs:dict)  -> None:
    global  lowCount
    global  lowOrnament

    value    :int  = music.generateScaleSequence(**kwargs)

    while  True:
        if  not lowThreadEnabled:  break
        if  not lowSequenceEnabled:  continue

        lowCount     = next(value)
        lowOrnament  = ""

        msg = client.cmixMessage("/lowSequence", [lowCount])

        if  lowSequenceOrnamentsEnabled:
            ornamentBlob = music.generateOrnament(lowCount, kwargs["key"], kwargs["mode"], bpm)

            if  ornamentBlob:
                ornamentName, ornamentBPM, ornamentSubdivision, ornament  = tuple(ornamentBlob)
                lowOrnament = ornamentName
                msg = client.cmixMessageAdd(msg, ornamentName, [ornamentBPM, ornamentSubdivision, ornament])

        client.send(msg)
        sleepSubdivisionPerBeat(lowSequenceSubdivision)


#                                               -o-
def  highSequence(**kwargs:dict)  -> None:
    global  highCount

    value  :int  = music.generateScaleSequence(**kwargs)

    while  True:
        if  not highThreadEnabled:  break
        if  not highSequenceEnabled:  continue

        highCount = next(value)
        client.messageSend("/highSequence", [highCount])

        sleepSubdivisionPerBeat(highSequenceSubdivision)


#                                               -o-
def  makeBoom()  -> None:
    global  boomString

    boomString = "BOOM."
    client.messageSend("/boom", [1])

    sleepSubdivisionPerBeat(commonSequenceSubdivision)
    boomString = ""

#                                               -o-
def  makeKapow()  -> None:
    global  kapowString

    kapowString = "KAPOW!"
    client.messageSend("/kapow", [1])

    sleepSubdivisionPerBeat(commonSequenceSubdivision)
    kapowString = ""
    

#                                               -o-
def  postOneEvent()  -> None:
    lowCountString   :str  = "   ."
    highCountString  :str  = "    ."
    asterisk         :str  = "  "

    global  lowCountPrev, highCountPrev
    global  lowOrnament


    #
    if  lowCount != lowCountPrev:
        lowCountString = lowCountPrev = lowCount

    if  len(lowOrnament) > 0:
        asterisk     = " *"
        lowOrnament  = "    " + lowOrnament

    if  highCount != highCountPrev:
        highCountString = highCountPrev = highCount

    s  :str  = f"|  {lowCountString:4}{asterisk}   {boomString:5} {kapowString:6}{highCountString:5}{lowOrnament}"

    log.message(s)

    lowOrnament = ""


#                                               -o-
def  postEvents()  -> None:
    while  True:
        if  not postThreadEnabled:  break
        if  not postEventsEnabled:  continue

        postOneEvent()
        sleepSubdivisionPerBeat(commonSequenceSubdivision)


#                                               -o-
def  sleepSubdivisionPerBeat(subDivision:int=1)  -> None:
    time.sleep(music.subdivisionPerBeat(bpm, subDivision))




#-------------------------------------- -o--
# Main.

#                                               -o-
def  postHotkeys()  -> None:
    print( f"""
  HOTKEYS--

      h    Enable/disable high sequence
      l    Enable/disable low sequence
      L    Enable/disable low sequence ornaments

      b    Trigger BOOM 
      k    Trigger KAPOW 

      R    Reset internal state of score.

    - - - - - - - - - - - - - - -

      M/m  Raise/lower BPM  ({bpm})
      o    Show/hide OSC output
      t    Hide/show timeline

      H    Post hotkeys (anytime)
      q    Quit


  NOTE--
      * mosRTcmix.cmixBuildEnablesOSC = {mosRTcmix.cmixBuildEnablesOSC}

    """ )



#-------------------------------------------- -o-
if  "__main__" == __name__:

    # Commandline arguments.
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
          "help"            : "Score to load into CMIX.  (When CMIX build enables OSC.)",    
        },                                                        

      ] )



    #-------------------------------------------- -o-
    # Sequence configuration.

    lowSequenceArgs  :dict  = {  
           "key"                  : music.Key.C,
           "mode"                 : music.ModeNames.mixolydian,
           #"mode"                 : music.ModeNames.pentatonic,
           "octave"               : music.MIDINote.C2, 
           #"octaveRange"          : 2,
           #"direction"            : music.Direction.UP,
           "scaleEndBoundByRoot"  : False,
         }

    highSequenceArgs  :dict  = {  
           "key"                   : music.Key.F,
           "mode"                  : music.ModeNames.mixolydian,
           "octave"                : music.MIDINote.C5, 
           "octaveRange"           : 3,
           "direction"             : music.Direction.DOWNUP,
           #"scaleEndBoundByRoot"   : False,
         }


    lowThread   :Thread  = Thread(target=lowSequence, kwargs=lowSequenceArgs)
    highThread  :Thread  = Thread(target=highSequence, kwargs=highSequenceArgs)
    postThread  :Thread  = Thread(target=postEvents)



    #-------------------------------------------- -o-
    # Client configuration.
    # Directives to initialize server.

    client = mosRTcmix.MOSRTcmix()   # NB  Global.

    client.createClient(cmdlineArgs.hostname, cmdlineArgs.port)
    client.enablePathLogging = False

    #mosRTcmix.cmixBuildEnablesOSC = False      
        # NB  Indicates whether CMIX build enables "CMIX-style" OSC.  DEFAULT is True.
        # Choosing False also ASSUMES the use of an OSC server that manages CMIX.

    if  mosRTcmix.cmixBuildEnablesOSC:
        client.sendScoreToCMIX(cmdlineArgs.pathToCMIXScore)

    postHotkeys()

    z.postCRToContinue()
    print("\n")

    client.messageSend("/resetScore")



    #-------------------------------------------- -o-
    # Run event loop.

    lowThread.start()
    highThread.start()
    postThread.start()

    while  True:
        ch = z.readOneCharacter()

        if  'q' == ch:                  # Quit
            client.messageSend("/quit")
            log.info("Quit.  Waiting for threads...")
            break

        elif  'H' == ch:                # Post hotkeys.
            postHotkeys()


        #
        elif  'M' == ch:                # BPM up/down
            bpm += 1
            log.info(f"BPM = {bpm}")

        elif  'm' == ch:
            bpm -= 1
            if  bpm <= 0:
                bpm = 1
                log.warning("bpm cannot DROP BELOW 1.")

            log.info(f"BPM = {bpm}")

        elif  'o' == ch:                # OSC reporting on/off
            client.enablePathLogging  = not client.enablePathLogging

        elif  't' == ch:                # Timeline off/on
            postEventsEnabled  = not postEventsEnabled


        #
        elif  'l' == ch:                # lowSequence on/off
            lowSequenceEnabled  = not lowSequenceEnabled

        elif  'L' == ch:                # lowSequence ornaments on/off
            ornamentStatus = "ENABLED"

            lowSequenceOrnamentsEnabled  = not lowSequenceOrnamentsEnabled
            if  not lowSequenceOrnamentsEnabled:
                music.generateOrnamentReset()
                ornamentStatus = "DISABLED"

            log.info(f"Ornaments for Low Sequence are {ornamentStatus}.")

        elif  'h' == ch:                # highSequence on/off
            highSequenceEnabled  = not highSequenceEnabled


        #
        elif  'b' == ch:                # BOOM
            makeBoom()

        elif  'k' == ch:                # KAPOW
            makeKapow()

    
        #
        elif  'R' == ch:                # Reset state of highSequenceSound(). 
            client.messageSend("/resetScore")
            music.generateOrnamentReset()
    

    #
    lowThreadEnabled    = False
    highThreadEnabled   = False
    postThreadEnabled   = False

    lowThread.join()
    highThread.join()
    postThread.join()

#ENDMAIN

