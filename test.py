#!/usr/bin/env python


from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageDetailed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from collections import defaultdict,OrderedDict
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdf2image import convert_from_path
from matplotlib import pyplot as plt
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from extraction import extract
from pprint import pprint
from PIL import Image
from mongo import *
import numpy as np
import collections
import argparse
import time
import sys
import cv2
import os

try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

class MyParser:

	def __init__(self, pdf):
		
		###read the pdf and read the text
		parser = PDFParser(open(pdf, 'rb')) # Parse
		document = PDFDocument(parser) # Get document
		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed # if document is protected
		rsrcmgr = PDFResourceManager()  # get all the objects from the pdf
		retstr = StringIO()
		laparams = LAParams()
		codec = 'utf-8'
		device = TextConverter(rsrcmgr, retstr,codec = codec,laparams = laparams) # Original text converter which coverts pdf into text by reading small chuncks and merging the ones close to each other
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		for page in PDFPage.create_pages(document):
			interpreter.process_page(page)
		self.records = [] # The text list
		lines = retstr.getvalue().splitlines()
	
		# Added functionality in converter.py in PDFMiner to get coordnates of bounding boxes bounding the texts.
		device1 = PDFPageDetailed(rsrcmgr, laparams=laparams)
		interpreter1 = PDFPageInterpreter(rsrcmgr, device1)

		for page in PDFPage.create_pages(document): 
    			interpreter1.process_page(page)
    			device1.get_result()# receive the LTPage object for this page

		txt_coordinates=device1.rows #list of coordinates and texts
		

		# Extracting components
		forcomponents=[]

		f=0
		p=[]
		for y in range(len(txt_coordinates)):
			q=[]
			
			if ((y+1)!=len(txt_coordinates) and txt_coordinates[y][1]==txt_coordinates[y+1][1] and txt_coordinates[y][3]==txt_coordinates[y+1][3]):
				p=[txt_coordinates[y+1][4]]
				q.append(txt_coordinates[y][4])
				forcomponents.append(q)
		forcomponents.append(p)
		

		#Extracting functions
		#functions=[s for s in txt_coordinates if "(" in s]
		functions=[]
		for i in range(len(txt_coordinates)): 
			if "(" in txt_coordinates[i][4]:
				q=[txt_coordinates[i][4]]
				functions.append(q)
		
		#Extracting the comments (Same x-coordinates of comments)		
		values=set(map(lambda x:x[0],txt_coordinates))
		comments = [[y[4] for y in txt_coordinates if y[0]==x] for x in values]#will have same x1 that is txt_coordinates[0]

		forcomments=[]

		for i in range(len(comments)):
			f=0
			for j in range(len(forcomponents)):
				if(comments[i]!=forcomponents[j]):
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
				forforcomments.append(i)

		##pprint(forcomponents)
		##print('\n')
		##pprint(functions)
		##print('\n')
		##pprint(forforcomments)

		words=[]#for the whole text
		
		words2=[]#for filtered text
		for i in lines:
			i=i.replace(" ","")
			
		for i in lines:
			words.append(i)
	
		#Filter the spaces
		for i in range(len(words)):
			if((i-1)>-1 and (i+1)!=len(words) and words[i]=='' and (words[i+1].startswith("("))):
				words2.append(words[i-1]+ "" + words[i+1] )
				

			if(((i+1)%2)!=0 and (i+1)!=len(words) and words[i+1]!=''):
				words2.append(words[i] + " " + words[i+1])
				i=i+2
			
			elif(i%2==0 and words[i]!='' ):
				words2.append(words[i])
		for i in range(len(words2)):
			if(words2[i].startswith("(") or words2[i].startswith(" (")):
				words2[i]="."
		
		#For the alternatives
		alt=[t for t in words2 if "alt" in t]
		#For the interactions
		inter=[t for t in words2 if "int" in t]
		#For the functions
		matching = [s for s in words2 if "(" in s]

	
		#For components
		comp=[]
		for i in range(len(words2)):
			if(words2[i]!=matching[0]):
				comp.append(words2[i])
			else:
				break
		##print("\n")
		##pprint(matching)
		##pprint(alt)
		##pprint(comp)

		#Convert pdf to png
		pages = convert_from_path(pdf, 500)
		for page in pages:
			page.save('input.png', 'PNG')
		image = cv2.imread('input.png')
		
		orient={'key':'value'}#dictionary for orientation of the arrows

		#read the right arrow
		right = "sample_images/right_arrow"#right arrow
		pick = extract(image,right)
		#read the left arrow
		left = "sample_images/left_arrow"#left arrow
		pick1 = extract(image,left)
		#read the self arrow
		slf= "sample_images/self_arrow"
		pick4 = extract(image,slf)
		#read the boxes
		template = "sample_images/small_boxes"#boxes
		pick3 = extract(image,template)
		#read the components
		template2 = "sample_images/components"#components
		pick2 = extract(image,template2)
		pick5=[]
		for i in range(len(pick1)):
			f=1
			for j in range(len(pick4)):
				if (pick1[i][0]>=pick4[j][0] and pick1[i][2]<=pick4[j][2]):
					f=0
					break
			if(f == 1):
				pick5.append(pick1[i])

		for (startX, startY, endX, endY) in pick:#for right
				orient[startY]='left to right'
		
		for (startX, startY, endX, endY) in pick5:
				orient[startY]='right to left'

		for (startX, startY, endX, endY) in pick4:
				orient[startY]='self'

		#Reversing the lists to get correct index
		pick3[:] = pick3[::-1]
		pick2[:] = pick2[::-1]
		
		#Get the directions of the arrows and map it to the functions extracted
		del orient['key']
		
		od = collections.OrderedDict(sorted(orient.items()))
		d2=[]
		for k, v in od.items(): 
			d2.append(v)

		#List of pairs of boxes(starting and ending points)
		i=1
		boxes=[]
		while(i<(len(pick3))):
			if(pick3[i-1][1]-pick3[i][1]>=-10):
				pair=[[pick3[i-1][0],pick3[i-1][1],pick3[i-1][2],pick3[i-1][3]],[pick3[i][0],pick3[i][1],pick3[i][2],pick3[i][3]]]
				boxes.append(pair)
				i=i+2
			else:
				single=[[pick3[i-1][0],pick3[i-1][1],pick3[i-1][2],pick3[i-1][3]],[]]
				boxes.append(single)
				i=i+1
		if(i==len(pick3)):
			single=[[pick3[i-1][0],pick3[i-1][1],pick3[i-1][2],pick3[i-1][3]],[]]
			boxes.append(single)
		
		#Create the dictionary of components and small boxes we need a list of coordinates of boxes in tuple
		real=[]
		for i in pick3:
			real.append(tuple(i))
		#Create dictionary of boxes and components(indexwise)
		components=dict()
		for j in range(len(real)):
			for(i,(startX, startY, endX, endY)) in enumerate(pick2):
				if(real[j][0]>startX and real[j][0]<endX):
					components[real[j]]=i
					break# resize the image according to the scale, and keep track
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
		#pprint(ds)
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
		
		#Making a list of components for arrows
		
		for i in range(len(final)):
			
			final[i][0]=comp[final[i][0]-1]
			if(final[i][1]==-1):
				final[i][1]='NULL'
			else:
				final[i][1]=comp[final[i][1]-1]

		#Find euclidean distance between
		arrow_coordinates=[]
		

		#Insert document in collection
		collobj=CreateCollection(CreateDB("admin"),"TOPAS")
		c=[]
		start='('
		end=')'
		count=1
		for i in matching:
			ip=(i.split(start))[1].split(end)[0]
			name=i.split('(')[0]
			method={"method_name ": name, "param" :{"Sequence": count, "input" : ip, "output" : "none" }}
			c.append(method)
			count+=1
		
		contentDict={"IPPC": {"EA_analytics" : c }}
		doc = InsertIntoCollection(collobj,contentDict)
		#Save the text in a text file
		f= open('EA_miner.txt','w')
		f.write('The Components are:')
		f.write('\n')
		for m in range(len(comp)):
			f.write(str(m+1) + ') ' + comp[m])
			f.write('\n\n')
		f.write('The methods are: ')
		f.write('\n\n')
		for i in range(len(matching)):
			f.write(str(i+1) + ') '+ matching[i] + ' is going from ' + final[i][0] + ' to ' + final[i][1])
			f.write("\n")
		f.write('\n\n')
		
		f.close()


	def handle_line(self, line):
		self.records.append(line)
		

		 
if __name__ == '__main__':
	p = MyParser(sys.argv[1])
	print ('\n'.join(p.records))

