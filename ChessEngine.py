#!/usr/bin/env python

import sys, subprocess

class ChessEngine:

	def __init__(self):
		path = r'/Users/marc/devtools/bin/stockfish'.split()['linux' in sys.platform]
		self.pipe = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
		print self.pipe.stdout.readline()	# Chess engine identifies itself, we just ignore
		self.pipe.stdin.write('uci\n')		# UCI mode
		self.waitFor('uciok')
		self.pipe.stdin.write('setoption name Skill Level value 20\n')	# Maximum difficulty!


	def waitFor(self, startsWith):
		while True:
			text = self.pipe.stdout.readline().strip()
			print(text)
			if text.find(startsWith) == 0:
				return text

