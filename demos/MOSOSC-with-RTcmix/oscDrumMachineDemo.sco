//
// oscDrumMachineDemo.sco
//
// ASSUME  oscDataObjectsFromPython is input to CMIX prior to this score.
//

include  ../../cmix/cmixHelper.sco

oscDemo_version  = 0.1   //RELEASE



//---------------------------------------- -o--
// Parse OSC parameters from calling environment.
// Set names of Disk Memory values.

op = parseOSCData(oscDataObjectsFromPython)   //XXX
opFirst = op[0]

//postOSCData(op, "OSC DATA OBJECTS FROM PYTHON"); exit()   //DEBUG


//
namesPerIndex = { 'hsState' }   
setDiskMemoryIndexNames(namesPerIndex)




//---------------------------------------- -o--
// Globals.

rtsetparams(44100, 2)

load("MULTEQ")
load("WAVETABLE") 

start = 0

srand(getRandomInteger())




//--------------------------- -o-
// Use MULTEQ to minimize click-sound introduced when each new score is run...
// Must bring other sounds through the notches, as necessary.
//
bus_config("WAVETABLE", "aux 0-1 out") 
bus_config("MULTEQ",    "aux 0-1 in", "out 0-1") 

bypassMulteq = 0

freq1 = 20      //XXX
freq2 = 38.38
freq3 = 75.11
freq4 = 145.01

toneDur = 3.5  // Longest tone generated from WAVETABLE().  (See below.)  XXX

Q = 0.75
gain = -24

MULTEQ(0, 0, toneDur, 1.0, bypassMulteq, 
        "peaknotch",  freq1, Q, gain, bypassMulteq,
        "peaknotch",  freq2, Q, gain, bypassMulteq,
        "peaknotch",  freq3, Q, gain, bypassMulteq,
        "peaknotch",  freq4, Q, gain, bypassMulteq
    )




//--------------------------- -o-
// See MOSMusic.Ornaments for full description of OSC inputs.

float  mo(float note, float offset)  { return cpsmidi(note + offset) }   // MIDI Offset

list  lowSequenceSound()
{
    MARK("/lowSequence", {})

    dur   = 3.5
    amp   = 50000
    note  = opFirst.o[0]
    pan   = 0


    //
    if  (len(op) == 1)  
    {
        wave    = maketable("wave", 4000, "tri")                                         //;plottable(wave)   //DEBUG
        ampenv  = maketable("curve", 1000, 0,0,-7, 0.1,1,4, 0.3,0.8,0, 0.4,0.8,-5, 1,0)  //;plottable(ampenv)   //DEBUG

        WAVETABLE(start, dur, amp*ampenv, cpsmidi(note), pan, wave)


    } else {
        opSecond     = op[1]

        bpm          = opSecond.o[0] * 4
        subdivision  = opSecond.o[1]
        orn          = opSecond.o[2]   // ornament

        six    = UNDEFINED   // sixteenth
        sixt   = UNDEFINED   // sixteenth triplet
        ei     = UNDEFINED   // eighth


        //
        if         (4 == subdivision)  {
            six  = subdivisionPerBeat(bpm, subdivision)
            ei   = six * 2

        } else if  (6 == subdivision)  {
            sixt  = subdivisionPerBeat(bpm, subdivision)
            ei    = sixt * 3

        } else {
            FATAL("UNRECOGNIZED subdivision.", {subdivision})
        }


        //
        wave    = maketable("wave", 4000, "tri")                                         //;plottable(wave)   //DEBUG
        ampenv  = maketable("curve", 1000, 0,0,-7, 0.1,1,4, 0.3,0.8,0, 0.4,0.8,-5, 1,0)  //;plottable(ampenv)   //DEBUG


        //
        if         ("sixteenthLeadIn" == opSecond.label)  {
            WAVETABLE(start+ei,      six,     amp*ampenv, mo(note,orn[0]), pan, wave)
            WAVETABLE(start+ei+six,  six,     amp*ampenv, mo(note,orn[1]), pan, wave)
            WAVETABLE(start+ei+ei,   ei+six,  amp*ampenv, mo(note,orn[2]), pan, wave)


        } else if  ("sixteenthPop" == opSecond.label)  {
            WAVETABLE(start,           ei+ei,  amp*ampenv, mo(note,orn[0]), pan, wave)
            WAVETABLE(start+six,       six,    amp*ampenv, mo(note,orn[1]), pan, wave)
            WAVETABLE(start+ei+six,    six,    amp*ampenv, mo(note,orn[2]), pan, wave)

            WAVETABLE(start+ei+ei,     ei,     amp*ampenv, mo(note,orn[3]), pan, wave)
            WAVETABLE(start+ei+ei+ei,  ei,     amp*ampenv, mo(note,orn[4]), pan, wave)


        } else if  ("sixteenthTripletTurnaround" == opSecond.label)  {
            WAVETABLE(start,               ei+sixt,    amp*ampenv, mo(note,orn[0]), pan, wave)
            WAVETABLE(start+sixt,          sixt,       amp*ampenv, mo(note,orn[1]), pan, wave)
            WAVETABLE(start+sixt+sixt,     sixt,       amp*ampenv, mo(note,orn[2]), pan, wave)

            WAVETABLE(start+ei,            sixt,       amp*ampenv, mo(note,orn[3]), pan, wave)
            WAVETABLE(start+ei+sixt,       sixt,       amp*ampenv, mo(note,orn[4]), pan, wave)
            WAVETABLE(start+ei+sixt+sixt,  sixt,       amp*ampenv, mo(note,orn[5]), pan, wave)

            WAVETABLE(start+ei+ei,         ei+sixt+sixt,    amp*ampenv, mo(note,orn[6]), pan, wave)
            WAVETABLE(start+ei+ei+ei+sixt, ei,              amp*ampenv, mo(note,orn[7]), pan, wave)


        } else {
            FATAL("UNRECOGNIZED ornament.", {opSecond.label})
        }
    }

    return  {}
}


