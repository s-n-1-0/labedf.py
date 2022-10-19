import os
import pyedflib
import labcsv
from labcsv import DefaultHeaderName as DHName
from typing import Optional
from .utilities import edf
import numpy as np
def merge_csv2edf(edf_path:str,csv_path:str,export_path:Optional[str] = None,marker_name:str = "Marker",end_marker_name:Optional[str]="__End__",end_marker_offset:float = 0,label_header_name:str = None):
    """
    Write the lab.js sender names to edf as annotations. (Generate a copy file)
    Args:
        edf_path (str): edf file path
        csv_path (str): csv file path
        export_path (str?): output file path. Defaults to None.(None is <edf_path + "-copy">)
        marker_name(str) : filter sender name(= "sender" value)
        end_marker_name(str?) : annotation of marker_name end time
        end_marker_offset(float) : marker_name end time offset (seconds)
        label_header_name(str?) : label header name
    """
    edf_dir_path = os.path.dirname(edf_path)
    edf_filename_path =  os.path.splitext(os.path.basename(edf_path))[0]
    if export_path is None:
        export_path = f"{edf_dir_path}/{edf_filename_path}_copy.edf"
    edf_reader = pyedflib.EdfReader(edf_path)

    #make lab.js annotaions
    annos = edf.get_annotations(edf_reader)
    rlab_dtype = {label_header_name:str} if not (label_header_name is None) else None
    rlab = labcsv.read_csv(csv_path,dtype=rlab_dtype)
    start_time_end = rlab.get_column_values(DHName.TIME_END)[0]
    senders = rlab.get_column_values(DHName.SENDER)
    marker_indexes = np.where(senders == marker_name)[0]
    time_ends = rlab.get_column_values(DHName.TIME_END)[marker_indexes]
    time_runs = rlab.get_column_values(DHName.TIME_RUN)[marker_indexes]
    offset_time_runs = ((time_runs - start_time_end) / 1000.0) + annos[1][1]
    offset_time_ends = ((time_ends - start_time_end) / 1000.0) + annos[1][1]
    labels = rlab.get_column_values(label_header_name)[marker_indexes] if not(label_header_name is None) else [None for _ in range(len(marker_indexes))]
    def copied_func(redf:pyedflib.EdfReader,wedf:pyedflib.EdfWriter):
        for otr,ote,l in zip(offset_time_runs,offset_time_ends,labels):
            mn = marker_name
            if not(l is None):
                mn += f"_{l}"
            wedf.writeAnnotation(otr,-1,mn)
            if not (end_marker_name is None):
                wedf.writeAnnotation(ote + end_marker_offset,-1,end_marker_name)
    edf.copy(edf_reader,export_path,copied_func)
