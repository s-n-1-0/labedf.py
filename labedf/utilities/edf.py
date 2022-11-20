from numpy import ndarray
import pyedflib
import math
from typing import Any, Callable,Union
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


GetAnnotationType = tuple[str,float,Any,int]
"""
tuple(name,time(s),duration,wave index)
"""


def get_annotations(edf:pyedflib.EdfReader):
    """
    get  annotations
    Returns:
       array of tuple(name,time(s),duration,wave index)
    """
    annotations = edf.readAnnotations()
    fs = get_fs(edf)
    rows:list[GetAnnotationType] = [(name,time,duration,math.floor(time * fs))for time,duration,name in zip(annotations[0],annotations[1],annotations[2])]
    return rows
def get_channels_length(edf:pyedflib.EdfReader):
    """
    get channels length
    """
    return len(edf.getSignalHeaders())
CopiedFuncType = Callable[[pyedflib.EdfReader,pyedflib.EdfWriter,list[ndarray]],Union[list[ndarray],None]]
def copy(redf:pyedflib.EdfReader,copy_path:str,copied_func:Union[CopiedFuncType,None] = None):
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
        all_signals = get_all_signals(redf)
        
        for i,_ in enumerate(annos[0]):
            wedf.writeAnnotation(annos[0][i],annos[1][i],annos[2][i])
        if not (copied_func is None):
            _all_signals = copied_func(redf,wedf,all_signals)
            if not (_all_signals is None):
                all_signals = _all_signals
        wedf.writeSamples(all_signals)
        wedf.close()
    return ch