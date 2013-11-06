import cv2

class ImgOut():
	counter = 1

	def save(self, img):
		if type(img) is list:
			for i in img:
				self.save(i)
		else:
			cv2.imwrite('board-%d.jpg' % self.counter, img)
			self.counter += 1