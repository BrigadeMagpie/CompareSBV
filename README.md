Programming support for the translation projects by The Magpie Bridge Brigage

Project homapage https://magpiebridgebrigade.cn/


`CompareSBV` repository compares YouTube sbv files and outputs an Excel spreasheet.


![Sample output in the `resource` folder](/resource/Comparing3SBV.png?raw=true)

## Instructions
```
pip install -r requirements.txt
```

## Usage
```
usage: compare.py [-h] [-c CONFIG_FILE] [-o OUT_FILE] [-f {review,database}]
                  [-nd]
                  [FROM_FILE] [TO_FILE] [REF_FILE]
```

### Run using configuration file
See .\config\config.py for sample configuration
```
python .\src\compare.py -c .\config\config.py
```

### Run using command line
```
python .\src\compare.py -o .\tmp\EP21Outfile.xlsx .\docs\EP21Volunteers.sbv .\docs\EP21Carsen.sbv .\docs\EP21Chinese.sbv

python .\src\compare.py -o .\tmp\EP21OutfileNoDiff.xlsx .\docs\EP21Chinese.sbv .\docs\EP21Carsen.sbv --no-diff

python .\src\compare.py -o .\tmp\EP21Outfile.csv .\docs\EP21Volunteers.sbv .\docs\EP21Carsen.sbv -f database
```
