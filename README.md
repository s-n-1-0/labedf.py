# labedf.py
 Merge the lab.js csv file and the edf file.

## Installation
`
pip install labedf
`

# How to Use
```py
from labedf import csv2,edf2,set2
```
### lab.js csv + edf file → merged edf file
```py
csv2.merge_csv2edf("./xxx.edf","./labjs.csv","./ex.edf")
```
#### Optional Arguments
+ https://github.com/s-n-1-0/labedf.py/blob/main/labedf/csv2.py
### merged edf file → hdf file
```py
edf2.split_annotations_edf2hdf("./ex.edf","./ex.hdf5",is_groupby=True)
```
#### Optional Arguments
+ is_groupby : GROUP BY (default value = False)
+ is_overwrite : overwite a file(default value = False)
+ before_preprocessing_func : preprocessing function
    + type : list[ndarray] -> (list[ndarray] | Any)
+ after_preprocessing_func(function?) : Preprocess the signals split by annotations. ndarray
    + type : [signals:ndarray, label:str] -> ndarray
+ others
    + https://github.com/s-n-1-0/labedf.py/blob/main/labedf/edf2.py

### merged set file → hdf file
.set(EEGLAB) files can be combined into hdf file.
```py
set2.merge_set2hdf("./merged_0.set", #input path
                    "./ex.h5", #export path
                    labels = ["0","1"],
                    is_overwrite = False, # hdf overwrite
                    is_groupby = True) # group by
```
#### Optional Arguments
+ https://github.com/s-n-1-0/labedf.py/blob/main/labedf/set2.py