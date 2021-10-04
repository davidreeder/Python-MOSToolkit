//
// cmixHelper.sco   
//
// Helper functions and data structures.  
// Test cases and examples.
// Intended as an include file.  Use only once.
//
// Includes subsystems for...
//     * Receiving OSC data from Python.
//     * Memory sharing across multiple score instances.
//
// Assumes CMIX v5.0.0.
//
//
// LOGGING FUNCTIONS--
//     MARK() DEBUG() INFO() 
//     WARNING() ERROR() 
//     FATAL()
//
//
// HELPER FUNCTIONS--
//     sep()
//     doesFileExist()
//     getRandomInteger()
//     percentTrue()
//     subdivisionPerBeat()
// 
//
// OSC DATA PUBLIC--
//     struct OSCData
// 
//     parseOSCData()
//     postOSCData()
// 
// OSC DATA SUPPORT--
//     float lengthOfOSCDataCommonList
//     testOSCData()
// 
// 
// DISK MEMORY PUBLIC--
//     struct DiskMemorySingleton
// 
//     setDiskMemoryIndexNames()
//     indexPerName()          (ipn)
//
//     readDiskMemoryIndex()   (readDMI)
//       readDiskMemoryName()    (readDMN)
//     writeDiskMemoryIndex()  (writeDMI)
//       writeDiskMemoryName()   (writeDMN)
//
//     clearDiskMemory()
//     postDiskMemory()
// 
// DISK MEMORY SUPPORT--
//     struct DiskMemorySingleton mosDMS
//     setDiskMemorySingleton()
//     getDiskMemory()
//     testDiskMemory()
// 
//
// ASSUME  system() invokes bash.
//
//
//---------------------------------------------------------------------
//     Copyright (C) David Reeder 2021.  rtcmix@mobilesound.org
//     Distributed under the Boost Software License, Version 1.0.
//     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
//---------------------------------------------------------------------

cmixHelper_version = 0.1   //RELEASE



//---------------------------------------------------- -o--
// Globals.

UNDEFINED  = -1.0

SECONDS_PER_MINUTE  = 60

TEXTHOOK   = "-o" + "-"




//---------------------------------------------------- -o--
// Logging.  
//
// Needs no body if print_on().
//

list  MARK     (string label, list l)  { return {} }
list  DEBUG    (string label, list l)  { return {} }
list  INFO     (string label, list l)  { return {} }
list  WARNING  (string label, list l)  { return {} }
list  ERROR    (string label, list l)  { return {} }
list  FATAL    (string label, list l)  { exit(); return {} }




//---------------------------------------------------- -o--
// Helper functions.

//---------------------- -o-
list  sep(string title)  {
    seplength30 = "------------------------------"
    printf("//%s%s %s\n", seplength30, seplength30, TEXTHOOK)
    return  {}
}


//---------------------- -o-
// RETURN:  0 if FILE EXISTS; otherwise non-zero.
//
float  doesFileExist(string filename) {
    print_on()
    return  system("test -e " + filename)
}


//---------------------- -o-
float  getRandomInteger()  {
    print_on()
    return  system("gri() { return $RANDOM; }; gri")
}


//---------------------- -o-
float  percentTrue(float lessThanOrEqual)  {
    return  ( (random() * 100) <= lessThanOrEqual )
}


//---------------------- -o-
float  subdivisionPerBeat(float bpm, float subdivisions)  {
    return  (SECONDS_PER_MINUTE / bpm / subdivisions)
}




//---------------------------------------------------- -o--
// OSC Data.
//
// Struct definition, parse and post functions, test example.
//
// Only first label is REQUIRED, the remainder are highly desirable.
//   Given a list of OSCData objects, the label of the first is expected
//   to be a well-formed OSC path.  Otherwise, label may have any format.
//
// label is FOLLOWED BY ONE OR TWO OPTIONAL LISTS.
//   The first, Free List, contains arbitrary parameters.
//   The second, Common List, contains an N-tuple of common parameters.
//     If Common List is present, Free List MUST ALSO be present, even if empty.
//
// Types available in Free List are a limited common subset of OSC 
//   and Minc types: float, string, list.  Supports nested lists.
//

