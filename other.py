import PyPDF2 
import textract as t
import re
import sys
import time
from PyPDF2 import PdfFileWriter, PdfFileReader


##from nltk.tokenize import word_tokenize
##from nltk.corpus import stopwords
#write a for-loop to open many files -- leave a comment if you'd #like to learn how


if len(sys.argv)==1:
    #filename = '/home/hvt5kor/osd3_share/Connectivity_FI/most_BTSet_fi.pdf'
    filename ='/home/gdi2kor/Desktop/Files/OCR/share/f.PNG'
    #filename ='/home/hvt5kor/server_backup/OCR_test/test2.pdf'
else :
    
    filename =sys.argv[1]
    print ("here : ",filename)
    

#open allows you to read the file
punctuations = '''![]{};'"\>./?@#$%^&_~'''
pdfFileObj = open(filename,'rb')

#The pdfReader variable is a readable object that will be parsed

pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

#discerning the number of pages will allow us to parse through all #the pages

num_pages = pdfReader.numPages
count = 0
text = ""


#The while loop will read each page
while count < num_pages:
    pageObj = pdfReader.getPage(count)
    count +=1
    text += pageObj.extractText()

#This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files.
#print("here:",text)
text=text.lstrip().rstrip()
if text != "":
   text = text
   print ("pyPDF2 based extarction was sucessful")
   

#If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text
text=text.lstrip().rstrip()
if text=="":
    print ("pyPDF2 failed..") 
    time.sleep(1)
    print ("Trying pdfminer")
    text=t.process(filename,method='pdfminer')
    text=text.lstrip().rstrip()
    
    if text!="":
        print ("pdfminer based extraction was sucessful")
    else:
        text.replace(" ",'')


text=text.lstrip().rstrip()
if text=="":
    print ("pdfminer failed trying tesseract")
    print ("Trying tesseract") 
    text = t.process(filename, method='tesseract', language='eng',extension='PNG')
    text=text.lstrip().rstrip()
    if text!="":
        print ("tesseract based extraction was sucessful") 
##    text=t.process(filename)
##    text=text.decode('utf-8')

print("\n",text)
text=text.lstrip().rstrip()
if text=="":
    print ("None of the extraction techniques were sucessful :(")
f= open('OCR_miner.txt','w')

#text = re.sub(r'[^\w\s]','',text, re.UNICODE)
no_punct = ""
for char in text:
   if char not in punctuations:
       no_punct = no_punct + char

no_punct='  '.join(no_punct.splitlines())
##print(no_punct)
f.write(no_punct)
f.close()

