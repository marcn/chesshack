#!/usr/bin/env python

from ChessBoard import ChessBoard
from ChessEngine import ChessEngine
from board_processing import ChessCV

import os, pygame, math, random, time
import numpy as np
from pygame.locals import *

class UserInterface:

	def __init__(self):
		self.engine = ChessEngine()
		self.startingPos = np.array(
			[[-1,-1,-1,-1,-1,-1,-1,-1],
			[-1,-1,-1,-1,-1,-1,-1,-1],
			[ 0, 0, 0, 0, 0, 0, 0, 0],
			[ 0, 0, 0, 0, 0, 0, 0, 0],
			[ 0, 0, 0, 0, 0, 0, 0, 0],
			[ 0, 0, 0, 0, 0, 0, 0, 0],
			[ 1, 1, 1, 1, 1, 1, 1, 1],
			[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8)

		# Eventually self.boardscan will be set by the CV code, just mocked for now
		self.cv = ChessCV()
		self.boardscan = np.ndarray(shape=(8,8), dtype=np.int8)
		self.boardscan.fill(0)
		self.chess = None
		self.boardScale = 1.5
		self.considering = []
		self.lastConsider = None
		self.waitingForEngine = False
		self.screen = pygame.display.set_mode((800, 800))
		#self.screen = pygame.display.set_mode((1824, 1016))
		#self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
		self.bgimage = self.loadImage("53.png")
		self.pieces = {}
		self.pieces['r'] = self.loadImage("br.png")
		self.pieces['n'] = self.loadImage("bn.png")
		self.pieces['b'] = self.loadImage("bb.png")
		self.pieces['k'] = self.loadImage("bk.png")
		self.pieces['q'] = self.loadImage("bq.png")
		self.pieces['p'] = self.loadImage("bp.png")
		self.pieces['R'] = self.loadImage("wr.png")
		self.pieces['N'] = self.loadImage("wn.png")
		self.pieces['B'] = self.loadImage("wb.png")
		self.pieces['K'] = self.loadImage("wk.png")
		self.pieces['Q'] = self.loadImage("wq.png")
		self.pieces['P'] = self.loadImage("wp.png")
		pygame.display.flip()

	def loadImage(self, file):
		img = pygame.image.load("./img/%s" % file).convert(32, pygame.SRCALPHA)
		rect = img.get_rect()
		return pygame.transform.smoothscale(img, (int(rect.w * self.boardScale), int(rect.h * self.boardScale)))

	def mainLoop(self):    
		pygame.init()
		clock = pygame.time.Clock()
		self.renderBoard()

		while 1:
			clock.tick(30)
			#self.renderBoard()

			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN:
					print event.key
					if event.key == K_ESCAPE:
						return
					if event.key == 32: # space
						self.boardscan = self.cv.current_board()
					if event.key == 49:	# 1
						self.boardscan = self.startingPos.copy()
					if event.key == 50:	# 2
						self.boardscan = np.array(
							[[-1,-1,-1,-1,-1,-1,-1,-1],
							[-1,-1,-1,-1,-1,-1,-1,-1],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 1, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 1, 1, 1, 1, 0, 1, 1, 1],
							[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8)
					if event.key == 51:	# 3
						self.boardscan = np.array(
							[[-1,-1,-1,-1,-1,-1,-1,-1],
							[-1,-1,-1, 0,-1,-1,-1,-1],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0,-1, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 1, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 1, 1, 1, 1, 0, 1, 1, 1],
							[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8)
			self.readBoard()


	def readBoard(self):
		self.updateConsideringLine()
		if np.array_equal(self.boardscan, self.startingPos) and self.chess is None:
			print "creating chess board"
			self.chess = ChessBoard()
			self.lastBoardscan = self.boardscan
			self.engine.newGame()
		elif self.chess is not None and self.chess.getTurn() == ChessBoard.BLACK:
			print "self.engine.bestmove = " + str(self.engine.bestmove)
			if self.waitingForEngine and self.engine.bestmove is not None:
				self.waitingForEngine = False
				self.considering = []
				print "calling addTextMove with:", self.engine.bestmove
				#self.chess.addTextMove(self.engine.bestmove)
			self.renderBoard()
		else:
			if self.chess is None:
				self.showWaitingForGameToStart()
				return
			changes = self.boardscan - self.lastBoardscan
			numChanges = np.count_nonzero(changes)
			if numChanges > 0:
				print "changes:\n" + str(changes)
				moveFrom = ()
				moveTo = ()
				nonzeroChanges = changes.nonzero()
				print "nonzeroChanges: " + str(nonzeroChanges)
				print "len(nonzeroChanges[0]) = %d" % len(nonzeroChanges[0])
				for i in range(len(nonzeroChanges[0])):
					change = (nonzeroChanges[1][i], nonzeroChanges[0][i])
					value = changes[change[1], change[0]]
					colorBefore = self.lastBoardscan[change[1], change[0]]
					print "\tchange: %s\tvalue: %s\tcolorBefore: %s" % (str(change), value, colorBefore)
					if self.chess.getTurn() == ChessBoard.WHITE:
						# WHITE's turn
						if value == -1:
							if numChanges != 4 or (change == (4,7)):
								moveFrom = change
						else:
							if numChanges == 4:
								if change == (6,7) or change == (2,7):
									moveTo = change
							elif numChanges == 3:
								if colorBefore == 0:
									moveTo = change
							else:
								moveTo = change
					else:
						# BLACK's turn
						if value == 1:
							if numChanges != 4 or (change == (4,0)):
								print "setting moveFrom to ", change
								moveFrom = change
						else:
							if numChanges == 4:
								if change == (6,0) or change == (2,0):
									print "setting moveTo to ", change
									moveTo = change
							elif numChanges == 3:
								if colorBefore == 0:
									print "setting moveTo to ", change
									moveTo = change
							else:
								moveTo = change
				print "moveFrom: " + str(moveFrom)
				print "moveTo:   " + str(moveTo)
				print "getTurn before:", self.chess.getTurn()
				result = self.chess.addMove(moveFrom, moveTo)
				print "getTurn after:", self.chess.getTurn()
				if result is False:
					print "Could not make move: ", self.chess.getReason()
				self.chess.printBoard()
				print "Last move type: " + str(self.chess.getLastMoveType())
				self.renderBoard()
				print "New FEN: " + self.chess.getFEN()
				self.waitingForEngine = True
				self.engine.makeMove(self.chess.getFEN())
			self.lastBoardscan = self.boardscan
			self.renderBoard()


	def updateConsideringLine(self):
		now = time.time()
		engine_considering = self.engine.considering
		if self.waitingForEngine and engine_considering is not None and (self.lastConsider is None or (now - self.lastConsider > 0.1)):
			if len(self.engine.considering) > 0:
				latest = engine_considering[0]
				if len(latest) == 0:
					engine_considering.pop()
					self.considering = []
					self.updateConsideringLine()
					return
				self.considering.append(latest.pop())
			self.lastConsider = now

	def showWaitingForGameToStart(self):
		pass

	def renderBoard(self):

		if self.chess is None:
			return
			
		boardOffsetX = 64
		boardOffsetY = 64

		# First the background
		bgsize = self.bgimage.get_rect().w
		for y in range(4):
			for x in range(4):
				self.screen.blit(self.bgimage, (boardOffsetX+x*bgsize, boardOffsetY+y*bgsize))

		# Render the pieces
		y = 0
		square_size = self.pieces['r'].get_rect().w
		for rank in self.chess.getBoard():
			x = 0
			for p in rank:
				#p = random.choice(('.','.','.','.','r','n','b','k','q','p','R','N','B','K','K','Q','P'))
				if p != '.':
					self.screen.blit(self.pieces[p],(boardOffsetX+x*square_size, boardOffsetY+y*square_size))
				x += 1
			y += 1

		# Render considering moves (if any)
		if len(self.considering) > 0:
			files = 'abcdefgh'
			for move in self.considering:
				x1 = boardOffsetX+files.find(move[0])*square_size+int(square_size/2)
				y1 = boardOffsetY+((8-int(move[1]))*square_size)+int(square_size/2)
				x2 = boardOffsetX+files.find(move[2])*square_size+int(square_size/2)
				y2 = boardOffsetY+((8-int(move[3]))*square_size)+int(square_size/2)
				pygame.draw.line(self.screen, (0, 255, 0), (x1,y1), (x2,y2), 15)
				pygame.draw.circle(self.screen, (255, 0, 0), (x1,y1), 15)
				pygame.draw.circle(self.screen, (0, 0, 255), (x2,y2), 15)


		pygame.display.flip()

				


def main():
	ui = UserInterface()
	ui.mainLoop()


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
