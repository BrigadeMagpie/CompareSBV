# coding: utf-8

# ` !pip install webvtt-py ` https://github.com/glut23/webvtt-py
# 
# `!pip install XlsxWriter`
# 
# Delete empty text after timestamp in the sbv files. Or try upload to YouTube and download the sbv file again.

import pandas as pd
import numpy as np
import webvtt
from datetime import datetime
from difflib import SequenceMatcher

#Chinese sbv file
InOriginal = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\4509 Templates with Chinese subs\\Empress In The Palace (YouTube Template) - E23 - converted.sbv"

#English translation
InTranslation = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP23Carsen.sbv"

#Revised translation
#InRevised = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP24 CarsenJan11.sbv"
InRevised = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP23 Anaya.sbv"

#Output file
#OutFile = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\测试 培训\\Carsen修改前后对比\\EP24组会.xlsx"
OutFile = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\测试 培训\\Carsen修改前后对比\\EP23CarsenAnaya.xlsx"

def sbv2df(sbv,textCol):
    """ 
    Store (start, end, and text) of each time segment in the sbv file in a row of a pandas dataframe.
    Input args 
        sbv (string): the file path of an sbv file
        textCol (string): the name of the text column
    """
    data = []
    global webvtt
    webvtt = webvtt.from_sbv(sbv)
    for caption in webvtt:
        data.append({'start':datetime.strptime(caption.start,'%H:%M:%S.%f').time(), 
                     'end':datetime.strptime(caption.end,'%H:%M:%S.%f').time(),
                     textCol:caption.text})
    df = pd.DataFrame(data)
    df = df.replace('\n',' ', regex=True)
    df = df[['start','end',textCol]] 
    return df   
original = sbv2df(InOriginal,"Chinese")
translation = sbv2df(InTranslation,"Translation")
revised = sbv2df(InRevised,"Revised")



o = original.set_index(['start','end'])
t = translation.set_index(['start','end'])
r = revised.set_index(['start','end'])
output = t.join(r, how='outer')

# For each time sgegment with the same start time, replace Translation or Revised with the last non-NaN value

lastStart = output.index[0][0]
for index, row in output.iterrows():
    if index[0] != output.index[0][0]:  #not datetime.time(0, 0)
        if index[0] != lastStart: #different start time from last time segment
            lastStart = index[0]
            lastTranslation = row[0]
            lastRevised = row[1]
        elif index[0] == lastStart: #same start time with last time segment
            if pd.isna(row[0]) and ~pd.isna(lastTranslation):
                row[0] = lastTranslation
            if pd.isna(row[1]) and ~pd.isna(lastRevised):
                row[1] = lastRevised


# Clean output (df): drop the rows like the following in the above output
    # 00:02:30.820000	00:02:32.580000
    # 00:02:34.100000	00:02:36.720000
#But keep the rows like 
    # 00:02:25.180000	00:02:28.620000
    # 00:02:26.420000	00:02:29.860000

lastStart = output.index[0][0]
clean=output
for index, row in output.iterrows():
    if index[0] != output.index[0][0]:  #not datetime.time(0, 0)
        if index[0] != lastStart: #different start time from last time segment
            lastStart = index[0]      
            #print("START",index[0],'\n',output.loc[index[0]].shape)  #to find out the pattern in shape
            if output.loc[index[0]].shape[0] == 2:   #one start (index) matches 2 end (index)
                clean.drop((index[0],index[1]), inplace=True)
clean[13:23]


#Calculate word change ratio (0-1) in clean (df)
    #word change ratio (0-1) with 1 indicating most different Revision from Translation 
    #However, 1 is usually due to unmatching timestamps
    #A ratio value over 0.6 (1-ratio<0.4) means the sequences are close matches
clean['WordChange'] =  np.nan
for idx,row in clean.iterrows():
    if pd.isna(row['Translation']):
        row['Translation'] = ''
    if pd.isna(row['Revised']):
        row['Revised'] = ''
    clean.loc[idx,'WordChange'] = 1- SequenceMatcher(None,row['Translation'],row['Revised']) .ratio()
    if clean.loc[idx,'WordChange'] == 0:
        clean.loc[idx,'WordChange'] = None



output = o.join(clean, how='outer')
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
worksheet.set_column('A:B', 12)
worksheet.set_column('C:E', 38, format1)
worksheet.set_column('F1:F1048576', 5)

# Conditional formatting based on word change %
    # https://xlsxwriter.readthedocs.io/working_with_conditional_formats.html
    #colors https://xlsxwriter.readthedocs.io/working_with_colors.html

# Green fill with dark green text.
format2 = workbook.add_format({'bg_color':   '#C6EFCE',
                               'font_color': '#006100'})
# Light red fill with dark red text.
format3 = workbook.add_format({'bg_color':   '#FFC7CE',
                               'font_color': '#9C0006'})

# Light yellow fill with dark yellow text.
format4 = workbook.add_format({'bg_color':   '#FFEB9C',
                               'font_color': '#9C6500'})


worksheet.conditional_format('F1:F1048576', {'type':     'cell',
                                        'criteria': '<',
                                        'value':    0.4,
                                        'format':   format2})

worksheet.conditional_format('F1:F1048576', {'type':     'cell',
                                        'criteria': 'between',
                                        'minimum':  0.4,
                                        'maximum':  0.99,
                                        'format':   format3})

worksheet.conditional_format('F1:F1048576', {'type':     'cell',
                                        'criteria': '>',
                                        'value':    0.99,
                                        'format':   format4})

# Close the Pandas Excel writer and output the Excel file.
writer.save()

