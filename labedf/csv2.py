import os
from numpy import ndarray
import pyedflib
import labcsv
from labcsv import DefaultHeaderName as DHName
from typing import Callable, Optional
from .utilities import edf
def merge_csv2edf(edf_path:str,
                csv_path:str,
                export_path:Optional[str] = None,
                marker_names:list[str] = ["Marker"],
                sync_marker_name:str = "sync",
                marker_offset:tuple[float] = (0,0),
                label_header_name:str = None,
                preprocessing_func:Optional[Callable[[list[ndarray]],list[ndarray]]] = None):
    """
    Write the lab.js sender names to edf as annotations. (Generate a copy file)
    Args:
        edf_path (str): edf file path
        csv_path (str): csv file path
        export_path (str?): output file path. Defaults to None.(None is <edf_path + "-copy">)
        marker_name(str) : filter sender name(= "sender" value)
        sync_marker_name(str) : "response" value to synchronize files (None = 0 index)
        marker_offset(tuple[float,float]) : marker_name time offset (seconds). (start,end)
        label_header_name(str?) : label header name
        preprocessing_func(function) : preprocessing function
    """
    edf_dir_path = os.path.dirname(edf_path)
    edf_filename_path =  os.path.splitext(os.path.basename(edf_path))[0]
    if export_path is None:
        export_path = f"{edf_dir_path}/{edf_filename_path}_copy.edf"
    edf_reader = pyedflib.EdfReader(edf_path)
    rlab_dtype = {label_header_name:str} if not (label_header_name is None) else None
    rlab = labcsv.read_csv(csv_path,dtype=rlab_dtype)

    edf_annos = edf.get_annotations(edf_reader)
    fs = edf.get_fs(edf_reader)
    senders,responses,time_ends,time_runs = rlab.get_column_list([DHName.SENDER,DHName.RESPONSE,DHName.TIME_END,DHName.TIME_RUN])
    labels = rlab.get_column_values(label_header_name) if not(label_header_name is None) else [None] * len(responses)
    sync_edf_annos = [ea for ea in edf_annos if ea[0] == sync_marker_name]
    sync_lab_annos_indexes = [i for i,r in enumerate(list(responses)) if r == sync_marker_name ]
    if len(sync_edf_annos) != len(sync_lab_annos_indexes):
        raise Exception("Number of sync_marker_name in edf and csv files do not match")
    start_time_count:int = -1
    start_time_end:float = None
    results:list[tuple[str,str,float,float]] = [] # marker,label,exact_time_run,offset_time_end
    for label,sender,res, time_end,time_run in zip(labels,senders,responses,time_ends,time_runs):
        if res == sync_marker_name:
            start_time_count += 1
            start_time_end = time_ends[sync_lab_annos_indexes[start_time_count]]
        if not sender in marker_names:
            continue
        exact_time_run = ((time_run - start_time_end) / 1000.0) + sync_edf_annos[start_time_count][1]
        exact_time_end = ((time_end - start_time_end) / 1000.0) + sync_edf_annos[start_time_count][1]
        start_offset,end_offset = marker_offset
        results.append((sender,label,exact_time_run + start_offset,exact_time_end - exact_time_run - start_offset + end_offset))

    def copied_func(_ ,wedf:pyedflib.EdfWriter,signals:list[ndarray]):
        for _marker_name,label,exact_time,offset_end, in results:
            offset_end_idx = int(offset_end * fs)
            mn = f"{offset_end_idx}__{_marker_name}"
            if not(label is None):
                mn += f"__{label}"
            wedf.writeAnnotation(exact_time,-1,mn)
        if preprocessing_func is not None:
            return preprocessing_func(signals)
        return signals
    edf.copy(edf_reader,export_path,copied_func)
