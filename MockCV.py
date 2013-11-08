
import numpy as np

class MockCV():

	def __init__(self):
		self.board = np.ndarray(shape=(8,8), dtype=np.int8).fill(0)

	def current_board(self):
		return self.board

	def set_board(self, board):
		self.board = board
