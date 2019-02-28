from pprint import pprint
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageDetailed
from collections import OrderedDict

fp = open('11.pdf', 'rb')
parser = PDFParser(fp)
doc = PDFDocument(parser)
rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageDetailed(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

for page in PDFPage.create_pages(doc):
    interpreter.process_page(page)
    # receive the LTPage object for this page
    device.get_result()
words=device.rows

values = set(map(lambda x:x[0], words))
forcomments = [[y[4] for y in words if y[0]==x] for x in values] # will have same x1 that is words[0]

forcomponents=[]
f=0
for y in range(len(words)):
	if ((y+1)!=len(words) and words[y][1]==words[y+1][1] and words[y][3]==words[y+1][3]):
		p=words[y+1][4]
		forcomponents.append(words[y][4])
		forcomponents.append(p)
			
forcomponents = list(OrderedDict.fromkeys(forcomponents))		
"""
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
	
