import cv2, numpy as np, sys, time
from utils import ImgOut, next_frame
from boardClassifier import BoardClassifier

img_out = ImgOut()

class Timer():
	_start_times = {}
	_end_times = {}
	_last_key = None

	# starts a key-bound timer
	def start(self, key):
		self._start_times[key] = time.time()
		if self._last_key is not None:
			self._end_times[self._last_key] = time.time()
		self._last_key = key

	# stops previously started timer
	def clock(self):
		if self._last_key is not None:
			self._end_times[self._last_key] = time.time()
		self._last_key = None

	# stops all active timers and prints durations
	def done(self):
		for k in self._start_times:
			if k not in self._end_times:
				diff = time.time() - self._start_times[k]
			else:
				diff = self._end_times[k] - self._start_times[k]
			print "[%s]: %dms" % (k, int(diff * 1000))

class ChessCV():

	def __init__(self, scale=1, file_name=None):
		self.scale = scale
		self.file_name = file_name

	def current_board(self):
		timer = Timer()
		timer.start("Image read")
		self.image = cv2.imread(self.file_name) if self.file_name is not None else next_frame()
		self.dimensions = (len(self.image[0]), len(self.image))

		# find corners of board
		timer.start("Grayscale")
		dst_img = self.grayscale(self.image)
		if self.scale != 1:
			timer.start("Resize")
			dst_img = self.resize(dst_img)
		#dst_img = self.quantize(dst_img)
		timer.start("Gaussian blur")
		dst_img = cv2.GaussianBlur(dst_img, (5, 5), 0)
		try:
			timer.start("Threshold")
			dst_img_thresh = self.threshold(dst_img)
			timer.start("Find corners")
			(tl, tr, br, bl) = self.find_corners(dst_img_thresh)
		except IndexError:
			timer.start("Find corners (2)")
			(tl, tr, br, bl) = self.find_corners(dst_img)

		# fix perspective
		timer.start("Warp perspective")
		dst_img = self.warp_perspective(self.image, tl, tr, br, bl)

		# classify board
		timer.start("Classify board")
		dst_img = cv2.cvtColor(dst_img, cv2.COLOR_BGR2GRAY)
		classifier = BoardClassifier()
		classification = classifier.make_classification_matrix(dst_img)
		for i in range(0,8):
			for j in range(0,8):
				print classification[i][j],
			print

		numeric_classification_matrix = classifier.make_numeric_classification_matrix(classification)

		timer.done()
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
		timer = Timer()
		timer.start("Find Contours")
		contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		timer.start("Find Largest")
		best_match = (None, 0, None)
		for contour in contours:
			area = cv2.contourArea(contour)
			if area > 100:
				peri = cv2.arcLength(contour, True)
				approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
				if area > best_match[1] and len(approx) == 4:
					best_match = (contour, area, approx)

		mean_point = np.average(best_match[2], axis=0)[0]

		timer.start("Match polygon points")
		tl, br, tr, bl = (None, None, None, None)
		for point in best_match[2]:
			point = point[0]
			if point[0] < mean_point[0]:
				if point[1] < mean_point[1]:
					tl = point
				elif point[1] > mean_point[1]:
					bl = point
			elif point[0] > mean_point[0]:
				if point[1] < mean_point[1]:
					tr = point
				elif point[1] > mean_point[1]:
					br = point

		timer.done()
		return (tl, tr, br, bl)

	def warp_perspective(self, img, tl, tr, br, bl):
		x = lambda y: (y[0] / self.scale, y[1] / self.scale)
		matrix = cv2.getPerspectiveTransform(np.array([x(tl), x(tr), x(br), x(bl)], np.float32), \
											 np.array([[0, 0], [499, 0], [499, 499], [0, 499]], np.float32))
		return cv2.warpPerspective(img, matrix, (500, 500))

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
			ChessCV(scale=1, file_name='board-pictures/640-480/1.jpg').current_board()
			#ChessCV(scale=1, file_name='board-pictures/640-480/2.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/3.jpg')
			#ChessCV(scale=1, file_name='board-pictures/640-480/4.jpg')
			#test_variance()
		elif sys.argv[1] == "camera":
			while True:
				cv2.imshow('win1', next_frame())
				cv2.waitKey(0)
	else:
		ChessCV().current_board()