#Delete empty text after timestamp in the sbv files
import pandas as pd
import webvtt
from datetime import datetime

#File paths
InOriginal = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP20volunteers.sbv"
InRevised = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP20 Sept21.sbv"
OutFile = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\测试 培训\\Carsen修改前后对比\\EP20组会20190922.xlsx"

data = []
webvtt = webvtt.from_sbv(InOriginal)
for caption in webvtt:
    data.append({'start':datetime.strptime(caption.start,'%H:%M:%S.%f').time(), 
                 'end':datetime.strptime(caption.end,'%H:%M:%S.%f').time(),
                 'old':caption.text})
original = pd.DataFrame(data)
original = original.replace('\n',' ', regex=True)
original = original[['start','end','old']]
#original.head()

data = []
webvtt = webvtt.from_sbv(InRevised)
for caption in webvtt:
    data.append({'start':datetime.strptime(caption.start,'%H:%M:%S.%f').time(), 
                 'end':datetime.strptime(caption.end,'%H:%M:%S.%f').time(),
                 'new':caption.text})
revised = pd.DataFrame(data)
revised = revised.replace('\n',' ', regex=True)
revised = revised[['start','end','new']]
#revised.head()

r = revised.set_index(['start','end'])
o = original.set_index(['start','end'])
output = r.join(o, how='outer')
output = output[['old','new']]
#output[15:26]


#Reset index so that "start" and "end" will appear in the Excel file
df = output.reset_index(level=['start','end'])

# Write to Excel file with formats
writer = pd.ExcelWriter(OutFile, engine='xlsxwriter') #https://xlsxwriter.readthedocs.io/index.html
df.to_excel(writer, sheet_name='Sheet1', index=False)
# Get the xlsxwriter objects from the dataframe writer object.
workbook  = writer.book
worksheet = writer.sheets['Sheet1']
# Set the column width and format.
format1 = workbook.add_format({'text_wrap': True})
worksheet.set_column('A:B', 18)
worksheet.set_column('C:D', 55, format1)

# Close the Pandas Excel writer and output the Excel file.
writer.save()