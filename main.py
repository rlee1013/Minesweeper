from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import random
import math

class MinesweeperCell(Label):
    """Creates a label object which shows the number of bombs nearby, if a cell is flagged,
    and if the cell has a bomb"""
    def __init__(self, master, row, column):
        Label.__init__(self, master, bg="white", fg="black", height=1, width=1,
                       font=('Arial', 20), bd=5, relief="raised")
        self.number = 0 # determined by the number of badcells next to it
        self.row = row
        self.column = column
        self.adjacent_squares = [] # squares next to the cell (to calculate how many bombs it is next to)
        self.badCell = False
        self.isFlagged = False
        self.isExposed = False # labels that have been exposed cannot be clicked
        self.bind('<Button-1>', self.expose_squares)
        self.bind('<Button-2>', self.flag)
        self.bind('<Button-3>', self.flag)
        self.colormap = ['','blue','dark green','red','purple','maroon','cyan','black','dim gray']

    def expose_squares(self, event):
        '''When a cell is clicked, reveal it (and then the game displays the board accordingly'''
        self.master.check_win() # checks if all good cells have been exposed
        if self.master.isWinning == False: # this just signifies the game is over (win or lose) and player cannot click
            return
        if self.master.isSet == False: # flag variable showing that no squares have been clicked
            for (row, column) in self.master.coords:
                if abs(self.row-row) > 1 or abs(self.column-column) > 1:
                    self.master.bombs.append((row, column))
            self.master.initialize_board()
            self.master.assign_numbers()
            self.master.isSet = True
        if self.master.isSet: # not else because then the very first square isn't revealed when clicked
            if self.isFlagged: # do not expose a cell if a user flagged it
                return
            if self.badCell: # you lose if you click a bomb
                self.lost_game()
                return
            if self.isExposed: # cannot expose a cell twice
                return
            else:
                self.isExposed = True
                self["bg"] = "light gray"
                self["relief"] = "sunken"
                if self.number != 0: # if the cell has a number
                    self["text"] = str(self.number)
                    self["fg"] = self.colormap[self.number]
                else: # reveal other squares
                    self.master.expose_adjacent_squares(self, event)
                self.master.check_win() # check if all the necessary cells have been exposed

    def find_adjacent_squares(self):
        for otherCell in self.master.cells.values():
            if abs(self.row-otherCell.row) <= 1 and abs(self.column-otherCell.column) <= 1:
                self.adjacent_squares.append(otherCell) # cell can be one row and one column away (touching at corner)
                if self.row == otherCell.row and self.column == otherCell.column:
                    self.adjacent_squares.remove(otherCell) # remove the cell itself

    def flag(self, event):
        if self.master.isWinning == False: # you cannot click anymore, either lost or won
            return
        if self.isExposed == True: # cannot flag a cell if you already know how many bombs are next to it
            return
        else:
            if self.isFlagged == False:
                if self.master.flagcount == 0: # you can only flag as many times as there are hidden bombs
                    return
                else:
                    self['text'] = '*'
                    self.isFlagged = True
                    self.master.flagcount -= 1 # remove one flag
            else: # this is if you want to remove a flag from a flagged cell
                self['text'] = '' # clear the cell of text
                self.isFlagged = False
                self.master.flagcount += 1 # add a flag back
            self.master.flagCounter["text"] = self.master.flagcount # the counter at the bottom updates accordingly

    def lost_game(self): # lost display
        self.master.reveal_bombs_lost()
        self.master.flagCounter["text"] = "L"
        messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
        self.master.isWinning = False

    def won_game(self): # win display
        self.master.reveal_bombs_won()
        self.master.flagCounter["text"] = "W"
        messagebox.showinfo('Minesweeper', 'Congratulations -- you won!', parent=self)
        self.master.isWinning = False # player officially won

