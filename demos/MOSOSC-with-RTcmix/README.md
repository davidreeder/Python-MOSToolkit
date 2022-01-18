
# MOSOSC-with-RTcmix 

.

## What is it?

**MOSRTcmix** enables real-time controls via **Open Sound Control (OSC)**
to trigger and parameterize sounds defined by RTcmix.  In this way,
**MOSRTcmix** separates sound design (original score) from the performance
(OSC data).  This is possible, whether or not CMIX is built to
receive OSC messages.

To get started, use the CMIX score template
([cmix/template-for-scores-receiving-arbitrary-OSC.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/template-for-scores-receiving-arbitrary-OSC.sco)),
to isolate sounds into functions.  Then, build a Python OSC client to
engage the score file.  See the working demo below for an example.

A Python OSC server is necessary only if CMIX is not built to support
arbitrary OSC inputs.

To check the status of the CMIX build, type **"CMIX -o"**.  If CMIX
supports arbitrary OSC inputs per the requirements of **MOSRTcmix**, CMIX
should generate output similar to the following:

      $ CMIX -o
      --------> RTcmix 5.0.0 (CMIX) <--------
      rtInteractive mode set

      runMainLoop():  waiting for audio_config . . .


If this output does NOT appear, you will need to create a Python OSC server.
This server can be simple -- little more than an index of OSC paths expected by
the score file.  See working demo below for examples.

The Python OSC client contains the main logic to manage the score file and
the performance of the score, for both server solutions.  By default,
this should "just work." If **"CMIX -o"** is NOT enabled, then set the
global variable **cmixBuildEnablesOSC** to false, in both the OSC client
and in the score file.  (The default setting for **cmixBuildEnablesOSC** is
true.)

See demo below for working examples of a score file built alongside
a Python OSC client and server.




.

## Run the demo.

Include path to `Python-MOSToolkit/modules/` directory in `PYTHONPATH`.  MOSToolkit assumes Python v3 and CMIX v5.0.0.

Run OSC server and client in two separate windows:

    First run server:
      $ CMIX -o

    Then run client:
      $ soundsAndSequences_oscClient.py --pathToCMIXScore ./soundsAndSequences.sco

      Study HOTKEYS, then use them to trigger sounds via OSC as the timeline scrolls past.


Review comments in both client and server for additional examples of class features.

**NOTE:** **"CMIX -o"** should be run in the SAME DIRECTORY as the score
file.  It defines the root directory for the score file.


If **"CMIX -o"** does NOT enable OSC, then use the Python OSC server in place of it, as follows:

    $ soundsAndSequences_oscServer.py --pathToCMIXScore ./soundsAndSequences.sco

.

### RTcmix score files used by this demo:

* [soundsAndSequences.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/demos/MOSOSC-with-RTcmix/soundsAndSequences.sco)
        :: Core CMIX score, written to receive OSC inputs and to work with both server solutions.
