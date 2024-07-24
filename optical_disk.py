import numpy as np
import scipy as sp
import scipy.ndimage as ndimage
import math
from skimage import exposure,filters
from matplotlib import pyplot as plt
import cv2
import matplotlib.pyplot as plt
from skimage.transform import hough_circle, hough_circle_peaks,hough_ellipse
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.segmentation import active_contour
from skimage.filters import gaussian
import argparse
import os

def resize(img):
	width = 1024
	height = 720
	#####
	return cv2.resize(img,(width,height), interpolation = cv2.INTER_CUBIC)

def rgb2Blue(img):
	b,g,r = cv2.split(img)
	return b

def rgb2Red(img):
	b,g,r = cv2.split(img)
	return r

def rgb2Green(img):
	b,g,r = cv2.split(img)
	return g

def rgb2Gray(img):
	return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

def rgb2lab(img):
	return cv2.cvtColor(img,cv2.COLOR_BGR2LAB)

def preprocess(img):
	if img is None or img.size == 0:
		print("Error: Image not found")
		return None

	b,g,r = cv2.split(img)
	gray = rgb2Red(img)
	gray_blur = cv2.GaussianBlur(gray, (5,5), 0)
	gray = cv2.addWeighted(gray, 1.5, gray_blur, -0.5, 0, gray)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31))
	gray = ndimage.grey_closing(gray,structure=kernel)
	gray = cv2.equalizeHist(gray)

	return gray

def getROI(image):
	image_resized = resize(image)
	b,g,r = cv2.split(image_resized)
	g = cv2.GaussianBlur(g,(15,15),0)
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
	g = ndimage.grey_opening(g,structure=kernel)
	(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(g)

	x0 = int(maxLoc[0])-110
	y0 = int(maxLoc[1])-110
	x1 = int(maxLoc[0])+110
	y1 = int(maxLoc[1])+110

	res = [y0,y1,x0,x1]

	return image_resized[y0:y1,x0:x1], res


def getValue(img):
	shapeRow = img.shape[0]
	shapeCol = img.shape[1]
	x = 0
	y = 0
	acu = 0
	maxloc = []
	for i in range(shapeRow):
		for j in range(shapeCol):
			(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(img[i-15:j-15,i+15:j+15])
			value = maxVal
			if value > acu:
				acu = value
				maxloc = maxLoc
	return maxloc

def kmeans(img):
	## K-Means
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	flags = cv2.KMEANS_RANDOM_CENTERS
	roi = img
	X = roi.reshape((-1, 1))
	X = np.float32(X)
	compactness,labels,centers = cv2.kmeans(X,3,None,criteria,10,flags)

	result = np.choose(labels, centers)
	result.shape = X.shape

	centers = np.uint8(centers)
	res= centers[labels.flatten()]
	res2 = res.reshape((roi.shape))
	return res2


def checkSide(img):
	shapeRow = img.shape[0]
	shapeCol = img.shape[1]
	if cv2.countNonZero(img[:,0:int(shapeCol/2)]) > cv2.countNonZero(img[:,int(shapeCol/2):shapeCol]):
		return True
	else:
		return False

def checkHigh(img):
	shapeRow = img.shape[0]
	shapeCol = img.shape[1]
	if cv2.countNonZero(img[0:int(shapeRow/2),:]) > cv2.countNonZero(img[int(shapeRow/2):shapeRow,:]):
		return True
	else:
		return False

def canny(img, sigma):
    if img is None or img.size == 0:
        print("Error: Image not found")
        return None

    v = np.mean(img)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(img, lower, upper)
    return edged

def hough(edged,limm,limM):
	hough_radii = np.arange(limm, limM, 1)
	hough_res = hough_circle(edged, hough_radii)
	return hough_circle_peaks(hough_res, hough_radii,total_num_peaks=1)


def extract_opticdisk(image):
    roi, roi_coords = getROI(image)
    preprocessed_roi = preprocess(roi)
    if preprocessed_roi is None:
        print("Preprocessed ROI is empty.")
        return None, None, None
    
    edged = canny(preprocessed_roi, 0.22)
    if edged is None:
        print("Canny edge detection failed.")
        return None, None, None
    
    edged = edged.astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    edged = cv2.dilate(edged, kernel, iterations=3)
    accums, cx, cy, radii = hough(edged, 55, 80)
    
    for center_y, center_x, radius in zip(cy, cx, radii):
        circy, circx = circle_perimeter(center_y, center_x, radius)
        try:
            roi[circy, circx] = (220, 20, 20)
        except IndexError:
            continue

    blue_pixels = np.where((roi[:, :, 0] == 220) &
                           (roi[:, :, 1] == 20) &
                           (roi[:, :, 2] == 20))

    blue_coordinates = list(zip(blue_pixels[0], blue_pixels[1]))

    if not blue_coordinates:
        print("No blue pixels found in ROI.")
        return roi, preprocessed_roi, None

    y0, y1, x0, x1 = roi_coords

    original_height, original_width = image.shape[:2]
    resized_width, resized_height = 1024, 720

    scale_x = original_width / resized_width
    scale_y = original_height / resized_height

    roi_coords_original = [
        int(roi_coords[0] * scale_y),
        int(roi_coords[1] * scale_y),
        int(roi_coords[2] * scale_x),
        int(roi_coords[3] * scale_x)
    ]

    adjusted_blue_circle_coords = [
        (int(x * scale_x + roi_coords_original[2]), int(y * scale_y + roi_coords_original[0]))
        for (x, y) in blue_coordinates
    ]

    if not adjusted_blue_circle_coords:
        print("No adjusted blue circle coordinates found.")
        return roi, preprocessed_roi, None

    x_coords, y_coords = zip(*adjusted_blue_circle_coords)
    center_x = int(np.mean(x_coords))
    center_y = int(np.mean(y_coords))
    radius = int(np.mean([np.linalg.norm((center_x - x, center_y - y)) for x, y in adjusted_blue_circle_coords]))

    mask = np.zeros((original_height, original_width), dtype=np.uint8)

    cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)

    output_img = np.zeros_like(image)
    output_img[np.where(mask == 255)] = [255, 255, 255]

    return roi, preprocessed_roi, output_img

if __name__ == "__main__":
    pathFolder = r"/Users/aarshpatel/Downloads/sparks-internship-diabetic-retinopathy/images/"
    destinationFolder = r"/Users/aarshpatel/Downloads/sparks-internship-diabetic-retinopathy/output/OD"

    if not os.path.exists(destinationFolder):
        os.mkdir(destinationFolder)

    for filename in os.listdir(pathFolder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(pathFolder, filename)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to read image {filename}.")
                continue
            img_mark, img_preprocess, final_img = extract_opticdisk(image)
            if final_img is not None:
                output_path = os.path.join(destinationFolder, filename)
                cv2.imwrite(output_path, final_img)
            else:
                print(f"Optic disk not found for image {filename}.")



