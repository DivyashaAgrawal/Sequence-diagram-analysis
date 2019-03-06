from pprint import pprint
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
import collections
try:
	from StringIO import StringIO  # TODO: Switch to future
except ImportError:
	from io import StringIO
fp = open('sample_images/pdfs/7.pdf', 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser) 

if not document.is_extractable:
# if document is not protected, Try to parse the document
	raise PDFTextExtractionNotAllowed
# Create a PDF resource manager object that stores shared resources. 
rsrcmgr = PDFResourceManager()
# Create a buffer for the parsed text 
retstr = StringIO() 
# Spacing parameters for parsing
laparams = LAParams() 
codec = 'utf-8'
# Original text converter which coverts pdf into text by reading small chuncks
# and merging the ones close to each other.
device = TextConverter(rsrcmgr, retstr,codec = codec,laparams = laparams) 
interpreter = PDFPageInterpreter(rsrcmgr, device)
for page in PDFPage.create_pages(document):
	interpreter.process_page(page)
records = [] # The text list
lines = retstr.getvalue().splitlines()
words=[]
for i in lines:
			words.append(i)
pprint(words)
"""values = set(map(lambda x:x[0], words))
forcomments = [[y[4] for y in words if y[0]==x] for x in values] # will have same x1 that is words[0]

forcomponents=[]
f=0
for y in range(len(words)):
	if ((y+1)!=len(words) and words[y][1]==words[y+1][1] and words[y][3]==words[y+1][3]):
		p=words[y+1][4]
		forcomponents.append(words[y][4])
		forcomponents.append(p)
			
forcomponents = list(collections.OrderedDict.fromkeys(forcomponents))		

		forcomments=[]

		for i in range(len(comments)):
			f=0
			for j in range(len(components)):
				if(comments[i]!=components[j]):
					f=1
				else:
					f=0
					break
			if(f==1):
				forcomments.append(comments[i])

		forforcomments=[]
		for i in forcomments:
			f=0
			for j in functions:
				if(i!=j):
					f=1
				else:
					f=0
					break
			if(f==1):
				forforcomments.append(i)"""
	
