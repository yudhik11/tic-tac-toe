import random
import datetime
import copy

class Player46:
    def __init__(self):
        self.INF = int(1e9)
        self.maxmove = False
        self.timeLimit = datetime.timedelta(seconds = 0.8)
        self.begin = 0
        self.mark = 'x'
        self.zobrist= []
        self.transpositionTable = {}
        self.index = 0
        self.moveOrder = dict()
        self.depth = 0
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
        global board_copy
        board_copy = copy.deepcopy(board)
        curr = copy.deepcopy(old_move)
        self.begin = datetime.datetime.utcnow()
        ans = self.IDS(curr)
        return ans
    
    def revertBoard(self, root, blockVal):
        board_copy.board_status[root[0]][root[1]] = '-'
        board_copy.block_status[root[0]/4][root[1]/4] = blockVal

    def check_time(self):
        if datetime.datetime.utcnow() - self.begin > self.timeLimit:
            return True
        return False

    def IDS(self, root):
        guess = 0
        for depth in range(1, 256):
            self.depth = depth
            self.transpositionTable = {}
            guess, move = self.MTDF(root, guess, depth)
            print(self.depth)
            if self.check_time():
                break
            saved_move = move
        return saved_move

    def MTDF(self, root, guess, depth):
        g = guess
        upperbound = self.INF
        lowerbound = -self.INF
        while lowerbound < upperbound:
            if g == lowerbound:
                beta = g + 1
            else:
                beta = g
            self.index = 0
            self.maxmove = True
            g, move = self.AlphaBetaWithMemory(root, beta - 1, beta, depth)
            if self.check_time():
                return g, move
            if g < beta:
                upperbound = g
            else:
                lowerbound = g
        return g, move

    def calcZobristHash(self, root):
        h = 0
        bs = board_copy.board_status
        for i in range(0, 16):
            for j in range(0, 16):
                if bs[i][j] == 'x':
                    h = h^self.zobrist[i][j][root[0]+1][root[1]+1][0]
                elif bs[i][j] == 'o':
                    h = h^self.zobrist[i][j][root[0]+1][root[1]+1][1]
        return h

    def cantorPairing(self, a, b):
        return (a + b)*(a + b + 1)/2 + b

    def getMarker(self, flag):
        if flag == 'x':
            return 'o'
        return 'x'

    def AlphaBetaWithMemory(self, root, alpha, beta, depth):
        board_hash = self.calcZobristHash(root)
        loweridx = self.cantorPairing(board_hash, 1)
        upperidx = self.cantorPairing(board_hash, 2)

        lower = -2*self.INF, root
        upper = 2*self.INF, root

        # Transposition table lookup
        if (loweridx in self.transpositionTable):
            lower = self.transpositionTable[loweridx]
            if (lower[0] >= beta):
                return lower

        if (upperidx in self.transpositionTable):
            upper = self.transpositionTable[upperidx]
            if (upper[0] <= alpha):
                return upper

        status = board_copy.find_terminal_state()
        if status[1] == "WON":
            if self.maxmove:
                return -self.INF, root
            else:
                return self.INF, root
    
        # Update values of alpha and beta based on values in Transposition Table
        alpha = max(alpha, lower[0])
        beta = min(beta, upper[0])

        # Get Unique Hash for moveOrder Table lookup
        moveHash = self.cantorPairing(board_hash, self.index)
        moveInfo = []

        # Reordered moves already present!
        if moveHash in self.moveOrder:
            children = []
            children.extend(self.moveOrder[moveHash])
            nSiblings = len(children)

        else:
            children = board_copy.find_valid_move_cells(root)
            nSiblings = len(children)

        if depth == 0 or nSiblings == 0:
            answer = root
            if self.check_time():
                return 0, answer
            g = self.heuristic(root)

        # Node is a max node
        elif self.maxmove:
            g = -self.INF
            answer = children[0]
            # Return value if time up
            if self.check_time():
                    return g, answer

            # Save original alpha value
            a = alpha
            i = 0
            while ((g < beta) and (i < nSiblings)):
                self.maxmove = False
                c = children[i]

                #Retain current block state for later restoration
                blockVal = board_copy.block_status[c[0]/4][c[1]/4]

                # Mark current node as taken by us for future reference
                board_copy.update(root, c, self.mark)
                self.index += 1

                val, temp = self.AlphaBetaWithMemory(c, a, beta, depth-1)

                # Revert Board state
                self.revertBoard(c, blockVal)
                self.index -= 1

                # Append returned values to moveInfo
                temp = (val, c)
                moveInfo.append(temp)

                if val > g:
                    g = val
                    answer = c

                a = max(a, g)
                i = i + 1
            self.maxmove = True

        # Node is a min node
        else:
            g = self.INF
            answer = children[0]
            # Return value if time up
            if self.check_time():
                return g, answer
            # Save original beta value
            b = beta
            i = 0
            while ((g > alpha) and (i < nSiblings)):
                self.maxmove = True
                c = children[i]
                # Retain current block state for later restoration
                blockVal = board_copy.block_status[c[0]/4][c[1]/4]

                # Mark current node as taken by us for future reference
                board_copy.update(root, c, self.getMarker(self.mark))
                self.index += 1

                val, temp = self.AlphaBetaWithMemory(c, alpha, b, depth-1)

                # Revert Board state
                self.revertBoard(c, blockVal)
                self.index -= 1

                # Append returned values to moveInfo
                temp = (val, c)
                moveInfo.append(temp)

                if val < g:
                    g = val
                    answer = c

                b = min(b, g)
                i = i + 1
            self.maxmove = False

        temp = []

        if self.maxmove:
            moveInfo = sorted(moveInfo, reverse = True)
        else:
            moveInfo = sorted(moveInfo)

        for i in moveInfo:
            temp.append(i[1])
            children.remove(i[1])

        random.shuffle(children)

        self.moveOrder[moveHash] = []
        self.moveOrder[moveHash].extend(temp)
        self.moveOrder[moveHash].extend(children)

        # if(len(self.moveOrder[moveHash]) != nSiblings):

        # Traditional transposition table storing of bounds
        # ----------------------------------------------------#
        # Fail low result implies an upper bound
        if g <= alpha:
            self.transpositionTable[upperidx] = g, answer

        # Fail high result implies a lower bound
        if g >= beta:
            self.transpositionTable[loweridx] = g, answer

        return g, answer

    def checkdiamond(self, currblockX, currblockY, flag, oflag, bs):
        scounter = 0
        save = [ [1,-1], [1,1], [2,0]]
        if bs[currblockX][currblockY] is flag:
            scounter+=3
        elif bs[currblockX][currblockY] is oflag:
            scounter -= 1
        if bs[currblockX+save[0][0]][currblockY+save[0][1]] is flag:
            scounter+=3
        elif bs[currblockX+save[0][0]][currblockY+save[0][1]] is oflag:
            scounter -= 1
        if bs[currblockX+save[1][0]][currblockY+save[1][1]] is flag:
            scounter+=3
        elif bs[currblockX+save[1][0]][currblockY+save[1][1]] is oflag:
            scounter -= 1
        if bs[currblockX+save[2][0]][currblockY+save[2][1]]  is flag:
            scounter+=3 
        elif bs[currblockX+save[2][0]][currblockY+save[2][1]] is oflag:
            scounter -= 1
        return scounter+4


    def is_centre(self, row, col):
        if row == 1 and col == 1:
            return 1
        if row == 1 and col == 2:
            return 1
        if row == 2 and col == 1:
            return 1
        if row == 2 and col == 2:
            return 1
        return 0

    def is_corner(self, row, col):
        if row == 0 and col == 0:
            return 1
        if row == 0 and col == 3:
            return 1
        if row == 3 and col == 0:
            return 1
        if row == 3 and col == 3:
            return 1
        return 0

    def check_current_board_state(self, bs, flag, oflag):
        h = 0
        dtops = [(0,1), (0,2), (1,1), (1,2)]
        arr_diamond = [-1000, -700, -400, -200, 0 ,20, 60, 120, 200, 300, 420, 560,720, 900 ,1000]
        arr = [0, 120, 220, 450]
        for cell in dtops:
            val = self.checkdiamond(cell[0],cell[1],flag,oflag,bs)
            h+=arr_diamond[val]

        for i in range(4):
            scounter_row = 0
            ocounter_row = 0
            scounter_column = 0
            ocounter_column = 0
            for j in range(4):
                if bs[i][j] == flag:
                    scounter_row+=1
                elif bs[i][j] == oflag:
                    ocounter_row+=1

                if bs[j][i] == flag:
                    scounter_column+=1
                elif bs[j][i] == oflag:
                    ocounter_column+=1
            if ocounter_row == 0:
                h+=arr[scounter_row]
            if ocounter_column == 0:
                h+=arr[scounter_column]
            if scounter_row == 0:
                h-=arr[ocounter_row]*1.25
            if scounter_column == 0:
                h-=arr[ocounter_column]*1.25
            
        return h
    def check_oppwin(self, nextblockX, nextblockY, oflag, flag):
        poss = 0
        board_status = board_copy.board_status
        for i in range(0,4):
            nuts = 0 
            for j in range(0,4):
                if (board_status[i+4*nextblockX][j+4*nextblockY] == oflag):
                    nuts+=1
                elif (board_status[i+4*nextblockX][j+4*nextblockY] == flag):
                    nuts-=1
            if nuts == 3:
                poss +=1

        for i in range(0,4):
            nuts = 0 
            for j in range(0,4):
                if (board_status[j+4*nextblockX][i+4*nextblockY] == oflag):
                    nuts+=1
                elif (board_status[j+4*nextblockX][i+4*nextblockY] == flag):
                    nuts-=1
            if nuts == 3:
                poss +=1
        for i in range(0,2):
            for j in range(0,2):
                diam =  board_status[4*nextblockX+i][4*nextblockY+j+1] == oflag + \
                        board_status[4*nextblockX+i+1][4*nextblockY+j] == oflag + \
                        board_status[4*nextblockX+i+1][4*nextblockY+j+2] == oflag + \
                        board_status[4*nextblockX+i+2][4*nextblockY+j+1] == oflag - \
                        board_status[4*nextblockX+i][4*nextblockY+j+1] == flag - \
                        board_status[4*nextblockX+i+1][4*nextblockY+j] == flag - \
                        board_status[4*nextblockX+i+1][4*nextblockY+j+2] == flag - \
                        board_status[4*nextblockX+i+2][4*nextblockY+j+1] == flag
                if (diam ==3 ):
                    poss+=1
        return poss

    def heuristic(self, move):

        currblockX = move[0]/4
        currblockY = move[1]/4
        nextblockX = move[0]%4
        nextblockY = move[1]%4

        bs = board_copy.block_status
        BS = board_copy.board_status
        immwin = [500, -5000, -5100, -5200, -5300]
        
        # if self.depth == 1 and :

        flag = self.mark
        if flag == 'x':
            oflag = 'o'
        else:
            oflag = 'x'
        heur = 0
        if bs[nextblockX][nextblockY] != '-':
            if self.maxmove:
                heur-=500/self.depth
            else:
                heur+=500/self.depth
        elif self.depth < 3:
            ret  = self.check_oppwin(nextblockX,nextblockY,oflag,flag)
            if ret > len(immwin):
                heur -= 5500
            else:
                heur += immwin[ret]


        a, b = board_copy.find_terminal_state()
        val = [[],[],[],[]]
        for i in range(4):
            for j in range(4):
                val[i].append(4)
                if self.is_corner(i,j):
                    val[i][j] = 6
                elif self.is_centre(i,j):
                    val[i][j] = 3
        if b == "WON":
            if a==flag:
                heur+=10000
            elif a==oflag:
                heur-=10000
        elif b == "DRAW":
            pts1=0
            pts2=0
            for i in range(4):
                for j in range(4):
                    if game_board.block_status[i][j] == flag:
                        pts1 += val[i][j]
                    if game_board.block_status[i][j] == oflag:
                        pts2 += val[i][j]
            heur+=(pts1-pts2)*20
        else:
            for i in range(4):
                for j in range(4):
                    if bs[i][j] == flag:
                        heur+=val[i][j]*50
                    elif bs[i][j] == oflag:
                        heur-=val[i][j]*50
                    else:
                        send = [[BS[4*i+k][4*j+l] for l in range(4)] for k in range(4)]
                        heur+=self.check_current_board_state(send, flag, oflag)/10
                        heur-=self.check_current_board_state(send, oflag, flag)/10

            heur+=(self.check_current_board_state(bs, flag, oflag)-self.depth*10)
            heur-=(self.check_current_board_state(bs, oflag, flag)-self.depth*10)


        return heur



        # if bs[currblockX][currblockY] == flag:
        #   heur+=1000
        #   if (currblockX == 1 or currblockX == 2) and (currblockY == 0 or currblockY == 1):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, up, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 1 or currblockX == 2) and (currblockY == 2 or currblockY == 3):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, down, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 0) and (currblockY == 1 or currblockY == 2):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, left, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 3) and (currblockY == 1 or currblockY == 2):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, right, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
            
        # elif bs[currblockX][currblockY] == oflag:
        #   heur-=300
