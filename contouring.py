import cv2
import time
import numpy as np
from pprint import pprint


#width=600.0
#height=420.0
#margin=0.0
corners = np.array([[[0.0, 0.0]],[[0.0,420.0 + 0.0]],[[ 600.0 + 0.0, 420.0 + 0.0]],[[ 600.0 + 0.0, 0.0]]])
pts_dst = np.array( corners, np.float32 )
rgb=cv2.imread('input.png',1)
gray = cv2.cvtColor( rgb, cv2.COLOR_BGR2GRAY )
gray = cv2.bilateralFilter( gray, 1, 10, 120 )
edges  = cv2.Canny( gray, 10, 250 )
kernel = cv2.getStructuringElement( cv2.MORPH_RECT, ( 7, 7 ) )
closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernel )
_ , contours, _ = cv2.findContours(closed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE )
app=[]
for cont in contours:
	if (cv2.contourArea( cont )>5000):
		arc = cv2.arcLength( cont,True)
		approx = cv2.approxPolyDP( cont, 0.1 * arc, True)
		
		if ( len( approx ) == 4):
			app.append(approx)
			pts_src = np.array( approx, np.float32 )
			h, status = cv2.findHomography( pts_src, pts_dst )
			out = cv2.warpPerspective( rgb, h, ( int( 600.0 + 0.0 * 2 ), int( 420.0 + 0.0 * 2 ) ) )
			cv2.drawContours( rgb, [approx], -1, ( 255, 0, 0 ), 2 )
pprint(app)
cv2.imwrite('Image.png',rgb)
