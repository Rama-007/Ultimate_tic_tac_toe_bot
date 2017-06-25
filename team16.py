import sys
import random
import signal
import time
import copy

class TimedOutExc(Exception):
	pass

def handler(signum, frame):
	#print 'Signal handler called with signal', signum
	raise TimedOutExc()

class Player16():
	def __init__(self):
		self.Approx_win_score=11
		self.Board_weight=31
		self.win_score=10**6
		self.depth=3
		self.win_sequences=[(0,1,2,3),(4,5,6,7),(8,9,10,11),(12,13,14,15),(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(3,6,9,12)]
		self.first=0
		self.maxx = 9223372036854775807 
		self.repeat=[[0 for x in range(16)] for y in range(16)] 
		self.starttime=0


	Maxx=9223372036854775807

	def move(self, board, old_move, flag):
		self.starttime=time.time()
		action_result=[]
		final_action=[]
		final_result=[]
		if(old_move[0] == -1 and old_move[1] == -1):
			return (6,6)
		cells = board.find_valid_move_cells(old_move)

		if(len(cells)==1):
			return (cells[0][0], cells[0][1])

		if(len(cells)>16):
			self.depth=1
		elif(len(cells)>2):
			self.depth=2
		else:
			self.depth=3

		mainflag=flag

		temp_block=copy.deepcopy(board.block_status)
		temp_state=copy.deepcopy(board.board_status)

		top_final=[]
		for winning in cells:
			next_state=self.generate_next(temp_state,winning,flag)
			next_state2=self.generate_next(temp_state,winning,self.opflag(flag))
#			print "not yet"
			x=winning[0]/4
			y=winning[1]/4
			if self.chance_win(next_state,x,y):
				top_final.append(winning)
				self.repeat[winning[0]][winning[1]]+=1
			elif self.chance_win(next_state2,x,y):
				top_final.append(winning)

		#print top_final

		
		if(len(top_final)==0):
			for winning in cells:
				if temp_state[winning[0]][winning[1]]=='-':
					next_state=self.generate_next(temp_state,winning,flag)
					next_state2=self.generate_next(temp_state,winning,self.opflag(flag))
#					print "not yet"
					x=winning[0]/4
					y=winning[1]/4
					if self.approx_chance_win(next_state,x,y):
						top_final.append(winning)
						self.repeat[winning[0]][winning[1]]+=1
					elif self.approx_chance_win(next_state2,x,y):
						top_final.append(winning)
		

		if len(top_final)>0:
			cells=top_final

		#print self.depth
		#print cells
		for action in cells:
			next_state=self.generate_next(temp_state,action,flag)
			next_block=self.generate_block(temp_block,next_state,action)
			value=self.__min_val_alphabeta(next_state,self.depth,next_block,self.opflag(flag),mainflag,old_move)
			action_result.append((action , value))
		_,best_value=max(action_result,key=lambda x:x[1])

		#print action_result

		if len(action_result)==0:
		#	print "hie"
			action_result=cells

		for act,val in action_result:
			if val==best_value:
				final_action.append(act)
		
		i=final_action[0]	
		x = i[0] - (i[0]%4)
		y = i[1] - (i[1]%4)
		arr = []

		for j in [x,x+1,x+2,x+3]:
			for k in [y,y+1,y+2,y+3]:
				if temp_state[j][k] == flag:
					arr.append(1)
				elif temp_state[j][k] == self.opflag(flag):
					arr.append(-1)
				else:
					arr.append(0)
		
		loc = []
		for i in xrange(len(arr)):
			if arr[i] == 1:
				self.rtup(i,arr,x,y,loc)
		final_result=list(set(loc).intersection(set(final_action)))
		if(len(final_result)>0):
			final_action=final_result

		final_move=random.choice(final_action)
		return final_move



	def rtup(self, i, arr, sx, sy, x):
		for j in self.win_sequences:
			if i in j:
				var = j.index(i)
				for k in xrange(len(j)):
					if k != var:
						if arr[k] == -1:
							break
						elif k == 2:
							for s in xrange(len(j)):
								if s != var:
									v1 = sx + (s/4)
									v2 = sy + (s%4)
									x.append((v1,v2))
		return

	def __min_val_alphabeta(self,state,depth,temp_block,flag,mainflag,old_move,alpha=-1*(Maxx),beta=Maxx):
		if self.terminal_test(state,depth,temp_block) or time.time()-self.starttime>=10:
			return self.evaluate(state,temp_block,mainflag)
		val=self.maxx
		for action in self.find_valid_move(old_move,temp_block,state):
			next_state=self.generate_next(state,action,flag)
			next_block=self.generate_block(temp_block,next_state,action)
			val=min(val,self.__max_val_alphabeta(next_state,depth-1,next_block,self.opflag(flag),mainflag,action,alpha,beta))
			if(val<=alpha):
				return val
			beta=min(beta,val)
		return val

	def __max_val_alphabeta(self,state,depth,temp_block,flag,mainflag,old_move,alpha=-1*(Maxx),beta=Maxx):
		if self.terminal_test(state,depth,temp_block) or time.time()-self.starttime>=10:
			return self.evaluate(state,temp_block,mainflag)
		val=-1*self.maxx
		for action in self.find_valid_move(old_move,temp_block,state):
			next_state=self.generate_next(state,action,flag)
			next_block=self.generate_block(temp_block,next_state,action)
			val=max(val,self.__min_val_alphabeta(next_state,depth,next_block,self.opflag(flag),mainflag,action,alpha,beta))
			if(val>=beta):
				return val
			alpha=max(alpha,val)
		return val

	def evaluate(self,state,temp_block,flag):
		test_block=[]
		for i in range(4):
			for j in range(4):
				test_block.append(temp_block[i][j])

		if self.get_winner(test_block)!=False:
			if self.get_winner(test_block)==flag:
				return self.win_score
			else:
				return -1*self.win_score
		if self.is_board_full(state):
			return 0
		ret_val=self.heuristic(test_block,flag)*self.Board_weight
		for i in range(16):
			if test_block[i]=='-':
				part_state=self.get_state(state,i)
				if '-' in part_state:
					ret_val=self.heuristic(part_state,flag)
		return ret_val

	def get_state(self,state,i):
		part_state=[]
		x=i/4
		y=i%4
		for k in range(4):
			for j in range(4):
				part_state.append(state[4*x+k][4*y+j])
		return part_state

	def heuristic(self,test_block,flag):
		if '-' not in test_block:
			return 0
		player_score=0
		opponent_score=0
		player=flag
		opponent=self.opflag(flag)
		for seq in self.win_sequences:
			net_sequence=[test_block[i] for i in seq if test_block[i]!='-']
			if player in net_sequence:
				if opponent in net_sequence:
					continue
				if len(net_sequence)>2:
					player_score+=self.Approx_win_score*3
				elif len(net_sequence)>1:
					player_score+=self.Approx_win_score
				player_score+=1
			elif opponent in net_sequence:
				if player in net_sequence:
					continue
				if len(net_sequence)>2:
					opponent_score+=self.Approx_win_score*3
				elif len(net_sequence)>1:
					opponent_score+=self.Approx_win_score
				opponent_score+=1
		return player_score - opponent_score


	def chance_win(self,state,z,w):
		x=4*z
		y=4*w
		
		for i in range(x,x+4):
			if state[i][y]==state[i][y+1] and state[i][y]==state[i][y+2] and state[i][y]==state[i][y+3] and state[i][y]!='-':
				return True
		for i in range(y,y+4):
			if state[x][i]==state[x+1][i] and state[x][i]==state[x+2][i] and state[x][i]==state[x+3][i] and state[x][i]!='-':
				return True
		if state[x][y]==state[x+1][y+1] and state[x][y]==state[x+2][y+2] and state[x][y]==state[x+3][y+3] and state[x][y]!='-':
			return True
		if state[x][y+3]==state[x+1][y+2] and state[x][y+3]==state[x+2][y+1] and state[x][y+3]==state[x+3][y] and state[x][y+3]!='-':
			return True

		return False

	def approx_chance_win(self,state,z,w):
		x=4*z
		y=4*w
		
		for i in range(x,x+4):
			a,b,c=self.check(state[i])
			if a>=2:
				if b>0:
					return False
				else:
					return True
			elif b>=2:
				if a>0:
					return False
				else:
					return True
		for i in range(y,y+4):
			tokka_state=[state[x][i],state[x+1][i],state[x+2][i],state[x+3][i]]
			a,b,c=self.check(tokka_state)
			if a>=2:
				if b>0:
					return False
				else:
					return True
			elif b>=2:
				if a>0:
					return False
				else:
					return True
		tokka_state=[state[x][y],state[x+1][y+1],state[x+2][y+2],state[x+3][y+3]]
		a,b,c=self.check(tokka_state)
		if a>=2:
			if b>0:
				return False
			else:
				return True
		elif b>=2:
			if a>0:
				return False
			else:
				return True
		tokka_state=[state[x][y+3],state[x+1][y+2],state[x+2][y+1],state[x+3][y]]
		a,b,c=self.check(tokka_state)
		if a>=2:
			if b>0:
				return False
			else:
				return True
		elif b>=2:
			if a>0:
				return False
			else:
				return True

		return False

	def check(self,state):
		x=0
		o=0
		d=0
		for i in range(0,4):
			if(state[i]=='x'):
				x+=1
			elif(state[i]=='o'):
				o+=1
			else:
				d+=1
		return (x,o,d) 

	def is_board_full(self,state):
		for i in range(16):
			if '-' in state[i]:
				return False
		return True

	def terminal_test(self,state,depth,temp_block):
		if depth==0:
			return True
		a,b=self.terminal_state_reached(state,temp_block)
		return a


	def terminal_state_reached(self,state,block):
		bs=[]
		for i in range(4):
			for j in range(4):
				bs.append(block[i][j])
		if self.get_winner(bs):
			return True,'W'
		else:
			flager=0
			for i in range(16):
				for j in range(16):
					if state[i][j]=='-' and bs[(i/4)*4+(j/4)] == '-':
						flager=1
						break
			if flager==1:
				return False,'R'
			else:
				p1=0
				p2=0
				for i in bs:
					if i=='x':
						p1+=1
					if i=='o':
						p2+=1
				if p1>p2:
					return True,'R'
				elif p1<p2:
					return True,'R'


	def find_valid_move(self,old_move,temp_block,state):
		allowed_cells=[]
		allowed_block=[old_move[0]%4,old_move[1]%4]
		if old_move!=(-1,-1) and temp_block[allowed_block[0]][allowed_block[1]]=='-':
			for i in range(4*allowed_block[0],4*allowed_block[0]+4):
				for j in range(4*allowed_block[1],4*allowed_block[1]+4):
					if state[i][j]=='-':
						allowed_cells.append((i,j))
		else:
			for i in range(16):
				for j in range(16):
					if state[i][j]=='-' and temp_block[i/4][j/4]=='-':
						allowed_cells.append((i,j))
		return allowed_cells


	def generate_next(self,rando_state,action,flag):
		brd=[['-' for x in range(16)] for y in range(16)]
		for i in range(16):
			for j in range(16):
				brd[i][j]=rando_state[i][j]
		brd[action[0]][action[1]] = flag
		return brd

	def generate_block(self,temp_block,next_state,action):
		result=[['-' for x in range(4)] for y in range(4)]
		for i in range(4):
			for j in range(4):
				result[i][j]=temp_block[i][j]
		x=action[0]/4
		y=action[1]/4
		stater=[]
		for i in range(4*x+4):
			for j in range(4*y+4):
				stater.append(next_state[i][j])
		if self.is_partboard_full(stater):
			result[x][y]='d'
		else:
			var=self.get_winner(stater)
			if var:
				result[x][y]=var
			return result

	def opflag(self,flag):
		if flag=='x':
			return 'o'
		return 'x'

	def get_winner(self,block):
		if block[0]==block[1] and block[1]==block[2] and block[1]==block[3] and block[1]!='-' and block[1]!='d':
			return block[1]
		if block[4]==block[5] and block[4]==block[6] and block[4]==block[7] and block[4]!='-' and block[4]!='d':
			return block[4]
		if block[8]==block[9] and block[8]==block[10] and block[8]==block[11] and block[8]!='-' and block[8]!='d':
			return block[8]
		if block[12]==block[13] and block[12]==block[14] and block[12]==block[15] and block[15]!='-' and block[15]!='d':
			return block[15]
		if block[0]==block[4] and block[0]==block[8] and block[0]==block[12] and block[0]!='-' and block[0]!='d':
			return block[0]
		if block[1]==block[5] and block[1]==block[9] and block[1]==block[13] and block[1]!='-' and block[1]!='d':
			return block[1]
		if block[2]==block[6] and block[2]==block[10] and block[2]==block[14] and block[2]!='-' and block[2]!='d':
			return block[2]
		if block[3]==block[7] and block[3]==block[11] and block[3]==block[15] and block[3]!='-' and block[3]!='d':
			return block[3]
		if block[0]==block[5] and block[0]==block[10] and block[0]==block[15] and block[0]!='-' and block[0]!='d':
			return block[0]
		if block[3]==block[6] and block[3]==block[9] and block[3]==block[12] and block[3]!='-' and block[4]!='d':
			return block[3]
		return False	


	def is_partboard_full(self,state):
		if '-' in state:
			return False
		return True


class Manual_Player:
	def __init__(self):
		pass
	def move(self, board, old_move, flag):
		print 'Enter your move: <format:row column> (you\'re playing with', flag + ")"	
		mvp = raw_input()
		mvp = mvp.split()
		return (int(mvp[0]), int(mvp[1]))

class Board:

	def __init__(self):
		# board_status is the game board
		# block status shows which blocks have been won/drawn and by which player
		self.board_status = [['-' for i in range(16)] for j in range(16)]
		self.block_status = [['-' for i in range(4)] for j in range(4)]

	def print_board(self):
		# for printing the state of the board
		print '==============Board State=============='
		for i in range(16):
			if i%4 == 0:
				print
			for j in range(16):
				if j%4 == 0:
					print "",
				print self.board_status[i][j],
			print 
		print

		print '==============Block State=============='
		for i in range(4):
			for j in range(4):
				print self.block_status[i][j],
			print 
		print '======================================='
		print
		print


	def find_valid_move_cells(self, old_move):
		#returns the valid cells allowed given the last move and the current board state
		allowed_cells = []
		allowed_block = [old_move[0]%4, old_move[1]%4]
		#checks if the move is a free move or not based on the rules

		if old_move != (-1,-1) and self.block_status[allowed_block[0]][allowed_block[1]] == '-':
			for i in range(4*allowed_block[0], 4*allowed_block[0]+4):
				for j in range(4*allowed_block[1], 4*allowed_block[1]+4):
					if self.board_status[i][j] == '-':
						allowed_cells.append((i,j))
		else:
			for i in range(16):
				for j in range(16):
					if self.board_status[i][j] == '-' and self.block_status[i/4][j/4] == '-':
						allowed_cells.append((i,j))
		return allowed_cells	

	def find_terminal_state(self):
		#checks if the game is over(won or drawn) and returns the player who have won the game or the player who has higher blocks in case of a draw
		bs = self.block_status

		cntx = 0
		cnto = 0
		cntd = 0

		for i in range(4):						#counts the blocks won by x, o and drawn blocks
			for j in range(4):
				if bs[i][j] == 'x':
					cntx += 1
				if bs[i][j] == 'o':
					cnto += 1
				if bs[i][j] == 'd':
					cntd += 1

		for i in range(4):
			row = bs[i]							#i'th row 
			col = [x[i] for x in bs]			#i'th column
			#print row,col
			#checking if i'th row or i'th column has been won or not
			if (row[0] =='x' or row[0] == 'o') and (row.count(row[0]) == 4):	
				return (row[0],'WON')
			if (col[0] =='x' or col[0] == 'o') and (col.count(col[0]) == 4):
				return (col[0],'WON')
		#checking if diagnols have been won or not
		if(bs[0][0] == bs[1][1] == bs[2][2] ==bs[3][3]) and (bs[0][0] == 'x' or bs[0][0] == 'o'):
			return (bs[0][0],'WON')
		if(bs[0][3] == bs[1][2] == bs[2][1] ==bs[3][0]) and (bs[0][3] == 'x' or bs[0][3] == 'o'):
			return (bs[0][3],'WON')

		if cntx+cnto+cntd <16:		#if all blocks have not yet been won, continue
			return ('CONTINUE', '-')
		elif cntx+cnto+cntd == 16:							#if game is drawn
			return ('NONE', 'DRAW')

	def check_valid_move(self, old_move, new_move):
		#checks if a move is valid or not given the last move
		if (len(old_move) != 2) or (len(new_move) != 2):
			return False 
		if (type(old_move[0]) is not int) or (type(old_move[1]) is not int) or (type(new_move[0]) is not int) or (type(new_move[1]) is not int):
			return False
		if (old_move != (-1,-1)) and (old_move[0] < 0 or old_move[0] > 16 or old_move[1] < 0 or old_move[1] > 16):
			return False
		cells = self.find_valid_move_cells(old_move)
		return new_move in cells

	def update(self, old_move, new_move, ply):
		#updating the game board and block status as per the move that has been passed in the arguements
		if(self.check_valid_move(old_move, new_move)) == False:
			return 'UNSUCCESSFUL'
		self.board_status[new_move[0]][new_move[1]] = ply

		x = new_move[0]/4
		y = new_move[1]/4
		fl = 0
		bs = self.board_status
		#checking if a block has been won or drawn or not after the current move
		for i in range(4):
			#checking for horizontal pattern(i'th row)
			if (bs[4*x+i][4*y] == bs[4*x+i][4*y+1] == bs[4*x+i][4*y+2] == bs[4*x+i][4*y+3]) and (bs[4*x+i][4*y] == ply):
				self.block_status[x][y] = ply
				return 'SUCCESSFUL'
			#checking for vertical pattern(i'th column)
			if (bs[4*x][4*y+i] == bs[4*x+1][4*y+i] == bs[4*x+2][4*y+i] == bs[4*x+3][4*y+i]) and (bs[4*x][4*y+i] == ply):
				self.block_status[x][y] = ply
				return 'SUCCESSFUL'

		#checking for diagnol pattern
		if (bs[4*x][4*y] == bs[4*x+1][4*y+1] == bs[4*x+2][4*y+2] == bs[4*x+3][4*y+3]) and (bs[4*x][4*y] == ply):
			self.block_status[x][y] = ply
			return 'SUCCESSFUL'
		if (bs[4*x+3][4*y] == bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2] == bs[4*x][4*y+3]) and (bs[4*x+3][4*y] == ply):
			self.block_status[x][y] = ply
			return 'SUCCESSFUL'

		#checking if a block has any more cells left or has it been drawn
		for i in range(4):
			for j in range(4):
				if bs[4*x+i][4*y+j] =='-':
					return 'SUCCESSFUL'
		self.block_status[x][y] = 'd'
		return 'SUCCESSFUL'

