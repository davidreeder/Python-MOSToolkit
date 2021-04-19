
# MOS Toolkit for Python: Feature and support classes

                                        v0.5
                                        April 2021

Contents                                          |
-----------------                                 |
  OVERVIEW                                        |
  MOSOSC                                          |
  VERSION HISTORY                                 |




## OVERVIEW

Feature and support classes for Python development.
Written for **Python v3**.


Core classes include:

* **MOSOSC**        :: Unified API for Open Sound Control (OSC) including timestamped logging, logic for unhandled OSC paths, support for delayed bundles.  Wrapper of **python-osc** module.


Support classes include:

* **MOSClass**      :: Collection of utility classes.
* **MOSDump**       :: Reflection on collections and objects.  Streamlined alternate to **pydoc**.
* **MOSLog**        :: Ready made, context specific logging for scripts, modules and classes.  Built upon **logging** module.
* **MOSZ**          :: Encapsulate common operations for script development and shell interaction.


Find demos in [demos/](https://github.com/davidreeder/Python-MOSToolkit/demos/).




## MOSOSC

MOSOSC provides a simple, unified API that implements client and server interfaces to [Open Sound Control (OSC)](https://en.wikipedia.org/wiki/Open_Sound_Control).
MOSOSC is a wrapper around [https://pypi.org/project/python-osc](https://pypi.org/project/python-osc).

Each instance of MOSOSC runs as client or server.  Use multiple instances to create multiple
clients and servers.


**OSCClient.py** demo includes...

* Create and destroy client
* Send messages and bundles
* Send nested bundles, bundles with delays
* Composable message and bundle content creation
* Optional automatic OSC path logging per send, including delay status

**OSCServer.py** demo includes...

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


See [demos/MOSOSC](https://github.com/davidreeder/Python-MOSToolkit/demos/MOSOSC), class headers and pydoc for more details.




## VERSION HISTORY


v0.5 -- April 2021
> Initial release.