//---------------------- -o-
struct  OSCData  { 
    string   label,     // REQUIRED.

    list     o,         // (optional) Free List: arbitrary values.

    float    start,     // (optional) Common List: N-tuple.
    float    dur, 
    float    amp,
    float    freq, 
    float    pan
}   

lengthOfOSCDataCommonList = 5



//---------------------- -o-
// NB  Error detection is minimal.  No type checking.
//     What errors are detected are not easily stopped.
//     RELY ON CALLING ENVIRONMENT to present well-formed input lists.
//
list  parseOSCData(list listOfStructuredLists)  
{
    list  listOfOSCDataObjects
    list  elem

    //
    listOfOSCDataObjects = {}

    for (i = 0; i < len(listOfStructuredLists); i += 1) {
        elem = listOfStructuredLists[i]
        //DEBUG("elem", {elem})


        //
        if (len(elem) <= 0)  {
            WARNING("parseOSCData(): SKIPPING empty list.", {})

        } else {
            struct OSCData  p
            p.o = {}
            p.start = p.dur = p.amp = p.freq = p.pan  = UNDEFINED

            p.label = elem[0]                       // Label is REQUIRED.

            if (len(elem) >= 3)  {                  // OPTIONAL Common List: N-tuple.
                if (len(elem[2]) != lengthOfOSCDataCommonList)  {
                    ERROR("parseOSCData(): IGNORING malformed Common List, MUST BE N-tuple.", {"N=", lengthOfOSCDataCommonList, "elem=", elem})

                } else {
                    p.start  = elem[2][0]
                    p.dur    = elem[2][1]
                    p.amp    = elem[2][2]
                    p.freq   = elem[2][3]
                    p.pan    = elem[2][4]
                }
            }

            if (len(elem) >= 2)  { p.o = elem[1] }  // OPTIONAL Free List: arbitrary values.

            listOfOSCDataObjects = listOfOSCDataObjects + {p}
        }
    }  //ENDFOR


    //
    return  listOfOSCDataObjects
}


//---------------------- -o-
list  postOSCData(list opList, string title)  
{
    struct OSCData  op
    indent = "  "

    if (len(title) >= 1)  { sep(title) }


    //
    if (len(opList) <= 0)  { 
        print("OSCData list is EMPTY.")
        return  {}
    }


    //
    fmtPath   = indent + "path: %s\n"
    fmtLabel  = indent + "label: %s\n"

    fmtRemainder =   indent + "o: %l\n"
                   + indent + "start:%f  dur:%f  amp:%f  freq:%f  pan:%f\n"

    for (i = 0; i < len(opList); i += 1) {
        op = opList[i]

        fmt = fmtLabel
        if (i <= 0)  { fmt = fmtPath }
        
        label = op.label
        if (len(label) <= 0)  { label = "''" }

        printf("%d:\n", i)
        printf(  fmt + fmtRemainder, 
                   label, 
                   op.o, 
                   op.start, op.dur, op.amp, op.freq, op.pan
              )
    }

    return  {}
}



//---------------------- -o-
list  testOSCData()
{
    sep("OSC DATA OBJECTS TEST -- BEGIN")


    //
    oscInputListExampleA  = { "/oscPath", {'a', 'b', 'c'}, {0, 1, 20000, 440, 0.5} }
    oscInputListExampleB  = { "label-b"                                            }
    oscInputListExampleC  = { "label-c",  {42, 108, 7, 0}                          }
    oscInputListExampleD  = { "label-d",  {},              {3, 0.5, 10000, 220, 1} }  

    oscDataInput  = { oscInputListExampleA, oscInputListExampleB, oscInputListExampleC, oscInputListExampleD }

    od = parseOSCData(oscDataInput)
    postOSCData(od, "")


    //
    sep("OSC DATA OBJECTS TEST -- END")
    exit()

    return  {}
}

//testOSCData()   //TEST




