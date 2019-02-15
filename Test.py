#!/usr/bin/env python


from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdf2image import convert_from_path
from matplotlib import pyplot as plt
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from collections import defaultdict
from extraction import extract
from PIL import Image
from mongo import *
import numpy as np
import collections
import argparse
import pprint
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
		parser = PDFParser(open(pdf, 'rb'))
		document = PDFDocument(parser)
		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed
		rsrcmgr = PDFResourceManager()
		retstr = StringIO()
		laparams = LAParams()
		codec = 'utf-8'
		device = TextConverter(rsrcmgr, retstr,codec = codec,laparams = laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		for page in PDFPage.create_pages(document):
			interpreter.process_page(page)
		self.records = []
		lines = retstr.getvalue().splitlines()
	
		pp = pprint.PrettyPrinter(indent=4)#For better indentation
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
				words2[i]=".."
		
		#For the alternatives
		alt=[t for t in words2 if "alt" in t]
		#For the interactions
		int=[t for t in words2 if "int" in t]
		#For the functions
		matching = [s for s in words2 if "(" in s]

	
		#For components
		comp=[]
		for i in range(len(words2)):
			if(words2[i]!=matching[0]):
				comp.append(words2[i])
			else:
				break
		
		
		#Convert pdf to png
		pages = convert_from_path(pdf, 500)
		for page in pages:
			page.save('input.png', 'PNG')
		image = cv2.imread('input.png')
		
		orient={'key':'value'}#dictionary for orientation of the arrows

		#read the right arrow
		right = cv2.imread('Images/arrow_right.png',0)#right arrow
		pick = extract(image,right,0.85)
		
		#read the left arrow
		left = cv2.imread('Images/arrow_left.png',0)#left arrow
		pick1 = extract(image,left,0.85)

		#read the boxes
		template = cv2.imread('Images/smallbox.png',0)#boxes
		pick3 = extract(image,template,0.85)
		
		#read the components
		template2 = cv2.imread('Images/box.png',0)#components
		pick2 = extract(image,template2,0.9)
		
		for (startX, startY, endX, endY) in pick:#for right
				orient[startY]='left to right'
		
		for (startX, startY, endX, endY) in pick1:
				orient[startY]='right to left'
		
		#Reversing the lists to get correct index
		pick3[:] = pick3[::-1]
		pick2[:] = pick2[::-1]
		
		#Get the directions of the arrows and map it to the functions extracted
		del orient['key']
		
		od = collections.OrderedDict(sorted(orient.items()))
		dir=[]
		for k, v in od.items(): 
			dir.append(v)

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
		
		#Making a list of components for arrows
		
		for i in range(len(final)):
			
			final[i][0]=comp[final[i][0]-1]
			if(final[i][1]==-1):
				final[i][1]='NULL'
			else:
				final[i][1]=comp[final[i][1]-1]
				
		collobj=CreateCollection(CreateDB("admin"),"TOPAS")
		
		
		#Insert document in collection
		c=[]
		start='('
		end=')'
		for i in matching:
			ip=(i.split(start))[1].split(end)[0]
			op=
			method={"method_name" : i , "input" : ip,"output" : "none" }
			c.append(method)
		
		contentDict={"_id" : 1, "IPPC": {"EA_analytics" : c }}
		doc=InsertIntoCollection(collobj,contentDict)
		#Save the text in a text file
		f= open('EA_miner.txt','w')
		f.write('The Components are:')
		f.write('\n')
		for m in range(len(comp)):
			f.write(str(m+1) + ') ' + comp[m])
			f.write('\n\n')
		f.write('The functions are: ')
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
