#!/usr/bin/env python

from ChessBoard import ChessBoard
from ChessEngine import ChessEngine
from board_processing import ChessCV
from MockCV import MockCV

import os, pygame, math, random, time, thread, sys, string
import numpy as np
from pygame.locals import *

class UserInterface:

	ROTATIONS_RIGHT = 2

	STATE_WAITING_FOR_START_POS = 0
	STATE_WAITING_FOR_BOARD_CHANGE = 1
	STATE_WAITING_FOR_ENGINE = 2
	STATE_GAME_OVER = 3

	def __init__(self):
		self.state = UserInterface.STATE_WAITING_FOR_START_POS
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
		if sys.platform == 'darwin':
			self.cv = MockCV()
		else:
			self.cv = ChessCV()
		self.cv.continuous = True
		thread.start_new_thread(self.cvThread, (self,))
		self.boardscan = np.ndarray(shape=(8,8), dtype=np.int8)
		self.boardscan.fill(0)
		self.chess = None
		self.boardScale = 1.5
		self.considering = []
		self.lastConsider = None
		self.requestedMove = None
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

			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN:
					print event.key
					if event.key == K_ESCAPE:
						return
					if event.key == 32: # space
						self.cv.snapshot = True
					if event.key == 49:	# 1
						self.cv.set_board(self.startingPos.copy())
					if event.key == 50:	# 2
						self.cv.set_board(np.array(
							[[-1,-1,-1,-1,-1,-1,-1,-1],
							[-1,-1,-1,-1,-1,-1,-1,-1],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 1, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 1, 1, 1, 1, 0, 1, 1, 1],
							[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8))
					if event.key == 51:	# 3
						self.cv.set_board(np.array(
							[[-1,-1,-1,-1,-1,-1,-1,-1],
							[-1,-1,-1, 0,-1,-1,-1,-1],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0,-1, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 1, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 1, 1, 1, 1, 0, 1, 1, 1],
							[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8))
					if event.key == 52:	# 4
						self.cv.set_board(np.array(
							[[-1,-1,-1,-1,-1,-1,-1,-1],
							[-1,-1,-1, 0,-1,-1,-1,-1],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 1, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 0, 0, 0, 0, 0, 0, 0, 0],
							[ 1, 1, 1, 1, 0, 1, 1, 1],
							[ 1, 1, 1, 1, 1, 1, 1, 1]], np.int8))
			self.gameTick()


	def gameTick(self):
		self.updateConsideringLine()
		if self.state == UserInterface.STATE_WAITING_FOR_START_POS:
			if np.array_equal(self.boardscan, self.startingPos):
				print "NEW GAME: Creating chess board"
				self.chess = ChessBoard()
				self.lastBoardscan = self.boardscan
				self.engine.newGame()
				self.state = UserInterface.STATE_WAITING_FOR_BOARD_CHANGE
		elif self.state == UserInterface.STATE_WAITING_FOR_ENGINE:
			if self.engine.bestmove is not None:
				self.requestedMove = self.engine.bestmove
				self.considering = []
				self.state = UserInterface.STATE_WAITING_FOR_BOARD_CHANGE
			self.renderBoard()
		elif self.state == UserInterface.STATE_WAITING_FOR_BOARD_CHANGE:
			changes = self.boardscan - self.lastBoardscan
			numChanges = np.count_nonzero(changes)
			if numChanges == 2 or numChanges == 3 or numChanges == 4:
				print ""
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
				if moveFrom and moveTo:
					print "getTurn before:", self.chess.getTurn()
					result = self.chess.addMove(moveFrom, moveTo)
					print "getTurn after:", self.chess.getTurn()
					if result is False:
						print "Could not make move: ", self.chess.getReason()
					else:
						lastMove = string.replace(self.chess.getLastTextMove(ChessBoard.AN), '-', '')
						if self.requestedMove is not None and self.requestedMove != lastMove:
							print "**** CHEATER!!! ****"
						if self.chess.isCheck():
							print "**** CHECK ****"
						self.requestedMove = None
						self.lastBoardscan = self.boardscan
						self.chess.printBoard()
						print "Last move type: " + str(self.chess.getLastMoveType())
						self.renderBoard()
						print "New FEN: " + self.chess.getFEN()
						# Check if game is over
						if self.chess.isGameOver():
							result = self.chess.getGameResult()
							if result == ChessBoard.WHITE_WIN:
								print "**** WHITE WINS ****"
							elif result == ChessBoard.BLACK_WIN:
								print "**** BLACK WINS ****"
							else:
								print "**** STALEMATE ****"
							self.state = UserInterface.STATE_GAME_OVER
						elif self.chess.getTurn() == ChessBoard.BLACK:
							# It's not black's turn, engage the engine
							self.engine.makeMove(self.chess.getFEN())
							self.state = UserInterface.STATE_WAITING_FOR_ENGINE
			elif numChanges != 0:
				print "Invalid number of board changes: ", numChanges
			# Set boardscan to the last one just so we don't keep analyzing it until next scan comes in
			self.boardscan = self.lastBoardscan
			self.renderBoard()


	def updateConsideringLine(self):
		now = time.time()
		engine_considering = self.engine.considering
		if self.state == UserInterface.STATE_WAITING_FOR_ENGINE and engine_considering is not None and (self.lastConsider is None or (now - self.lastConsider > 0.1)):
			if len(self.engine.considering) > 0:
				latest = engine_considering[0]
				if len(latest) == 0:
					engine_considering.pop()
					self.considering = []
					self.updateConsideringLine()
					return
				self.considering.append(latest.pop())
			self.lastConsider = now

	def displayMoveToMakeForComputer(self, move):
		print "********* PLEASE MAKE MOVE: ", move


	def renderBoard(self):

		if self.chess is None:
			return
			
		files = 'abcdefgh'
		boardOffsetX = 64
		boardOffsetY = 64
		square_size = self.pieces['r'].get_rect().w

		# First the background
		bgsize = self.bgimage.get_rect().w
		for y in range(4):
			for x in range(4):
				self.screen.blit(self.bgimage, (boardOffsetX+x*bgsize, boardOffsetY+y*bgsize))

		# Render the pieces
		y = 0
		for rank in self.chess.getBoard():
			x = 0
			for p in rank:
				if p != '.':
					self.screen.blit(self.pieces[p],(boardOffsetX+x*square_size, boardOffsetY+y*square_size))
				x += 1
			y += 1

		# Render considering moves (if any)
		if len(self.considering) > 0:
			for move in self.considering:
				x1 = boardOffsetX+files.find(move[0])*square_size+int(square_size/2)
				y1 = boardOffsetY+((8-int(move[1]))*square_size)+int(square_size/2)
				x2 = boardOffsetX+files.find(move[2])*square_size+int(square_size/2)
				y2 = boardOffsetY+((8-int(move[3]))*square_size)+int(square_size/2)
				pygame.draw.line(self.screen, (0, 255, 0), (x1,y1), (x2,y2), 15)
				pygame.draw.circle(self.screen, (255, 0, 0), (x1,y1), 15)
				pygame.draw.circle(self.screen, (0, 0, 255), (x2,y2), 15)

		# Render requested move (if any)
		if self.requestedMove is not None:
			x1 = boardOffsetX+files.find(self.requestedMove[0])*square_size+int(square_size/2)
			y1 = boardOffsetY+((8-int(self.requestedMove[1]))*square_size)+int(square_size/2)
			x2 = boardOffsetX+files.find(self.requestedMove[2])*square_size+int(square_size/2)
			y2 = boardOffsetY+((8-int(self.requestedMove[3]))*square_size)+int(square_size/2)
			pygame.draw.line(self.screen, (255, 0, 0), (x1,y1), (x2,y2), 15)
			pygame.draw.circle(self.screen, (255, 0, 0), (x2,y2), 15)
			# Redraw piece on "from" square so line comes from underneath it (but covers other pieces, potentially)
			y = 8-int(self.requestedMove[1])
			x = files.find(self.requestedMove[0])
			piece = self.chess.getBoard()[y][x]
			self.screen.blit(self.pieces[piece],(boardOffsetX+x*square_size, boardOffsetY+y*square_size))


		pygame.display.flip()

				
	def cvThread(self, cv):
		while True:
			try:
				if self.state == UserInterface.STATE_WAITING_FOR_BOARD_CHANGE or self.state == UserInterface.STATE_WAITING_FOR_START_POS:
					if self.cv.continuous == True or self.cv.snapshot == True:
						self.cv.snapshot = False
						sys.stdout.write('.')
						sys.stdout.flush()
						board = self.cv.current_board()
						if board is not None:
							self.boardscan = np.rot90(board, UserInterface.ROTATIONS_RIGHT)
			except Exception, e:
				print e
			time.sleep(0.25)


def main():
	ui = UserInterface()
	ui.mainLoop()


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
