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
			UserInterface.ROTATIONS_RIGHT = 0
		else:
			self.cv = ChessCV()
		self.cv.continuous = True
		thread.start_new_thread(self.cvThread, (self,))
		self.boardscan = np.ndarray(shape=(8,8), dtype=np.int8)
		self.boardscan.fill(0)
		self.chess = None
		self.lastFullScreenToggle = 0
		self.boardScale = 2
		self.considering = []
		self.lastConsider = None
		self.requestedMove = None
		self.dirtyUi = True
		pygame.init()
		#self.screen = pygame.display.set_mode((800, 800))
		#self.screen = pygame.display.set_mode((1824, 1016))
		self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

		self.bgimage = pygame.image.load("./img/background.png")
		self.light_sabers = pygame.image.load("./img/light_sabers2.png")
		self.would_you_like_to_play = pygame.image.load("./img/headings/would_you_like_to_play.png")
		self.checkmate_suckah = pygame.image.load("./img/headings/checkmate_suckah.png")
		self.my_turn = pygame.image.load("./img/headings/my_turn.png")
		self.my_turn_move_piece = pygame.image.load("./img/headings/my_turn_move_piece.png")
		self.one_moment_please = pygame.image.load("./img/headings/one_moment_please.png")
		self.would_you_like_to_play = pygame.image.load("./img/headings/would_you_like_to_play.png")
		self.your_turn = pygame.image.load("./img/headings/your_turn.png")
		self.your_turn_cheater = pygame.image.load("./img/headings/your_turn_cheater.png")

		self.check = pygame.image.load("./img/bottom_headers/check.png")
		self.checkmate_suckah = pygame.image.load("./img/bottom_headers/checkmate_suckah.png")

		self.topHeading = None
		self.bottomHeading = None
		self.boardbg = self.loadImage("board_v2.gif")
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

	def getFont(self, size):
		return pygame.font.SysFont("freesans", size, bold=True)

	def mainLoop(self):    
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
					if event.key == 102: # F
						if time.time() - self.lastFullScreenToggle > 1:
							self.lastFullScreenToggle = time.time() 
							pygame.display.toggle_fullscreen()
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
				self.topHeading = self.your_turn
				self.dirtyUi = True

				'''
				self.chess.addTextMove("e2e4")
				self.chess.addTextMove("e7e6")
				self.chess.addTextMove("d2d4")
				self.chess.addTextMove("d7d5")
				self.chess.addTextMove("b1c3")
				self.chess.addTextMove("f8b4")
				self.chess.addTextMove("e4e5")
				self.chess.addTextMove("c7c5")
				self.chess.addTextMove("a2a3")
				self.chess.addTextMove("b4c3")
				self.chess.addTextMove("b2c3")
				self.chess.addTextMove("b8c6")
				self.chess.addTextMove("g1f3")
				self.chess.addTextMove("g8e7")
				self.chess.addTextMove("f1e2")
				self.chess.addTextMove("e8g8")
				self.chess.addTextMove("e1g1")
				self.chess.addTextMove("c5c4")
				self.chess.addTextMove("a3a4")
				self.chess.addTextMove("c8d7")
				self.chess.addTextMove("c1a3")
				self.chess.addTextMove("d8a5")
				self.chess.addTextMove("a3b2")
				self.chess.addTextMove("f7f6")
				self.chess.addTextMove("d1d2")
				self.chess.addTextMove("f6e5")
				self.chess.addTextMove("d4e5")
				self.chess.addTextMove("e7g6")
				self.chess.addTextMove("d2g5")
				self.chess.addTextMove("f8f5")
				self.chess.addTextMove("g5e3")
				self.chess.addTextMove("c6e5")
				self.chess.addTextMove("f3g5")
				self.chess.addTextMove("e5g4")
				self.chess.addTextMove("e2g4")
				self.chess.addTextMove("f5e5")
				self.chess.addTextMove("e3d2")
				self.chess.addTextMove("a8f8")
				self.chess.addTextMove("f2f4")
				self.chess.addTextMove("g6f4")
				self.chess.addTextMove("f1f4")
				self.chess.addTextMove("h7h6")
				self.chess.addTextMove("g5f3")
				self.chess.addTextMove("e5e4")
				self.chess.addTextMove("g2g3")
				self.chess.addTextMove("e6e5")
				self.chess.addTextMove("f4f8")
				self.chess.addTextMove("g8f8")
				self.chess.addTextMove("g4d7")
				self.chess.addTextMove("d5d4")
				self.chess.addTextMove("c3d4")
				self.chess.addTextMove("a5c7")
				self.chess.addTextMove("f3e5")
				self.chess.addTextMove("f8e7")
				self.chess.addTextMove("b2a3")
				self.chess.addTextMove("e7d8")
				self.chess.addTextMove("a1f1")
				self.chess.addTextMove("c7b6")
				self.chess.addTextMove("f1f8")
				'''

				self.state = UserInterface.STATE_WAITING_FOR_BOARD_CHANGE
		elif self.state == UserInterface.STATE_WAITING_FOR_ENGINE:
			if self.engine.bestmove is not None:
				self.requestedMove = self.engine.bestmove
				self.considering = []
				self.state = UserInterface.STATE_WAITING_FOR_BOARD_CHANGE
				self.topHeading = self.my_turn_move_piece
				self.dirtyUi = True
			self.renderBoard()
		elif self.state == UserInterface.STATE_WAITING_FOR_BOARD_CHANGE:
			changes = self.boardscan - self.lastBoardscan
			numChanges = np.count_nonzero(changes)
			if numChanges == 2 or numChanges == 3 or numChanges == 4:
				self.dirtyUi = True
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
						cheater = False
						if self.requestedMove is not None and self.requestedMove != lastMove:
							cheater = True
						if self.chess.isCheck():
							print "**** CHECK ****"
							self.bottomHeading = self.check
						else:
							self.bottomHeading = None
						self.requestedMove = None
						self.lastBoardscan = self.boardscan
						self.chess.printBoard()
						print "Last move type: " + str(self.chess.getLastMoveType())
						print "New FEN: " + self.chess.getFEN()
						# Check if game is over
						if self.chess.isGameOver():
							result = self.chess.getGameResult()
							if result == ChessBoard.WHITE_WIN:
								print "**** WHITE WINS ****"
							elif result == ChessBoard.BLACK_WIN:
								print "**** BLACK WINS ****"
								self.bottomHeading = self.checkmate_suckah
							else:
								print "**** STALEMATE ****"
							self.state = UserInterface.STATE_GAME_OVER
						elif self.chess.getTurn() == ChessBoard.BLACK:
							# It's black's turn, engage the engine
							self.topHeading = self.one_moment_please
							self.engine.makeMove(self.chess.getFEN())
							self.state = UserInterface.STATE_WAITING_FOR_ENGINE
						else:
							if cheater:
								self.topHeading = self.your_turn_cheater
							else:
								self.topHeading = self.your_turn
						self.renderBoard()

			elif numChanges != 0:
				print "Invalid number of board changes: ", numChanges
			# Set boardscan to the last one just so we don't keep analyzing it until next scan comes in
			self.boardscan = self.lastBoardscan
			self.renderBoard()


	def updateConsideringLine(self):
		now = time.time()
		engine_considering = self.engine.considering
		#if self.state == UserInterface.STATE_WAITING_FOR_ENGINE and engine_considering is not None and (self.lastConsider is None or (now - self.lastConsider > 0.1)):
		if self.state == UserInterface.STATE_WAITING_FOR_ENGINE and engine_considering is not None:
			if len(self.engine.considering) > 0:
				latest = engine_considering[0]
				if len(latest) == 0:
					engine_considering.pop()
					self.considering = []
					self.updateConsideringLine()
					return
				self.considering.append(latest.pop())
			self.lastConsider = now
			self.dirtyUi = True
			self.renderBoard()


	def renderBoard(self):

		if not self.dirtyUi:
			return

		self.dirtyUi = False

		self.screen.blit(self.bgimage, (0,0))
		if self.chess is None:
			self.screen.blit(self.would_you_like_to_play, (587, 395))
			pygame.display.flip()
			return
			
		files = 'abcdefgh'
		boardOffsetX = 64
		boardOffsetY = 64
		square_size = self.pieces['r'].get_rect().w

		# First the background
		bgsize = self.boardbg.get_rect().w
		for y in range(4):
			for x in range(4):
				self.screen.blit(self.boardbg, (boardOffsetX+x*bgsize, boardOffsetY+y*bgsize))

		# Render the pieces
		y = 0
		for rank in self.chess.getBoard():
			x = 0
			for p in rank:
				if p != '.':
					self.screen.blit(self.pieces[p],(boardOffsetX+x*square_size, boardOffsetY+y*square_size))
				x += 1
			y += 1

		# Heading
		if self.topHeading is not None:
			self.screen.blit(self.topHeading, (1105, 84))

		# Sabers
		self.screen.blit(self.light_sabers, (1105, 84 + 140))

		# Render considering moves (if any)
		if len(self.considering) > 0:
			for move in self.considering:
				x1 = boardOffsetX+files.find(move[0])*square_size+int(square_size/2)
				y1 = boardOffsetY+((8-int(move[1]))*square_size)+int(square_size/2)
				x2 = boardOffsetX+files.find(move[2])*square_size+int(square_size/2)
				y2 = boardOffsetY+((8-int(move[3]))*square_size)+int(square_size/2)
				pygame.draw.line(self.screen, (164, 119, 131), (x1,y1), (x2,y2), 15)
				pygame.draw.circle(self.screen, (127, 91, 102), (x1,y1), 15)
				pygame.draw.circle(self.screen, (127, 91, 102), (x2,y2), 15)

		# Render requested move (if any)
		if self.requestedMove is not None:
			x1 = boardOffsetX+files.find(self.requestedMove[0])*square_size+int(square_size/2)
			y1 = boardOffsetY+((8-int(self.requestedMove[1]))*square_size)+int(square_size/2)
			x2 = boardOffsetX+files.find(self.requestedMove[2])*square_size+int(square_size/2)
			y2 = boardOffsetY+((8-int(self.requestedMove[3]))*square_size)+int(square_size/2)
			pygame.draw.line(self.screen, (229, 72, 84), (x1,y1), (x2,y2), 15)
			pygame.draw.circle(self.screen, (173, 58, 75), (x2,y2), 15)
			# Redraw piece on "from" square so line comes from underneath it (but covers other pieces, potentially)
			y = 8-int(self.requestedMove[1])
			x = files.find(self.requestedMove[0])
			piece = self.chess.getBoard()[y][x]
			self.screen.blit(self.pieces[piece],(boardOffsetX+x*square_size, boardOffsetY+y*square_size))

		# Top heading

		# Bottom heading
		if self.bottomHeading is not None:
			self.screen.blit(self.bottomHeading, (1105, 84 + 140 + 165 + 403))

		# Render chess moves
		color = (255, 255, 255)
		x = 1105
		startY = 84 + 140 + 165
		y = startY
		font = self.getFont(20)
		allMoves = self.chess.getAllTextMoves(ChessBoard.LAN)
		if allMoves is not None:
			whiteMoves = allMoves[0::2]
			blackMoves = allMoves[1::2]
			num = 1
			for move in whiteMoves:
				txt = "%d.  %s" % (num, move)
				if num < 10:
					txt = " " + txt
				fs = font.render(txt, True, color)
				self.screen.blit(fs, (x, y))
				y += 25
				num = num + 1
				if y > startY + 403:
					break
			x += 200
			y = startY
			for move in blackMoves:
				fs = font.render(move, True, color)
				self.screen.blit(fs, (x, y))
				y += 25
				if y > startY + 403:
					break


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
