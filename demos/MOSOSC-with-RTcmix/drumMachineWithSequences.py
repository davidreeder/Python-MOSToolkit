#!/usr/bin/env python
#                                       -o--
"""
  drumMachineWithSequences.py

  Demo how OSC can manage sound objects defined by RTcmix.

  Event loop manages threads for sending MIDI sequences and other data
  via OSC paths.  One thread to track the others and post state to
  stdout.

"""

version  :str  = "0.1"   #RELEASE

USAGE  :str  = "USAGE: drumMachineWithSequences.py [--help] [--hostname HOSTNAME][--port PORT]"




#-------------------------------------- -o--
from threading import Thread
import time


#
import MOSLog
log = MOSLog.MOSLog(logTime=True, logDate=False)

#import MOSDump as dump
import MOSZ as z

import MOSMusic as music

import MOSOSC
import MOSRTcmix




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
highCount                :float  = -1.0         #NB Initial value out of range.
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

    value  :int  = music.generateScaleSequence(**kwargs)

    while  True:
        if  not lowThreadEnabled:  break
        if  not lowSequenceEnabled:  continue

        lowCount     = next(value)
        lowOrnament  = ""

        msg = MOSRTcmix.cmixMessage(client, "/lowSequence", [lowCount])

        if  lowSequenceOrnamentsEnabled:
            ornamentBlob = music.generateOrnament(lowCount, kwargs["key"], kwargs["mode"], bpm)

            if  ornamentBlob:
                ornamentName, ornamentBPM, ornamentSubdivision, ornament  = tuple(ornamentBlob)
                lowOrnament = ornamentName
                msg = MOSRTcmix.cmixMessageAdd(client, msg, ornamentName, [ornamentBPM, ornamentSubdivision, ornament])

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
    if  (bpm <= 0)  or  (subDivision <= 0):
        z.postAndExit(f"{log.defName}: bpm or subDivision are LESS THAN OR EQUAL TO ZERO.")

    time.sleep(music.subdivisionPerBeat(bpm, subDivision))




#-------------------------------------- -o--
# Local sequence generators.

#                                               -o-
def  generateMonotonicSequence(initialValue:int=0)  -> int:
    startValue  :int  = initialValue

    while  True:
        yield  startValue
        startValue += 1




#-------------------------------------- -o--
# Test things.

#                                               -o-
def  testOSC()  -> None:
    test1  :bool  = False
    test2  :bool  = True

    client = MOSOSC.MOSOSC()
    client.createClient()


    # Send frequencies.
    # 
    if  test1:
        for r in range(200, 400, 25):
            client.messageSend("/lowSequence", [r])
            time.sleep(1)


    # Send MIDI.  Traverse all modes on ivory keys only.
    #
    if  test2:
        ivoryKeys  :list  = music.ModesAdditional[music.ModeNames.major].copy()
        root       :int   = 60

        for  name  in music.Modes.keys():
            midiRoot = root + ivoryKeys.pop(0)
            log.info(name)

            scale  :list  = music.Modes[name].copy()
            scale.append(scale[0] + music.NOTES_PER_OCTAVE)

            for  note  in scale:
                client.messageSend("/lowSequence", [midiRoot + note])
                time.sleep(0.5)
            
            time.sleep(1)
        
    # 
    print()
    z.postAndExit("")

#ENDDEF -- testOSC()


#                                               -o-
def  testCMIXOSCData()  -> None:
    client = MOSOSC.MOSOSC()
    client.createClient(cmdlineArgs.hostname, cmdlineArgs.port)

    MOSRTcmix.testSendingRawOSCMessagesToScoreEnabledWithMincOSCData(client) 
    MOSRTcmix.testSendingCMIXOSCMessagesToScoreEnabledWithMincOSCData(client)   

    print()
    z.postAndExit("")


