/*
 * RTcmix/test/suite/osc_send_test.cpp
 *
 * Updated to send multiple score files.  After which... this test is hardwired to 
 *   exercise elememts of MOSToolkit demo/MOSOSC-with-RTcmix/soundsAndSequences.sco .
 *
 * Assumes CMIX version 5.0.0.
 * Build with "make osc_send".
 *
 * 
 * NB--
 *   * Score files must be less than ~9k characters (9188).
 *       Q  The difference being UDP header length?
 *
 *   * Score "include" paths are relative to the directory in which "CMIX -o" is run.
 *       Include files do not have (small) length limits.
 *
 *   * All OSC sends to CMIX are cumulative.  Restart "CMIX -o" to start with a new score context.
 *
 *   * OSC server network address is hardwired to localhost:7777.
 */

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <unistd.h>
#include <fstream>
#include <string>

#include <lo/lo.h>



// Function signatures.
//
void  sendStringViaOSC(char *str);



//----------------------------------------- -o-
// Globals.
//
#define  OSC_PORTNUM            "7777"
#define  RTCMIX_OSCPATH         "/RTcmix/ScoreCommands"

#define  USAGE                  "Usage: " << argv[0] << " <scorefile(s)>"

#define  LENGTH(x)              ( sizeof(x) / sizeof(x[0]) )
#define  OCTAVE                 12



// MinC shortcuts.
//
#define  BOOM                           "boomSound()\n" 
#define  KAPOW                          "kapowSound()\n" 

//#define  HIGH_SEQUENCE_STRING(b, x)     sprintf(b, "highSequenceSound(%d)\n", x)                // Raw score.  NB Needs minor update in main score.
#define  HIGH_SEQUENCE_STRING(b, x)     sprintf(b, "main({{ '/highSequence', { %d } }})\n", x);   // OSC "API".




//----------------------------------------- -o-
int 
main(int argc, char *argv[])
{    
    char  *stuff;


    //
    if (argc < 2) {
        std::cout << USAGE << std::endl;
        return 0;
    }


    // Send base score(s).
    //
    for (int argCount = 1; argCount < argc; argCount +=1)
    {
        char  *filename = argv[argCount];
             
        sprintf(stuff, "include  %s\n", filename);

        sendStringViaOSC(stuff);
    }


    // Test score.
    //
    srand((unsigned)time(0)); 
    sleep(1);

                                        // Boom.
    sendStringViaOSC(BOOM);            
    sleep(2);


                                        // High sequence.
    int  midiCScale[]  = { 60, 62, 64, 65, 67, 69, 71 };
    //int  midiCScale[]  = { 60, 64, 67 };
    int  offset  = -1;

    for (int repeats = 2; repeats > 0; repeats -= 1)
    {
        for (int octaveRange = 0; octaveRange < 2; octaveRange += 1)
        {
            for (int note = 0; note < LENGTH(midiCScale); note += 1)
            {
                int  midiValue  = midiCScale[note] + (octaveRange * OCTAVE);

                HIGH_SEQUENCE_STRING(stuff, midiValue);
                sendStringViaOSC(stuff);

                HIGH_SEQUENCE_STRING(stuff, midiValue + 7);
                sendStringViaOSC(stuff);

                offset =  (rand() % 2) ? 9 : 2;
                offset += (rand() % 2) ? 0 : OCTAVE;
                HIGH_SEQUENCE_STRING(stuff, midiValue + offset);
                sendStringViaOSC(stuff);

                sleep(1);
            }
        }
    }

    
                                        // Low sequence (one test).
    sleep(2);
    sendStringViaOSC( "main( { { '/lowSequence',                {50},                                    -1, -1, -1, -1, -1 }, "
                      "        { 'sixteenthTripletTurnaround',  {15, 6, {0, 2, 0, -2, -4, -5, 12, 10}},  -1, -1, -1, -1, -1 }  " 
                      "      } )"
                    );
    sleep(3);


                                        // /kapow + /boom (with global comb filter).
    sendStringViaOSC("main({{ '/kapow', {1} }})");
    sleep(1);
    sendStringViaOSC(BOOM);


    //
    return 0;
}


//----------------------------------------- -o-
void
sendStringViaOSC(char *str)
{
    lo_address  t  = lo_address_new(NULL, OSC_PORTNUM);

    if (lo_send(t, RTCMIX_OSCPATH, "s", str) == -1)
    {
        printf("OSC error %d: %s\n", lo_address_errno(t), lo_address_errstr(t));

    } else {
        std::cerr <<  ">>>  " << str  << std::endl;
    }
}

