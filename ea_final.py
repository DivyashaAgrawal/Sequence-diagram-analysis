import os
import sys
import cv2
import collections
import numpy as np
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO


from mongo import *
from extraction import extract
from text_coordinates import PDFPageDetailed

from pprint import pprint
from matplotlib import pyplot as plt
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdf2image import convert_from_path
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFTextExtractionNotAllowed

class MyParser:
	def __init__(self,pdf):
		document=createPDFDoc(pdf)
		device,interpreter=createDeviceInterpreter()
		pages=PDFPage.create_pages(document)
		for page in PDFPage.create_pages(document):
    			interpreter.process_page(page)
		self.txt_coordinates=device.rows
		
		
class PdfMiner:
		
	def createPDFDoc(fpath):
    		fp = open(fpath, 'rb')
   		parser = PDFParser(fp)
    		document = PDFDocument(parser, password='')
    		# Check if the document allows text extraction. If not, abort.
    		if not document.is_extractable:
        		raise "Not extractable"
    		else:
        		return document


	def createDeviceInterpreter():
    		rsrcmgr = PDFResourceManager()
		retstr = StringIO() 
    		laparams = LAParams()
    		device = PDFPageDetailed(rsrcmgr, laparams=laparams) 
    		interpreter = PDFPageInterpreter(rsrcmgr, device)
    		return device, interpreter


class Text_Extraction:

	def comment_extract(text):
		_sorted = sorted(text ,key=lambda x:(x[5],-x[1])) #Sorted according to font type
		comments=[]
		#Extracting Comments
		for i in range(len(_sorted)):
			if((i+1)!=len(_sorted) and _sorted[i][5]!=_sorted[i+1][5]):#If there is a change in type of font put it in comment array
				p=i+1
				break
			else:
				p=0
		rest=[] # Array for text with coordinates except comments
		rest1=[]# Array for text without coordinates except comments
		for i in range(len(forcomments)):
			if(i>=p):
				comments.append(_sorted[i][4])
			else:
				rest.append(_sorted[i])
				rest1.append(_sorted[i][4])
	
	def component_extract(text):
		# Extracting components
		comp=[]
		f=0
		p=0
		for y in range(len(rest)):
			if ((y+1)!=len(rest) and 
			rest[y][1]==rest[y+1][1] and 
			rest[y][3]==rest[y+1][3]):
				comp.append(rest[y][4])
				p=rest[y+1][4]
		comp.append(p)
	
	def function_extract:
		#Extracting functions
		functions=[s for s in rest1 if "(" in s]
		#For the alternatives
		alt=[t for t in rest1 if "alt" in t]
		#For the interactions
		inter=[t for t in rest1 if "int" in t]
	
class convert pdf_to_image:

	def convert():
		#Convert pdf to png
		pages = convert_from_path(pdf, 500)
		for page in pages:
			page.save('input.png', 'PNG')
		image = cv2.imread('input.png')#Save the image in the same folder

class Image_Extraction:
	
	orient={'key':'value'}
	def component_extract():
		

		
		#read the components_boxes
		temp_comp = "sample_images/components"
		pick_comp = extract(image,temp_comp)

	def arrow_extract():

		#read the self arrow
		slf= "sample_images/self_arrow"
		pick_self = extract(image,slf)

		#read the right_to_left arrow
		rght_lft = "sample_images/right_arrow"
		pick_rght_lft = extract(image,rght_lft)

		#read the left_to_right arrow
		lft_rght = "sample_images/left_arrow"
		pick = extract(image,lft_rght)		
		pick_lft_rght=[]
		for i in range(len(pick)):
			f=1
			for j in range(len(pick_self)):
				if (pick[i][0]>=pick_self[j][0] and pick[i][2]<=pick_self[j][2]):
					f=0
					break
			if(f == 1):
				pick_lft_rght.append(pick[i])

	def point_extract():
		#read the boxes
		template = "sample_images/small_boxes"
		pick_box = extract(image,template)

