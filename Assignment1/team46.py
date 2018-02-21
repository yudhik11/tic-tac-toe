import sys
import random
import datetime
import copy

class Player46:
	def __init__(self):
		self.INF = int(1e9)
		self.maxmove = False
		self.timeLimit = datetime.timedelta(seconds = 2.5)
		self.begin = 0
		self.mark = 'x'
		self.zobrist= []
		self.transpositionTable = {}
		self.index = 0
		for i in range(0, 16):
			self.zobrist.append([])
			for j in range(0, 16):
				self.zobrist[i].append([])
				for k in range(0, 17):
					self.zobrist[i][j].append([])
					for l in range(0, 17):
						self.zobrist[i][j][k].append([])
						for m in range(0, 2):
							self.zobrist[i][j][k][l].append(random.randint(0, 2**64))

	def move(self, board, old_move, flag):
		self.mark = flag
		board_copy = copy.deepcopy(board)
		curr = copy.deepcopy(old_move)
		self.begin = datetime.datetime.utcnow()
		ans = self.IDS(curr)
		return ans

	def check_time(self):
		if datetime.datetime.utcnow() - self.begin > self.timeLimit:
			return True
		return False

	def IDS(self, root):
		guess = 0
		for depth in range(1, 500):
			self.transpositionTable = {}
			guess, move = self.MTDF(root, guess, depth)
			if self.check_time():
				break
			saved_move = move
		return saved_move

	def MTDF(self, root, guess, depth):
		g = guess
	    upperbound = self.INF
	    lowerbound = -self.INF
	    while lowerbound < upperbound
	        if g == lowerbound:
	        	beta = g + 1
	        else:
	        	beta = g
	        self.index = 0
	        self.maxmove = True
	        g = AlphaBetaWithMemory(root, beta - 1, beta, d)
	        if check_time():
	        	retrun g, move
	        if g < beta:
	        	upperbound = g
	        else:
	        	lowerbound = g
	    return g, move

	def calcZobristHash(self, root):
		h = 0
		bs = board.board_status
		for i in range(0, 16):
			for j in range(0, 16):
				if bs[i][j] == 'x':
					h = h^self.zobrist[i][j][root[0]+1][root[1]+1][0]
				elif bs[i][j] == 'o':
					h = h^self.zobrist[i][j][root[0]+1][root[1]+1][1]
		return h

	def cantorPairing(self, a, b):
		return (a + b)*(a + b + 1)/2 + b

	def AlphaBetaWithMemory(self, root, alpha, beta, depth):
		board_hash = self.calcZobristHash(root)
		loweridx = self.cantorPairing(board_hash, 1)
		upperidx = self.cantorPairing(board_hash, 2)
