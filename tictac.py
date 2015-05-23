# CS 331
# Kevin Jones
# Tic-Tac-Toe minimax algorithm
# GUI from Daniel Tan
# GUI cleaned up for the assignment by Aaron Johnson.

import os
if os.sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

from tkinter import *
from tkinter import ttk
from random import randint
import time

debug = 0
class main:
   
    def __init__(self, master, args = None):
        # master frame
        self.frame = Frame(master)
        self.frame.pack(fill="both", expand=True)
        
        self.canvas_width = 300
        self.canvas_height = 300

        # canvas where the game is played on
        self.canvas = Canvas(self.frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill="both", expand=True)
        
        # shows status of game
        self.label = Label(self.frame, text='Tic Tac Toe Game', height=2, bg='black', fg='grey')
        self.label.pack(fill="both", expand=True)
        
        # frame to contain the buttons and drop downs
        self.bframe = Frame(self.frame)
        self.bframe.pack(fill="both", expand=True)
        
        self.player_choices = ['human','random','minimax']

        # frame to contain drop downs
        self.cframe = Frame(self.bframe)
        self.cframe.pack(fill="both", expand=True, side=LEFT)

        # player1 dropdown        
        self.p1_chose = StringVar()
        self.p1_choice = ttk.Combobox(self.cframe, textvariable=self.p1_chose, 
            height = 2, values = self.player_choices)
        self.p1_choice.pack(fill="both", expand=True, side=TOP)

        # player2 dropdown        
        self.p2_chose = StringVar()
        self.p2_choice = ttk.Combobox(self.cframe, textvariable=self.p2_chose, 
            height = 2, values = self.player_choices)
        self.p2_choice.pack(fill="both", expand=True, side=BOTTOM)


        # button to initiate the game
        self.start = Button(self.bframe, text='Click here to start', 
            height=2, command=self.start_clicked, bg='white', fg='purple')
        self.start.pack(fill="both", expand=True, side=RIGHT)
        
        # canvas board drawing function call
        self._board()

        # set defaults upon receiving command line input, and run game without click
        if args is not None:
        	self.p1_chose.set(args[0])
        	self.p2_chose.set(args[1])
        	self.start_clicked()

    def start_clicked(self):
        '''Starts a new game.'''
        
        # refresh canvas
        self.canvas.delete(ALL)
        
        # function call on click
        self._board()
        
        # logical game board
        self.TTT = [[None,None,None],[None,None,None],[None,None,None]]

        # validate user choices and initialize the game!
        if self.p1_chose.get() != '' and self.p2_chose.get() != '':
            self.players = [self.p1_chose.get(), self.p2_chose.get()]
            if 'human' in self.players:
                self.canvas.bind("<ButtonPress-1>", self.human_clicked)
            print('Game start - ' + ' vs. '.join(self.players))
            self.cur_player = 0            
            self.moves_total = 0
            self.branch_moves_total = 0
            self.move_next()
        else:
            print('Error: you must choose player types')


    def _board(self):
        '''Creates or clears the board and gridlines.'''
        self.canvas.create_rectangle(0,0,self.canvas_width,self.canvas_height, outline="black")
        # dividing lines can be simply two rectangles intersecting
        self.canvas.create_rectangle(self.canvas_width//3, self.canvas_height, 
            2*self.canvas_width//3,0, outline="black")
        self.canvas.create_rectangle(0, self.canvas_height//3,
            self.canvas_width,2*self.canvas_height//3, outline="black")

                        
    def draw_mark(self, row, column):
        '''Draw an X for player 0, an O for player 1'''
        y = row*self.canvas_width//3 + self.canvas_width//6
        x = column*self.canvas_height//3 + self.canvas_height//6
        if self.cur_player == 0:
            self.canvas.create_line( x+20, y+20, x-20, y-20, width=4, fill="black")
            self.canvas.create_line( x-20, y+20, x+20, y-20, width=4, fill="black")
        elif self.cur_player == 1:
            self.canvas.create_oval( x+25, y+25, x-25, y-25, width=4, outline="black")


    def human_clicked(self, event):
        '''A human clicked on the canvas - decide what happens next.'''

        if self.players[self.cur_player] != 'human':
        	print('Other player is still moving')
        	return

        where = self.where_clicked(event)
        if where is not None:
            self.move_human(where[0], where[1])


    def where_clicked(self, event):
        '''Find where on the logical grid (x, y) was clicked.'''
        w = self.canvas_width
        h = self.canvas_height

        for column, k in enumerate(range(0, w, w//3)):
            for row, j in enumerate(range(0, h, h//3)):
                #checks if the mouse input is in a bounding box
                if event.x in range(k,k+w//3) and event.y in range(j,j+h//3):
                    #checks if there is nothing in the bounding box
                    if self.canvas.find_enclosed(k, j, k+w//3, j+h//3) == ():
                        return row, column


    def proceed_next_player(self):
        '''Set cur_player to the next player.'''
        self.cur_player = (self.cur_player + 1) % 2

    def check_term(self, state):
        '''Check if the game is over, but do not invoke game_over'''
        t = state
        if t[1][1] is not None                        \
            and ((t[1][1] == t[0][0] == t[2][2]) or   \
                (t[1][1] == t[0][2] == t[2][0]) or    \
                (t[0][1] == t[1][1] == t[2][1]) or    \
                (t[1][0] == t[1][1] == t[1][2])):
            return 10
        # through top-left
        elif t[0][0] is not None                      \
            and ((t[0][0] == t[0][1] == t[0][2]) or   \
                (t[0][0] == t[1][0] == t[2][0])):
            return 10
           
        # through bottom-right
        elif t[2][2] is not None                      \
            and ((t[2][2] == t[2][1] == t[2][0]) or   \
                (t[2][2] == t[1][2] == t[0][2])):
            return 10
           
        if self.branch_moves_total >= 9:
            return 0
        return -1

        
    def game_is_over(self):
        '''Check if the game is over - whether it be a draw or win scenario.'''
        # check the 8 ways to win
        t = self.TTT
        # through center
        if t[1][1] is not None                        \
            and ((t[1][1] == t[0][0] == t[2][2]) or   \
                (t[1][1] == t[0][2] == t[2][0]) or    \
                (t[0][1] == t[1][1] == t[2][1]) or    \
                (t[1][0] == t[1][1] == t[1][2])):
                return self.game_over(t[1][1])
        # through top-left
        elif t[0][0] is not None                      \
            and ((t[0][0] == t[0][1] == t[0][2]) or   \
                (t[0][0] == t[1][0] == t[2][0])):
                return self.game_over(t[0][0])
        # through bottom-right
        elif t[2][2] is not None                      \
            and ((t[2][2] == t[2][1] == t[2][0]) or   \
                (t[2][2] == t[1][2] == t[0][2])):
                return self.game_over(t[2][2])
        # no winner and full board means draw
        if self.moves_total >= 9:
            return self.game_over(-1)
        return False


    def game_over(self, winner):
        '''The game is over - end the game and display the winner.'''
        if winner < 0:
            s = 'Draw between ' + ' and '.join(self.players)
        else:
            s = 'Game over - player ' + str(self.cur_player + 1) + " wins (" + self.players[self.cur_player] + ")"
        print(s)
        # print('Board end-configuration:')
        # print(self.TTT)
        self.label['text']=(s)
        self.canvas.unbind("<ButtonPress-1>")
        return True


    def move_next(self):
        '''Determine who has the next move, and move appropriately.'''
        s = 'Player ' + str(self.cur_player + 1) + "'s move (" + self.players[self.cur_player] + ")"
        self.label['text'] = (s)

        # draw now, not later
        self.canvas.update_idletasks()

        if self.players[self.cur_player] == 'human':          
            return # wait for human GUI input
        elif self.players[self.cur_player] == 'random':
            self.move_random()
        elif self.players[self.cur_player] == 'minimax':
            # raise Warning('Unsupported player type')
            self.move_minimax()
        self.moves_total += 1
        if self.game_is_over():
            print(self.TTT)
            return
        self.proceed_next_player()
        self.move_next()


    def move_human(self, r, c):
        '''The human chose the position r, c as their next move.'''
        if self.TTT[r][c] is not None:
            return # there is already a mark there
        else:
            # update logical board
            self.TTT[r][c] = self.cur_player
            # update GUI board
            self.draw_mark(r, c)

            # end-move tasks
            print('Human chose ' + str((r, c)))
            self.moves_total += 1
            if self.game_is_over():
                return
            self.proceed_next_player()
            self.move_next()


    def move_random(self):
        '''Let the computer move randomly.'''
        d = { 1:(0,0),2:(0,1),3:(0,2),
              4:(1,0),5:(1,1),6:(1,2),
              7:(2,0),8:(2,1),9:(2,2) }
        t = time.time()
        while time.time() - t < 10:
            r = randint(1,9)
            r, c = d[r]

            if self.TTT[r][c] is not None:
                continue # there is already a mark there
            else:
                self.TTT[r][c] = self.cur_player
                self.draw_mark(r, c)
                print('Random chose ' + str((r, c)))
                return 
        print('Random move errored')	
	
 
        
    def	move_minimax(self):
        '''Use minimax algorithm to determine next move given a state.'''
        '''We can assume that the game is not over when this function is called'''
        #branch = list(self.TTT)
        temp = [row[:] for row in self.TTT]
        self.branch_moves_total = self.moves_total
        v, move = self.max_move(temp)
        self.TTT[move[0]][move[1]] = self.cur_player
        self.draw_mark(move[0], move[1])
        print('Minimax chose ' + str((move[0], move[1])))
        return		


    def max_move(self, state):
        best_score = -9999
        best_move = None        
        moves = self.gen_moves(state)
        self.branch_moves_total += 1
        moves_to_here = self.branch_moves_total
        for m in moves:
            
            r, c = m
            temp = [row[:] for row in state]
            temp[r][c] = self.cur_player
            score =  self.check_term(temp)
            if(score == -1):
                score, move = self.min_move(temp)
                self.branch_moves_total = moves_to_here
            if (score > best_score):
                best_score = score
                best_move = (r,c)
        return best_score, best_move


    def min_move(self, state):
        best_score = 9999
        best_move = None   
        moves = self.gen_moves(state)
        self.branch_moves_total += 1
        moves_to_here = self.branch_moves_total
        for m in moves:
            self.branch_moves_total = moves_to_here
            r, c = m
            temp = [row[:] for row in state]
            temp[r][c] = ((self.cur_player+1)%2)
            score =  self.check_term(temp)
            if(score == -1):
                score, move = self.max_move(temp)
            else:
                score = -score
            if (score < best_score):
                best_score = score
                best_move = (r,c)
        return best_score, best_move
    
	

    def gen_moves(self, state):
        d = { 1:(0,0),2:(0,1),3:(0,2),
        4:(1,0),5:(1,1),6:(1,2),
        7:(2,0),8:(2,1),9:(2,2) }
        moves = []
        for i in range(1,10):
            r, c = d[i]
            if state[r][c] is None:
                moves.append(d[i])
        return moves


def valid(args):
	p = ['human','random','minimax']
	return all((x in p for x in args))

if __name__ == "__main__":
	args = os.sys.argv[1:]
	if len(args) == 0:
		root=Tk()
		app=main(root)
		root.mainloop()
	elif len(args) == 2 and valid(args):
		root=Tk()
		app=main(root, args)
		root.mainloop()
	else:
		print("Usage: " + os.sys.argv[0] + " <player 1 type> <player 2 type>")
		print("       where player type = human, random, or minimax")