#                                               -o-
def  testScaleSequencer(): 
    # kwargs for generateScaleSequence().
    #
    d  :dict  = {  
            #"key"               : music.Key.C,                  #DEFAULT
            #"key"               : music.Key.D,
            #"key"               : music.Key.Gs,

            #"octave"            : music.MIDINote.C4,            #DEFAULT
            "octave"             : music.MIDINote.C2,

            #"scaleForMode"      : music.ModeNames.ionian,       #DEFAULT
            "mode"               : music.ModeNames.locrian,

            #"octaveRange"       : 2,                            #DEFAULT
            "octaveRange"        : 3,

            #"direction"         : music.Direction.UP,           #DEFAULT
            #"direction"         : music.Direction.DOWN,
            #"direction"         : music.Direction.DOWNUP,
            #"direction"         : music.Direction.UPDOWN,

            #"scaleEndBoundByRoot"  : True,                      #DEFAULT
            #"scaleEndBoundByRoot"  : False,
        }

    index = music.generateScaleSequence(**d)


    #
    while  True:
        if  z.readOneCharacter() == 'q':  break
        nextNote  :int  = next(index)
        print(f"  {nextNote}", end="", flush=True)


    #
    print("\n\nDONE.", end="\n\r", flush=True)
    z.postAndExit("")

#ENDDEF -- testScaleSequencer()


#                                               -o-
def  testOrnaments(): 
    rval  :list  = []


    rval = music._translateOrnamentScaleToMIDI("sixteenthLeadIn", 60, music.Key.C, music.ModeNames.ionian)
    log.info(f"01:  {rval}")
    rval = music._translateOrnamentScaleToMIDI("sixteenthLeadIn", 69, music.Key.C, music.ModeNames.ionian)
    log.info(f"02:  {rval}")

    #music._translateOrnamentScaleToMIDI("sixteenthLeadIn", 63, music.Key.C, music.ModeNames.ionianX)         #FAIL (system).
    #music._translateOrnamentScaleToMIDI("sixteenthLeadIn", -1, music.Key.C, music.ModeNames.pentatonic)       #FAIL
    #music._translateOrnamentScaleToMIDI("sixteenthLeadIn", 110, music.Key.C, music.ModeNames.pentatonic)       #FAIL

    rval = music._translateOrnamentScaleToMIDI("sixteenthLeadIn", 66, music.Key.C, music.ModeNames.pentatonic)
    log.info(f"03:  {rval}")

    rval = music._translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 52, music.Key.E, music.ModeNames.phrygian)
    log.info(f"04:  {rval}")
    rval = music._translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 59, music.Key.E, music.ModeNames.phrygian)
    log.info(f"05:  {rval}")
    rval = music._translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 67, music.Key.C, music.ModeNames.ionian)
    log.info(f"06:  {rval}")

    rval = music._translateOrnamentScaleToMIDI("sixteenthPop", 60, music.Key.C, music.ModeNames.mixolydian)
    log.info(f"07:  {rval}")
    rval = music._translateOrnamentScaleToMIDI("sixteenthPop", 64, music.Key.C, music.ModeNames.mixolydian)
    log.info(f"08:  {rval}")


    print()
    z.postAndExit("")




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

      C    Clear CMIX Disk Memory

    - - - - - - - - - - - - - - -

      M/m  Raise/lower BPM  ({bpm})
      o    Show/hide OSC output
      t    Hide/show timeline

      H    Post hotkeys (anytime)
      q    Quit

    """ )


if  "__main__" == __name__:

    cmdlineArgs = z.parseCommandlineArguments( [
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




    #-------------------------------------------- -o-
    #testOSC()             #DEBUG
    #testCMIXOSCData()     #DEBUG
    #testScaleSequencer()  #DEBUG
    #testOrnaments()       #DEBUG



    #-------------------------------------------- -o-
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


    #
    client = MOSOSC.MOSOSC()
    client.createClient(cmdlineArgs.hostname, cmdlineArgs.port)
    client.enablePathLogging = False

    postHotkeys()

    z.postCRToContinue()
    print("\n")

    client.messageSend("/clearDiskMemory")


    #
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
            lowSequenceOrnamentsEnabled  = not lowSequenceOrnamentsEnabled
            if  not lowSequenceOrnamentsEnabled:
                music.generateOrnamentReset()

        elif  'h' == ch:                # highSequence on/off
            highSequenceEnabled  = not highSequenceEnabled


        #
        elif  'b' == ch:                # BOOM
            makeBoom()

        elif  'k' == ch:                # KAPOW
            makeKapow()

    
        #
        elif  'C' == ch:                # clearDiskMemory
            client.messageSend("/clearDiskMemory")
            music.generateOrnamentReset()
    

    #
    lowThreadEnabled    = False
    highThreadEnabled   = False
    postThreadEnabled   = False

    lowThread.join()
    highThread.join()
    postThread.join()

#ENDMAIN