//---------------------------------------------------- -o--
// Disk memory table.
//
// A small table to maintain state across score invocations.
// Table data is NEVER NORMALIZED.
//
// Read and writes are atomic.
// Disk is read the first time an index is read or written.  
//   Disk is written with every index write.
// DiskMemorySingleton may be reconfigured at anytime. 
//
//
// ASSUME  It is faster to read/write from a list than it is from a table.
//
// NB  modtable(table, "draw", "literal", index, value) DID NOT WORK.
//     If it did, all operations could happen on tables directly.
//     Instead, lists are used for reading and writing.
//

//---------------------- -o-
struct  DiskMemorySingleton
{
    handle  table,
    string  tableFilename,
    float   tableLength,
    list    tableAsList,
    list    namesPerIndex  
}


//---------------------- -o-
// Only necessary if default is not sufficient.
//
list  setDiskMemorySingleton(string tableName, float tableLength, list namesPerIndex)
{
    if  ((len(tableName) <= 0) || (tableLength <= 0))  {
        FATAL("setDiskMemoryTable(): One or more INVALID PARAMETERS.", 
                        {"tableLength=", tableLength, "tableName=", tableName} )
    }

    print_off()


    //
    //mosDMS.table           = UNDEFINED   //DEBUG
    mosDMS.tableFilename   = tableName
    mosDMS.tableLength     = tableLength
    mosDMS.tableAsList     = {}
    mosDMS.namesPerIndex   = namesPerIndex


    //
    print_on()
    return  {}
}


// XXX  Treat as SINGLETON.  Only update via functions.
//
struct DiskMemorySingleton  mosDMS   

setDiskMemorySingleton(  "cmixDiskMemoryTable.txt",   //DEFAULTS.
                         12,
                         {}
                      )



//---------------------- -o-
list  setDiskMemoryIndexNames(list namesPerIndex)
{
    mosDMS.namesPerIndex  = namesPerIndex
    return  {}
}


//---------------------- -o-
// (Not so) Quick-n-dirty mapping from names to disk memory table indices.
//
// XXX  O(n).  DOES NOT NOTICE or give warnings about duplicate names.
//
float  indexPerName(string name)
{
    namesPerIndex  = mosDMS.namesPerIndex

    for (i = 0; i < len(namesPerIndex); i += 1)  {
        if (name == namesPerIndex[i])  { return i }
    }

    return  UNDEFINED
}

ipn = indexPerName   //ALIAS



//---------------------- -o-
// Treat createTableIfMissing as type boolean.
//
// Uses list if it exists.
// Otherwise, load the table and return it as a list.  
//
// (optionally) Create new table and write it immediately.
//
list  getDiskMemory(float createTableIfMissing)
{
    print_off()

    //
    if (len(mosDMS.tableAsList) <= 0)  
    {
        if (doesFileExist(mosDMS.tableFilename) != 0)  
        {
            print_off()

            if (createTableIfMissing) {
                mosDMS.table = maketable("line", mosDMS.tableLength, 0,UNDEFINED, 1,UNDEFINED)
                dumptable(mosDMS.table, mosDMS.tableFilename)

            } else {
                mosDMS.table = UNDEFINED

                print_on()
                ERROR("getDiskMemory(): CANNOT FIND file.", {mosDMS.tableFilename})
                return  {}
            }

        } else {
            mosDMS.table = maketable("textfile", "nonorm", mosDMS.tableLength, mosDMS.tableFilename)
        }


        tal = {}
        for (i = 0; i < mosDMS.tableLength; i += 1)  {
            tal = tal + { samptable(mosDMS.table, "nointerp", i) }
        }

        mosDMS.tableAsList = tal
    }


    //
    print_on()
    return  mosDMS.tableAsList
}


//---------------------- -o-
list  clearDiskMemory()
{
    mosDMS.tableAsList = {}
    system("rm " + mosDMS.tableFilename)

    return  {}
}



