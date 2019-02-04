import cv2
import numpy as np
from matplotlib import pyplot as plt
from nms import non_max_suppression_slow, non_max_suppression_fast



img_rgb = cv2.imread('input.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
template = cv2.imread('smallbox.png',0)
w, h = template.shape[::-1]
template2 = cv2.imread('box.png',0)
w2, h2 = template2.shape[::-1]

res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
res2 = cv2.matchTemplate(img_gray,template2,cv2.TM_CCOEFF_NORMED)



loc = np.where( res >= 0.9)
loc2 = np.where( res2 >= 0.9)

arr=[]
for pt in zip(*loc[::-1]):
	cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
	arr.append([pt[0],pt[1],pt[0] + w,pt[1] + h])
arr.pop(0)
arr=np.array(arr)
images = [("input.png",arr)]
iter_num= 1
images = images*iter_num  
    
		###Loop over the images
for (i, (imagePath, Boxes)) in enumerate(images):
	image = cv2.imread(imagePath)
	orig = image.copy()
	 
			###Loop over the bounding boxes for each image and draw them
	for (startX, startY, endX, endY) in Boxes:
		cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
	pick = non_max_suppression_fast(Boxes,probs=None,  overlapThresh=0.3)
print(pick)

arr1=[]
for pt in zip(*loc2[::-1]):
	cv2.rectangle(img_rgb, pt, (pt[0] + w2, pt[1] + h2), (0,0,0), 2)
	arr1.append([pt[0],pt[1],pt[0] + w2,pt[1] + h2])
arr1.pop(0)
arr1=np.array(arr1)
images = [("input.png",arr1)]
iter_num= 1
images = images*iter_num  
    
		###Loop over the images
for (i, (imagePath, Boxes)) in enumerate(images):
	image = cv2.imread(imagePath)
	orig = image.copy()
	 
			###Loop over the bounding boxes for each image and draw them
	for (startX, startY, endX, endY) in Boxes:
		cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
	    
	pick1 = non_max_suppression_fast(Boxes,probs=None,  overlapThresh=0.3)
  
print(pick1)
pick[:] = pick[::-1]

boxes=[]

for(startx,starty,endx,endy)in pick:
	boxes.append(starty)

cv2.imwrite('res.png',img_rgb)
