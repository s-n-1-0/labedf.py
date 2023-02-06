# %%
from typing import Callable
import numpy as np
import mne
import h5py

def merge_set2hdf(set_path:str,
    export_path:str,
    marker_names:list[str] = ["Marker"],
    labels:list[str] = [],
    is_overwrite:bool = False,
    is_groupby:bool = False,
    preprocessing_func:Callable[[np.ndarray,str],np.ndarray] = None):
    """ EEGLAB(.set) -> HDF Dataset(.h5)
     Args:
        set_path : read set path
        export_path : write hdf path
        is_overwrite : overwrite the edf file
        is_groupby : grouping
        preprocessing_func(function[[signals,label],ndarray]?) : Processes each segmented data. ndarray : ch × annotation range
    """

    epochs = mne.io.read_epochs_eeglab(set_path)
    with h5py.File(export_path, mode='r+' if is_overwrite else 'w') as f:
        def write_hdf(marker_name:str,label:str):
            data = epochs.get_data(item=f"{marker_name}__{label}" if label != "" else marker_name)
            ann_group = f.require_group("/annotations")
            for idx in range(data.shape[0]):
                data_ch = data[idx,:,:]
                if not(preprocessing_func is None):
                    data_ch = preprocessing_func(data_ch,label)
                if is_groupby:
                        local_group = ann_group.require_group("./" + marker_name)
                        counter = local_group.attrs.get("count")
                        counter = 0 if counter is None else counter + 1
                        local_group.attrs["count"] = counter
                        d = local_group.create_dataset(f"{counter}",data_ch.shape,data=data_ch)
                        d.attrs["label"] = label
                else:
                        d = ann_group.create_dataset(f"{idx}.{marker_name}",data_ch.shape,data=data_ch)
                        d.attrs["label"] = label
        for marker_name in marker_names:
            if len(labels) > 0:
                for label in labels:
                    write_hdf(marker_name,label)
            else:
                write_hdf(marker_name,"")