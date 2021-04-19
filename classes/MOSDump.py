#                                                                        -o--
"""
    MOSDump.py 

    Dump things (initially) as strings.


    COLLECTIONS--
        dicto(), dictop()
        listo(), listop()

    OBJECTS--
        sysModules()
        dirp()
        magic()
        mro()

        obj(), objp() 
            objModule(), objModulep() 
            objClass(), objClass()
            objBody(), objBodyp()
            objFunction(), objFunctionp()

    ENVIRONMENT--
        env()
        selectVars(), sv() 
            selectVarsp(), svp()


    See module and function headers or pydoc for more details.

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.5"   #RELEASE



#----------------------------------------- -o--
# Modules.

import inspect
import sys

from typing import Dict, List, Union


#
import MOSLog 
log = MOSLog.MOSLog()

import MOSZ as z 




#----------------------------------------- -o--
# Protected attributes.

_fourSpaces  :str  = "    "

_localHook   :str  = f"\t\t\t{z.TEXTHOOK}"




#----------------------------------------------- -o--
# Dump collections.

#                                                                    -o-
def  dicto(  dictionary:dict, 
             title:str=None, indent:str=None, sort:bool=False, 
             depth:int=1 
          )  -> str:
    """
    NB  sort=True means "sort keys".
    """

    USAGE  :str  = "dictionary:dict, [title:str], [indent:str], [sort:bool]"

    keys          = None
    keyLengthMax  = -1
    s             = ""
    value         = None 


    # DEFAULTS.  Sanity checks.
    #
    if  not title:   title  = "" 
    if  not indent:  indent = "    " 

    if  not dictionary:
        if  len(title) > 0:  return  title + " = None"
        else:                return  "None"

    if      not isinstance(dictionary, dict)   \
        or  not isinstance(title, str)         \
        or  not isinstance(indent, str)        \
        or  not isinstance(sort, bool):
        z.postDefUsage(log.defName(), USAGE)
        return

    if  len(title) > 0:  title += " = "


    # NB  Always wrap dict.keys() element in str().
    #
    if  sort:
        keys = sorted(dictionary.keys())
    else:
        keys = dictionary.keys()

    for k in keys:
        keyLengthMax = max( keyLengthMax, len(str(k)) )

    s = title + "{\n"

    depth -= 1

    for k in keys:
        s += indent + str(k)
        s += (keyLengthMax - len(str(k))) * " "
        s += "  = "

        value = dictionary[k]

        if    isinstance(value, dict)  and  (depth > 0):
            s += dicto(value, indent=indent + _fourSpaces, sort=sort, depth=depth)
        elif  isinstance(value, list)  and  (depth > 0):
            s += listo(value, indent=indent + _fourSpaces, sort=sort, depth=depth)
        else:
            s += str(value)

        s += "\n"
    
    s += indent + "}"


    #
    return  s

#ENDDEF -- dicto()


#                                                                    -o-
def  dictop(  dictionary:dict, 
              title:str=None, indent:str=None, sort:bool=False, 
              depth:int=1 
           )  -> str:   #PRINT dicto()
    print(dicto(dictionary, title, indent, sort, depth))   


#                                                                    -o-
def  listo(  aList:list, 
             title:str=None, indent:str=None, sort:bool=False,
             depth:int=1
          )  -> str:

    USAGE = "aList:list, [title:str], [indent:str]"

    powerOfListLength              = -1
    indexPrefixMax                 = 1
    indexRightJustifyFormatString  = None
    aListIndex                     = 0

    s = ""


    # DEFAULTS.  Sanity checks.
    #
    if  not title:   title  = "" 
    if  not indent:  indent = "    " 

    if  not aList:   
        if  len(title) > 0:  return  title + " = None"
        else:                return  "None"

    if  not (      isinstance(aList, list)
              and  isinstance(title, str)  
              and  isinstance(indent, str) ):
        z.postDefUsage(log.defName(), USAGE)
        return

    if  len(title) > 0:  title += " = "


    #
    powerOfListLength = len(aList)

    while  (powerOfListLength / 10) >= 1:
        powerOfListLength /= 10
        indexPrefixMax += 1

    indexRightJustifyFormatString = "{:>%d}" % indexPrefixMax


    #
    if  sort:  aList.sort()


    #
    s = title + "[\n"

    depth -= 1

    for _ in aList:
        s += indent + indexRightJustifyFormatString.format(aListIndex) + ": "

        value = aList[aListIndex]
        aListIndex += 1

        if    isinstance(value, dict)  and  (depth > 0):
            s += dicto(value, indent=indent + _fourSpaces, sort=sort, depth=depth)
        elif  isinstance(value, list)  and  (depth > 0):
            s += listo(value, indent=indent + _fourSpaces, sort=sort, depth=depth)
        else:
            s += str(value)

        s += "\n"
    
    s += indent + "]"


    #
    return  s

#ENDDEF -- listo()


#                                                                    -o-
def  listop(  aList:list, 
              title:str=None, indent:str=None, sort:bool=False,
              depth:int=1
           )  -> str:   #PRINT listo()
    print(listo(aList, title, indent, sort, depth))




#----------------------------------------------- -o--
# Dump objects.

#                                                                    -o-
def  sysModules()  -> None:
    z.pager(dicto(sys.modules, sort=True), title="sys.modules")
    

#                                                                    -o-
def  dirp(classnameOrInstance=None, noPager:bool=False)  -> None:
    """
    Dump dir().
    """
    USAGE  :str  = "classnameOrInstance, [noPager:bool]"

    #
    if  not classnameOrInstance:
        z.postDefUsage(log.defName(), USAGE)
        return

    #
    z.pager(listo(dir(classnameOrInstance)), noPager=noPager)


#                                                                    -o-
def  magic(classnameOrInstance=None, noPager:bool=False, depth:int=2)  -> None:
    """
    Dump __dict__ from (any) object.
    """
    USAGE  :str  = "classnameOrInstance, [noPager:bool=False], [depth:int=1]"

    #
    if  not classnameOrInstance:
        z.postDefUsage(log.defName(), USAGE)
        return

    #
    z.pager(dicto(dict(classnameOrInstance.__dict__), sort=True, depth=depth), noPager=noPager)



#                                                                    -o-
def  mro(cls)  -> None:
    """
    Method resolution order.
    """

    try:        
        listop(list(inspect.getmro(cls)))
    except  Exception as e:     
        log.error(e)



#                                                                    -o-
def  obj(thing:object=None)  -> Union[str,None]:
    """
    Pretty print (any) object.
    """
    if    inspect.ismodule(thing):
        return  objModule(thing)

    elif  inspect.isclass(thing):
        return  objClass(thing)

    else:
        log.error(f"UNKNOWN object type.  ({thing})")


def  objp(thing=None)  -> Union[str,None]:              #PRINT
    print(obj(thing))



#                                                                    -o-
def  objModule(thing:object=None)  -> str:
    """
    Pretty print (any) module.
    NB  Unsorted attribute list indicates code order within the module file.
    """

    d      :Dict  = {}
    s      :str   = ""


    #
    if  not thing:
        z.postDefUsage(log.defName(), "thing:object")


    # Header documentation, including name, version, file.
    #
    d = thing.__dict__

    if  "__name__" in d:
        s += f"MODULE :: {d['__name__']}\n\n"

    if  "version" in d:
        s += f"version: {d['version']}\n"

    if  "__file__" in d:
        s += f"{d['__file__']}\n"

    s += "\n"

    if  ("__doc__" in d)  and  d["__doc__"]:
        if  not d["__doc__"].startswith("\n"):  s += "\n\t"
        s += f"{d['__doc__']}\n"
        if  not d["__doc__"].endswith("\n"):    s += "\n\n"


    #
    s += objBody(thing)


    # List all attributes.
    #
    dcopy = d.copy()

    for k in d:
        if  k.startswith("__") and k.endswith("__"):
            dcopy.pop(k)

    s += f"\n\nNON-MAGIC ATTRIBUTES--{_localHook}\n"
    s += listo(list(dcopy.keys()))


    #
    return  s


def  objModulep(thing:object=None)  -> str:             #PRINT
    print(objModule(thing))


#                                                                    -o-
def  objClass(thing:object=None)  -> str:
    """
    Pretty print (any) class.
    """

    d       :Dict    = {}
    module  :object  = None
    s       :str     = ""


    #
    if  not thing:
        z.postDefUsage(log.defName(), "thing:object")


    #
    d       = dict(thing.__dict__)
    module  = inspect.getmodule(thing)


    # Header documentation, including name, USAGE, module.
    #
    _ = str(thing).split("'")       # XXX -- Finding name.
    if  len(_) <= 1:  name = _[0]
    else:             name = _[1]
        
    if  "." in name:
        name = name.rsplit(".")[1]

    usage = ""

    if  "USAGE" in d:
        usage = d["USAGE"]
    elif  "USAGE" in module.__dict__:
        usage = module.__dict__["USAGE"]

    s += f"CLASS :: {name}({usage})\n\n"

    if  "version" in d  and  d["verion"]:
        s += f"version: {d['version']}\n"

    if  "__module__" in d  and  d["__module__"]:
        s += f"module: {d['__module__']}\n"

    if  "__doc__" in d  and  d["__doc__"]:
        if  not d["__doc__"].startswith("\n"):  s += "\n\t"
        s += f"{d['__doc__']}"
        if  not d["__doc__"].endswith("\n"):  s += "\n"

    #
    s += "\n"
    s += objBody(thing, True)


    # Module.
    #
    s += z.headerMark(short=True)
    s += objModule(module)


    #
    return  s


def  objClassp(thing:object=None)  -> str:              #PRINT
    print(objModule(thing))


#                                                                    -o-
def  objBody(thing:object=None, isClass:bool=False)  -> str:

    d  :Dict  = {}
    s  :str   = ""

    bulletIndent   :str  = "  . "
    functionLabel  :str  = "FUNCTIONS"


    #
    if  not thing:
        z.postDefUsage(log.defName(), "thing:object")


    #
    d = dict(thing.__dict__)


    # Attributes.
    #
    annotations = d["__annotations__"]  if "__annotations__" in d  else None

    if  annotations:
        publicAnnotations     = list(filter(lambda s: not s.startswith("_"), annotations))
        protectedAnnotations  = list(filter(lambda s: s.startswith("_"), annotations))

        #s += "\n\n"

        if  len(publicAnnotations) > 0:
            s += f"\n\nPUBLIC ATTRIBUTES--{_localHook}\n"
            s += selectVars(d, publicAnnotations)

        if  len(protectedAnnotations) > 0:
            s += f"\n\nPROTECTED ATTRIBUTES--{_localHook}\n"
            s += selectVars(d, protectedAnnotations)


    # Functions.
    #
    functions = list(filter(lambda f: inspect.isfunction(d[f]), d.keys()))

    if  functions:
        publicFunctions     = list(filter(lambda s: not s.startswith("_"), functions))
        protectedFunctions  = list(filter(lambda s: s.startswith("_") and not s.endswith("_"), functions))
        privateFunctions    = list(filter(lambda s: s.startswith("__"), functions))

        if  isClass:  functionLabel = "METHODS"

        if  annotations:
            s += "\n\n"

        if  len(publicFunctions) > 0:
            s += f"\n\nPUBLIC {functionLabel}--{_localHook}\n\n"
            for m in publicFunctions:
                s += bulletIndent + objFunction(d[m])

        if  len(protectedFunctions) > 0:
            s += f"\n\nPROTECTED {functionLabel}--{_localHook}\n\n"
            for m in protectedFunctions:
                s += bulletIndent + objFunction(d[m])

        if  len(privateFunctions) > 0:
            s += f"\n\nPRIVATE (AND DUNDER) {functionLabel}--{_localHook}\n\n"
            for m in privateFunctions:
                s += bulletIndent + objFunction(d[m])


    if  annotations  or  functions:
        s += "\n\n"

    #
    return  s


def  objBodyp(thing:object=None, isClass:bool=False)  -> str:              #PRINT
    print(objBody(thing, isClass))



#                                                                    -o-
def  objFunction(thing:object=None)  -> str:
    """
    Pretty print (any) function.
    """
    s  :str  = ""

    #
    if  not thing:
        z.postDefUsage(log.defName(), "thing:object")

    #
    s += f"{thing.__name__}{inspect.signature(thing)}"

    if  thing.__doc__:
        if  not thing.__doc__.startswith("\n"):  s += "\n\t"
        s += thing.__doc__
        if  not thing.__doc__.endswith("\n"):    s += "\n"
    else:
        s += "\n"

    s += "\n"

    return  s


def  objFunctionp(thing:object=None)  -> str:           #PRINT
    print(objFunction(thing))




#----------------------------------------------- -o--
# Dump environment.

def  env(globalsOrLocals:dict=None)  -> None:
    """
    Dump globals() or locals().
    """
    if  not globalsOrLocals  or  not isinstance(globalsOrLocals, dict):
        z.postDefUsage(log.defName(), "globals() | locals()")
        return

    z.pager(dicto(globalsOrLocals, sort=True))


#                                                                    -o-
def  selectVars(  contextDict   :dict       = None, 
                  variableList  :List[str]  = [], 
                  title:str=None, indent:str=None, sort:bool=False)  -> None:
    """
    Dump a selection of key/value pairs from contextDict.
    String elements of variableList select keys from contextDict.  
      If the key value represents an object, the string representation may
      be suffixed with any arbitrary standard syntax normally used to
      return attributes or elements within the object.
    Use with locals(), globals() or any dictionary.
    """

    USAGE  :str  = "contextDict:dict, [varibleList:List[str]], [title:str], [indent:str], [sort:bool]"

    newDict  :dict  = {}

    objectSeparators    :str   = ".["   #XXX
    tokenArray          :list  = []
    baseToken           :str   = None
    tokenModifier       :str   = None

    #
    if  not isinstance(contextDict, dict):
        z.postDefUsage(log.defName(), USAGE)
        return


    #
    if  len(variableList) <= 0:  
        newDict = contextDict

    else:
        for v in variableList:
            baseToken = None

            for c in objectSeparators:
                tokenArray = v.split(c, maxsplit=1)
                if  len(tokenArray) > 1:
                    baseToken      = tokenArray[0]
                    tokenModifier  = c + tokenArray[1]
                    break

            if  not baseToken:
                newDict[v] = contextDict[v]

            else:
                newDict[v] = eval(f"contextDict[baseToken]{tokenModifier}")

    #
    return  dicto(newDict, title, indent, sort)


def  sv(  contextDict   :dict       = None,                  
          variableList  :List[str]  = [], 
          title:str=None, indent:str=None, sort:bool=False)  -> None:           #ALIAS
    return  selectVars(contextDict, variableList, title, indent, sort)



#                                                                    -o-
def  selectVarsp(  contextDict   :dict       = None,         
                   variableList  :List[str]  = [], 
                   title:str=None, indent:str=None, sort:bool=False)  -> None:   #PRINT 
    return  print(selectVars(contextDict, variableList, title, indent, sort))

def  svp(  contextDict   :dict       = None,        
           variableList  :List[str]  = [], 
           title:str=None, indent:str=None, sort:bool=False)  -> None:
    return  print(selectVars(contextDict, variableList, title, indent, sort))   #ALIAS PRINT


