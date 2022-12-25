# %%
import pyedflib
from typing import Any, Optional
from .utilities import edf
import numpy as np
import h5py
from typing import Callable
def split_annotations_edf2hdf(edf_path:str,
    export_path:str,
    is_overwrite:bool = False,
    is_groupby:bool = False,
    annotation_filter_func:Optional[Callable[[str],bool]] = None,
    label_filter_func:Optional[Callable[[str],bool]] = None,
    before_preprocessing_func:Optional[Callable[[list[np.ndarray]],Any]] = None,
    split_signals_func:Optional[Callable[[Any,edf.GetAnnotationType,Optional[edf.GetAnnotationType]],np.ndarray]] = None,
    after_preprocessing_func:Callable[[np.ndarray,str],np.ndarray] = None,
    end_marker_name:Optional[str] = "__End__"):
    """Split the edf file by annotation and save it in the hdf file.
     Args:
        edf_path : read edf path
        export_path : write hdf path
        is_overwrite : overwrite the edf file
        is_groupby : grouping
        annotation_filter_func(function[[str],bool]?) : annotation filter
        label_filter_func(function[[str],bool]?) : label filter
        before_preprocessing_func(function?) : before preprocessing function (split_signals_func must also be used when changing the signal length)
        split_signals_func(function?) : signal split function
        after_preprocessing_func(function[[signals,label],ndarray]?) : Preprocess the signals split by annotations. ndarray : ch × annotation range 
        end_marker_name(str?) : annotation of marker_name end time
    """
    with pyedflib.EdfReader(edf_path) as edf_reader:
        signals = edf.get_all_signals(edf_reader)
        if before_preprocessing_func is not None:
            signals = before_preprocessing_func(signals)
        # simple type check(np.ndarray or list[np.ndarray])
        common_attrs = {}
        if isinstance(signals,np.ndarray) or \
           (isinstance(signals,list) and isinstance(signals[0],np.ndarray) and [type(s) for s in signals].count(type(signals[0])) == len(signals)):
            signals = np.array(signals)
            common_attrs = {
            "presplit_mean":np.mean(signals,axis=1),
            "presplit_std" :np.std(signals,axis=1)
            }
        annotations =  edf.get_annotations(edf_reader)
        split_signals:list[tuple[str,np.ndarray,str,dict]] = [] #[(annotation name,signal,label,attrs)]
        for idx,ann in enumerate(annotations):
            next_ann:Optional[edf.GetAnnotationType] = annotations[idx + 1] if idx + 1 < len(annotations) else None
            ann_name,ann_time,_,ann_idx = ann
            if ann_name == end_marker_name:
                continue
            split_ann_name = ann_name.split("_")
            ann_group_name = "_".join(split_ann_name[:-1]) if len(split_ann_name) > 1 else ann_name
            label= split_ann_name[-1] if len(split_ann_name) > 1 else ""
            if split_signals_func is None:
                signals = np.array(signals)
                split_signals.append((ann_group_name,signals[:,ann_idx:(next_ann[3] if next_ann is not None else signals.shape[1])],label,common_attrs))
            else:
                s = split_signals_func(signals,ann,next_ann)
                split_signals.append((ann_group_name,s,label,common_attrs))
        if annotation_filter_func is not None:
            split_signals =  [ss for ss in split_signals if annotation_filter_func(ss[0])]
        if label_filter_func is not None:
            split_signals =  [ss for ss in split_signals if label_filter_func(ss[2])]
        if not(after_preprocessing_func is None):
            split_signals = [(ann_name,after_preprocessing_func(ann_signals,label),label,common_attrs) for ann_name,ann_signals,label,common_attrs in split_signals]
    with h5py.File(export_path, mode='r+' if is_overwrite else 'w') as f:
        ann_group = f.require_group("/annotations")
        if is_groupby:
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label,attrs = ann
                local_group = ann_group.require_group("./" + ann_group_name)
                counter = local_group.attrs.get("count")
                counter = 0 if counter is None else counter + 1
                local_group.attrs["count"] = counter
                d = local_group.create_dataset(f"{counter}",ann_signals.shape,data=ann_signals)
                for key in attrs.keys():
                    d.attrs[key] = attrs[key]
                d.attrs["label"] = label

        else:
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label,attrs = ann
                d = ann_group.create_dataset(f"{idx}.{ann_group_name}",ann_signals.shape,data=ann_signals)
                for key in attrs.keys():
                    d.attrs[key] = attrs[key]
                d.attrs["label"] = label
# %%
