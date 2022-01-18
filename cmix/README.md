
## RTcmix Support


Assumes CMIX v5.0.0.

Files to support RTcmix scores:

  * [cmixHelper.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixHelper.sco)
        :: MinC library defines **OSCData** and **DiskMemory** features, amongst other minor tools and tests.
  * [cmixScoreAddPlottable.sh](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/cmixScoreAddPlottable.sh)
        :: Script to add realtime debug plots for any use of **maketable()** in RTcmix scores.
  * [osc\_send\_test.cpp](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/osc_send_test.cpp)
        :: RTcmix code test for **"CMIX -o"** feature.  See header for build details.
  * [template-for-scores-receiving-arbitrary-OSC.sco](https://github.com/davidreeder/Python-MOSToolkit/blob/main/cmix/template-for-scores-receiving-arbitrary-OSC.sco)
        :: Template to build clearly defined, parametrized sounds for use with **MOSRTcmix**.



For more details, see...

  * Section about **RTcmix** in top-level [README](https://github.com/davidreeder/Python-MOSToolkit/).
  * Demo of [MOSOSC-with-RTcmix](https://github.com/davidreeder/Python-MOSToolkit/tree/main/demos/MOSOSC-with-RTcmix).

