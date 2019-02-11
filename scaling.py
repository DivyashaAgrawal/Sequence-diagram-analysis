# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--template", required=True, help="Path to template image")

args = vars(ap.parse_args())
 
# load the image image, convert it to grayscale, and detect edges
template = cv2.imread(args["template"])
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
image = cv2.imread('input.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
# loop over the scales of the image
for scale in np.linspace(0.2, 1.0, 20)[::-1]:
# resize the image according to the scale, and keep track
# of the ratio of the resizing
	resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
	r = gray.shape[1] / float(resized.shape[1])
	# if the resized image is smaller than the template, then break
	# from the loop
	if resized.shape[0] < tH or resized.shape[1] < tW:
		break
	# detect edges in the resized, grayscale image and apply template
	# matching to find the template in the image
	edged = cv2.Canny(resized, 50, 200)
	res = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
loc = np.where( res >= 0.95)
arr=[[]]
for pt in zip(*loc[::-1]):
    	cv2.rectangle(image, int(pt*r), (int((pt[0] + tW)*r), int((pt[1] + tH)*r)), (0,255,0), 2)
	arr.append([int(pt[0]*r),int(pt[1]*r),int((pt[0]+tW)*r),int((pt[1] + tH)*r)])
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
	for (startX, startY, endX, endY) in pick:
		cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
cv2.imwrite('re.png',image)