//--------------------------- -o-
list  highSequenceSound()
{
    MARK("/highSequence", {})

    startOffset   = 0.15
    dur           = 3

    amp           = 4500
    ampOctFifth   = amp*0.9
    ampOct2       = amp*1.2

    midinote      = opFirst.o[0]
    oct           = 12
    oct2          = 24

    freq          = cpsmidi(midinote)
    freqoctFifth  = cpsmidi(midinote + oct + 7)
    freqoct2      = cpsmidi(midinote + oct2)
    microOffset   = rand() * 1.5   //NB -- flange, cancellation
    freqMicro     = freq + microOffset

    pan           = 1


    //
    buzz7  = maketable("wave", 4000, "buzz7")          
    buzz2  = maketable("wave", 4000, "buzz2")         

    octtri        = maketable("wave", 4000, "tri")        
    octfifthsine  = maketable("wave", 4000, "sine") 

    ampenv  = maketable("line", 1000, 0,0, 0.250,1, 0.600,0.3, 1,0)               //;plottable(ampenv)   //DEBUG
    ampenvFollow  
            = maketable("line", 1000, 0,0, 0.375,1, 0.550,0.4, 0.650,0.25, 1,0)   //;plottable(ampenvFollow)   //DEBUG


    //
    hsState = readDMN('hsState')

    if       (1 >= hsState)  { hsState = pickwrand( 1,85,  2,15,  3,0  ) }   // 1 -> 2
    else if  (2 == hsState)  { hsState = pickwrand( 1,10,  2,82,  3,8  ) }   // 2 -> 3,1
    else if  (3 == hsState)  { hsState = pickwrand( 1,5,   2,5,   3,90 ) }   // 3 -> 2,1

    else { FATAL("UNKNOWN hsState value.", {hsState}) }

    writeDMN('hsState', hsState) 


    //
    WAVETABLE(start, dur, amp*ampenv, freq, pan, buzz7)
                                                  // 1: foundation

    if (hsState >= 2) {                           // 2: detuning, thicken foundation
        WAVETABLE(start, dur, amp*ampenv, freqMicro, pan, buzz2)
    }

    if (hsState >= 3) {                           // 3: color, highlight
        WAVETABLE(start+startOffset, dur, ampOct2*ampenvFollow, freqoct2, pan, octtri)
        WAVETABLE(start+startOffset, dur, ampOctFifth*ampenvFollow, freqoctFifth, pan, octfifthsine)
    }


    return  {}
}


//--------------------------- -o-
load("BUTTER")
load("COMBIT")
load("CRACKLE")
load("DUST")

list  boomSound()
{
  MARK("/boom", {})

  // Global parameters.
  //
  amp    = 6000
  dur    = 5
  pan    = 0.7   # Percent towards left.


  //
  // Spacechord.
  //
  bus_config("CRACKLE", "aux 2 out")
  bus_config("BUTTER",  "aux 2 in", "aux 4-5 out")
  bus_config("COMBIT",  "aux 4-5 in", "out 0-1")


  // CRACKLE.
  //
  chaos  = 0.73

  CRACKLE(0, dur, amp, chaos, pan)


  // BUTTER.
  //
  bypassButter  = 0
  steepness     = 2  // [1,30]
  balanceInOut  = 0
  filtFreq      = 100

  freqCurve = maketable("line", "nonorm", 1000, 0,10000, 1,50)

  BUTTER(0, 0, dur*1.5, 1.0, "lowpass", steepness, balanceInOut, 0, pan, bypassButter, freqCurve)


  // COMBIT.  Arepeggiate the spacechord, from high to low.  Emphasize lower frequencies.
  //
  // TBD Q  Can we hear dynamic parameters from BUTTER in the shimmer of spacechord?
  //
  combitRingdownDuration = dur 
  reverbTime = 5

  combitStart  = 0.500
  combitFreq   = 103

  COMBIT(combitStart + 0.750, 0, dur, 0.17, (combitFreq),         reverbTime, 0, pan, combitRingdownDuration)
  COMBIT(combitStart + 0.400, 0, dur, 0.10, (combitFreq*2)+3.07,  reverbTime, 0, pan, combitRingdownDuration)
  COMBIT(combitStart + 0.250, 0, dur, 0.05, (combitFreq*10)+1.53, reverbTime, 0, pan, combitRingdownDuration)


  //
  // Compliment spacechord: Lead with a few loud(er) pops, then taper off.
  //
  density  = 11

  DUST(0, dur,      amp*10, density/5,  0, getRandomInt(), pan)
  DUST(0, dur*1.25, amp*5,  density/3,  0, getRandomInt(), pan)
  DUST(0, dur*1.5,  amp*2,  density,   -1, getRandomInt(), pan)


  //
  return  {}
}