def gameplay(obj1, obj2):				#game simulator

	game_board = Board()
	fl1 = 'x'
	fl2 = 'o'
	old_move = (-1,-1)
	WINNER = ''
	MESSAGE = ''
	TIME = 15
	pts1 = 0
	pts2 = 0

	game_board.print_board()
	signal.signal(signal.SIGALRM, handler)
	while(1):
		#player 1 turn
		temp_board_status = copy.deepcopy(game_board.board_status)
		temp_block_status = copy.deepcopy(game_board.block_status)
		signal.alarm(TIME)

		try:									#try to get player 1's move			
			p1_move = obj1.move(game_board, old_move, fl1)
		except TimedOutExc:					#timeout error
#			print e
			WINNER = 'P2'
			MESSAGE = 'TIME OUT'
			pts2 = 16
			break
		
		signal.alarm(0)

		#check if board is not modified and move returned is valid
		if (game_board.block_status != temp_block_status) or (game_board.board_status != temp_board_status):
			WINNER = 'P2'
			MESSAGE = 'MODIFIED THE BOARD'
			pts2 = 16
			break
		if game_board.update(old_move, p1_move, fl1) == 'UNSUCCESSFUL':
			WINNER = 'P2'
			MESSAGE = 'INVALID MOVE'
			pts2 = 16
			break

		status = game_board.find_terminal_state()		#find if the game has ended and if yes, find the winner
		print status
		if status[1] == 'WON':							#if the game has ended after a player1 move, player 1 would win
			pts1 = 16
			WINNER = 'P1'
			MESSAGE = 'WON'
			break
		elif status[1] == 'DRAW':						#in case of a draw, each player gets points equal to the number of blocks won
			WINNER = 'NONE'
			MESSAGE = 'DRAW'
			break

		old_move = p1_move
		game_board.print_board()

		#do the same thing for player 2
		temp_board_status = copy.deepcopy(game_board.board_status)
		temp_block_status = copy.deepcopy(game_board.block_status)
		signal.alarm(TIME)

		try:
			p2_move = obj2.move(game_board, old_move, fl2)
		except TimedOutExc:
			WINNER = 'P1'
			MESSAGE = 'TIME OUT'
			pts1 = 16
			break
		
		signal.alarm(0)
		if (game_board.block_status != temp_block_status) or (game_board.board_status != temp_board_status):
			WINNER = 'P1'
			MESSAGE = 'MODIFIED THE BOARD'
			pts1 = 16
			break
		if game_board.update(old_move, p2_move, fl2) == 'UNSUCCESSFUL':
			WINNER = 'P1'
			MESSAGE = 'INVALID MOVE'
			pts1 = 16
			break

		status = game_board.find_terminal_state()	#find if the game has ended and if yes, find the winner
		print status
		if status[1] == 'WON':						#if the game has ended after a player move, player 2 would win
			pts2 = 16
			WINNER = 'P2'
			MESSAGE = 'WON'
			break
		elif status[1] == 'DRAW':					
			WINNER = 'NONE'
			MESSAGE = 'DRAW'
			break
		game_board.print_board()
		old_move = p2_move

	game_board.print_board()

	print "Winner:", WINNER
	print "Message", MESSAGE

	x = 0
	d = 0
	o = 0
	for i in range(4):
		for j in range(4):
			if game_board.block_status[i][j] == 'x':
				x += 1
			if game_board.block_status[i][j] == 'o':
				o += 1
			if game_board.block_status[i][j] == 'd':
				d += 1
	print 'x:', x, ' o:',o,' d:',d
	if MESSAGE == 'DRAW':
		pts1 = x
		pts2 = o
	return (pts1,pts2)



if __name__ == '__main__':

	if len(sys.argv) != 2:
		print 'Usage: python simulator.py <option>'
		print '<option> can be 1 => Random player vs. Random player'
		print '                2 => Human vs. Random Player'
		print '                3 => Human vs. Human'
		sys.exit(1)
 
	obj1 = ''
	obj2 = ''
	option = sys.argv[1]	
	if option == '1':
		obj1 = Random_Player()
		obj2 = Random_Player()

	elif option == '2':
		obj1 = Random_Player()
		obj2 = Manual_Player()
	elif option == '3':
		obj1 = Manual_Player()
		obj2 = Manual_Player()
	else:
		print 'Invalid option'
		sys.exit(1)

	x = gameplay(obj1, obj2)
	print "Player 1 points:", x[0] 
	print "Player 2 points:", x[1]
