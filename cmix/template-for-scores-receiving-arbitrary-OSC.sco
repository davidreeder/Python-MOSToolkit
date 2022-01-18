//
// template-for-scores-receiving-arbitrary-OSC.sco
//
//
// Score designed to accept arbitrary OSC arguments whether or not CMIX is built to accept CMIX-style OSC via "CMIX -o".
//
// NB  If CMIX is built to enable OSC, no further action is required.  Otherwise, set cmixBuildEnablesOSC to false.
//
//
// ASSUME  Score invocation includes call to main() with list of OSC arguments.
//
// SEE ../../cmix/cmixHelper.sco for more details and OSC features.
//

include  ../../cmix/cmixHelper.sco

thisfile_version = "0.1"




//---------------------------------------- -o--
// Globals.

// OPTIONAL -- CMIX globals.
// ...



// Capture incoming OSC messages.
//
list            od        // List of struct OSCData.
struct OSCData  odFirst   // First OSCData object in list.



// Set cmixBuildEnablesOSC to false if "CMIX -o" is NOT supported.  DEFAULT is true.
//
// ASSUME  MOSRTcmix.cmixBuildEnableOSC is set to same value in MOSRTcmix module for Python OSC client.
//
//cmixBuildEnablesOSC  = false   



// Configure DiskMemory if CMIX is not configured to support OSC.
// Otherwise, use local shared memory.
//
float  param1State
// ...

namesPerIndex  = UNDEFINED

if (! cmixBuildEnablesOSC) {
    namesPerIndex = { 'param1State', 'param2State', 'abc', 'xyz', 'paramNState' }   
    setDiskMemoryIndexNames(namesPerIndex)
}


list  resetScore()
{
    if (! cmixBuildEnablesOSC) {
        clearDiskMemory()
    }

    param1State = UNDEFINED
    // ...

    return  {}
}

resetScore()

if (! cmixBuildEnablesOSC) {
    param1State = readDMN('param1State')   // For example.
    // ...
}




//--------------------------- -o-
if (! cmixBuildEnablesOSC)
{
    # OPTIONAL -- Compensate for artifacts introduced by invoking one process per OSC message.
    // ...
}




//--------------------------- -o-
// Define one function for each sounds or sound process.
// Find OSC data in "od".
//

list  soundOne()
{
    MARK("/soundOne", {})
    // ...
    return  {}
}

list  soundTwo()
{
    MARK("/soundTwo", {})
    // ...
    return  {}
}

list  soundN()
{
    MARK("/soundN", {})
    // ...
    return  {}
}

// ...




//---------------------------------------- -o--
// Main.
//
// NB  Input is a list of lists representing OSCData structs.  
//     Curly brackets will be DOUBLED at the beginning and the end.
//

list  main(list arbitraryOSCDataFromPython)
{
    INFO("cmixBuildEnablesOSC =", {cmixBuildEnablesOSC})

    od       = parseOSCData(arbitraryOSCDataFromPython)
    odFirst  = od[0]

    //postOSCData(od, "OSC DATA OBJECTS FROM PYTHON"); exit()   //DEBUG


    //
    if       ("/soundOne"      == odFirst.label)  { soundOne() } 
    else if  ("/soundTwo"      == odFirst.label)  { soundTwo() } 
    else if  ("/soundN"        == odFirst.label)  { soundN() } 

    // ...

    else if  ("/resetScore"    == odFirst.label)  { resetScore() }
    else if  ("/quit"          == odFirst.label)  { exit() }

    else {
        ERROR("UNKNOWN OSC path.", {odFirst.label})
    } 


    return  {}
}

