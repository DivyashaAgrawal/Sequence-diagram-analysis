#!/usr/bin/env python


#Import the system libraries

import os
import sys
import glob
import collections
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO


INT_MAX = sys.maxsize 

#Import downloaded libraries
import cv2
import numpy as np
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

#Import created modules
from mongo import *
from extraction import extract
from text_coordinates import PDFPageDetailed

class MyParser:

	def __init__(self, pdf):
		
		# read the pdf and read the text
		parser = PDFParser(open(pdf, 'rb')) # Parse
		# Create the document model from the file
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
		# get coordnates of bounding boxes bounding the texts.
		# Create a PDF device object
		device = PDFPageDetailed(rsrcmgr, laparams=laparams) 
		# Create a PDF interpreter object
		interpreter = PDFPageInterpreter(rsrcmgr, device)  

		for page in PDFPage.create_pages(document): 
    			interpreter.process_page(page)
		#list of coordinates and texts
		txt_coordinates=device.rows 
		print(txt_coordinates)

		forcomments = sorted(txt_coordinates,key=lambda x:(x[5],-x[1]))#Sorted according to font type
		comments=[]
		#Extracting Comments
		for i in range(len(forcomments)):
			if((i+1)!=len(forcomments) and forcomments[i][5]!=forcomments[i+1][5]):#If there is a change in type of font put it in comment array
				pp=i+1
				break
			else:
				pp=0
		
		rest=[]# Array for text with coordinates except comments
		rest1=[]# Array for text without coordinates except comments
		comments1=[]#List of comments with coordinates
		for i in range(len(forcomments)):
			if(i>=pp):
				comments.append(forcomments[i][4])
				comments1.append(forcomments[i])
			else:
				rest.append(forcomments[i])
				rest1.append(forcomments[i][4])
		
		if(len(rest)==0):
			rest=comments1.copy()
			rest1=comments.copy()
			del comments1[:]
			del comments[:]
		
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
		
		forcomments = sorted(txt_coordinates)
		
		#Cleaned functions names
		
		c = []
		for i in range(len(rest)):
			if(i+1!=len(rest)):
				c.append(int(rest[i][1] - rest[i+1][1]))
		minimum = INT_MAX
		
		for i in c:
			if(i!=0 and i<=minimum and i>=9) :
				minimum=i
		
		
		
		for i in range(len(c)):
			if((c[i] == minimum and c[i] < 11) and c[i]>=8):
				
				rest1[i]= rest1[i]+rest1[i+1]
				rest1[i+1] = ''
		

		# Cleaned Comments box
		comments1=sorted(comments1,key=lambda x:(x[0] , -x[1]))
		
		comments2=[]
		st=""
		for i in range(len(comments1)):
			if((i+1)!=len(comments1) and comments1[i][0]==comments1[i+1][0] and  (abs(comments1[i][1]-comments1[i+1][1])) < 27):# Customized according to diagrams. Pixel range could be different
				st += comments1[i][4]
				
			elif(((i+1)!=len(comments1) and comments1[i][0]==comments1[i+1][0] and  (abs(comments1[i][1]-comments1[i+1][1])) >= 27) or 
((i+1)!=len(comments1) and comments1[i][0]!=comments1[i+1][0] and  (abs(comments1[i][1]-comments1[i+1][1])) >= 27) or 
(i+1==len(comments1))):
				st += comments1[i][4]
				
				comments2.append(st)
				st="" 
					
		
		# Extracting functions
		functions = [s for s in rest1 if "(" in s]
		
		# For the alternatives
		alt=[t for t in rest1 if "alt" in t]
		# For the interactions
		inter=[t for t in rest1 if "int" in t]
		

		# Removing spaces
		for i in range(len(comp)):
			comp[i]=comp[i].replace(' ','')
		for i in range(len(functions)):
			functions[i]=functions[i].replace(' ','')
		for i in range(len(alt)):
			alt[i]=alt[i].replace(' ','')
		for i in range(len(inter)):
			inter[i]=inter[i].replace(' ','')
		

		# Convert pdf to png
		pages = convert_from_path(pdf, 500)
		for page in pages: 

			page.save('input.png', 'PNG')
		image = cv2.imread('input.png')

		# dictionary for orientation of the arrows

		orient={'key':'value'}

		# Change in threshold according to image
		pdf_no = pdf.rsplit('.')[0].split('/')[2]
		 
		# read the components_boxes
		temp_comp = "sample_images/components"
		pick_comp = extract(image,temp_comp,0.94) 
		if(pdf_no == '4'):
			pick_comp = np.delete(pick_comp, 0, 0)
		
		# read the self arrow
		slf= "sample_images/self_arrow"
		pick_self = extract(image,slf,0.9)

		# read the right_to_left arrow
		rght_lft = "sample_images/right_arrow"
		pick_rght_lft = extract(image,rght_lft,0.9)

		# read the left_to_right arrow
		lft_rght = "sample_images/left_arrow"
		pick_lft_rght = extract(image,lft_rght,0.9)	
	

		# read the boxes
		template = "sample_images/small_boxes"
		pick_box = extract(image,template,0.95)
		
	
		# Reversing the lists to get correct index
		pick_box[:] = pick_box[::-1]
		pick_box = sorted(pick_box,key=lambda x:(x[1],x[0]))
		pick_box1=[]
		pick_lft_rght1=[]


		if(functions[0]=="StartPairing()"):
			
			for i in range(len(pick_box)):
				if(i>1):
					pick_box1.append(pick_box[i])
			del functions[0]
			for i in range(len(pick_lft_rght)):
				if(i!=0 ):
					pick_lft_rght1.append(pick_lft_rght[i])
			
		else:
			for i in range(len(pick_box)):
				pick_box1.append(pick_box[i])
			
			for i in range(len(pick_lft_rght)):
				pick_lft_rght1.append(pick_lft_rght[i])


		pick_comp[:] = pick_comp[::-1]
		
		pick_comp = sorted(pick_comp,key=lambda x:(x[0]))# Sorted components coordinates
		
		# List of pairs of boxes(starting and ending points)
		i=1
		boxes=[]
		while(i<(len(pick_box1))):
			if(pick_box1[i-1][1]-pick_box1[i][1]>=-100):
				pair=[[pick_box1[i-1][0],pick_box1[i-1][1],pick_box1[i-1][2],pick_box1[i-1][3]],[pick_box1[i][0],pick_box1[i][1],pick_box1[i][2],pick_box1[i][3]]]
				boxes.append(pair)
				i=i+2
			else:
				single=[[pick_box1[i-1][0],pick_box1[i-1][1],pick_box1[i-1][2],pick_box1[i-1][3]],[]]
				boxes.append(single)
				i=i+1
		if(i==len(pick_box1)):
			single=[[pick_box1[i-1][0],pick_box1[i-1][1],pick_box1[i-1][2],pick_box1[i-1][3]],[]]
			boxes.append(single)



		# Create the dictionary of components and small boxes we need a list of coordinates of boxes in tuple
		real=[]
		for i in pick_box1:
			real.append(tuple(i))
		
		# Create dictionary of boxes and components(indexwise)
		components=dict()
		for j in range(len(real)):
			for i in range(len(pick_comp)):
				
				if((real[j][0]>pick_comp[i][0]) and (real[j][0]<pick_comp[i][2])):
					components[real[j]]=i
					break
					
		pprint(components)
		# Create the dictionary of components and arrows 
		for i in range(len(boxes)):
			r=tuple(boxes[i][0])
			if r in components:	
					boxes[i][0]=components[r]+1
					
			q=tuple(boxes[i][1])
			if q in components:	
					boxes[i][1]=components[q]+1
			
		
		pprint(boxes)		
		for (startX, startY, endX, endY) in pick_rght_lft:#for right
				orient[startY] ='left to right'
		
		for (startX, startY, endX, endY) in pick_lft_rght1: #for left
				orient[startY] ='right to left'

		for (startX, startY, endX, endY) in pick_self:#for self
				orient[startY] ='self'
		
		
		# Get the directions of the arrows and map it to the functions extracted
		del orient['key']
		
		dv=[]
		od = collections.OrderedDict(sorted(orient.items()))
		# Removing the extra arrows of right_left//different from self_arrows
		for k,v in od.items():
			dv.append(v)
		
		for i in range(len(dv)):
			if(i!=len(dv) and dv[i-1]=="self" and dv[i]=="right to left"):
				dv[i]=""
		
		dvv=[]
		for i in dv:
			if(i!=""):
				dvv.append(i)
		odd={'key':'value'}

		for i in range(len(dvv)):
			odd[i+1]=dvv[i]

		del odd['key']
		

		# Dictionary of coordinates of arrows and pair of starting and ending boxes
		cor_box=dict(zip(odd,boxes))
		pprint(cor_box)
		# Map the orientatoin and components
		ds = [odd, cor_box]
		
		d = {}
		for k in odd:
    			d[k] = tuple(d[k] for d in ds)

		# Correction of the orientation
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
			if(l[0]=='left to right' or l[0] =='self'):
				p=l[1][0]
				q=l[1][1]
				if(p>q and q!=-1):
					t=l[1][0]
					l[1][0]=l[1][1]
					l[1][1]=t
			elif(l[0]=='right to left' ):
				p=l[1][0]
				q=l[1][1]
				if(p<q and q!=-1):
					t=l[1][0]
					l[1][0]=l[1][1]
					l[1][1]=t
			final.append(l[1])
				
		
		# Making a list of components for arrows
		# Naming the arrows
		
		for i in range(len(final)):
			
			final[i][0]=comp[(final[i][0]-1)]
			if(final[i][1]==-1):
				final[i][1]='NULL'
			else:
				final[i][1]=comp[final[i][1]-1]
		

		# Insert document in collection
		collobj=CreateCollection(CreateDB("admin"),"EA_PROJECT")

		c=[]
		cc=[]
		start='('
		end=')'
		count=1
		out=":"
		for i in range(len(functions)):
			ip=(functions[i].split(start))[1].split(end)[0]
			if(":" in functions[i]):
				ii=functions[i][::-1]
				op=ii.split(out)[0]
				op=op[::-1]
			else:
				op=""
			name=functions[i].split('(')[0]
			method={"method_name ": name, "Src ": final[i][0],"Dest ": final[i][1],"param" :{"Sequence": count, "input" : ip, "output" : op }}
			c.append(method)
			count+=1
		count1=1
		for j in comments2:
			method1={"Number-" : count1,"comment " : j}
			count1+=1
			cc.append(method1)
		
		
		cl=[{"Sequence_Block " : c},{ "Comments " : cc}]
		
		contentDict={"Project_name": {"EA_analytics" : {"Component " : c}, "Comments " : cc}}
		doc=InsertIntoCollection(collobj,contentDict)

		 
if __name__ == '__main__':
	
	files= glob.glob('sample_images/pdfs' + '/*')
	for myfile in files:
		print("Sequence diagram of " + myfile.rsplit('.')[0].split('/')[2] + "th pdf")
		p = MyParser(myfile)
