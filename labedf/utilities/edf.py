import pyedflib
import math
from typing import Any
from pyclbr import Function
def get_all_signals(edf:pyedflib.EdfReader):
    """
    get all signals
    """
    return [edf.readSignal(idx) for idx,_ in enumerate(edf.getSignalLabels())]

def get_fs(edf:pyedflib.EdfReader,chn=0):
    """
    get sample rate
    """
    return edf.getSignalHeader(chn)['sample_rate'] # = fs
    
def get_annotations(edf:pyedflib.EdfReader):
    """
    get  annotations
    Returns:
       array of tuple(name,time(s),duration,wave index)
    """
    annotations = edf.readAnnotations()
    fs = get_fs(edf)
    rows:list[tuple[str,float,Any,int]] = [(name,time,duration,math.floor(time * fs))for time,duration,name in zip(annotations[0],annotations[1],annotations[2])]
    return rows
def get_channels_length(edf:pyedflib.EdfReader):
    """
    get channels length
    """
    return len(edf.getSignalHeaders())
def copy(redf:pyedflib.EdfReader,copy_path:str,copied_func:Function = None):
    """
    edf file copy
    """
    ch = get_channels_length(redf)
    with pyedflib.EdfWriter(copy_path,ch) as wedf:
        header = redf.getHeader()
        header["birthdate"] = ""
        annos = redf.readAnnotations()
        wedf.setHeader(header)
        wedf.setSignalHeaders(redf.getSignalHeaders())
        wedf.writeSamples(get_all_signals(redf))
        for i,_ in enumerate(annos[0]):
            wedf.writeAnnotation(annos[0][i],annos[1][i],annos[2][i])
        if not (copied_func is None):
            copied_func(redf,wedf)
        wedf.close()
    return ch