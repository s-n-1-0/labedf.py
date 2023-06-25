# labedf.py
 Merge the lab.js csv file and the edf file.  
Finally, an EDF file is generated with lab.js annotations written.

## Installation
`
pip install labedf
`

# How to Use
```py
from labedf import merge_edf_csv
```

### lab.js csv + edf file → merged edf file
```py
merge_edf_csv("./xxx.edf","./labjs.csv","./export.edf")
```

#### Optional Arguments
+ https://github.com/s-n-1-0/labedf.py/blob/main/labedf/edf_csv.py


### Merged EDF File → HDF File, Merged SET File → HDF File
These functions were removed because they were not the original purpose of the library.

