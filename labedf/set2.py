# %%
import mne
import h5py

def merge_set2hdf(edf_path:str,
    export_path:str,
    labels:list[str],
    marker_names:list[str] = ["Marker"],
    is_overwrite:bool = False,
    is_groupby:bool = False):
    """Split the edf file by annotation and save it in the hdf file.
     Args:
        edf_path : read edf path
        export_path : write hdf path
        is_overwrite : overwrite the edf file
        is_groupby : grouping
    """

    epochs = mne.io.read_epochs_eeglab(edf_path)
    with h5py.File(export_path, mode='r+' if is_overwrite else 'w') as f:
        def write_hdf(marker_name:str,label:str):
            data = epochs.get_data(item=f"{marker_name}__{label}")
            ann_group = f.require_group("/annotations")
            if is_groupby:
                for idx in range(data.shape[0]):
                    local_group = ann_group.require_group("./" + marker_name)
                    counter = local_group.attrs.get("count")
                    counter = 0 if counter is None else counter + 1
                    local_group.attrs["count"] = counter
                    d = local_group.create_dataset(f"{counter}",data[idx,:,:].shape,data=data[idx,:,:])
                    d.attrs["label"] = label
            else:
                for idx in range(data.shape[0]):
                    d = ann_group.create_dataset(f"{idx}.{marker_name}",data[idx,:,:].shape,data=data[idx,:,:])
                    d.attrs["label"] = label
        for marker_name in marker_names:
            for label in labels:
                write_hdf(marker_name,label)