def dist(boxA, boxB):
	# compute the dist between two boxes
	dis = boxA[3] - boxB[1]
	return dis

DIST = []
boxes=[[194.68158975, 746.56167456, 355.11789764250005, 754.6008576000000], #tclD T S IC anS ignal(2,"STA_DIAG_TP_DATA")
[118.53307125, 721.37175456, 356.55466214250004, 729.4109376000000], #topas_api::tclC anR aw (2,0x18FF0301,true,tclDiagReq* const poApp)
[157.32571275, 696.18183456, 232.91389309500000, 704.2210176000000], #topas_api::tclCanRaw
[118.53307125, 686.82557856, 279.68776139250000, 694.8647616000001], #(2,0x18F F 0200,true,tclDiagReq* const poApp)
[84.769105500, 670.99191456, 124.51719539250000, 679.0310976000001]] #DIAGREQ()


for i in range(len(boxes)):
	if(i+1!=len(boxes)):
		DIST.append(dist(boxes[i],boxes[i+1]))

print(min(DIST))

