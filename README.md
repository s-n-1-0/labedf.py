# labedf.py
 Merge the lab.js csv file and the edf file.

## Installation
`
pip install labedf
`

# How to Use
```py
from labedf import csv2,edf2
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
    + type : ndarray(ch × annotation range) -> ndarray
+ others
    + https://github.com/s-n-1-0/labedf.py/blob/main/labedf/edf2.py