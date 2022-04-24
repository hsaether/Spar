# -*- coding: utf-8 -*-

import numpy as np
from numpy import pi
import SxP as sp
# simport re

def __init__():
    __all__ = ["parse"]

Ver = 0.3
#Ver 0.2: If |S11| > 1 |S12| = 0
#Ver 0.3: Oufile automatic; Restructure som code into SxP, Prep for Lossy network  

# Usage:
# Update the fs1p link and the fs2p link
# F5
# In shell run:
# toS2P(fs1p, fGain),
# toS2P(fs1p)
# (freq, s1p, Z0) = toS2P(fs1p, fGain)
#

fs1p = r"C:\GitWrk\Spar\Data\dummy.s1p"
fGain = r"C:\GitWrk\Spar\Data\Gain.s1p"

def toS2P(fileS1P, fileGain = "", outFormat = 'MA'):
    # fileGain = "": Lossless (|S21| < 1)  
    # Outformat = 'RI', 'MA', 'DB'
    
    # Finding nr of ports from filename extension    
    ports = sp.nrOfPorts(fileS1P, False)
    if(ports != 1):
        print("Error: Input file must be one port")
        return

    if(fileGain != ""):
        ports = sp.nrOfPorts(fileGain, False)
        if(ports != 1):
            print("Error: Input file must be one port")
            return
        lossless = False
    else:
        lossless = True
        
    # Output s2p file
    index = fileS1P.rfind(".")
    if lossless:
        fileS2P = fileS1P[:index] + ".s2p"
    else:
        fileS2P = fileS1P[:index] + "_G.s2p"
    print("Output file: " + fileS2P)

    (freq, s1p, Z0) = sp.parse(fileS1P)

    if (lossless == False):
        # Using Gain file, interpolating to freq samples
        (freqG, s1pG_, Z0G) = sp.parse(fileGain)
        if(Z0 != Z0G):
            print("Error: Z0 must be equal")
            return
        s1pG = np.interp(freq, freqG, s1pG_[:,0])
    # print(s1pG)    
    # print(freq)
    # print(s1p)
    # print(Z0)

    try:        
        f = open(fileS2P, "w")
        f.write("! S1P to S2P converted from file: " + fileS1P + "\n")
        if(lossless == False):
            f.write("! Using gain file: " + fileGain + "\n")
        f.write("! Spar Program version " + str(Ver) + "\n")
        f.write("# HZ S " + outFormat + " R " + str(Z0) + "\n")
        i = 0
        for f1 in freq:
            s11 = s1p[i,0]
            if (lossless):
                s12 = sp.S12Lossless(f1, s11)
            else:
                s12G = s1pG[i]
                s12 = sp.S12Lossy(f1, s11, s12G)
                # print("s12=" + str(s12) + ", s12G=" + str(s12G))
            sline = '{0:10.0f} '.format(f1) + sp.SparToLine([s11, s12, s12, s11], outFormat)
            #print(sline)
            f.write(sline + '\n')
            i = i + 1

    except IOError:
        print("Error: IOError writing output file")
        return(freq, s1p, Z0)
    finally:
        f.close()

    return(freq, s1p, Z0)

toS2P(fs1p, fGain),
