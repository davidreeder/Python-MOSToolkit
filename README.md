
# MOS Toolkit for Python: Feature classes and support

Contents                                          |
-----------------                                 |
  Overview                                        |
  MOSOSC                                          |
  MOSRTcmix                                       |
  Version History                                 |

                                        v0.6
                                        October 2021


## Overview

Feature classes and support modules for Python development.  

MOSToolKit assumes Python v3.  Recently tested under version 3.8.


Core classes and modules include:

  * **MOSOSC**        :: Unified API for Open Sound Control (OSC) including timestamped logging, logic for unhandled OSC paths, support for delayed bundles.  Wrapper of **python-osc** package.
  * **MOSRTcmix**     :: Enable arbitrary OSC messages to trigger RTcmix scores.  Extend MOSOSC to support CMIX **OSCData** format.


Support classes and modules include:

  * **MOSClass**      :: Collection of utility classes.
  * **MOSDump**       :: Reflection on collections and objects.  Streamlined alternate to **pydoc**.
  * **MOSLog**        :: Ready-made, context specific logging for scripts, modules and classes.  Built upon **logging** module.
  * **MOSMusic**      :: Generate scales and ornaments within a scale.
  * **MOSZ**          :: Encapsulate common operations for Python development and shell interaction.


Additional support code includes:

  * **cmix**          :: Libraries and support for RTcmix sound design.  Support for OSCData and DiskMemory.


Find demos in [demos/](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/).




## MOSOSC

**MOSOSC** provides a simple, unified API that implements client and server interfaces to [Open Sound Control (OSC)](https://en.wikipedia.org/wiki/Open_Sound_Control).
**MOSOSC** is a wrapper around [https://pypi.org/project/python-osc](https://pypi.org/project/python-osc), version 1.8.0.

Each instance of **MOSOSC** runs as client or server.  Use multiple instances to create multiple clients and servers.


**OSCClient.py** demo includes...

* Create and destroy client
* Send messages and bundles
* Send nested bundles, bundles with delays
* Composable message and bundle content creation
* Optional automatic OSC path logging per send, including delay status

**OSCServer.py** demo includes...

* Create and destroy server
* Start and stop server
* Add, remove, list OSC path handlers
* Pass user arguments to handlers
* Convenience methods to parse and log handler inputs
* Default handler and optional default handler function
* Multiple matching handlers
* OSC event logging, optionally with millisecond timestamps or client source
* Attributes to configure OSC path logging, default handler, and more
* Manage server control via OSC


See [demos/MOSOSC](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/MOSOSC), class headers and pydoc for more details.



## MOSRTcmix

Enable OSC messages to trigger [RTcmix](http://rtcmix.org/) scores.

**MOSRTcmix** translates an OSC message into a list format supported by [Minc](http://rtcmix.org/reference/scorefile/Minc.php), then it prepends this to the score before executing it.  Thereby, one can create a score that depends upon OSC data to make decisions in real-time.  Any simple OSC client/server can be enhanced to send OSC for RTcmix, then pass the OSC to a specific score file (or files).

The score must include a small Minc library ([cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/tree/main/cmix/cmixHelper.sco)), and it must prepare to use a well-known variable shared between Python and Minc so the score can identify the list-translated OSC message.  

**cmixHelper.sco** library can accept any arbitrary OSC message, though **MOSRTcmix** can also receive OSC messages in a CMIX "OSCData format".

This works!  Try the demo (below) or see a video of the demo in the same directory.  However, it does not scale well.  Each OSC message requires creating an anonymous file to be concatenated with the score file.  Python/UNIX can only do this so fast in a standard user-process with a standard kernel configuration.  The developer benchmark is ~14 OSC messages per second.  Nonetheless, it works well as a general solution.  Future iterations may include integrating similar functionality into RTcmix itself.


_**NOTE:**_ **cmixHelper.sco** contains a second library to read/write small tables to disk, which enables sharing of state between score files in real-time.  This works well in combination with scores triggered by OSC data.  Again, this works well in practice, but clearly has scaling issues in its present form.



See also...

  * [demos/MOSOSC-with-RTcmix](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/MOSOSC-with-RTcmix)
  * [cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/tree/main/cmix/cmixHelper.sco)
  * What is [RTcmix](http://rtcmix.org/)?
  * What is [Minc](http://rtcmix.org/reference/scorefile/Minc.php)?




## Version History


v0.6 -- October 2021  (RTcmix)
> Enhance RTcmix scores with **cmix/cmixHelper.sco** and **MOSRTcmix** module.

v0.5 -- April 2021  (OSC)
> Initial release.

