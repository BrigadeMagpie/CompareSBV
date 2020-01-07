#Install Tesseract and make sure it is in your $PATH
    #https://github.com/tesseract-ocr/tesseract/wiki
    #Open Environment Variable, add the folder path C:\Program Files\Tesseract-OCR to Path
#!pip install videocr
    #https://pypi.org/project/videocr/
    #https://github.com/apm1467/videocr
from videocr import get_subtitles
if __name__ == '__main__':  # This check is mandatory for Windows.
    print(get_subtitles("C:\\Users\\jwei06\\Downloads\\ChinaNowEP01.mp4",
                        lang='chi_sim', sim_threshold=70, conf_threshold=65))
