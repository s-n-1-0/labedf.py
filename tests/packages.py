# %%
from pickle import TRUE
import pyedflib
import labcsv
import numpy as np
import h5py
import mne
# %% print used libraries
lst = [pyedflib,labcsv,np,h5py,mne]
replace_key = '\''
is_break = True
txt = "["
for item in lst:
    txt += f"\"{str(item).split(' ')[1].replace(replace_key,'')}>={item.__version__}\","
if not (txt == "["):
    txt = txt[:-1]
txt += "]"
if is_break:
    txt = txt.replace(",",",\n")
print(txt)

# %%
