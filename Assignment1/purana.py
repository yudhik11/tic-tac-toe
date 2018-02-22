import random
import datetime
import copy

class Player46:

	def __init__(self):
        self.begin = 0
        self.timer = 0
		self.timelimit = datetime.timedelta(seconds=2.5)
        self.depth = 4
        self.cnt = 0

    def check_timer(self, exp):
        if exp - self.begin > self.timelimit :
        	return True
        return False

    def minimax(self,board,old_move,alpha,beta,maxim,flag,depthi,depth,initial):
    	if self.check_timer(datetime.datetime.utcnow()):
    		return (0, (-1, -1))
    	else:
    		check_end = board.find_terminal_state()
    		if check_end[1] == "WON":
    			if check_end[0] == flag:
    				return (10000, old_move)
    			return (-10000, old_move)

    		if initial_depth == depth


    def move(self ,board, old_move, flag):
    	self.begin = datetime.datetime.utcnow()
    	global initial_depth
    	initial_depth = 0
    	while self.check_timer(datetime.datetime.utcnow()) == False and self.initial_depth < 8:
    		optimal = self.minimax(board, old_move, int(1e9) , -int(1e9), 1, flag, 0, (5,7))
    		index = ()
    		if optimal[1] != (-1,-1):
    			index = optimal[1]
    		initial_depth += 1
    	return index




