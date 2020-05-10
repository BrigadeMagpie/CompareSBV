Programming support for the translation projects by The Magpie Bridge Brigage

Project homapage https://liberapay.com/ZHZSubbers/


`CompareSBV` repository compares YouTube sbv files and outputs an Excel spreasheet.


![Sample output in the `resource` folder](https://github.com/BrigadeMagpie/CompareSBV/blob/master/resource/Comparing3SBV.png)

## Instructions
```
pip install -r requirements.txt
```

### Run using command line
```
python .\src\compare.py -o .\tmp\EP21Outfile.xlsx -f .\docs\EP21Chinese.sbv .\docs\EP21Volunteers.sbv .\docs\EP21Carsen.sbv
```
```
usage: compare.py [-h] [-f foreign_file] [-o out_file] [-c config_file]
                  [--timeline-only]
                  [original_file] [revised_file]
```

### Run using configuration file
```
python .\src\compare.py -c .\src\paths.py
```

#### Sample configuration file
```
ORIGINAL_FILE = "C:\\Users\\...\\docs\\EP21Volunteers.sbv"
REVISED_FILE = "C:\\Users\\...\\docs\\EP21Carsen.sbv"
CHINESE_FILE = "C:\\Users\\...\\docs\\EP21Chinese.sbv" # Optional
OUT_FILE = "C:\\Users\\...\\resource\\EP21Output.xlsx"
```