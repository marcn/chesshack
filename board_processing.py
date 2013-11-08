import cv2, numpy as np, sys
from timeit import Timer
from utils import ImgOut, next_frame
from boardClassifier import BoardClassifier

img_out = ImgOut()

class ChessCV():

	def __init__(self, scale=1, file_name=None):
		self.scale = scale
		self.file_name = file_name

	def current_board(self):
		self.image = cv2.imread(self.file_name) if self.file_name is not None else next_frame()
		self.dimensions = (len(self.image[0]), len(self.image))

		# find corners of board
		dst_img = self.grayscale(self.image)
		if self.scale != 1:
			dst_img = self.resize(dst_img)
		#dst_img = self.quantize(dst_img)
		dst_img = cv2.GaussianBlur(dst_img, (5, 5), 0)
		try:
			dst_img_thresh = self.threshold(dst_img)
			(tl, tr, br, bl) = self.find_corners(dst_img_thresh)
		except IndexError:
			(tl, tr, br, bl) = self.find_corners(dst_img)

		# fix perspective
		dst_img = self.warp_perspective(self.image, tl, tr, br, bl)

		# classify board
		dst_img = cv2.cvtColor(dst_img, cv2.COLOR_BGR2GRAY)
		classifier = BoardClassifier()
		classification = classifier.make_classification_matrix(dst_img)
		for i in range(0,8):
			for j in range(0,8):
				print classification[i][j],
			print

		numeric_classification_matrix = classifier.make_numeric_classification_matrix(classification)
		for i in range(0,8):
			for j in range(0,8):
				print numeric_classification_matrix[i][j],
			print

		classifier.markup_board(dst_img)

		return numeric_classification_matrix

	def resize(self, img):
		new_dimensions = (int(self.dimensions[0] * 0.5), int(self.dimensions[1] * 0.5))
		return cv2.resize(img, new_dimensions)

	def grayscale(self, img):
		return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	def quantize(self, img):
		Z = img.reshape((-1, 3))
		Z = np.float32(Z)

		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
		K = 3

		if cv2.__version__.find("2.4.6") > -1:
			ret, label, center = cv2.kmeans(Z, K, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
		else:
			ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

		dst = np.uint8(center)
		dst = dst[label.flatten()]
		return dst.reshape((img.shape))

	def threshold(self, img):
		return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 0)
		#return cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)[1]
		#return cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)[1]

	def find_corners(self, img):
		contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		best_match = (None, 0)
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > 100:
				peri = cv2.arcLength(contour, True)
				approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
				if area > best_match[1] and len(approx) == 4:
					best_match = (contour, area)

		(tl, br), (tr, bl) = self.bounding_box(best_match[0])
		tl = self.find_nearest_point(tl, best_match[0])
		br = self.find_nearest_point(br, best_match[0])
		tr = self.find_nearest_point(tr, best_match[0])
		bl = self.find_nearest_point(bl, best_match[0])

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

def test_variance():
	dst_img = cv2.imread('board-pictures/test-variance.jpg')
	dst_img = cv2.cvtColor(dst_img, cv2.COLOR_BGR2GRAY)
	# classify board
	classifier = BoardClassifier()
	classification = classifier.make_classification_matrix(dst_img)
	for i in range(0,8):
		for j in range(0,8):
			print classification[i][j],
		print

	numeric_classification_matrix = classifier.make_numeric_classification_matrix(classification)
	for i in range(0,8):
		for j in range(0,8):
			print numeric_classification_matrix[i][j],
		print

	classifier.markup_board(dst_img)
	img_out.show(dst_img)

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "test":
			#ChessCV(scale=1, file_name='board-pictures/test-variance.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/1.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/2.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/3.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/4.jpg')
			test_variance()
		elif sys.argv[1] == "camera":
			while True:
				cv2.imshow('win1', next_frame())
				cv2.waitKey(0)
	else:
		ChessCV().current_board()