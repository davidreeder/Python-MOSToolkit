#                                                                        -o--
"""
    MOSLog.py

    Log messages at different log levels in context of <class>.<method>.
    Use inspect to find class, module, function or script names.

    Each level has its own method.  
        * standard levels -- debug(), info(), warning(), error(), critical()
        * MOS levels -- mark(), osc()

    Log message under INFO are streamed to stderr, including DEBUG and MARK.
    Otherwise, log messages are streamed to stdout.


    NB  Only the first call to logging.basicConfig() configures logging package; 
        all future calls are silently ignored.

    This module is INDEPENDENT of all other MOS toolkit modules.


    RESOURCES--
       . https://docs.python.org/3/howto/logging-cookbook.html
       . https://docs.python.org/3/library/logging.html#filter-objects

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.5"   #RELEASE

USAGE  :str  = "[logTime:bool], [logDate:bool]"   



#----------------------------------------- -o--
# Modules.

import inspect

# NB  Relative to logging module lowest level DEBUG=10.
#
import logging
logging.MOS_LOGGER_LEVEL_MARK  = 11   # DEBUG=10
logging.MOS_LOGGER_LEVEL_OSC   = 21   # INFO=20

import os
import sys

import typing
from typing import Any, List, Tuple




#----------------------------------------- -o--
class  MOSLog:
    """
    Log messages that stream to stderr--
        debug()
        mark()          (introduced by MOS)

    Log messages that stream to stdout--
        info()
        warning()
        error()
        critical()
        osc()           (introduced by MOS)


    All logging methods take a variable number of arguments,
      ASSUMED to have the following form:

        formatString, [formatElements...]

    error() and critical() can take single argument representing Exception.


    Convenience methods return the name of encapsulating block--
        className()   -- Generally works within classes.
        moduleName()  -- Generally works where className() fails.
        defName()     -- For both script functions and class methods.
        scriptName()  -- Returns the filename, optionally stripping basename.
    """



    #----------------------------------------------- -o--
    # Public methods.

    #                                                                    -o-
    def  osc(self, *args)  -> None:
        s = " ".join(str(x) for x in args)
        logging.log(logging.MOS_LOGGER_LEVEL_OSC, s)

    #                                                                    -o-
    def  mark(self, *args)  -> None:                          
        logging.log( logging.MOS_LOGGER_LEVEL_MARK,                \
                     "%s %s",                                      \
                        self._makeSignature(inspect.stack()[1]),   \
                        self._processArguments(args)               \
                   )


    #                                                                    -o-
    def  debug(self, *args)  -> None:                                 
        logging.debug("%s %s", self._makeSignature(inspect.stack()[1]), self._processArguments(args))

    #                                                                    -o-
    def  info(self, *args)  -> None:                                
        logging.info("%s %s", self._makeSignature(inspect.stack()[1]), self._processArguments(args))

    #                                                                    -o-
    def  warning(self, *args)  -> None:                           
        logging.warning("%s %s", self._makeSignature(inspect.stack()[1]), self._processArguments(args))

    #                                                                    -o-
    def  error(self, *args)  -> None:                                
        """
        NB  *args may be a single Exception, -OR-
            variable arguments in the form: formatString, [formatElements, ...]
        """
        args = self._processException(args)
        #args = _processException(args)
        logging.error("%s %s", self._makeSignature(inspect.stack()[1]), self._processArguments(args))

    #                                                                    -o-
    def  critical(self, *args, exitValue:int=1)  -> None:                           
        """
        NB  ALWAYS exits with exitValue, unless exitValue==None.  (DEFAULT:1)
        NB  *args may be a single Exception, -OR-
            variable arguments in the form: formatString, [formatElements, ...]
        """
        stack  = inspect.stack()[1]
        args   = self._processException(args)

        logging.critical("%s %s", self._makeSignature(stack), self._processArguments(args))

        if  exitValue:
            print( f"\n{self.scriptName()}: {self._makeSignature(stack)} -- Exiting...  ({exitValue})",
                   file=sys.stderr )
            exit(exitValue)



    #                                                                    -o-
    def  className(self, additionalFrameDepth:int=None)  -> str:
        """
        In the general case, ASSUME a frameDepth of one (1).  
        This handles the case where MOSLog().className() is called from a method in another class.

        Calling from the class itself (outside of any method) requires additionalFrameDepth = -1.
        Nested methods or functions may require higher values of additionalFrameDepth.
        """

        if  not additionalFrameDepth:  additionalFrameDepth = 0
        frameDepth = 1 + additionalFrameDepth

        try:
            return  sys._getframe(frameDepth).f_locals["self"].__class__.__name__
        except:
            return  ""


    #                                                                    -o-
    def  moduleName(self, depth:int=2)  -> str:
        """
        XXX  Look for filename, N-from-the-bottom of the stack.
        """
        callingEnvironment = inspect.stack()[depth][1]   #filename
        return  os.path.basename(callingEnvironment).rsplit(".", 1)[0]


    #                                                                    -o-
    def  defName(self, depth:int=1, omitModuleName:bool=False)  -> str:
        """
        XXX  Look for function, N-from-the-bottom of the stack.
        """
        stack               = inspect.stack()
        stackSize     :int  = len(stack)
        functionName  :str  = ""

        if  stackSize >= depth:  depth = 1

        functionName = stack[depth][3]   #function

        if  omitModuleName:  return functionName

        return  self.moduleName(depth+1) + "." + functionName


    #                                                                    -o-
    def  scriptName(self, excludeSuffix:bool=False)  -> str:
        """
        NB  Look for filename, at the top of the stack.
        """
        stack      :list  = inspect.stack()
        stackSize  :int   = len(stack)
        basename   :str   = os.path.basename(stack[stackSize-1][1])   #filename

        if  excludeSuffix:  basename = basename.rsplit(".", 1)[0]

        return  basename




    #----------------------------------------------- -o--
    # Lifecycle.

    #                                                                    -o-
    def  __init__(      self, 
                        logTime                   :bool   =None, 
                        logDate                   :bool   =None, 
                        outputStreamBelowInfo             =None,
                        outputStreamAboveInfo             =None
                  ):
        """
        NB  First instance of MOSLog configures logging package for entire application. 
        """

        logFormatWithTime  = ""
        dateFormat         = ""
        stderrHandler      = None
        stdoutHandler      = None

        global USAGE
        usage = f"USAGE: {self.className()}({USAGE})"


        # DEFAULTS.  Sanity check.
        #
        if  not logTime:  logTime = False
        if  not logDate:  logDate = False

        if  not outputStreamBelowInfo:  outputStreamBelowInfo   = sys.stderr
        if  not outputStreamAboveInfo:  outputStreamAboveInfo   = sys.stdout

        if  not (isinstance(logTime, bool)  and  isinstance(logDate, bool)):
            print(usage, file=sys.stderr)
            exit(1)
            return


        #
        logging.addLevelName(logging.MOS_LOGGER_LEVEL_OSC,  "OSC") 
        logging.addLevelName(logging.MOS_LOGGER_LEVEL_MARK, "MARK") 


        #
        if  logTime  and  logDate:
            logFormatWithTime  = "%(asctime)s.%(msecs)03d  "
            dateFormat  = "%Y-%m-%d %H:%M:%S"

        elif  logTime:
            logFormatWithTime  = "%(asctime)s.%(msecs)03d  "
            dateFormat  = "%H:%M:%S"

        elif  logDate:
            logFormatWithTime  = "%(asctime)s  "
            dateFormat  = "%Y-%m-%d"

        logFormatWithTime += "%(levelname)s  %(message)s"
            

        #
        class  StderrFilter(logging.Filter):
            def  filter(record):
                return  record.levelno in ( logging.DEBUG, logging.MOS_LOGGER_LEVEL_MARK )

        class  StdoutFilter(logging.Filter):
            def  filter(record):
                return  record.levelno in ( logging.INFO, logging.MOS_LOGGER_LEVEL_OSC, 
                                            logging.WARNING, logging.ERROR, logging.CRITICAL )

        stderrHandler = logging.StreamHandler(outputStreamBelowInfo)
        stderrHandler.setLevel(logging.DEBUG)
        stderrHandler.addFilter(StderrFilter)

        stdoutHandler = logging.StreamHandler(outputStreamAboveInfo)
        stdoutHandler.setLevel(logging.INFO)
        stdoutHandler.addFilter(StdoutFilter)

        # NB  stream= and handlers= are mutually exclusive.
        #
        logging.basicConfig( format    = logFormatWithTime, 
                             datefmt   = dateFormat,
                             level     = logging.DEBUG,           # NB  Lowest level.
                             #stream    = outputStreamBelowInfo,   #DEFAULT.
                             handlers  = [
                                 stdoutHandler,
                                 stderrHandler
                               ]
                           )
    #ENDDEF -- __init__




    #----------------------------------------------- -o--
    # Protected methods.

    #                                                                    -o-
    def  _makeSignature(self, frameStackElement:List)  -> None:
        """
        Alternate source for method or function name: sys._getframe(N).f_code.co_name
        Where N = 2 from in this method context.
        """

        callingClass     :str  = self.className(2)
        callingFunction  :str  = frameStackElement[3]   
        callingLine      :str  = frameStackElement[2]

        if  len(callingClass) > 0:
            callingClass = callingClass + "."

        if  "<module>" == callingFunction:
            callingFunction = self.scriptName(excludeSuffix=True)

        return  callingClass + callingFunction + ":" + str(callingLine)


    #                                                                    -o-
    def  _processArguments(self, argsList:Tuple[Any])  -> str:
        argsList = list(argsList)

        if len(argsList) <= 0:
            return  ""

        formatString = "-- " + str(argsList.pop(0))

        if len(argsList) <= 0:
            return(formatString)

        return  (formatString % tuple(argsList))


    #                                                                    -o-
    def  _processException(self, argsList:Tuple[Any])  -> str:
        """
        NB  Throws away any arguments after Exception object, if it exists.
        """
        e                :Exception  = None
        exceptionString  :str        = ""
        errno            :int        = None
        errnoString      :str        = ""
        description      :str        = ""

        #
        argsList = list(argsList)

        if  (len(argsList) <= 0)  or  not isinstance(argsList[0], Exception):
            return  tuple(argsList)

        #
        e = argsList.pop(0)

        if  len(e.args) > 1:
            errno        = e.args[0]
            errnoString  = f"  ({errno})"
            description  = e.args[1]
        else:
            description  = e.args[0]

        exceptionString = f"EXCEPTION: {description}.{errnoString}"

        #
        argsList.insert(0, exceptionString)

        return  (exceptionString,)

#ENDCLASS -- MOSLog()

