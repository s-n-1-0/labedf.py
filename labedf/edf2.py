# %%
import pyedflib
from typing import Optional
from .utilities import edf
import numpy as np
import h5py
from typing import Callable
def split_annotations_edf2hdf(edf_path:str,
    export_path:str,
    is_overwrite:bool = False,
    is_groupby:bool = False,
    filters:list[str] = None,
    preprocessing_func:Optional[Callable[[list[np.ndarray]],list[np.ndarray]]] = None,
    end_marker_name:Optional[str] = "__End__"):
    """Split the edf file by annotation and save it in the hdf file.
     Args:
        edf_path : read edf path
        export_path : write hdf path
        is_overwrite : overwrite the edf file
        is_groupby : grouping
        filters : annotation filters
        preprocessing_func(function) : preprocessing function
        end_marker_name(str?) : annotation of marker_name end time
    """
    with pyedflib.EdfReader(edf_path) as edf_reader:
        signals = edf.get_all_signals(edf_reader)
        if preprocessing_func is not None:
            signals = preprocessing_func(signals)
        signals = np.array(signals)
        annotations =  edf.get_annotations(edf_reader)
        split_signals = [] #[(annotation name,signal,label)]
        for idx,ann in enumerate(annotations):
            ann_name,ann_time,_,ann_idx = ann
            if ann_name == end_marker_name:
                continue
            split_ann_name = ann_name.split("_")
            ann_group_name = "_".join(split_ann_name[:-1]) if len(split_ann_name) > 1 else ann_name
            label= split_ann_name[-1] if len(split_ann_name) > 1 else ""
            split_signals.append((ann_group_name,signals[:,ann_idx:(annotations[idx + 1][3] if idx + 1 < len(annotations) else signals.shape[1])],label))
        if not(filters is None):
            split_signals =  [ss for ss in split_signals if ss[0] in filters]
    with h5py.File(export_path, mode='r+' if is_overwrite else 'w') as f:
        ann_group = f.require_group("/annotations")
        if is_groupby:
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label = ann
                local_group = ann_group.require_group("./" + ann_group_name)
                counter = local_group.attrs.get("count")
                counter = 0 if counter is None else counter + 1
                local_group.attrs["count"] = counter
                d = local_group.create_dataset(f"{counter}",ann_signals.shape,data=ann_signals)
                d.attrs["label"] = label

        else:
            for idx,ann in enumerate(split_signals):
                ann_group_name,ann_signals,label = ann
                d = ann_group.create_dataset(f"{idx}.{ann_group_name}",ann_signals.shape,data=ann_signals)
                d.attrs["label"] = label
# %%
