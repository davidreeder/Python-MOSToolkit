#                                                                        -o--
"""
    MOSClass.py

    Helpful classes.


    CLASSES--
        StringEnum

"""
#---------------------------------------------------------------------
#     Copyright (C) David Reeder 2021.  python@mobilesound.org
#     Distributed under the Boost Software License, Version 1.0.
#     (See ./LICENSE_1_0.txt or http://www.boost.org/LICENSE_1_0.txt)
#---------------------------------------------------------------------

version  :str  = "0.2"   #RELEASE



#----------------------------------------- -o--
# Modules.

from enum import Enum




#----------------------------------------- -o--
# Classes.

class  StringEnum(Enum):
    """
    Use StringEnum to define an Enum class whose attributes have string values.
    """

    def  __repr__(self):
        return  '<%s.%s>' % (self.__class__.__name__, self.name)

#ENDCLASS -- StringEnum()



