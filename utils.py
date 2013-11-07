import cv2, numpy as np, shlex, subprocess

def next_frame():
	args = shlex.split("raspistill -w 640 -h 480 -t 1000 -o -")
	p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	nparr = np.frombuffer(out, dtype='uint8')
	return cv2.imdecode(nparr, 1)

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