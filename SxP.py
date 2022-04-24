# -*- coding: utf-8 -*-

import numpy as np
from numpy import pi
import re

def __init__():
    __all__ = ["parse"]

#Ver 0.2: If |S11| > 1 |S12| = 0
#Ver 0.3: SxP:parse, Fixed freq_mult, Added nrOfPorts, S12Lossless

# import SxP as sxp
# (f,s1p,z) = sxp.parse(r"C:\Users\hsaether\OneDrive\Source\repos\Spar\Data\Sma-3p9-att0.0.s1p")

def parse(filename, show=True):
    # Declarations
    ports = 0
    freq = np.array([])
    Spar = np.array([[]])
    Data = np.array([[]])
    Z = 50
    freq_unit = "HZ"
    freq_mult = 1
    type = "S"
    format ="MA"
    
    # Check ports S1P, S2P
    ports = nrOfPorts(filename, False)
    if(ports == 0):
        return(freq, Spar, Z)

    try:
        f = open(filename, "r")
    except:
        print("SxP:parse, Could not open filename")
        return(freq, Spar, Z)

    first = True
    try:
        for x in f:
            if not x:
                continue
            if(x[0] == '!'):
                # Comment
                continue
            if(x[0] == '#'):
                # Format, <FREQ_UNITS>  <TYPE>  <FORMAT>  <Rn>
                header = re.split("\s+", x)
                freq_unit = header[1]
                if (str.lower(freq_unit) == "hz"):
                    freq_mult = 1
                elif (str.lower(freq_unit) == "khz"):
                    freq_mult = 1e3
                elif (str.lower(freq_unit) == "mhz"):
                    freq_mult = 1e6
                elif (str.lower(freq_unit) == "ghz"):
                    freq_mult = 1e9
                else:
                    print("SxP:parse, Unrecognized frequency unit, default=Hz")
                type = header[2]
                format = header[3]
                Z = int(header[5])
                print(freq_unit + " " + type + " " + format + " " + str(Z))
            else:
                # Data
                d = parseLine(x)
                if not d:
                    continue
                freq = np.append(freq, [d[0]*freq_mult])
                sp = dataToSpar(d[1:], format, ports)
                if first:    
                    Spar = np.append(Spar, [sp], 1)
                    first = False
                else:
                    Spar = np.append(Spar, [sp], 0)
    except:
        print("SxP:parse, Could not extract data from file")
        return(freq, Spar, Z)
    finally:
        f.close()

    records = Spar.shape
    print("Records: " + str(records[0]))
    return(freq, Spar, Z)

def nrOfPorts(filename, show=True):
    ports = 0
    try:
        s1 = re.findall("[sS][1-9][pP]$", filename)
        s2 = re.findall("[0-9]", s1[0])
        ports = int(s2[0])
        if show:
            print("Nr of ports: " + str(ports))
    except:
        print("SxP:nrOfPorts, Could not find nr of ports from extension") 
    return(ports)

def parseLine(line, show=True):
    data = []
    l1 = re.sub("^\s+","", line)
    line = re.sub("\s+$","", l1)
    d = re.split("\s+", line)
    for f in d:
        if not f:
            continue
        data.append(float(f))
    return(data)

def dataToSpar(data, format, ports):
    sp = np.array([])
    for i in range(0, ports**2):
        if str.upper(format) == "RI":
            sxx = complex(data[i*2], data[i*2+1])
        elif str.upper(format) == "MA":
            sxx = complex(data[i*2]*np.cos(data[i*2+1]*pi/180), data[i*2]*np.sin(data[i*2+1]*pi/180))
        elif str.upper(format) == "DB":
            sxx = complex(10 **(data[i*2]/20)*np.cos(data[i*2+1]*pi/180), 10 **(data[i*2]/20)*np.sin(data[i*2+1]*pi/180))
        sp = np.append(sp,  [sxx])    
    return(sp)

def SparToLine(spar, format):
    line = ""
    for sxx in spar:
        if str.upper(format) == "RI":
            s1 = np.real(sxx)
            s2 = np.imag(sxx)
        elif str.upper(format) == "MA":
            s1 = np.abs(sxx)
            s2 = np.angle(sxx, True)
        elif str.upper(format) == "DB":
            s1 = 20*np.log10(np.abs(sxx))
            s2 = np.angle(sxx, True)
        line = line + ' {0:13.8f} {1:13.8f}'.format(s1, s2)

    return(line)

def S12Lossless(f, s11):
    # Conversion
    # Symmetry S11 = S22
    # Resiprocial S12 = S21
    # Lossless |S11|^2 + |S12|^2 = 1
    # p12 + p21 - (p11 + p22) = pi
    if (np.abs(s11) > 1):
        print("Warning: Freq: " + str(np.round(f/1000000,1)) + "MHz, |S11|>1: " + str(np.round(np.abs(s11),3)) )
        abs12 = 0
    else:
        abs12 = np.sqrt(1-np.abs(s11)**2)
        angle12 = -pi/2 + np.angle(s11)
        s12 = complex(abs12 * np.cos(angle12), abs12 * np.sin(angle12))
    return(s12)

def S12Lossy(f, s11, s12G):
    # Conversion
    # Symmetry S11 = S22
    # Resiprocial S12 = S21
    # Lossy |S11|^2 + |S12|^2 < 1 = s12G 
    # p12 + p21 - (p11 + p22) = pi
    if (np.abs(s11) > 1):
        print("Warning: Freq: " + str(np.round(f/1000000,1)) + " MHz, S11|>1: " + str(np.round(np.abs(s11),3)) )
        abs12 = 0
    else:
        abs12 = np.sqrt(1-np.abs(s11)**2)
    abs12G = np.abs(s12G)
    if abs12 < abs12G:
        print("Warning: Freq: " + str(np.round(f/1000000,1)) + " MHz, Lossless |S12|< S12G: " + str(np.round(abs12,3)) +" < " + str(np.round(abs12G,3)) )
    else:   
        abs12 = abs12G            
    angle12 = -pi/2 + np.angle(s11)
    s12 = complex(abs12 * np.cos(angle12), abs12 * np.sin(angle12))
    return(s12)