* [cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
        :: MinC libraries for **OSCData** and **DiskMemory**.

### MOSToolkit files used by this demo, include:

* [soundsAndSequences_oscClient.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/demos/MOSOSC-with-RTcmix/soundsAndSequences_oscClient.py)
* [soundsAndSequences_oscServer.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/demos/MOSOSC-with-RTcmix/soundsAndSequences_oscServer.py)
* [modules/mosRTcmix.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosRTcmix.py) :: module including subclass of [MOSOSC](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosOSC.py).  Both of which are reliant on other elements of **MOSToolkit**.




. 

## Other ways to see the demo and play with score code.

Watch a VIDEO of a live demo session.  The video also demonstrates how both
server solutions can work with the same score file and OSC client code:

    $ open rtcmix-osc-live-demo.m4v

Simulate the Python action for a single OSC message by prepending the OSC
message to the score file and piping the result into CMIX:

    $ CMIX < handyOSCData.sco 

[cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
contains a number of **test*()** functions which can be uncommented to run
with any score.

The MinC code in
[handyOSCData.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/demos/MOSOSC-with-RTcmix/handyOSCData.sco)
provides a light-weight vehicle for testing the score without Python.  It also demonstrates the basic principle upon which **MOSRTcmix** is built.




.

## What's in the demo score file?

The "lowSequence" of notes demonstrates the use of OSC messages to trigger
ornaments.

The "highSequence" of notes demonstrates how state shared within a score
can be used to create a complex single voice from the emerging properties
of similarly composed sounds.

The other two BOOM and KAPOW sounds simply trigger precomposed sound
sequences.  They also demonstrate how the RTcmix enhancements provided by
[modules/mosRTcmix.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosRTcmix.py)
and
[cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
can quickly create a complex environment for improvisation, performance or
automation, and yet be accessible on any machine (or suite of machines)
that supports Python with a simple client/server setup.




.

## Tradeoff: Server solutions do not behave identicaly.

The audio output from CMIX is clearly superior when **"CMIX -o"** functions
as a native OSC server.  However, the current implementation of RTcmix
imposes other limits, as follows:


| CMIX enables OSC              | Use Python OSC server to support CMIX         |
| ---                           | ---                           |
| | |
| Runs a single score in a single process.  Efficient.  All memory shared between all OSC messages.  | Run one score in separate process, per OSC message.  May generate audio artifacts as frequency of messages increases.  Share memory between messages via [cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco) **DiskMemory** feature.    |
| | |
| **"CMIX -o"** is the server.          | Requires additional (albeit simple) Python OSC server.   |
| | |
| Runs only on localhost, port 7777.    | Runs on any host:port combination, on any machine that runs both a Python OSC server and CMIX.      |
| | |
| Does not support OSC bundles.         | Supports OSC bundles.         |
| | |
| Set **cmixBuildEnablesOSC = true**.   | Set **cmixBuildEnablesOSC = false**.      | 


.

### What is similar between the two server solutions?

  * Use of 
    [MOSOSC](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosOSC.py) 
    and 
    [MOSRTcmix](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosRTcmix.py) 
    class APIs by the Python OSC client is identical.
  * CMIX scores must include 
    [cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
    for MinC **OSCData** feature.

MinC **DiskMemory** feature is needed only when CMIX build does not enable
arbitrary OSC.  And then, only if the score needs to share state across OSC
messages.

Scores and OSC clients written for one server solution will always operate
with the other solution.  This can be automated by setting and using the
global variable **cmixBuildEnablesOSC**.  This variable appears in both the
[mosRTcmix.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosRTcmix.py)
module and in
[cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
-- by default it is set to true.
See also the CMIX score template file,
[cmix/template-for-scores-receiving-arbitrary-OSC.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/template-for-scores-receiving-arbitrary-OSC.sco).

**NOTE:** Although the audio artifacts can be truly terrible, such as clipping
pops with each OSC message...  the artifacts can be minimized simply by
writing more CMIX code, such as adding an array of parametric EQs
([MULTEQ](http://rtcmix.org/reference/instruments/MULTEQ.php)).  See demo
(above) for an example.




.

## In what ways does CMIX support Open Sound Control (OSC)?


#### 1 :: **"CMIX -o"** presents a server that recognizes just enough OSC to inject scores in fragments.

The best way to guarantee this option is enabled, is to build CMIX from
scratch.  In particular, this means modifying the build process to pass the
"--with-osc" option to "configure" during the build lifecycle.  To learn
more about building CMIX see [http://rtcmix.org/standalone](http://rtcmix.org/standalone).

In this form CMIX will open port **7777** on **localhost** and accept OSC
messages from a single OSC path in the following form:

    /RTcmix/ScoreCommands mincString

where **mincString** is arbitrary MinC code.  Initially, the server waits
and the score is undefined.  Each new OSC message can build a new score,
add to or somehow engage the existing score.  **MOSRTcmix** initializes the
score using the **include** directive, then posts OSC arguments via
**main()** which is defined to parse incoming, arbitrary OSC data into a
list of **struct OSCData**.

Even if **"CMIX -o"** is not supported, **MOSRTcmix** can simulate this
case by running the named score with each new OSC message.  See above for a
list of tradeoffs between these two server solutions.


.

#### 2 :: RTcmix can generate P-field variables that reflect the current value of a stream of OSC messages.

OSC driven P-field variables are initialized via the **makeconnection()**
directive with the undocumented option **"osc"**.  The following example
comes from Jerod Sommerfeldt's book [Computer Music Composition With
RTcmix](https://jerodsommerfeldt.com/rtcmix-book/):

    amp = makeconnection("osc", "/p5glove_data", index=9, inmin=-500, inmax=500, outmin=40, outmax=90, dflt=0, lag=70)

This example waits for OSC messages of the following form:

    /p5glove_data numericValue

where **numericValue** is selected and filtered by the additional
arguments to **makeconnection()**.  

The following gives a simple example of OSC driven P-field variables:

    rtsetparams(44100, 1)
    load("WAVETABLE")

    set_option("osc_inport = 50001")

    midi   = makeconnection("osc", "/midi",  index=0, inmin=-500,inmax=500, outmin=-500,outmax=500, dflt=0, lag=10)  
    pitch  = makeconverter(midi, "pchmidi")

    WAVETABLE(0, 300, 20000, pitch)

This example score listens for an OSC message on localhost, port 50001, having the following form:

    /midi midiValue

where **midiValue** is a MIDI note that is played by **WAVETABLE()**.

**MOSRTcmix** does not use this method to manage OSC messages because it
relies on a thin stream of values strongly bound to a particular code
function.  Instead, **MOSRTcmix** enables an arbitrary list of OSC values
which can be presented at any time to all features and across all types
supported by MinC code.



.

## MOSToolkit Class and MinC Feature Support Reference

  * [mosRTcmix.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosRTcmix.py)

  * [mosOSC.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/modules/mosOSC.py)

  * [cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)

  * [template-for-scores-receiving-arbitrary-OSC.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/template-for-scores-receiving-arbitrary-OSC.sco)

  * What is [RTcmix](http://rtcmix.org)?  What is [MinC](http://rtcmix.org/reference/scorefile/Minc.php)?


