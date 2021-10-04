#                                                                        -o--
"""
    MOSZ.py   (module)

    Kitchen sink from A to Z, methods and classes.
    Put everything here that cannot make for its own class.
    Minimize dependencies on other MOS Toolkit classes.


    INTERACTIVE SHELL--
        pyrc()
        pymos()

        history()      (h)
        clearScreen()  (c)

        viewScript()   (vs)
        readScript()   (rs)

        isInteractive()

    DIAGNOSTICS--
        postAndExit()
        postStderr()
        postCRToContinue()
        
        postDefUsage()
        postScriptUsage()

        headerMark()  (hm)

    USER INTERACTION--
        getKeyboardInput()
        yesno()
        pager()
        readOneCharacter()

    SCRIPT MANAGEMENT--
        parseCommandlineArguments()
        signalHandlerGraceful()

    OTHER STUFF--
        isNumber()
        collectionToString()  (c2s)
        addScriptSuffix()
        timeNowInSeconds()
        percentTrue()


    See module and function headers or pydoc for more details.

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------
#
# TBD--
#   . clarify types of all local variables
# 

version  :str  = "0.6"   #RELEASE



#----------------------------------------- -o--
# Modules.

import argparse
import collections
from datetime import datetime
import os
import random
import readline
import signal
import sys
import tempfile
import tty, termios

from typing import List, Union

import __main__ as main



#
import MOSLog
log = MOSLog.MOSLog()




#----------------------------------------- -o--
# Attributes.

TEXTHOOK  :str  = "-o""-"




#----------------------------------------------- -o--
# Interactive shell.
# Edit startup script, MOS modules.

_MOSTOOLKITPATH  :str  = "$MOSTOOLKITPATH"   #ENVIRONMENT VARIABLE.

_MOSFILES_ORDERED  :list  = [
        "MOSZ.py",
        "MOSDump.py",
        "*.py",
        "MOSLog.py",
    ]


#
def  pyrc()  -> None:
    os.system("$PAGER -p" + TEXTHOOK + " $PYTHONSTARTUP")

#
def  pymos()  -> None:
    libFilesOrdered  :str  = ",".join(_MOSFILES_ORDERED)
    os.system("$PAGER -p" + TEXTHOOK + " " + _MOSTOOLKITPATH + "/{%s}" % libFilesOrdered)


#                                                                    -o-
def  history(noPager:bool=False)  -> None:
    s  :str  = '\n'.join([ str(readline.get_history_item(i + 1)) for i in range(readline.get_current_history_length()) ])
    pager(s, doEnumerate=True, seekToBottom=True, noPager=noPager)


h = history   #ALIAS


#                                                                    -o-
def  clearScreen()  -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

c = clearScreen   #ALIAS



#                                                                    -o-
def  viewScript(scriptName:str=None, addSuffix:bool=True, scriptSuffix:str="py")  -> None:

    if  addSuffix:  scriptName = addScriptSuffix(scriptName, scriptSuffix)

    try:                    pager(open(scriptName).read())
    except Exception as e:  log.error(e)

vs = viewScript   #ALIAS


#                                                                    -o-
# NB  Use exec() to execute and capture context in globals().
#
def  readScript(  scriptName    :str    = None, 
                  addSuffix     :bool   = True, 
                  scriptSuffix  :str    = "py"
                ) -> str:
    scriptContent  :str  = None

    if  addSuffix:  scriptName = addScriptSuffix(scriptName, scriptSuffix)

    try:                    scriptContent = open(scriptName).read()
    except Exception as e:  log.error(e)

    return  scriptContent

rs = readScript   #ALIAS



#                                                                    -o-
def  isInteractive()  -> bool:
    return  not hasattr(main, "__file__")




#----------------------------------------------- -o--
# Diagnostics.

#                                                                    -o-
def  postAndExit(message:str, exitValue:int=1, omitScriptName:bool=False)  -> int:

    scriptName  = "" if omitScriptName else  log.scriptName() + f"({exitValue}): "

    postStderr(f"{scriptName}{message}")

    if  not isInteractive():
        sys.exit(exitValue)

    return  exitValue


#                                                                    -o-
def  postStderr(message:str)  -> None:
    print(message, file=sys.stderr)


#                                                                    -o-
def  postCRToContinue(message:str=None)  -> None:
    s  :str  = "<CR> to continue..."

    if  message:  s = message

    print(s.strip() + "   ", end="", flush=True)
    input()


#                                                                    -o-
def  postDefUsage(defName:str=None, signature:str=None)  -> None:
    usageString  :str  = "USAGE: "

    if  not defName:    raise Exception()
    if  not signature:  signature = ""

    usageString = f"USAGE: {defName}({signature})"
    postAndExit(usageString, omitScriptName=True)


#                                                                    -o-
def  postScriptUsage(scriptName:str=None, signature:str=None)  -> None:
    usageString  :str  = "USAGE: "

    if  not scriptName:  raise Exception()
    if  not signature:   signature = ""

    usageString = f"USAGE: {scriptName} {signature}"
    postAndExit(usageString, omitScriptName=True)



#                                                                    -o-
def  headerMark(title:str=None, short:bool=None)  -> None:
    s  :str  = ""

    if  not title:  title = ""
    if  not short:  short = False

    if  not short:  s = "\n\n\n"
    s += "#------------------------------------------------ -o" + "--  \n"
    if  len(title) > 0:
        s += title + "\n\n"

    return s

hm = headerMark




#----------------------------------------------- -o--
# User interaction.

#                                                                    -o-
def  getKeyboardInput(  prompt               :str   = None,         
                        validationFunction          = None, 
                        leadWithPrompt       :bool  = None
                      ) -> Union[str, None]:
    """
    RETURNS:  None  If user exits with ^C;
              str   Mediated by validationFunction(), if it exists.
   
    If validationFunction() is undefined the input is returned immediately.
   
    Otherwise validationFunction() is ASSUMED to have the following signature:
      def  validationFunction([self], input:str)  -> bool
    validationFunction() returns True when the input is correct, else it might post guidance 
      on how the user can improve their choice of input.
    getKeyboardInput() loops until validateFunction() is True.
    """

    USAGE  :str  = "[prompt:str], [validationFunction:def], [leadWithPrompt:bool]"

    userInput = None


    # DEFAULTS.  Sanity check.
    #
    if  not leadWithPrompt:  leadWithPrompt = True

    if      (not prompt  or  not isinstance(prompt, str))                       \
        or  (      validationFunction                                           \
              and  not isinstance(validationFunction, collections.Callable) )   \
        or  not isinstance(leadWithPrompt, bool):
        postDefUsage(log.defName(), USAGE)
        return  None


    #
    if  not prompt:
        prompt = ""
    else:
        prompt += "  "

    if  leadWithPrompt:
        print(prompt, end="")


    while  True: 
        try:     userInput = input()
        except:  return  None

        if  not validationFunction:
            return  userInput
        elif  validationFunction(userInput):
            return  userInput

        print(prompt, end="")

#ENDDEF -- getKeyboardInput()


#                                                                    -o-
def  yesno(  prompt:str=None,           
             expectedInput:str=None,   
             leadWithPrompt:bool=None 
           ) -> Union[bool, None]:   
    """
    RETURN:  bool  True if choice matches expectedInput, False otherwise.
             None  if user cancels with ^C.
    """

    USAGE  :str  = "prompt:str, [expectedInput:str], [leadWithPrompt:bool]"

    promptExpected  :str  = None
    userResponse    :str  = None

    promptIndentation = ""



    # DEFAULTS.  Sanity check.
    #
    if  not prompt:          prompt         = "Do the thing?"
    if  not expectedInput:   expectedInput  = "y"
    if  not leadWithPrompt:  leadWithPrompt = True

    if  not (      isinstance(prompt, str)  
              and  isinstance(expectedInput, str)  
              and  isinstance(leadWithPrompt, bool) ):
        postDefUsage(log.defName(), USAGE)
        return  None

    expectedInput = expectedInput.lower()[0]

    if  expectedInput not in ("y", "n"):
        postAndExit(f"{log.defName()}: <expectedInput> must lead with 'y' or 'n'.")
        return  None


    #
    if  "y" == expectedInput:
        promptExpected = "  (Y/n)"
    else:
        promptExpected = "  (y/N)"


    # Guess at indentation of prompt...
    #
    for _ in range(0, len(prompt)):
        if  prompt[_].isalnum():
            break
        else:
            promptIndentation += " "
        

    #
    def  validateLeadingCharacterInput(charInput)  -> bool:
        if  len(charInput) <= 0:
            return  True

        charInput = charInput.lower()[0]

        if  charInput not in ("y", "n"):
            print(promptIndentation + "  Please answer 'y' or 'n'.")
            return  False
        else:
            return  True


    userResponse = getKeyboardInput(  prompt + promptExpected,
                                      validateLeadingCharacterInput,
                                      leadWithPrompt )

    #
    if  not userResponse:
        return  None

    if  len(userResponse) <= 0:
        return  True

    userResponse = userResponse.lower()[0]

    return  (expectedInput == userResponse)

#ENDDEF -- yesno()


#                                                                    -o-
def  pager(     fileOrStr               = None,         \
                title           :str    = None,         \
                doEnumerate     :bool   = False,        \
                seekToBottom    :bool   = False,        \
                noPager         :bool   = False         \
            )  -> None:
    """
    If fileOrStr is a string, then open a temporary file with string in the header.
    Otherwise, open fileOrStr as if it were a file.

    NB XXX  Currently used primarily to capture ephemeral output into a temporary file.
    """

    USAGE  :str  = "fileOrStr:Union[<file>,str], [title:str], [doEnumerate:bool]"

    tmpFile      = None
    pagerCmd     = " $PAGER -p" + TEXTHOOK
    pagerBottom  = " "                      #XXX  One space minimum

    # 
    if  not fileOrStr:
        postDefUsage(log.defName(), USAGE)
        return

    if  not title:  title = ""

    if  seekToBottom:  pagerBottom  = " +G "

    if  noPager:
        pagerCmd        = " cat "
        pagerBottom  = " "


    #
    if  isinstance(fileOrStr, str):
        tmpFile = tempfile.NamedTemporaryFile(mode="w+")   # XXX  Not binary.
        tmpFile.write(headerMark(title))
        tmpFile.write(fileOrStr)
        tmpFile.write("\n")
        tmpFile.seek(0)
        fileOrStr = tmpFile   #XXX

    if  doEnumerate:
        os.system("cat -n " + fileOrStr.name + " | " + pagerCmd + pagerBottom)
    else:
        os.system(pagerCmd + pagerBottom + fileOrStr.name)

    if  tmpFile:
        tmpFile.close()

#ENDDEF -- pager()


#                                               -o-
def  readOneCharacter()  -> str:
    """
    Read one character from the keyboard and return it immediately.
    """
    fd            :int   = sys.stdin.fileno()
    fdTCPrevious  :list  = termios.tcgetattr(fd)
    ch            :str   = None

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, fdTCPrevious)

    return  ch




#----------------------------------------------- -o--
# Script management.

#                                                                    -o-
def  parseCommandlineArguments(listOfDictOfArgs:List[dict]=None)  -> Union[argparse.Namespace, None]:
    """
    Shortcut for simple use of argparse.
    Supports only optional_strings, default, type, help.
    """

    if  not listOfDictOfArgs  or  len(listOfDictOfArgs) <= 0:
        postAndExit("listOfDictOfArgs CANNOT be empty.", log.defName())
        return  None
        
    #
    parser = argparse.ArgumentParser()

    for  e in listOfDictOfArgs:
        if  "option_strings" not in e:
            postAndExit(                                               
                "listOfDictOfArgs entries MUST CONTAIN 'option_strings'.", 
                log.defName() )
            return  None

        parser.add_argument(
                           e["option_strings"],
                default  = e["default"]  if "default" in e  else None,
                type     = e["type"]     if "type"    in e  else None,
                help     = e["help"]     if "help"    in e  else None,
            )

    return  parser.parse_args()

#ENDDEF -- parseCommandlineArguments()


#                                                                    -o-
def  signalHandlerGraceful(caughtSignal, frame):
    if  not isInteractive():
        if  2 == caughtSignal:      # SIGINT
            print(f"\n{log.scriptName()}: Exiting...")
            sys.exit(1)

    log.warning(f"Received UNEXPECTED SIGNAL.  ({caughtSignal})")


#NB XXX -- Active for anything that imports MOSZ.
#
if  not isInteractive():   #XXX  Also affects interactive shell.
    signal.signal(signal.SIGINT, signalHandlerGraceful)   

#signal.signal(signal.SIGHUP, signalHandlerGraceful)   #TESTING





#----------------------------------------------- -o--
# Other stuff.

#                                                                    -o-
def  isNumber(obj:object)  -> bool:
    if  isinstance(obj, (int, float)):
        return  True
    return  False


#                                                                    -o-
def  collectionToString(someCollection=None, separator:str=" ")  -> str:
    if  not someCollection:  
        return  ""

    return  separator.join(map(str, someCollection))

c2s = collectionToString   #ALIAS


#                                                                    -o-
def  addScriptSuffix(scriptName:str=None, scriptSuffix:str="py")  -> str:
    """
    Be lazy: Type in scriptName without the suffix.  
    ASSUMES Python script.
    """

    splitArray  :list  = scriptName.rsplit(".")
    if  (len(splitArray) <= 1)  or  scriptSuffix != scriptName.rsplit(".")[1]:
        scriptName = f"{scriptName}.{scriptSuffix}"

    return  scriptName


#                                                                    -o-
def  timeNowInSeconds(withOffset:float=0.0, useUTC:bool=False)  -> float:
    dt  :datetime  = None

    if  useUTC:
        #dt = datetime.now(timezone.utc)
        dt = datetime.utcnow()

    else:
        dt = datetime.now()

    return  dt.timestamp() + withOffset


#                                                                    -o-
def  percentTrue(lessThanOrEqualTo:float)  -> bool:
    return  ((random.random() * 100) <= lessThanOrEqualTo)


