# %%
import pyedflib
from .utilities import edf
import numpy as np
import h5py
from typing import Callable
def split_annotations_edf2hdf(edf_path:str,export_path:str,filters:list[str] = None,is_groupby:bool = False,preprocessing_annsignals_func:Callable[[np.ndarray],np.ndarray] = None):
    """Split the edf file by annotation and save it in the hdf file.
     Args:
        edf_path : read edf path
        export_path : write hdf path
        filters : annotation filters
        preprocessing_annsignals_func : Preprocess the signals split by annotations. ndarray : ch × annotation range 
    """
    with pyedflib.EdfReader(edf_path) as edf_reader:
        signals = np.array(edf.get_all_signals(edf_reader))
        annotations =  edf.get_annotations(edf_reader)
        split_signals = [] #[(annotation name,signal,label)]
        for idx,ann in enumerate(annotations):
            ann_name,ann_time,_,ann_idx = ann
            split_ann_name = ann_name.split("_")
            ann_group_name = "_".join(split_ann_name[:-1]) if len(split_ann_name) > 1 else ann_name
            label= split_ann_name[-1] if len(split_ann_name) > 1 else ""
            split_signals.append((ann_group_name,signals[:,ann_idx:(annotations[idx + 1][3] if idx + 1 < len(annotations) else signals.shape[1])],label))
        if not(filters is None):
            split_signals =  [ss for ss in split_signals if ss[0] in filters]
        if not(preprocessing_annsignals_func is None):
            split_signals = [(ann_name,preprocessing_annsignals_func(ann_signals),label) for ann_name,ann_signals,label in split_signals]
    with h5py.File(export_path, mode='w') as f:
        ann_group = f.create_group("/annotations")
        if is_groupby:
            counts = {}
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label = ann
                j = 0
                if ann_group_name in counts:
                    j = counts[ann_group_name] + 1
                    counts[ann_group_name] = j
                else:
                    counts[ann_group_name] = 0

                local_group = ann_group.require_group("./" + ann_group_name)
                d = local_group.create_dataset(f"{j}",ann_signals.shape,data=ann_signals)
                d.attrs["label"] = label
        else:
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label = ann
                d = ann_group.create_dataset(f"{idx}.{ann_group_name}",ann_signals.shape,data=ann_signals)
                d.attrs["label"] = label
# %%
