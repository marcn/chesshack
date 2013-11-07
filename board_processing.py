import cv2, numpy as np, math
from utils import ImgOut

M = lambda x: int(x * 0.5)

img_out = ImgOut()

def threshold(img):
	#return img_out.save(cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0))
	return img_out.save(cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)[1])

def harris_corner(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = np.float32(gray)
	dst = cv2.goodFeaturesToTrack(gray, 8, 0.01, 10)
	corners = np.int0(dst)
	print corners
	for i in corners:
		x,y = i.ravel()
		cv2.circle(img,(x,y), 10, 255, 5)

	img_out.save([gray, img])

def perspective_correction(img):
	edges = img_out.save(cv2.Canny(gray, M(100), M(150), 7))
	lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 1, None, M(120), M(100))
	for line in lines[0]:
		pt1 = (line[0], line[1])
		pt2 = (line[2], line[3])
		cv2.line(img, pt1, pt2, (0, 0, 255), 3)
	img_out.save(img)

def chessboard_detection(img):
	gray = img_out.save(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
	corners = cv2.findChessboardCorners(gray, (7, 7))
	for corner in corners[1]:
		pt = (corner[0][0], corner[0][1])
		cv2.circle(img, pt, 10, 255, 5)
	img_out.save(img)

def quantization(img):
	blur = img_out.save(cv2.GaussianBlur(img, (M(15), M(15)), 0))

	Z = img.reshape((-1, 3))
	Z = np.float32(Z)

	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	K = 3
	ret, label, center = cv2.kmeans(Z, K, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

	center = np.uint8(center)
	res = center[label.flatten()]
	res2 = res.reshape((img.shape))

	return img_out.save(res2)

def resize(img):
	return cv2.resize(img, (M(2592), M(1944)))

def contours(img):
	contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	print "contours", contours
	print "hierarchy", hierarchy
	cv2.drawContours(img, contours, -1, (255, 0, 0))
	img_out.save(img)

img = img_out.save(resize(cv2.imread('board-pictures/board2.jpg')))
gray = img_out.save(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
quant = quantization(gray)
thresh = threshold(quant)
cont = contours(thresh)