class MinesweeperGrid(Frame):
    '''Creates the visual graphics of the board and
    controls what happens after players click squares'''
    def __init__(self, master, width, height, numBombs): # three user inputs
        Frame.__init__(self, master, bg="black", width=width, height=height+2)
        self.grid()
        self.width = width
        self.height = height
        self.numBombs = numBombs
        self.coords = [] # stores the coordinates for each cell
        for row in range(int(self.height)):
            for column in range(int(self.width)):
                self.coords.append((row, column))
        self.cells = {} # identify cells by self.cells[coord]
        for (row, column) in self.coords:
            self.cells[(row, column)] = MinesweeperCell(self, row, column)
            self.cells[(row, column)].grid(row=row, column=column)
        self.bombs = [] # numBombs randomly chosen cells which hold a bomb
        self.flagCounter = Label(self, bg="white", fg="black", text=numBombs)
        self.flagCounter.grid(row=int(self.height), rowspan=2, column=math.floor(self.width/2) - 1, columnspan=2)
        self.flagcount = numBombs
        self.isSet = False # becomes true when the first square is clicked and bombs are randomly assigned
        self.win = False # becomes true if all non-bomb cells are exposed
        self.isWinning = True # if this flag variable is false (due to win/loss), player can no longer click on stuff

    def initialize_board(self):
        '''After the first click, the board is set up'''
        self.badcells = random.sample(self.bombs, self.numBombs) # pick random cells (not the first cell you click)
        for (row, column) in self.badcells:
            self.cells[(row, column)].badCell = True #

    def reveal_bombs_lost(self):
        '''Losing the game animation'''
        for (row, column) in self.badcells: # if you click on cell with bomb
            self.cells[(row, column)]["bg"] = "red"
            self.cells[(row, column)]["relief"] = "sunken"
            self.cells[(row, column)]["text"] = "*"

    def reveal_bombs_won(self):
        '''Part of winning the game animation'''
        for (row, column) in self.badcells: # if you click on cell with bomb
            self.cells[(row, column)]["relief"] = "sunken"
            self.cells[(row, column)]["text"] = "*"

    def assign_numbers(self): # for each cell, if a square next to it has a bomb, add one to the number it displays
        '''For each cell, check if it is a bomb. If not,
        count how many bombs touch it, and that's the cell's number'''
        for cell in self.cells.values():
            cell.find_adjacent_squares()
            for unit in cell.adjacent_squares:
                if unit.badCell:
                    cell.number += 1

    def expose_adjacent_squares(self, cell, event):
        '''When a square is clicked, given it is not a bomb and itself has no bombs,
        other squares around it are recursively revealed until there are no
        adjacent squares that are blank (just like in the game)'''
        # find the coordinates of the cell
        for (row, column) in self.cells.keys():
            if self.cells[(row, column)] == cell:
                break
        for nrow in [row - 1, row, row + 1]:
            for ncol in [column - 1, column, column + 1]:
                # make sure it's in the grid; if so, expose it
                if (0 <= nrow < self.height) and (0 <= ncol < self.width):
                    self.cells[(nrow, ncol)].expose_squares(event)

    def check_win(self):
        '''When a particular cell is clicked, the game checks
        if all good squares have been clicked'''
        for cell in self.cells.values():
            if not cell.badCell and not cell.isExposed: # if there are more cells to expose, stop running the function
                return
        self.win = True # if all safe cells have been exposed, flip the flag to true
        if self.win == True: # then you win the game
            cell.won_game()

def play_minesweeper():
    """Creates a minesweeper grid with w *h squares and n bombs so player can play the game"""
    root = Tk()
    root.title('Minesweeper')
    root.eval('tk::PlaceWindow . center')
    (width, height, numBombs) = decide_difficulty()
    MinesweeperGrid(root, width, height, numBombs)
    root.mainloop()

def decide_difficulty():
    """Takes user input and to set board according to difficulty"""
    user_input = simpledialog.askstring(title="Choose difficulty",
                                        prompt="What difficulty would you like to play (easy/medium/hard/custom)?")

    if user_input.lower() == '':
        messagebox.showwarning("Unable to start game", "You need to pick a difficulty")
    elif user_input.lower() == "easy": # return parameter list for set_board function to use
        return 9, 9, 10 # this is conventional game settings from the official website
    elif user_input.lower() == "medium":
        return 16, 16, 40
    elif user_input.lower() == "hard":
        return 30, 16, 99
    elif user_input.lower() == "custom":
        width = int(simpledialog.askstring(title="Choose width",
                                            prompt="How tall is the board going to be?"))
        height = int(simpledialog.askstring(title="Choose height",
                                            prompt="How high is the board going to be?"))
        numBombs = int(simpledialog.askstring(title="Choose number of bombs",
                                              prompt="How many bombs will there be?"))
        if numBombs < width * height:
            return width, height, numBombs
        else:
            messagebox.showerror("Too many bombs",
                                 "You need to have less bombs than total squares")

if __name__ == "__main__":
    '''Drives the game'''
    play_minesweeper()


