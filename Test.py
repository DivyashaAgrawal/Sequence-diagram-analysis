#!/usr/bin/env python
import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
import cv2
import time
from nms import non_max_suppression_slow, non_max_suppression_fast
import numpy as np
import argparse
from PIL import Image
import pytesseract
import os
from pdf2image import convert_from_path
import pprint
import collections
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

class MyParser(object):

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
	
		
		words=[]
		for i in lines:
			i=i.replace(" ","")
			
		for i in lines:
			words.append(i)
		
		print(words)
		"""matching = [s for s in words if "(" in s]
		methods=[]
		for i in range(len(words)):
			if(words[i]!=matching[0] and words[i]!=''):
				methods.append(words[i])
			elif(words[i]==matching[0]):
				break
		"""
		###Convert pdf to png
		 
		page = convert_from_path(pdf, 500)
		page.save('input.png', 'PNG')

		###read the image

		image = cv2.imread('input.png')
		img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#Convert to grayscale
		
		###read the templates
		right = cv2.imread('Images/arrow_right.png',0)
		wr, hr = right.shape[::-1]
		left=cv2.imread('Images/arrow_left.png',0)
		wl, hl = left.shape[::-1]
		slf=cv2.imread('Images/self_arrow.jpg',0)
		ws, hs = slf.shape[::-1]
		

		d={'key':'value'}

		###Template Matching
		res = cv2.matchTemplate(img_gray,right,cv2.TM_CCOEFF_NORMED)
		res1= cv2.matchTemplate(img_gray,left,cv2.TM_CCOEFF_NORMED)
		res2= cv2.matchTemplate(img_gray,slf,cv2.TM_CCOEFF_NORMED)
		
		###To get multiple instances set a threshold
		threshold = 0.85
		loc = np.where(res >= threshold)
		pp = pprint.PrettyPrinter(indent=4)
		loc1=np.where(res1 >= threshold)
		loc2 = np.where( res2 >= threshold)
		
		arr=[[]]

		###Draw rectangles around each instance in the image
		for pt in zip(*loc[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wr, pt[1] + hr), (0,0,255), 1)
			arr.append([pt[0],pt[1],pt[0] + wr,pt[1] + hr])

		arr.pop(0)
		arr=np.array(arr)
	
		images = [("input.png",arr)]
		iter_num= 1
		images = images*iter_num  
    
		###Loop over the images
		for (i, (imagePath, Boxes)) in enumerate(images):
    			
			###Load the image
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			###Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
	    
			###Non-maximum suppression on the bounding boxes
			pick = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)

	    
			###Loop over the picked bounding box and append them to array.
			for (startX, startY, endX, endY) in pick:
				d[startY]='right to left'


		arr1=[[]]
	    
		for pt in zip(*loc1[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wl, pt[1] + hl), (0,255,0), 1)
			arr1.append([pt[0],pt[1],pt[0] + wr,pt[1] + hr])

		arr1.pop(0)
		arr1=np.array(arr1)
	
		images = [("input.png",arr1)]
		iter_num= 1
		images = images*iter_num  
    
		###Loop over the images
		for (i, (imagePath, Boxes)) in enumerate(images):
    			
			###Load the image
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			###Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in Boxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
			###Non-maximum suppression on the bounding boxes
			pick1 = non_max_suppression_fast(Boxes, probs=None, overlapThresh=0.3)
  
	    
			###Loop over the picked bounding boxes and draw them
			for (startX, startY, endX, endY) in pick1:
				d[startY]='left to right'
		del d['key']
		od = collections.OrderedDict(sorted(d.items()))
		dir=[]
		for k, v in od.items(): 
			dir.append(v)
		
		
		"""###save the text in a text file
		f= open('EA_miner.txt','w')
		f.write('The functions are: ')
		f.write('\n\n')
		for i in range(len(matching)):
			f.write(str(i+1) + ') '+ matching[i] + ' is going from ' + dir[i])
			f.write("\n")
		f.write('\n\n')
		f.write('The methods are:')
		f.write('\n')
		for m in range(len(methods)):
			f.write(str(m+1) + ') ' + methods[m])
			f.write('\n\n')
		f.close()"""

		for pt in zip(*loc2[::-1]):
			cv2.rectangle(image, pt, (pt[0] + ws, pt[1] + hs), (255,0,0), 1)

		 		
	def handle_line(self, line):
		self.records.append(line)		 
if __name__ == '__main__':
	p = MyParser(sys.argv[1])
	print ('\n'.join(p.records))
