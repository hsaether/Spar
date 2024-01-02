# -*- coding: utf-8 -*-

import numpy as np
import SxP as sp
import SparTool as spt

def __init__():
    __all__ = ["parse"]

Ver = 0.4
#Ver 0.2: If |S11| > 1 |S12| = 0
#Ver 0.3: Oufile automatic; Restructure som code into SxP, Prep for Lossy network  
#Ver 0.4: SxP:S12Lossless, converting whole array instead of single freq. 
#         SxP:S12Lossy, converting whole array instead of single freq. 
#         SxP:S12Lossy, adjustment of gain if to high.  

# Usage:
# Update the fs1p link and the fs2p link
# F5
# In shell run:
# toS2P(fs1p, fGain),
# toS2P(fs1p)
# (freq, s1p, Z0) = toS2P(fs1p, fGain)
#

fs1p = r"C:\GitWork\Spar\Data\dummy.s1p"
fGain = r"C:\GitWork\Spar\Data\Gain.s1p"
#fadrv = r"C:\GitWork\Spar\Data\ADRV9008-1.s1p"
fadrv_orx = r"C:\GitWork\Spar\Data\ADRV9009_ORX.s1p"
fadrv_rx = r"C:\GitWork\Spar\Data\ADRV9009_RX.s1p"
fadrv_tx = r"C:\GitWork\Spar\Data\ADRV9009_TX.s1p"

fadl5904 = r"G:/My Drive/Sim/Slib/PwrDetector/ADL5904_S11_DEEMBED.S1P"

def toS2P(fileS1P, fileGain = "", outFormat = 'MA', adrv:bool=False):
    # fileGain = "": Lossless (|S21| < 1)  
    # Outformat = 'RI', 'MA', 'DB'
    
    # Finding nr of ports from filename extension    
    ports = sp.nrOfPorts(fileS1P, False)
    if(ports != 1):
        raise ValueError('Error: Input file must be one port')

    if(fileGain != ""):
        ports = sp.nrOfPorts(fileGain, False)
        if(ports != 1):
            raise ValueError('Error: Input file must be one port')
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
    if adrv:
        # adrv specific conversion
        S11 = s1p[:,0]
        Zin = spt.S11ToZin(S11, Z0)
        S11_2 = spt.ZinToS11(Zin/2)
        s1p = np.expand_dims(S11_2,axis=1)

    if (lossless == False):
        # Using Gain file, interpolating to freq samples
        (freqG, s1pG_, Z0G) = sp.parse(fileGain)
        if(Z0 != Z0G):
            raise ValueError('Error: Z0 must be equal')
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
        if (lossless):
            s2 = sp.SLossless(freq, s1p[:,0])
        else:
            s2 = sp.SLossy(freq, s1p[:,0], s1pG)
        for i in range(len(freq)):
            f1 =freq[i]
            sline = '{0:10.0f} '.format(f1) + sp.SparToLine(s2[i], outFormat)
            #print(sline)
            f.write(sline + '\n')

    except IOError:
        print("Error: IOError writing output file")
        return(freq, s1p, Z0)
    finally:
        f.close()
    return(freq, s1p, Z0)

def adrv9008(fileS1P, outFormat = 'MA'):
    '''
        ADRV 9008/9009 has balanced ports and requires special conversion.
        S11 is converted to Z and converted back divided by 2
    '''
    # Outformat = 'RI', 'MA', 'DB'
    
    # Finding nr of ports from filename extension    
    ports = sp.nrOfPorts(fileS1P, False)
    if(ports != 1):
        raise ValueError('Error: Input file must be one port')
        
    # Output s2p file
    index = fileS1P.rfind(".")
    fileS2P = fileS1P[:index] + ".s2p"
    print("Output file: " + fileS2P)

    (freq, s1p, Z0) = sp.parse(fileS1P)

    try:        
        # adrv specific conversion
        S11 = s1p[:,0]
        Zin = spt.S11ToZin(S11, Z0)
        S11_2 = spt.ZinToS11(Zin/2)

        f = open(fileS2P, "w")
        f.write("! S1P to S2P converted from file: " + fileS1P + "\n")
        f.write("! Spar Program version " + str(Ver) + "\n")
        f.write("# HZ S " + outFormat + " R " + str(Z0) + "\n")
        i = 0
        s2 = sp.SLossless(freq, S11_2)
        for i in range(len(freq)):
            f1 =freq[i]
            sline = '{0:10.0f} '.format(f1) + sp.SparToLine(s2[i], outFormat)
            #print(sline)
            f.write(sline + '\n')

    except IOError:
        print("Error: IOError writing output file")
        return(freq, s1p, Z0)
    finally:
        f.close()
    return(freq, S11_2, Z0)




#toS2P(fs1p, fGain)
#toS2P(fs1p)
#toS2P(fadl5904)

padrv = r"C:\GitWrk\Spar\Data\ADRV9009"
#toS2P(padrv + "_ORX.s1p", padrv + "_ORX_G.s1p", adrv=True)
#toS2P(padrv + "_TX.s1p", padrv + "_TX_G.s1p", adrv=True)
#toS2P(padrv + "_RX.s1p", padrv + "_RX_G.s1p", adrv=True)
#toS2P(padrv + "_TX.s1p", adrv=True)
#toS2P(padrv + "_RX.s1p", adrv=True)
toS2P(padrv + "_ORX.s1p", adrv=True)
#adrv9008(fadrv_rx)
#adrv9008(fadrv_tx)
