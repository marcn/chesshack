import cv2, numpy as np, math, random, time
from utils import ImgOut

img_out = ImgOut()

class ChessCV():

	def __init__(self, file_name, scale=0.25):
		t = int(round(time.time() * 1000))
		self.image = cv2.imread(file_name)
		print "read img", (int(round(time.time() * 1000)) - t)
		self.scale = scale
		self.dimensions = (len(self.image[0]), len(self.image))

		# find corners of board
		t = int(round(time.time() * 1000))
		dst_img = self.grayscale(self.image)
		dst_img = self.resize(dst_img)
		# dst_img = self.quantize(dst_img)
		dst_img = self.threshold(dst_img)
		(tl, tr, br, bl) = self.find_corners(dst_img)
		print "find corners", (int(round(time.time() * 1000)) - t)

		# fix perspective
		t = int(round(time.time() * 1000))
		dst_img = self.warp_perspective(self.image, tl, tr, br, bl)
		print "wrap perspective", (int(round(time.time() * 1000)) - t)

		t = int(round(time.time() * 1000))
		img_out.save(dst_img)
		print "save img", (int(round(time.time() * 1000)) - t)

	def resize(self, img):
		new_dimensions = (int(self.dimensions[0] * self.scale), int(self.dimensions[1] * self.scale))
		return cv2.resize(img, new_dimensions)

	def grayscale(self, img):
		return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	def quantize(self, img):
		Z = img.reshape((-1, 3))
		Z = np.float32(Z)

		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
		K = 3
		ret, label, center = cv2.kmeans(Z, K, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

		dst = np.uint8(center)
		dst = dst[label.flatten()]
		return dst.reshape((img.shape))

	def threshold(self, img):
		return cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)[1]

	def find_corners(self, img):
		contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

		contour_areas = [(cv2.contourArea(c), c) for c in contours]
		contours_sorted = sorted(contour_areas, key=lambda c2: c2[0], reverse=True)

		(tl, br), (tr, bl) = self.bounding_box(contours_sorted[0][1])

		board_contour = contours_sorted[0][1]
		tl = self.find_nearest_point(tl, board_contour)
		br = self.find_nearest_point(br, board_contour)
		tr = self.find_nearest_point(tr, board_contour)
		bl = self.find_nearest_point(bl, board_contour)

		return (tl, tr, br, bl)

	def find_nearest_point(self, pt, pts):
		nearest = (None, 0)
		for comp_point in pts:
			distance = np.linalg.norm(pt - comp_point)
			if nearest[0] is None or distance < nearest[1]:
				nearest = (comp_point, distance)
		return [nearest[0][0][0], nearest[0][0][1]]

	def warp_perspective(self, img, tl, tr, br, bl):
		x = lambda y: (y[0] / self.scale, y[1] / self.scale)
		matrix = cv2.getPerspectiveTransform(np.array([x(tl), x(tr), x(br), x(bl)], np.float32), \
											 np.array([[0, 0], [499, 0], [499, 499], [0, 499]], np.float32))
		return cv2.warpPerspective(img, matrix, (500, 500))

	def bounding_box(self, points):
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

for x in np.arange(0.25, 1.25, 0.25):
	try:
		t = int(round(time.time() * 1000))
		ChessCV('board-pictures/board3.jpg', x)
		print "scale %d%%" % int(x * 100), int(round(time.time() * 1000)) - t
	except:
		print x, 'failed'
		raise
	print