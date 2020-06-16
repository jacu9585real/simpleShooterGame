import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import math

def populateBreakPoints(currRoot):		#This function simply goes through the current xml file to populate arrays which contain x and y values that are the breakpoints for each of the 4 bands
	numBands = 4
	redBandX = []
	redBandY = []
	greenBandX = []
	greenBandY = []
	blueBandX = []
	blueBandY = []
	nirBandX = []
	nirBandY = []
	allBandArrays = [redBandX, redBandY, greenBandX, greenBandY, blueBandX, blueBandY, nirBandX, nirBandY]
	for i in range(numBands):
		currLutSize = int(currRoot[i+1][1].text)
		for j in range(currLutSize):
			newXVal = (float(currRoot[i+1][2][j].text))/2047
			newXVal = str(newXVal)									#must convert back to string after dividing to get the correct looking output
			newYVal = (float(currRoot[i+1][3][j].text))/255
			newYVal = str(newYVal)
			allBandArrays[i*2].append(newXVal)
			allBandArrays[i*2+1].append(newYVal)

	return allBandArrays


def createMosaicXML():
	oldTree= ET.parse('autodra2_lut.xml')
	oldFileRoot = oldTree.getroot() 
	allBandArrays = populateBreakPoints(oldFileRoot)
	######defining the header to the xml file######
	root= ET.Element("MosaicProject", ver="1.0")
	orderID_obj = ET.SubElement(root, "orderID").text = "012511962010 430da328-b7c2-4b40-ad49-45bc94d5da4c-OFS"
	AOI_Shapefile_obj = ET.SubElement(root, "AOI_Shapefile").text = "s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.shp"
	boundaries_Shapefile_obj = ET.SubElement(root, "boundariesShapefile").text = "s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.shp"
	rasterPath_obj = ET.SubElement(root, "baseRasterPath")
	raster_obj = ET.SubElement(root, "Raster", ID="1")
	####Under here I define the subelements of the rasterObj######
	ET.SubElement(raster_obj, "band", type="pshRed", file="s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.vrt", bandNumber="3")
	ET.SubElement(raster_obj, "band", type="pshGrn", file="s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.vrt", bandNumber="2")
	ET.SubElement(raster_obj, "band", type="pshBlu", file="s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.vrt", bandNumber="1")
	ET.SubElement(raster_obj, "band", type="pshNir", file="s3://deliveries-us-east-1-232376128214/APS/a5ab7e1c-5582-41c5-9499-7f560c61c5fb-APS/c3850a7c-527a-4691-bd48-936c1167c478/gp_input/20MAY05130601-S2AS-012511962010_VNIR.vrt", bandNumber="4")
	ET.SubElement(raster_obj, "red", AC="0", gainMidPoint="147.68498317871342")
	ET.SubElement(raster_obj, "grn", AC="0", gainMidPoint="327.11846263635437")
	ET.SubElement(raster_obj, "blu", AC="0", gainMidPoint="327.11846263635437")
	ET.SubElement(raster_obj, "nir", AC="0", gainMidPoint="327.11846263635437")
	####Done with SubElements for Raster######
	ET.SubElement(root, "AOI", ID="1", rasterID="1", redGain="1", redBias="0", grnGain="1", grnBias="0", bluGain="1", bluBias="0", nirGain="1", nirBias="0")

	#######Now I will create all of the DRAs with the breakpoints gotten above#########
	subSampleSize = 10
	myRedDRA = ET.SubElement(root, "redDRA")
	ET.SubElement(myRedDRA, "breakpoint", x="-1", y="0")
	ET.SubElement(myRedDRA, "breakpoint", x="0", y="0")
	for i in range(subSampleSize):
		currIndexIncrement = math.floor(len(allBandArrays[0])/subSampleSize)
		ET.SubElement(myRedDRA, "breakpoint", x=allBandArrays[0][i*currIndexIncrement], y=allBandArrays[1][i*currIndexIncrement])
	#####Adding in final breakpoint (may be slightly unevenly spaced when compared to the others)
	finalIndex = len(allBandArrays[0])-1
	ET.SubElement(myRedDRA, "breakpoint", x=allBandArrays[0][finalIndex], y = allBandArrays[1][finalIndex])
	#####Final two static breakpoints that were given
	ET.SubElement(myRedDRA, "breakpoint", x="1", y="1")
	ET.SubElement(myRedDRA, "breakpoint", x="2", y="1")
	
	myBluDRA = ET.SubElement(root, "bluDRA")
	ET.SubElement(myBluDRA, "breakpoint", x="-1", y="0")
	ET.SubElement(myBluDRA, "breakpoint", x="0", y="0")
	for i in range(subSampleSize):
		currIndexIncrement = math.floor(len(allBandArrays[2])/subSampleSize)
		ET.SubElement(myBluDRA, "breakpoint", x=allBandArrays[2][i*currIndexIncrement], y=allBandArrays[3][i*currIndexIncrement])
	#####Adding in final breakpoint (may be slightly unevenly spaced when compared to the others)
	finalIndex = len(allBandArrays[2])-1
	ET.SubElement(myBluDRA, "breakpoint", x=allBandArrays[2][finalIndex], y = allBandArrays[3][finalIndex])
	#####Final two static breakpoints that were given
	ET.SubElement(myBluDRA, "breakpoint", x="1", y="1")
	ET.SubElement(myBluDRA, "breakpoint", x="2", y="1")

	myGrnDRA = ET.SubElement(root, "grnDRA")
	ET.SubElement(myGrnDRA, "breakpoint", x="-1", y="0")
	ET.SubElement(myGrnDRA, "breakpoint", x="0", y="0")
	for i in range(subSampleSize):
		currIndexIncrement = math.floor(len(allBandArrays[4])/subSampleSize)
		ET.SubElement(myGrnDRA, "breakpoint", x=allBandArrays[4][i*currIndexIncrement], y=allBandArrays[5][i*currIndexIncrement])
	#####Adding in final breakpoint (may be slightly unevenly spaced when compared to the others)
	finalIndex = len(allBandArrays[4])-1
	ET.SubElement(myGrnDRA, "breakpoint", x=allBandArrays[4][finalIndex], y = allBandArrays[5][finalIndex])
	#####Final two static breakpoints that were given
	ET.SubElement(myGrnDRA, "breakpoint", x="1", y="1")
	ET.SubElement(myGrnDRA, "breakpoint", x="2", y="1")

	myNirDRA = ET.SubElement(root, "nirDRA")
	ET.SubElement(myNirDRA, "breakpoint", x="-1", y="0")
	ET.SubElement(myNirDRA, "breakpoint", x="0", y="0")
	for i in range(subSampleSize):
		currIndexIncrement = math.floor(len(allBandArrays[6])/subSampleSize)
		ET.SubElement(myNirDRA, "breakpoint", x=allBandArrays[6][i*currIndexIncrement], y=allBandArrays[7][i*currIndexIncrement])
	#####Adding in final breakpoint (may be slightly unevenly spaced when compared to the others)
	finalIndex = len(allBandArrays[6])-1
	ET.SubElement(myNirDRA, "breakpoint", x=allBandArrays[6][finalIndex], y = allBandArrays[7][finalIndex])
	#####Final two static breakpoints that were given
	ET.SubElement(myNirDRA, "breakpoint", x="1", y="1")
	ET.SubElement(myNirDRA, "breakpoint", x="2", y="1")


	myTree = ET.ElementTree(root)
	myTree.write("reformattedBPT2.xml")

createMosaicXML()










