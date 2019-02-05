#!/usr/bin/env python

from nms import non_max_suppression_slow, non_max_suppression_fast
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
from PIL import Image
import pytesseract
import numpy as np
import collections
import argparse
import pprint
import time
import cv2
import sys
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
			
			if(((i+1)%2)!=0 and (i+1)!=len(words) and words[i+1]!=''):
				words2.append(words[i] + " " + words[i+1])
				i=i+2
			
			elif(i%2==0 and words[i]!=''):
				words2.append(words[i])
				
				
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

		
		#Read the image and convert to grayscale
		image = cv2.imread('input.png')
		img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		#Read the templates
		right = cv2.imread('Images/arrow_right.png',0)#right arrow
		wr, hr = right.shape[::-1]
		left=cv2.imread('Images/arrow_left.png',0)#left arrow
		wl, hl = left.shape[::-1]
		slf=cv2.imread('Images/self_arrow.jpg',0)#self arrow
		ws, hs = slf.shape[::-1]
		template = cv2.imread('Images/smallbox.png',0)#boxes
		w, h = template.shape[::-1]
		template2 = cv2.imread('Images/box.png',0)#components
		w2, h2 = template2.shape[::-1]

		
		#Template Matching
		res = cv2.matchTemplate(img_gray,right,cv2.TM_CCOEFF_NORMED)
		res1= cv2.matchTemplate(img_gray,left,cv2.TM_CCOEFF_NORMED)
		res2= cv2.matchTemplate(img_gray,slf,cv2.TM_CCOEFF_NORMED)
		res3 = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		res4 = cv2.matchTemplate(img_gray,template2,cv2.TM_CCOEFF_NORMED)

		#To get multiple instances set a threshold
		threshold = 0.85
		loc = np.where(res >= threshold)
		loc1=np.where(res1 >= threshold)
		loc2 = np.where( res2 >= threshold)
		loc3 = np.where( res3 >= threshold)
		loc4 = np.where( res4 >= 0.9)
		
		orient={'key':'value'}#dictionary for orientation of the arrows

		###Create bounding boxes over every right arrow
		arr=[[]]
		#Draw rectangles around each instance in the image
		for pt in zip(*loc[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wr, pt[1] + hr), (0,0,255), 1)
			arr.append([pt[0],pt[1],pt[0] + wr,pt[1] + hr])

		arr.pop(0)
		arr=np.array(arr)
		images = [("input.png",arr)]
		iter_num= 1
		images = images*iter_num  
    
		#Loop over the images
		for (imagePath, Boxes) in images:
    			
			#Load the image
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			#Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
	    
			#Non-maximum suppression on the bounding boxes
			pick = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)

	    
			#Loop over the picked bounding box and append them to array.
			for (startX, startY, endX, endY) in pick:#for right
				orient[startY]='left to right'
		
		###Create bounding boxes over every left arrow
		arr1=[[]]
		for pt in zip(*loc1[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wl, pt[1] + hl), (0,255,0), 1)
			arr1.append([pt[0],pt[1],pt[0] + wr,pt[1] + hr])

		arr1.pop(0)
		arr1=np.array(arr1)
	
		images = [("input.png",arr1)]
		iter_num= 1
		images = images*iter_num  
    
		#Loop over the images
		for (imagePath, Boxes) in images:
    			
			#Load the image
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			#Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
			#Non-maximum suppression on the bounding boxes
			pick1 = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)#for left
 			
			#Loop over the picked bounding box and append them to array
			for (startX, startY, endX, endY) in pick1:
				orient[startY]='right to left'
		

		###Create bounding boxes over every component
		arr2=[]
		for pt in zip(*loc4[::-1]):
			cv2.rectangle(image, pt, (pt[0] + w2, pt[1] + h2), (0,0,0), 2)
			arr2.append([pt[0],pt[1],pt[0] + w2,pt[1] + h2])
		arr2.pop(0)
		arr2=np.array(arr2)
		images = [("input.png",arr2)]
		iter_num= 1
		images = images*iter_num  
    
		#Loop over the images
		for(imagePath, Boxes) in images:
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			#Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
			pick2 = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)#for components

		###Create bounding boxes over every smallboxes
		arr3=[]
		for pt in zip(*loc3[::-1]):
			cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
			arr3.append([pt[0],pt[1],pt[0] + w,pt[1] + h])
		arr3.pop(0)
		arr3=np.array(arr3)
		images = [("input.png",arr3)]
		iter_num= 1
		images = images*iter_num  
    
		#Loop over the image
		for (imagePath, Boxes) in images:
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			#Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
			pick3 = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)#for smallboxes
		
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
		final=[]
		for k,v in d.items():
			final.append(v)

		pp.pprint(final)
		#Save the text in a text file
		f= open('EA_miner.txt','w')
		f.write('The functions are: ')
		f.write('\n\n')
		for i in range(len(matching)):
			f.write(str(i+1) + ') '+ matching[i] + ' is going from ' + dir[i])
			f.write("\n")
		f.write('\n\n')
		f.write('The Components are:')
		f.write('\n')
		for m in range(len(comp)):
			f.write(str(m+1) + ') ' + comp[m])
			f.write('\n\n')
		f.close()
		
		"""#for self arrow
		for pt in zip(*loc2[::-1]):
			cv2.rectangle(image, pt, (pt[0] + ws, pt[1] + hs), (255,0,0), 1)"""

		 		
	def handle_line(self, line):
		self.records.append(line)		 
if __name__ == '__main__':
	p = MyParser(sys.argv[1])
	print ('\n'.join(p.records))