class Mapping:

	def arrow_component():

		for (startX, startY, endX, endY) in pick_rght_lft:#for right
				orient[startY] ='left to right'
		
		for (startX, startY, endX, endY) in pick_lft_rght: #for left
				orient[startY] ='right to left'

		for (startX, startY, endX, endY) in pick_self:#for self
				orient[startY] ='self'
		
		#Reversing the lists to get correct index
		pick_box[:] = pick_box[::-1]
		pick_comp[:] = pick_comp[::-1]
		
		#Get the directions of the arrows and map it to the functions extracted
		del orient['key']
		
		od = collections.OrderedDict(sorted(orient.items()))
		d2=[]
		for k, v in od.items(): 
			d2.append(v)
		#List of pairs of boxes(starting and ending points)
		i=1
		boxes=[]
		while(i<(len(pick_box))):
			if(pick_box[i-1][1]-pick_box[i][1]>=-10):
				pair=[[pick_box[i-1][0],pick_box[i-1][1],pick_box[i-1][2],pick_box[i-1][3]],[pick_box[i][0],pick_box[i][1],pick_box[i][2],pick_box[i][3]]]
				boxes.append(pair)
				i=i+2
			else:
				single=[[pick_box[i-1][0],pick_box[i-1][1],pick_box[i-1][2],pick_box[i-1][3]],[]]
				boxes.append(single)
				i=i+1
		if(i==len(pick_box)):
			single=[[pick_box[i-1][0],pick_box[i-1][1],pick_box[i-1][2],pick_box[i-1][3]],[]]
			boxes.append(single)
	
		#Create the dictionary of components and small boxes we need a list of coordinates of boxes in tuple
		real=[]
		for i in pick_box:
			real.append(tuple(i))
		#Create dictionary of boxes and components(indexwise)
		components=dict()
		for j in range(len(real)):
			for(i,(startX, startY, endX, endY)) in enumerate(pick_comp):
				if(real[j][0]>startX and real[j][0]<endX):
					components[real[j]]=i
					break
		#Create the dictionary of components and arrows 
		for i in range(len(boxes)):
			r=tuple(boxes[i][0])
			if r in components:	
					boxes[i][0]=components[r]+1
					
			q=tuple(boxes[i][1])
			if q in components:	
					boxes[i][1]=components[q]+1
			
		 
		#Dictionary of coordinates of arrows and pair of starting and ending boxes
		cor_box=dict(zip(od,boxes))
		
		#Map the orientatoin and components
		ds = [orient, cor_box]
		
		d = {}
		for k in orient:
    			d[k] = tuple(d[k] for d in ds)
        
		#correction of the orientation
		l=list()
		final=[]
		d1=dict()
		ll=list()
		for k,v in d.items():
			ll.append(k)
		ll.sort()
		for i in range(len(ll)):
			p=ll[i]
			d1[i]=d[p]
			
		
		for k,v in d1.items():
			l=list(d1[k])
			if(l[1][1]==[]):
				l[1][1]=-1
			if(l[0]=='left to right'):
				p=l[1][0]
				q=l[1][1]
				if(p>q and q!=-1):
					t=l[1][0]
					l[1][0]=l[1][1]
					l[1][1]=t
			elif(l[0]=='right to left'):
				p=l[1][0]
				q=l[1][1]
				if(p<q and q!=-1):
					t=l[1][0]
					l[1][0]=l[1][1]
					l[1][1]=t
			final.append(l[1])

	def arrow_function():
		#Making a list of components for arrows
		
		for i in range(len(final)):
			
			final[i][0]=components[final[i][0]-1]
			if(final[i][1]==-1):
				final[i][1]='NULL'
			else:
				final[i][1]=components[final[i][1]-1]

	

	
class DataBase:

	def push_db():
		#Insert document in collection
		collobj=CreateCollection(CreateDB("admin"),"TOPAS")
		c=[]
		start='('
		end=')'
		count=1
		for i in functions:
			ip=(i.split(start))[1].split(end)[0]
			name=i.split('(')[0]
			method={"method_name ": name, "param" :{"Sequence": count, "input" : ip, "output" : "none" }}
			c.append(method)
			count+=1
		
		contentDict={"IPPC": {"EA_analytics" : c }}
		doc=InsertIntoCollection(collobj,contentDict)

	def find_element():
	
class file:
	
	def arrange_file():

		#Save the text in a text file

		f= open('EA_miner.txt','w')
		f.write('The Components are:')
		f.write('\n')
		for m in range(len(comp)):
			f.write(str(m+1) + ') ' + comp[m])
			f.write('\n\n')
		f.write('The methods are: ')
		f.write('\n\n')
		for i in range(len(functions)):
			f.write(str(i+1) + ') '+ functions[i] + ' is going from ' + final[i][0] + ' to ' + final[i][1])
			f.write("\n")
		f.write('\n\n')
		
		f.close()
		


if __name__ == '__main__':
	p = MyParser(sys.argv[1])
	