//---------------------- -o-
float  readDiskMemoryIndex(float index)
{
    print_off()
    
    //
    if ((index >= mosDMS.tableLength) || (index < 0))  {
        print_on()
        FATAL("readDiskMemoryIndex(): Index OUT OF RANGE.", 
                                {"index=", index, "tableLength=", mosDMS.tableLength} )
    }

    //
    getDiskMemory(true)

    print_on()
    return  mosDMS.tableAsList[index]
}


float  readDiskMemoryName(string indexName)
{
    print_off()
    return  readDiskMemoryIndex(indexPerName(indexName))
}


readDMI = readDiskMemoryIndex   //ALIAS
readDMN = readDiskMemoryName    //ALIAS



//---------------------- -o-
// NB XXX  Writes entire table to disk, EVERY TIME.
//
list  writeDiskMemoryIndex(float index, float value)
{
    print_off()
    
    //
    if ((index >= mosDMS.tableLength) || (index < 0))  {
        print_on()
        FATAL("writeDiskMemoryIndex(): Index OUT OF RANGE.", 
                                {"index=", index, "tableLength=", mosDMS.tableLength} )
    }


    //
    getDiskMemory(true)
    print_off()

    mosDMS.tableAsList[index] = value

    dmt = maketable("literal", "nonorm", mosDMS.tableLength, mosDMS.tableAsList)
    dumptable(dmt, mosDMS.tableFilename)


    //
    print_on()
    return  {}
}


list  writeDiskMemoryName(string indexName, float value)
{
    print_off()
    return  writeDiskMemoryIndex(indexPerName(indexName), value)
}


writeDMI = writeDiskMemoryIndex   //ALIAS
writeDMN = writeDiskMemoryName    //ALIAS




//---------------------- -o-
list  postDiskMemory(string title)
{
    indent = "    "   // Four spaces.

    print_off()


    //
    getDiskMemory(true)

    if (len(mosDMS.tableAsList) <= 0)  {
        print("Disk memory has NOT BEEN LOADED.")
        return  {}
    }


    //
    if (len(title) >= 1)  { sep(title) }

    npiLen = len(mosDMS.namesPerIndex)

    for (i = 0; i < mosDMS.tableLength; i += 1)
    {
        name = ""

        if ((i < npiLen) && (len(mosDMS.namesPerIndex[i]) > 0))  {
            name = mosDMS.namesPerIndex[i]
        }

        printf("%s%f:  %f  %s\n", indent, i, mosDMS.tableAsList[i], name)
    }


    //
    //print_on()
    return  mosDMS.tableAsList
}



//---------------------- -o-
list  testDiskMemory(float useBasicTest)
{
    sep("DISK MEMORY TEST -- BEGIN")

    if (useBasicTest) {
        readDMI(2)
        postDiskMemory("BASIC EXAMPLE")
        exit()
    }


    //
    //setDiskMemorySingleton("", 8, {})     
    //setDiskMemorySingleton("diskMemoryTable--example.txt", -8, {}) 
            //Demonstrate FAIL.

    setDiskMemorySingleton("diskMemoryTable--example.txt", 8, {})
            
    indexNames = { 'n', 'ne', '', 'e', 'se', 's', 'sw', 'w', 'nw', 'inexactcountisok' }
    setDiskMemoryIndexNames(indexNames)


    //
    //readDiskMemoryIndex(42)   //Demonstrate FAIL.
    v = readDiskMemoryIndex(5)
    print("index 5 = " + v)

    postDiskMemory("DISK MEMORY (initial)")


    //
    //writeDiskMemoryIndex(17, 0)   //Demonstrate FAIL.
    writeDiskMemoryIndex(5, 25)
    writeDiskMemoryIndex(4, 108)

    postDiskMemory("DISK MEMORY (after change)")

    v = readDiskMemoryIndex(5)
    print("index 5 = " + v)
    v = readDiskMemoryIndex(ipn('se'))
    print("index 'se' = " + v)


    //
    clearDiskMemory()
    postDiskMemory("DISK MEMORY (after clear)")


    //
    sep("DISK MEMORY EXAMPLE -- END")
    exit()

    return  {}
}

//testDiskMemory(true)    //TEST (short)
//testDiskMemory(false)   //TEST (full)