//--------------------------- -o-
// Looch sample library--
//   SCRUB(NN,  0,     0.215,  1.0, 1.0)   # bark1
//   SCRUB(NN,  0.215, 0.201,  1.0, 1.0)   # bark2
//   SCRUB(NN,  4.650, 0.325,  1.0, 1.0)   # bark3
//   SCRUB(NN,  4.983, 0.197,  1.0, 1.0)   # bark4
//
//   SCRUB(NN,  2.465, 0.930,  1.0, 1.0)   # whine1
//   SCRUB(NN,  2.765, 0.530,  1.0, 1.0)   # whine2
//
load("DELAY")
load("SCRUB")
load("STEREO")

list  kapowSound()
{
  MARK("/kapow", {})

  rtinput("loocher.aiff")
  //dur = DUR(); DEBUG("DUR=", { dur })

  scrubPan  = 0.0  # Percent to left.  Q Has no effect?
  busPan    = 0.0

  whine1Amp  = maketable("line", 1000, 0,0.4, 850,1.0, 1000,3.0)
  bark2Fade  = maketable("curve", 1000, 0,1.0,4, 1.0,0)                 //;plottable(bark2Fade)  //DEBUG


  // Score A: b3-w1-b2 - b1,b4.  b3.  b3.
  //
  st = 0
  SCRUB(st,  4.650, 0.325,  1.0, 1.0,  16,16,0, scrubPan)   # bark3

  st += 0.190
  SCRUB(st,  2.485, 0.820,  0.9*whine1Amp, 1.0,  16,16,0, scrubPan)   # whine1

  st += 0.330
  SCRUB(st,  0.215, 0.201,  1.0, 1.0,  16,16,0, scrubPan)   # bark2


  st += 0.303
  SCRUB(st,  0,     0.215,  0.8, 1.0,  16,16,0, scrubPan)   # bark1

  st += 0.170
  SCRUB(st,  4.983, 0.197,  1.0, 1.0,  16,16,0, scrubPan)   # bark4


  //
  st += 0.635
  SCRUB(st,  4.650, 0.325,  1.0, 1.0,  16,16,0, scrubPan)   # bark3

  st += 0.470
  SCRUB(st,  4.650, 0.325,  1.0, 1.0,  16,16,0, scrubPan)   # bark3


  // Begin input with delay....
  //
  // Score B: - b2(w2), b1-b2-b3.  b1.  b2.
  //
  bus_config("SCRUB", "in 0", "aux 2 out") 
  bus_config("DELAY", "aux 2 in", "aux 3 out") 
  bus_config("STEREO", "aux 3 in", "out 0-1") 

  inputStartTime    = st - 0.350
  inputDuration     = 4.0
  inputMultiplier   = 1.0
  delayTime         = 0.650
  delayFeedback     = 0.11
  ringdownDuration  = 10.0

  st += 0.815
  SCRUB(st,  0.215, 0.201,  1.0, 1.0,  16,16,0, scrubPan)   # bark2

  st += 0.150
  SCRUB(st,  2.765, 0.530,  0.85, 1.0,  16,16,0, scrubPan)   # whine2

  st += 0.185
  SCRUB(st,  0,     0.215,  1.0, 1.0,  16,16,0, scrubPan)   # bark1

  st += 0.125
  SCRUB(st,  0.215, 0.201,  1.0, 1.0,  16,16,0, scrubPan)   # bark2

  st += 0.140
  SCRUB(st,  4.650, 0.325,  1.0, 1.0,  16,16,0, scrubPan)   # bark3


  //
  st += 0.555
  SCRUB(st,  0,     0.215,  1.0, 1.0,  16,16,0, scrubPan)   # bark1

  st += 0.490
  SCRUB(st,  0.215, 0.251,  1.0*bark2Fade, 1.0,  16,16,0, scrubPan)   # bark2


  //
  DELAY(inputStartTime, 0, inputDuration, inputMultiplier, delayTime, delayFeedback, ringdownDuration, 0, busPan)
  STEREO(0, 0, ringdownDuration, 1.0, busPan) 

  return  {}
}




//---------------------------------------- -o--
// Main.

if       ("/lowSequence"   == opFirst.label)  { lowSequenceSound() } 
else if  ("/highSequence"  == opFirst.label)  { highSequenceSound() } 
else if  ("/boom"          == opFirst.label)  { boomSound() } 
else if  ("/kapow"         == opFirst.label)  { kapowSound() } 

else if  ("/clearDiskMemory" == opFirst.label) {
    clearDiskMemory()

} else {
    ERROR("UNKNOWN OSC path.", {opFirst.label})
} 


