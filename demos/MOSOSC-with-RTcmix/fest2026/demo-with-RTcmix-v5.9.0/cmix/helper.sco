//
// helper.sco   
//
// General helper and logging functions.
// 
//
// ASSUME--
//   . CMIX version >= 5.0.0
//   . system() invokes Bash shell
//
//
//--------------------------------------------------------------------
//     Copyright (C) David Reeder 2021-2026.  info@mobilesound.org
//     Distributed under the Boost Software License, Version 1.0.
//     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
//---------------------------------------------------------------------

helper_version = "3"   #RELEASE DRAFT



//---------------------------------------------------- -o--
// Globals.

UNDEFINED  = -1.0

SECONDS_PER_MINUTE  = 60

TEXTHOOK   = "-o" + "-"




//---------------------------------------------------- -o--
// Logging.  
//

float  MARK     (string reason, list context)  {           return  0 }
float  DEBUG    (string reason, list context)  {           return  0 }
float  INFO     (string reason, list context)  {           return  0 }
float  WARNING  (string reason, list context)  {           return  0 }
float  ERROR    (string reason, list context)  {           return  1 }
float  FATAL    (string reason, list context)  { exit(1);  return  1 }




//---------------------------------------------------- -o--
// Helper functions.
//
// sep()
// doesFileExist()
// getRandomInteger()
// percentTrue()
// subdivisionPerBeat()
//

//
list  sep(string title)  {
    seplength30 = "------------------------------"
    printf("//%s%s %s\n", seplength30, seplength30, TEXTHOOK)
    return  {}
}


// RETURN:  0 if FILE EXISTS; otherwise non-zero.
//
float  doesFileExist(string filename) {
    return  system("test -e " + filename)
}


//
float  getRandomInteger()  
{
    return  system("echo $RANDOM")
}


//
float  percentTrue(float lessThanOrEqual)  {
    return  ( (random() * 100) <= lessThanOrEqual )
}


//
float  subdivisionPerBeat(float bpm, float subdivisions)  {
    return  (SECONDS_PER_MINUTE / bpm / subdivisions)
}

