import cv2, numpy as np, math, random
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

def bounding_box(points):
	tl = (None, None)
	tr = (None, None)
	bl = (None, None)
	br = (None, None)
	for (x, y) in [p[0] for p in points]:
		if tl[0] is None or x < tl[0]:
			tl = (x, tl[1])
		if tl[1] is None or y < tl[1]:
			tl = (tl[0], y)
		if tr[0] is None or x > tr[0]:
			tr = (x, tr[1])
		if tr[1] is None or y < tr[1]:
			tr = (tr[0], y)
		if bl[0] is None or x < bl[0]:
			bl = (x, bl[1])
		if bl[1] is None or y > bl[1]:
			bl = (bl[0], y)
		if br[0] is None or x > br[0]:
			br = (x, br[1])
		if br[1] is None or y > br[1]:
			br = (br[0], y)
	return ((tl, br), (tr, bl))

def find_nearest_point(point, points):
	nearest = (None, 0)
	for comp_point in points:
		distance = np.linalg.norm(point - comp_point)
		if nearest[0] is None or distance < nearest[1]:
			nearest = (comp_point, distance)
	return nearest[0]


def find_corners(img, original):
	contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
	img_out.save(img)

	area_contours = [(cv2.contourArea(c), c) for c in contours]
	area_sorted = sorted(area_contours, key=lambda c2: c2[0], reverse=True)

	img_out.save(original)

	cv2.cvtColor(original, cv2.COLOR_BGR2RGBA)

	(tl, br), (tr, bl) = bounding_box(area_sorted[0][1])
	ta = lambda x: [x[0], x[1]]
	tl = find_nearest_point(tl, area_sorted[0][1])[0]
	br = find_nearest_point(br, area_sorted[0][1])[0]
	tr = find_nearest_point(tr, area_sorted[0][1])[0]
	bl = find_nearest_point(bl, area_sorted[0][1])[0]

	cv2.polylines(original, [np.array([ta(tl), ta(tr), ta(br), ta(bl)], np.int0)], True, (255, 0, 0), 2)

	img_out.save(original)
	return (tl, tr, br, bl)

def transform_perspective(img, tl, tr, br, bl):
	canvas = np.zeros((500, 500, 3), np.uint8)
	ta = lambda x: [x[0], x[1]]
	matrix = cv2.getPerspectiveTransform(np.array([ta(tl), ta(tr), ta(br), ta(bl)], np.float32), \
										 np.array([[0, 0], [499, 0], [499, 499], [0, 499]], np.float32))
	warp = cv2.warpPerspective(img, matrix, (500, 500))
	img_out.save(warp)

img = img_out.save(resize(cv2.imread('board-pictures/board2.jpg')))
gray = img_out.save(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
quant = quantization(gray)
thresh = threshold(quant)
(tl, tr, br, bl) = find_corners(thresh, img)
transform_perspective(img, tl, tr, br, bl)