# -*- coding: utf-8 -*-

import numpy as np
from numpy import double

def __init__():
    __all__ = ["SSerialZ", "S11ToZin", "ZinToS11"]

ver = 0.1
#Ver 0.1:   Added SSerialZ, S11toZin, ZinToS11

# Usage
# import SparTool as spt

def SSerialZ(Z : np.array, Z0 : double = 50) -> np.array:
    # Serial Z to s parameters
    # Conversion:
    # Symmetry S11 = S22
    # Resiprocial S12 = S21
    # S11 = Z/(2Z0+Z)
    # S12 = 2Z0/(2Z0+Z)
    # Returns s2 parameters

    s2 = np.empty([0,4])
    for i in range(len(Z)):
        z1 = Z[i]
        s11 = z1/(2*Z0+Z)
        s12 = 2*Z0/(2*Z0+Z)
        s2 = np.vstack([s2, [s11, s12, s12, s11]])
    return(s2)

def S11ToZin(S11 : np.array, Z0 : double = 50) -> np.array:
    # S11 to Zin conversion
    # Conversion:
    # Zin = Z0*(1+s11)/(1-s11)
    # Returns Zin
    Zin = Z0 * (1+S11) / (1-S11)
    return(Zin)

def ZinToS11(Zin : np.array, Z0 : double = 50) -> np.array:
    # Zin to S11 conversion
    # Conversion:
    # S11 = (Zin-Z0)/(Zin+Z0)
    # Returns S11
    S11 = (Zin-Z0) / (Zin+Z0)
    return(S11)
