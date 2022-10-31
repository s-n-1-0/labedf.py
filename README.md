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

### merged edf file → hdf file
```py
edf2.split_annotations_edf2hdf("./ex.edf","./ex.hdf5",is_groupby=True)
```