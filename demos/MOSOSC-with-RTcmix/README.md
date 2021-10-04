
# MOSOSC-with-RTcmix Demo



## Run the demo.

Include path to `Python-MOSToolkit/classes/` directory in `PYTHONPATH`.  MOSToolKit assumes Python v3 and CMIX v5.0.0.

Build RTcmix with the result that CMIX is available in your PATH.

Run RTcmix OSC demo server and client:

    First run server:
      $ ./rtcmixOSCServer.py --cmixScore oscDrumMachineDemo.sco

    Then run client:
      $ ./drumMachineWithSequences.py

      Study HOTKEYS, then use them to trigger sounds via OSC as if playing a drum machine.


Review comments in both client and server for additional examples of class features.


RTcmix score files used by this demo:

* **oscDrumMachineDemo.sco** :: Core CMIX score, written to receive OSC inputs.
* **MOSToolKit/cmix/cmixHelper.sco** :: Minc libraries for OSCData and DiskMemory.


**exampleOfOSCDataFromPython.sco** provides an example of how OSC from Python appears in Minc, when prepended to score file.





## Other ways to see the demo and play with score code.

Watch a VIDEO of a live demo session:

    $ open rtcmix-osc-live-demo.mp4

Simulate the Python action for a single OSC message by prepending the OSC message to the score file and piping the result into CMIX: 

    $ cat handyOSCData.sco oscDrumMachineDemo.sco | CMIX

**cmixHelper.sco** contains a number of **test*()** functions which can be uncommented to run with any score.



## What's in the demo?

The "lowSequence" of notes demonstrates the use of OSC messages to trigger ornaments.

The "highSequence" of notes demonstrates how state shared between scores can be used to create a complex single voice from the emerging properties of similarly composed sounds.

The other two BOOM and KAPOW sounds simply trigger precomposed sounds.  They also demonstrate how the RTcmix enhancements provided
by **RTcmix.py** and **cmixHelper.sco** can quickly create a complex environment for improvisation, performance or automation, and yet be accessible
on any machine (or suite of machines) that supports Python with a simple client/server setup.



## Class Reference

* [MOSRTcmix.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/classes/MOSRTcmix.py)
* [MOSOSC.py](https://github.com/davidreeder/Python-MOSToolkit/blob/main/classes/MOSOSC.py)

