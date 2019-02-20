import os
import cv2
import glob
import numpy as np
from PIL import Image
from nms import non_max_suppression_slow, non_max_suppression_fast

def extract(image,string):
	
	image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#Read the templates
	template_data=[]
	
	#make a list of all template images from a directory
	files= glob.glob(string + '/*')
	for myfile in files:
		t_image = cv2.imread(myfile,0)
		template_data.append(t_image)
	arr=[[]]
	#loop for matching
	for tmp in template_data:
		(tW, tH) = tmp.shape[::-1]
		res = cv2.matchTemplate(image_gray, tmp, cv2.TM_CCOEFF_NORMED)
		loc = np.where(res >= 0.9)

	
		#Draw rectangles around each instance in the image
		for pt in zip(*loc[::-1]):
			cv2.rectangle(image, pt, (pt[0] + tW, pt[1] + tW), (0,0,255), 1)
			arr.append([pt[0],pt[1],pt[0] + tW,pt[1] + tH])
	arr.pop(0)
	arr=np.array(arr)
	images = [('input.png',arr)]
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
	print(pick)	
	return pick
