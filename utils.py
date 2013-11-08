import cv2, numpy as np, shlex, subprocess

def _get_frame(width=480, height=480):
	args = shlex.split("raspistill -w %d -h %d -t 0 -ev 6 -n -o -" % (width, height))
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	nparr = np.frombuffer(out, dtype='uint8')
	return cv2.imdecode(nparr, 1)

def next_frame():
	return _get_frame()

def comparison_frames():
	return [_get_frame(50, 50), _get_frame(50, 50)]

class ImgOut():
	counter = 1

	def save(self, img):
		if type(img) is list:
			for i in img:
				self.save(i)
		else:
			cv2.imwrite('board-%d.jpg' % self.counter, img)
			self.counter += 1
			return img

	def show(self, img):
		cv2.imshow('win1', img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		return img