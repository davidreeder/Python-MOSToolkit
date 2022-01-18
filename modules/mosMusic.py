#                                                                        -o--
"""
    mosMusic.py   (module)

    Initial focus: Generate MIDI scale sequences.


    PUBLIC ENUMS--
        * Key
        * MIDINote
        * Direction
        * ModeNames

    PUBLIC DICTIONARIES--
        * Modes
        * ModesAdditional
        * Ornaments


    HELPER FUNCTIONS--
        * subdivisionPerBeat()
        * findScaleForMode()


    GENERATOR FUNCTIONS--
        * generateScaleSequence()
        * generateOrnament()
        * generateOrnamentReset()


    PROTECTED FUNCTIONS--
        * _discoverMIDINoteScaleIndexInMode()
        * _translateOrnamentScaleToMIDI()


    TEST FUNCTIONS--
        * testIvoryModesViaOSC()
        * testScaleSequencer()
        * testOrnaments()

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021-2022.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.2"   #RELEASE



#----------------------------------------- -o--
# Modules.

from enum import IntEnum
import random
import sys
import time

from typing import Any, Dict, List, Union


#
import mosLog 
log = mosLog.MOSLog(logTime=False, logDate=False)   

#import mosDump as dump
import mosZ as z




#----------------------------------------- -o--
# Globals.

SECONDS_PER_MINUTE  :float  = 60   #CONSTANT
NOTES_PER_OCTAVE    :int    = 12   #CONSTANT




#----------------------------------------- -o--
# Enum and Dict types to capture well-known constants.

#                                               -o-
class  Key(IntEnum):
    """
    Key offset starting with C=0.  
    Enum keys "Kx" where x is "s" for sharp, "f" for flat.
    """
    C   = 0
    Cs  = 1
    Cf  = 11

    D   = 2
    Ds  = 3
    Df  = 1

    E   = 4
    Es  = 5
    Ef  = 3

    F   = 5
    Fs  = 6
    Ff  = 4

    G   = 7
    Gs  = 8
    Gf  = 6

    A   = 9
    As  = 10
    Af  = 8

    B   = 11
    Bs  = 0
    Bf  = 10


#                                               -o-
class  MIDINote(IntEnum):
    """
    Common key indices.
    """
    C1  = 24
    C2  = 36
    C3  = 48
    C4  = 60
    C5  = 72
    C6  = 84
    C7  = 96
    C8  = 108


#                                               -o-
class  Direction(IntEnum):
    """
    Up, down, up/down, down/up.
    """
    UP      = 1
    DOWN    = -1
    UPDOWN  = 2    #XXX
    DOWNUP  = -2


#
class  ModeNames(IntEnum):
    ionian      = 1
    dorian      = 2
    phrygian    = 3
    lydian      = 4
    mixolydian  = 5
    aeolian     = 6
    locrian     = 7

    major          = 10
    harmonicMinor  = 11
    minor          = 12

    pentatonic     = 15


#                                               -o-
# See findScaleForMode().
#
Modes  :Dict[ModeNames,List]  = {
    ModeNames.ionian      : [0, 2, 4, 5, 7, 9, 11],   # - - v - - - v
    ModeNames.dorian      : [0, 2, 3, 5, 7, 9, 10],   # - v - - - v -
    ModeNames.phrygian    : [0, 1, 3, 5, 7, 8, 10],   # v - - - v - -
    ModeNames.lydian      : [0, 2, 4, 6, 7, 9, 11],   # - - - v - - v
    ModeNames.mixolydian  : [0, 2, 4, 5, 7, 9, 10],   # - - v - - v -
    ModeNames.aeolian     : [0, 2, 3, 5, 7, 8, 10],   # - v - - v - -
    ModeNames.locrian     : [0, 1, 3, 5, 6, 8, 10],   # v - - v - - -
  }

ModesAdditional  :Dict[ModeNames,List]  = {
    ModeNames.major          : Modes[ModeNames.ionian],         # - - v - - - v

    ModeNames.harmonicMinor  : [0, 2, 3, 5, 7, 8, 11],          # - v - - v -v
    ModeNames.minor          : Modes[ModeNames.aeolian],        # - v - - v - -

    ModeNames.pentatonic     : [0, 2, 4, 6, 8, 10],             # - - - - -
  }



# Scale note offsets from current note in scale.
#
# * Offsets serve as indices into mode definitions allowing translation 
#     of ornaments into specific MIDI notes per starting pitch, key, and mode.
# * Zero(0) is current note, NOT ROOT.  Offsets are relative to current note.
# * If a scale has N notes, then N represents the octave.  (Eg: 6 is the octave for a pentatonic scale.)
# * Duration of notes within the ornament, its syncopation, interpretation, &c 
#     are implemented by the receiver of the ornament data.  Sender and receiver are 
#     ASSUMED to have a shared sense of beats per minute (BPM).
# * Ornament and scale length mismatches may result in incorrect ornament translation.
#
# sixteenthsLeadIn 
#   One beat: Eighth rest + two(2) sixteenth rising adjacent leading tones to MIDINote (1 note).
#   Subdivision: Sixteenths.
# 
# sixteenthsTripletTurnaround 
#   Two beats: Sixteenth triplet ornament beginning with <MIDINote> (6 notes), followed by eighth note denouement (2 notes).
#   Subdivision: Sixteenth triplets.
# 
# sixteenthPop 
#   Two beats: Octave jump from <MIDINote> on sixteenth offbeats (3 notes), followed by eighth note "6, 5" (2 notes).
#   Subdivision: Sixteenths.
#
#
# Dictionary value format: [ subdivision, [ ornamentScaleTones... ] ]
# 

Ornaments  :Dict[str,List[Any]]  = {
    "sixteenthLeadIn"             : [4,  [ -2, -1, 0 ]],
    "sixteenthTripletTurnaround"  : [6,  [ 0, 1, 0, -1, -2, -3,  7, 6 ]],
    "sixteenthPop"                : [4,  [ 0, 7, 7,  3, 5 ]], 
  }


# Used by generateOrnament*().
#
ornamentState  :Dict[str,int]  = {
    "sixteenthLeadIn"             : 0,
    "sixteenthTripletTurnaround"  : 0,
    "sixteenthPop"                : 0,
  }




#----------------------------------------- -o--
# Helper functions.

#                                                                    -o-
def  subdivisionPerBeat(bpm:float, subdivision:float)  -> float:
    if  (bpm <= 0)  or  (subdivision <= 0):
        log.critical("bpm or subdivision are LESS THAN OR EQUAL TO ZERO.")

    return  (SECONDS_PER_MINUTE / bpm / subdivision)


#                                                                    -o-
def  findScaleForMode(mode:ModeNames) -> Union[List[int],None]:
    if  mode in Modes:
        return  Modes[mode]
    elif  mode in ModesAdditional:
        return  ModesAdditional[mode]

    return  None




#----------------------------------------- -o--
# Generators.

#                                                                    -o-
# RETURN  Infinite sequences of... scale starting at key within an
#         octave, run up or down for range octaves.
#
def  generateScaleSequence(  key                  :Key         = Key.C,
                             mode                 :ModeNames   = ModeNames.ionian,
                             octave               :MIDINote    = MIDINote.C4, 
                             octaveRange          :int         = 2,
                             direction            :Direction   = Direction.UP,
                             scaleEndBoundByRoot  :bool        = True,
                           ) -> int:
    lowNote       :int   = -1
    scaleForMode  :list  = findScaleForMode(mode)
    listOfNotes   :list  = []


    #
    if  (octaveRange < 1)  or  (octaveRange > 6):   #XXX
        log.critical(f"{log.defName()}: octaveRange OUT OF BOUNDS ({octaveRange}).")

    if  None is scaleForMode:
        log.critical(f"mode is named, but NOT DEFINED.  ({mode})")

    lowNote  = octave.value + key.value


    # Determine range, regardless of direction.
    #
    if  direction in [Direction.DOWN, Direction.DOWNUP]:
        lowNote -= (octaveRange * NOTES_PER_OCTAVE)

    for  octa  in range(lowNote, lowNote + (octaveRange * NOTES_PER_OCTAVE), NOTES_PER_OCTAVE):
        for  pitch  in scaleForMode:
            listOfNotes.append(octa + pitch)

    if  scaleEndBoundByRoot:
        listOfNotes.append(octa + NOTES_PER_OCTAVE)


    # Iterate.
    #
    if  direction in [Direction.DOWN, Direction.DOWNUP]:
        listOfNotes.reverse()

    index = iter(listOfNotes)

    while  True:
        try:
            yield  index.__next__()

        except  StopIteration:
            if  direction in [Direction.UP, Direction.DOWN]:
                index = iter(listOfNotes)

            else:
                listOfNotes.reverse()
                index = iter(listOfNotes)
                index.__next__()
                        #NB  Avoid duplication of first note, which caused StopIteration.

#ENDDEF -- generateScaleSequence


#                                                                    -o-
def  generateOrnament(fromMIDINote:int, key:Key, mode:ModeNames, bpm:float) -> Union[List[Any],None]:
    """
    Generate OSC arguments describing ornaments, with the form:

        [ <ornamentName> <BPM> <beatSubdivision> [<listOfOrnamentNoteMIDIOffsets...>] ]

    ASSUME  This function is called on every beat, or with some organic 
            regularity so output over time is roughly consistent with itself.

    Maintain module internal state to govern frequency and type of ornaments produced.
    Random filters to manage internal state are arbitrrary, specific and experimental.  YMMV.

    Call generateOrnamentReset() to reset ornament module internal state.
    """

    ornamentChoice  :str        = None
    ornamentBlob    :List[Any]  = None
    oscArgs         :List[Any]  = []
    fourCount       :int        = 4

    global  ornamentState


    #
    if  ornamentState["sixteenthTripletTurnaround"] > 0:        # Check existing state.
        ornamentState["sixteenthTripletTurnaround"] -= 1

        if  ornamentState["sixteenthTripletTurnaround"] == 2:
            if  z.percentTrue(35):
                ornamentChoice = "sixteenthPop"

    if  not ornamentChoice:
        if  z.percentTrue(70):  return None                     # Frequency to bypass ornaments.
        ornamentChoice  = random.choice(list(Ornaments.keys()))


    #
    if    "sixteenthLeadIn"             == ornamentChoice:  
        pass

    elif  "sixteenthPop"                == ornamentChoice:
        if       ornamentState["sixteenthTripletTurnaround"] > 0    \
            and  ornamentState["sixteenthTripletTurnaround"] != 2:
            return  None

    elif  "sixteenthTripletTurnaround"  == ornamentChoice:
        # Generate no more often than once every fourCount.
        # Optionally generate "sixteenthPop" at half-way (above).
        #
        if  ornamentState["sixteenthTripletTurnaround"] > 0:
            return  None

        ornamentState["sixteenthTripletTurnaround"] = fourCount 

    else:
        log.error(f"UNRECOGNIZED ornament choice.  ({ornamentChoice})")
        return  None

   
    #
    ornamentBlob  = _translateOrnamentScaleToMIDI(ornamentChoice, fromMIDINote, key, mode)
    if  not ornamentBlob:  return None 

    oscArgs = [ornamentChoice, bpm, ornamentBlob[0]]
    oscArgs += ornamentBlob[1]

    return  oscArgs


#                                                                    -o-
def  generateOrnamentReset()  -> None:
    global  ornamentState
    ornamentState = ornamentState.fromkeys(ornamentState.keys(), 0)




#----------------------------------------- -o--
# Protected functions.

#                                                                    -o-
def  _discoverMIDINoteScaleIndexInMode(midiNote:int, key:Key, mode:ModeNames) -> Union[int,None]:
    """
    RETURN  Scale tone of midiNote in mode, or None if it cannot be found.

    NB  Range of scale tone depends upon the mode (generally 0-7).  Zero(0) is root.

    Scale tone is also the index into scale array.
    """

    listOfRegisters  :list  = None
    register         :int   = -1
    scaleForMode     :List  = findScaleForMode(mode)
    scaleIndex       :int   = 0


    #
    if  (midiNote < MIDINote.C1) or (midiNote > MIDINote.C8):
        log.error(f"midiNote is OUT OF RANGE.  ({midiNote})")
        return  None

    if  None is scaleForMode:
        log.error(f"mode is UNRECOGNIZED.  ({mode})")
        return  None


    #
    listOfRegisters  = list(MIDINote)
    register  = listOfRegisters.pop(0)

    for reg in listOfRegisters:
        if  midiNote < reg:  break
        register = reg

    register += key

    while  scaleIndex < len(scaleForMode):
        if  midiNote == (register + scaleForMode[scaleIndex]):
            return  scaleIndex
        scaleIndex += 1

    log.debug("hi3")
    return  None


#                                                                    -o-
def  _translateOrnamentScaleToMIDI(ornamentName:str, fromMIDINote:int, key:Key, mode:ModeNames) -> Union[List[Any],None]:
    """
    Goal: Find sequence of ornament notes, relative to both an arbitrary
          scale and an arbitrary starting pitch within that scale.

    Ornament array provides offsets from starting pitch that represent
    scale tones.  Each ornament ASSUMES the number of pitches in its
    scale (usually 7).

    NB  Just find the mapping.  Without regard to harmonic theory to find
        conventional use of more appropriate accidentals.
   
    Normalize ornament sequence relative to scalar index of starting note.
    Simplify mapping of scale indices into scales, by artifically extending
      scale sequences up and down, as necessary.  
      This also transforms negative scalar indices into positive.
    Finally, walk through artificial array per scale indices to find each 
      MIDI note of the ornament, represented as an offset from the 
      arbitrary starting pitch.
    """

    scale          :List[int]  = findScaleForMode(mode)
    scaleAdjusted  :List[int]  = None
    scaleLen       :int        = -1
    octave         :int        = NOTES_PER_OCTAVE
    octOffset      :int        = 0

    ornamentBlob         :List[Any]  = None
    ornamentSubdivision  :int        = None
    ornament             :List[int]  = None
    ornamentIndexOffset  :int        = 0
    ornamentAdjusted     :List[int]  = None
    ornamentMax          :int        = -1
    ornamentMin          :int        = -1

    midiNoteScaleIndex  :int        = _discoverMIDINoteScaleIndexInMode(fromMIDINote, key, mode)
    midiNoteNormalized  :int        = -1


    #
    if  None is scale:
        log.error(f"mode is UNRECOGNIZED.  ({mode.name})")
        return  None

    if  not ornamentName in Ornaments:
        log.error(f"Ornament DOES NOT EXIST.  ({ornamentName})")
        return  None

    if  None is midiNoteScaleIndex:
        log.error(f"fromMIDINote does NOT EXIST in mode \"{mode.name}\".  ({fromMIDINote})")
        return  None


    scaleLen  = len(scale)

    ornamentBlob         = Ornaments[ornamentName]
    ornamentSubdivision  = ornamentBlob[0]
    ornament             = ornamentBlob[1]


    #
    ornamentAdjusted = [_ + midiNoteScaleIndex for _ in ornament]
    ornamentMin = min(ornamentAdjusted)
    ornamentMax = max(ornamentAdjusted)

    scaleAdjusted = scale.copy()


    octOffset = 0
    while  True:
        ornamentMax /= scaleLen
        if  int(ornamentMax) <= 0:  break
        octOffset += octave
        scaleAdjusted += [_ + octOffset for _ in scale ]


    if  ornamentMin < 0:
        octOffset = 0

        while  True:
            octOffset -= octave
            scaleAdjusted = [_ + octOffset for _ in scale ] + scaleAdjusted
            ornamentMin /= scaleLen
            if  int(ornamentMin) >= 0:  break

        if  octOffset < 0:
            ornamentIndexOffset  = (int(octave / 12) * scaleLen) 
            ornamentAdjusted     = [_ + ornamentIndexOffset for _ in ornamentAdjusted ] 
            midiNoteScaleIndex  +=      ornamentIndexOffset

            scaleAdjusted        = [_ + abs(octOffset) for _ in scaleAdjusted ] 


    #
    midiNoteNormalized = scaleAdjusted[midiNoteScaleIndex]
    listOfMIDIOffsets = []

    # NB  Exceptions possible if ornament is used on a shorter scale, than expected.
    for oi in ornamentAdjusted:
        try:
            listOfMIDIOffsets.append( scaleAdjusted[oi] - midiNoteNormalized )
        except Exception as e:
            log.error(e)
            log.error(f"SKIPPING ornament index.  ({oi})")
       

    return  [ornamentSubdivision, [listOfMIDIOffsets]]

#ENDDEF -- _translateOrnamentScaleToMIDI




#-------------------------------------- -o--
# Testing.

#                                               -o-
def  testIvoryModesViaOSC()  -> None:
    """
    Demonstrate sending ivory modes via OSC.
    Optionally, use RTcmix score MOSOSC-with-RTcmix/soundsAndSequences.sco to hear them.
    """
    log.mark()

    test1  :bool  = False
    test2  :bool  = True

    client = mosOSC.MOSOSC()
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
        ivoryKeys  :list  = ModesAdditional[ModeNames.major].copy()
        root       :int   = 60

        for  name  in Modes.keys():
            midiRoot = root + ivoryKeys.pop(0)
            log.info(name)

            scale  :list  = Modes[name].copy()
            scale.append(scale[0] + NOTES_PER_OCTAVE)

            for  note  in scale:
                client.messageSend("/lowSequence", [midiRoot + note])
                time.sleep(0.5)
            
            time.sleep(1)
        
    # 
    print()
    z.postAndExit("DONE.")


#                                               -o-
def  testScaleSequencer(): 
    """
    Eyeball test.
    """
    log.mark()

    # kwargs for generateScaleSequence().
    #
    d  :dict  = {  
            #"key"               : Key.C,                        #DEFAULT
            #"key"               : Key.D,
            #"key"               : Key.Gs,

            #"octave"            : MIDINote.C4,                  #DEFAULT
            "octave"             : MIDINote.C2,

            #"scaleForMode"      : ModeNames.ionian,             #DEFAULT
            "mode"               : ModeNames.locrian,

            #"octaveRange"       : 2,                            #DEFAULT
            "octaveRange"        : 3,

            #"direction"         : Direction.UP,                 #DEFAULT
            #"direction"         : Direction.DOWN,
            #"direction"         : Direction.DOWNUP,
            #"direction"         : Direction.UPDOWN,

            #"scaleEndBoundByRoot"  : True,                      #DEFAULT
            #"scaleEndBoundByRoot"  : False,
        }

    index = generateScaleSequence(**d)


    #
    log.info("Type any key.  'q' to quit.")

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
    """
    Eyeball test.
    """
    log.mark()

    rval  :list  = []


    rval = _translateOrnamentScaleToMIDI("sixteenthLeadIn", 60, Key.C, ModeNames.ionian)
    log.info(f"01:  {rval}")
    rval = _translateOrnamentScaleToMIDI("sixteenthLeadIn", 69, Key.C, ModeNames.ionian)
    log.info(f"02:  {rval}")

    #_translateOrnamentScaleToMIDI("sixteenthLeadIn", 63, Key.C, ModeNames.ionianX)         #FAIL (system).
    #_translateOrnamentScaleToMIDI("sixteenthLeadIn", -1, Key.C, ModeNames.pentatonic)       #FAIL
    #_translateOrnamentScaleToMIDI("sixteenthLeadIn", 110, Key.C, ModeNames.pentatonic)       #FAIL

    rval = _translateOrnamentScaleToMIDI("sixteenthLeadIn", 66, Key.C, ModeNames.pentatonic)
    log.info(f"03:  {rval}")

    rval = _translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 52, Key.E, ModeNames.phrygian)
    log.info(f"04:  {rval}")
    rval = _translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 59, Key.E, ModeNames.phrygian)
    log.info(f"05:  {rval}")
    rval = _translateOrnamentScaleToMIDI("sixteenthTripletTurnaround", 67, Key.C, ModeNames.ionian)
    log.info(f"06:  {rval}")

    rval = _translateOrnamentScaleToMIDI("sixteenthPop", 60, Key.C, ModeNames.mixolydian)
    log.info(f"07:  {rval}")
    rval = _translateOrnamentScaleToMIDI("sixteenthPop", 64, Key.C, ModeNames.mixolydian)
    log.info(f"08:  {rval}")


    print()
    z.postAndExit("DONE.")




#-------------------------------------- -o--
# Main, for testing.

import mosOSC


#
if  "__main__" == __name__:

    #testIvoryModesViaOSC()
    #testScaleSequencer()
    testOrnaments()

    sys.exit(0)


