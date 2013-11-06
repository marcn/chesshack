#!/usr/bin/env python

from ChessBoard import ChessBoard

import os, pygame, math, random
from pygame.locals import *

class UserInterface:

	def __init__(self):
		self.bgimage = pygame.image.load("./img/53.gif")
		self.pieces = {}
		self.pieces['r'] = pygame.image.load("./img/br.png")
		self.pieces['n'] = pygame.image.load("./img/bn.png")
		self.pieces['b'] = pygame.image.load("./img/bb.png")
		self.pieces['k'] = pygame.image.load("./img/bk.png")
		self.pieces['q'] = pygame.image.load("./img/bq.png")
		self.pieces['p'] = pygame.image.load("./img/bp.png")
		self.pieces['R'] = pygame.image.load("./img/wr.png")
		self.pieces['N'] = pygame.image.load("./img/wn.png")
		self.pieces['B'] = pygame.image.load("./img/wb.png")
		self.pieces['K'] = pygame.image.load("./img/wk.png")
		self.pieces['Q'] = pygame.image.load("./img/wq.png")
		self.pieces['P'] = pygame.image.load("./img/wp.png")
		self.chess = ChessBoard()
		self.board = self.chess.getBoard()
		self.turn = self.chess.getTurn()
		#self.screen = pygame.display.set_mode((1824, 1016),1)
		self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

	def mainLoop(self):    
		pygame.init()
		clock = pygame.time.Clock()

		while 1:
			clock.tick(30)
			self.renderBoard()

			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						return


	def renderBoard(self):

		boardOffsetX = 64
		boardOffsetY = 64

		# First the background
		for y in range(4):
			for x in range(4):
				self.screen.blit(self.bgimage, (boardOffsetX+x*106, boardOffsetY+y*106))

		# Render the pieces
		y = 0
		for rank in self.board:
			x = 0
			for p in rank:
				#p = random.choice(('.','.','.','.','r','n','b','k','q','p','R','N','B','K','K','Q','P'))
				if p != '.':
					self.screen.blit(self.pieces[p],(boardOffsetX+x*53, boardOffsetY+y*53))
				x += 1
			y += 1             

		pygame.display.flip()

				


def main():
	ui = UserInterface()
	ui.mainLoop()


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
