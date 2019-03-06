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
