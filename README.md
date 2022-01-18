
# MOSToolkit for Python: Feature and Support Classes and Modules

CONTENTS                                          |
-----------------                                 |
  Overview                                        |
  MOSOSC                                          |
  MOSRTcmix                                       |
  Version History                                 |

                                        v0.6.1
                                        January 2022


## Overview

Features and support classes and modules for Python development.  MOSToolkit assumes Python v3.


Core classes include:

  * **mosOSC.MOSOSC**        :: Unified API for Open Sound Control (OSC) including timestamped logging, logic for unhandled OSC paths, support for delayed bundles.  Wrapper of **python-osc** module, version 1.8.0.
  * **mosRTcmix.MOSRTcmix**  :: Enable arbitrary OSC messages to trigger and parametrize RTcmix scores.  Extend MOSOSC to support CMIX **OSCData** format.


Support modules include:

  * **mosClass**      :: Collection of utility classes.
  * **mosDump**       :: Reflection on collections and objects.
  * **mosLog**        :: Ready made, context specific logging for scripts, modules and classes.  Built upon **logging** module.
  * **mosMusic**      :: Generate scales and ornaments within a scale.
  * **mosZ**          :: Encapsulate common operations for script development and shell interaction.


Additional support code includes:

  * **cmix**          :: Libraries and support for RTcmix sound design, including **OSCData** and **DiskMemory**.


Find demos in [demos/](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/).




.

## mosOSC.MOSOSC

**MOSOSC** provides a simple, unified API that implements client and server interfaces to [Open Sound Control (OSC)](https://en.wikipedia.org/wiki/Open_Sound_Control).
**MOSOSC** is a wrapper around [https://pypi.org/project/python-osc](https://pypi.org/project/python-osc), version 1.8.0.

Each instance of **MOSOSC** may run as client or server.  Use multiple instances to create multiple clients and servers.


**oscClient.py** demo includes...

* Create and destroy client
* Send messages and bundles
* Send nested bundles, bundles with delays
* Composable message and bundle content creation
* Optional automatic OSC path logging per send, including delay status

**oscServer.py** demo includes...

* Creating and destroying the server
* Starting and stopping the server
* Adding, removing, listing OSC path handlers
* Passing user arguments to handlers
* Convenience method for parsing and logging handler inputs
* Default handler and optional default handler function
* Multiple matching handlers
* OSC event logging optionally with millisecond timestamps or client source
* Attributes to configure OSC path logging, default handler, and more
* Managing server control via OSC


See [demos/MOSOSC](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/MOSOSC), class headers and pydoc for more details.




. 

## mosRTcmix.MOSRTcmix

**MOSRTcmix** enables real-time controls via **Open Sound Control (OSC)**
to trigger and parametrize sounds defined by [RTcmix](http://rtcmix.org/)
scores.  In this way, **MOSRTcmix** separates sound design (original score)
from the performance (OSC data).  This is possible, whether or not
CMIX is built to receive OSC messages.

**MOSRTcmix** translates an OSC message into a list format supported by
[MinC](http://rtcmix.org/reference/scorefile/Minc.php) which is then
injected into an active score.

Try the demo (below) or see a video of the demo (in the same directory).


See also...

  * [demos/MOSOSC-with-RTcmix](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/MOSOSC-with-RTcmix)
  * [cmix/cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/tree/main/cmix/cmixHelper.sco)

  * What is [RTcmix](http://rtcmix.org/)?  What is [MinC](http://rtcmix.org/reference/scorefile/Minc.php)?




.

## Version History

v0.6.1 -- January 2022  (RTcmix)
> Enable arbitrary OSC messages to trigger and parametrize RTcmix sound objects whether or not CMIX supports OSC.

v0.6 -- September 2021  (RTcmix)
> Enhance RTcmix scores with **cmix/cmixHelper.sco** and **mosRTcmix** module.

v0.5 -- April 2021  (MOSOSC)
> Initial release.

