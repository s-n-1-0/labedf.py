# %%
import pyedflib
from .utilities import edf
import numpy as np
import h5py
def split_annotations_edf2hdf(edf_path:str,export_path:str,filters:list[str] = None,is_groupby:bool = False):
    """Split the edf file by annotation and save it in the hdf file.
    """
    with pyedflib.EdfReader(edf_path) as edf_reader:
        signals = np.array(edf.get_all_signals(edf_reader))
        annotations =  edf.get_annotations(edf_reader)
        split_signals = []
        for idx,ann in enumerate(annotations):
            ann_name,ann_time,_,ann_idx = ann
            split_signals.append((ann_name,signals[:,ann_idx:(annotations[idx + 1][3] if idx + 1 < len(annotations) else signals.shape[1])]))
        if not(filters is None):
            split_signals =  [ss for ss in split_signals if ss[0] in filters]
    with h5py.File(export_path, mode='w') as f:
        ann_group = f.create_group("/annotations")
        if is_groupby:
            counts = {}
            for idx,ann in enumerate(split_signals):
                ann_name,ann_signals = ann
                j = 0
                if ann_name in counts:
                    j = counts[ann_name] + 1
                    counts[ann_name] = j
                else:
                    counts[ann_name] = 0

                local_group = ann_group.require_group("./" + ann_name)
                local_group.create_dataset(f"{j}",ann_signals.shape,data=ann_signals)
        else:
            for idx,ann in enumerate(split_signals):
                ann_name,ann_signals = ann
                ann_group.create_dataset(f"{idx}.{ann_name}",ann_signals.shape,data=ann_signals)
# %%