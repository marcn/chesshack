#!/usr/bin/env python

import sys, subprocess, thread

class ChessEngine:

	def __init__(self):
		self.bestmove = None
		self.considering = []
		path = r'/usr/local/bin/stockfish'
		self.pipe = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
		self.pipe.stdout.readline()	# Chess engine identifies itself, we just ignore
		self.pipe.stdin.write('uci\n')		# UCI mode
		self.waitFor('uciok')
		self.pipe.stdin.write('setoption name Skill Level value 20\n')	# Maximum difficulty!


	def waitFor(self, startsWith):
		while True:
			text = self.pipe.stdout.readline().strip()
			#print(text)
			parts = text.split()
			if parts.count('pv') > 0:
				self.considering.append(parts[parts.index('pv')+1:])
			if text.find(startsWith) == 0:
				return text

	def newGame(self):
		self.pipe.stdin.write('ucinewgame\n')		# new game, engine doesn't reply

	# Ask the computer to make a move
	def makeMove(self, fen):
		self.bestmove = None
		self.pipe.stdin.write('position fen %s\n' % fen)	# set current position
		self.pipe.stdin.write('go movetime 10000\n')	# set current position
		thread.start_new_thread(self.waitForBestMove, (self,))

	def waitForBestMove(self, blah):
		print "self is: " + str(self)
		self.bestmove = self.waitFor('bestmove').split()[1]
		
