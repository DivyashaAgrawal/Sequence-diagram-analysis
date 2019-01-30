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
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

class MyParser(object):
	def __init__(self, pdf):
		parser = PDFParser(open(pdf, 'rb'))###read the pdf and read the text
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
		f= open('OCR_miner.txt','w')###save the text in a text file
		for i in lines:
			i=i.replace(" ","")
			print(i)
			f.write(i)
			f.write(" ")
		f.close()
		pages = convert_from_path(pdf, 500)###Convert pdf to png
		for page in pages:
			page.save('input.jpg', 'JPEG')
		image = cv2.imread('input.jpg')###read the image
		img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		
		###read the templates
		right = cv2.imread('Images/arrow_right.jpg',0)
		wr, hr = right.shape[::-1]
		left=cv2.imread('Images/arrow_left.jpg',0)
		wl, hl = left.shape[::-1]
		slf=cv2.imread('Images/self_arrow.jpg',0)
		ws, hs = slf.shape[::-1]
		
		###Template Matching
		res = cv2.matchTemplate(img_gray,right,cv2.TM_CCOEFF_NORMED)
		res1= cv2.matchTemplate(img_gray,left,cv2.TM_CCOEFF_NORMED)
		res2= cv2.matchTemplate(img_gray,slf,cv2.TM_CCOEFF_NORMED)
		threshold = 0.85
		
		loc = np.where(res >= threshold) 
		loc1=np.where(res1 >= threshold)
		loc2 = np.where( res2 >= threshold)
		
		arr=[[]]
		
		###Draw rectangles around each instance in the image
		for pt in zip(*loc[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wr, pt[1] + hr), (0,0,255), 1)
			arr.append([pt[0],pt[1],pt[0] + wr,pt[1] + hr])
		
		arr=arr.pop(0)
		arr=np.array(arr)
		print(arr)
		
		images = [("input.png",arr)]
		iter_num= 1
		images = images*iter_num
		t1 = time.time()
    
		###Loop over the images
		for (i, (imagePath, boundingBoxes)) in enumerate(images):
    			###Load the image 
			image = cv2.imread(imagePath)
			orig = image.copy()
	 
			###Loop over the bounding boxes for each image and draw them
			for (startX, startY, endX, endY) in boundingBoxes:
				cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
	    
			###Non-maximum suppression on the bounding boxes
			pick = non_max_suppression_fast(boundingBoxes, probs=None, overlapThresh=0.3)

			print ("[x] after applying non-maximum, %d bounding boxes" % (len(pick)))   
	    
			###Loop over the picked bounding boxes and draw them
			for (startX, startY, endX, endY) in pick:
				cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    

		t2 = time.time()
		print('cost {} ms to process {} images'.format((t2 - t1)*1000, len(images)))

		for pt in zip(*loc1[::-1]):
			cv2.rectangle(image, pt, (pt[0] + wl, pt[1] + hl), (0,255,0), 1)
			
		for pt in zip(*loc2[::-1]):
			cv2.rectangle(image, pt, (pt[0] + ws, pt[1] + hs), (255,0,0), 1)
			
		cv2.imwrite('arrow_extracted.jpg',image)
		
	def handle_line(self, line):
		self.records.append(line)		 
if __name__ == '__main__':
	p = MyParser(sys.argv[1])
	print ('\n'.join(p.records))








