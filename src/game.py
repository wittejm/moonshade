import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

# center space at (3,3)
# row indicated by y coord 0 to 6 (top to bot)
# top row has x coord 0 to 3
# middle row has x coord 0 to 6
# bottom row has x coord 3 to 6
# 0,0 is the upper-left
# 6,6 is the bottom-right
# 0,6 and 6,0 don't exist.
# the N/S axis is slanted to the upper-right / lower-left.

# coords are in (y, x) format

# Moon in position 1 thru 6:
# Having a direction of its shine/shade
# Starts in the east, shining west
# +0 -1 (W-facing)
# -1 -1 (NW-facing)
# -1 +0 (NE-facing)
# +0 +1 (E-facing)
# +1 +1 (SE-facing)
# +1 +0 (SW-facing)


'''
       1  1  1  1  0  0  0
      1  1  1  1  1  0  0
     1  1  1  1  1  1  0
    1  1  1  X  1  1  1
   0 1  1  1  1  1  1
  0 0 1  1  1  1  1
 0 0 0 1  1  1  1
'''

# actions:
# from a chosen tree, place a seed; or, grow or harvest that tree.
# if a chosen tree is shaded, it can't be used.

# so, best way to track a player's possible moves is through their set
# of trees on the board.

# There's also the AVAILABLE pool pieces; and the reserve.

# From any board state (locations of trees, seeds, and moon) we get
# the shade map. and use trees+shade to determine permitted moves.

# game setup: select 1 of the 18 edge spaces; then repeat for 2 x #players

colors = "\033[92m", "\033[91m", "\033[93m", "\033[96m"
ENDCOLOR = "\033[0m"
CAST = ((0,-1),(-1,-1),(-1,0),(0,1),(1,1),(1,0))
#y-coord first)
# +0 -1 ( W-facing)
# -1 -1 (NW-facing)
# -1 0 (NE-facing)
# +0 +1 ( E-facing)
# +1 1 (SE-facing)
# +1 0 (SW-facing)


SEED = 0
SMALL = 1
MEDIUM = 2
LARGE = 3

def size_name(size):
    return ["SEED", "SMALL", "MEDIUM", "LARGE"][size]

class Reserve:
    costs = (
        (1,1,2,2),
        (2,2,3,3),
        (3,3,4),
        (4,5)
    )
    count = [4, 4, 3, 2]
    MAX = 4, 4, 3, 2

    def cost(self, size):
        return self.costs[size][self.MAX[size] - self.count[size]]

@dataclass
class Tree:
    # includes Seed, which has size 0
    player: int
    size: int
    y: int
    x: int


@dataclass
class Player:
    available: List[int]
    reserve: Reserve
    moonlight: int
    victory_tokens: List[int]

    @staticmethod
    def initial():
        return Player(
            available= [2,4,1,0],
            reserve= Reserve(),
            moonlight= 0,
            victory_tokens=[]
            )

@dataclass
class Game:
    players: Tuple[Player, Player, Player, Player]
    trees: List[Tree]
    direction: int

    @staticmethod
    def create_game(num_players):
        game = Game(
            players = tuple([Player.initial() for i in range(num_players)]),
            trees = [
                Tree(0,1,0,0),
                Tree(0,1,0,3),
                Tree(1,1,3,0),
                Tree(1,1,6,3),
                Tree(2,1,6,6),
                Tree(2,1,3,6),
            ], #assume 3 players
            direction = 0 # starts west-facing.
        )
        return game

    def get_light_map(self):
        light_map = np.ones((7,7), dtype=int)
        shadow_dir = CAST[self.direction]
        for tree in self.trees:
            for i in range(1,tree.size+1):
                if (
                    tree.y + (shadow_dir[0]*i) > 6 or
                    tree.x + (shadow_dir[1]*i) > 6 or
                    tree.y + (shadow_dir[0]*i) < 0 or
                    tree.x + (shadow_dir[1]*i) < 0):
                        continue # off-board.
                light_map[tree.y+(shadow_dir[0]*i)][tree.x + (shadow_dir[1]*i)]=0
        return light_map

    def get_tree_map(self):
        """
        From the set of trees, make the array whose values represent all the tree data
        -1 is empty space
        0-15 are pieces.
        -2 is a reserved value for visualizing valid seed spots.
        -3 is off-board (upper-right, lower-left corner regions)
        """

        tree_map = -1 * np.ones((7,7), dtype=int)
        for tree in self.trees:
            tree_map[tree.y][tree.x] = tree.size + tree.player*4
        # mark the out-of-bounds spaces
        for y in range(3):
            for x in range(4+y,7):
                tree_map[y][x] = -3
        for y in range(4,7):
            for x in range(0,y-3):
                tree_map[y][x] = -3
        return tree_map


    def apply_move(self, move):
        player = self.players[move.player]
        player.moonlight -= move.cost()
        if move.name == "Harvest":
            player.reserve.large += 1
        elif move.name == "Grow":
            player.reserve.count[move.new_size-1] = min(Reserve.MAX[move.new_size-1], player.reserve.count[move.new_size-1] + 1)
            player.available[move.new_size] -= 1
        elif move.name == "Throw":
            player.available[SEED] -= 1
        for ind in range(len(self.trees)):
                tree=self.trees[ind]
                if tree.y == move.y0 and tree.x == move.x0:
                    tree_index = ind
                    break
        if move.name=="Grow":
                tree=self.trees[tree_index]
                if tree.y == move.y0 and tree.x == move.x0:
                    tree.size+=1
        elif move.name == "Harvest":
            self.trees = self.trees[:tree_index] + trees[tree_index+1:]
        elif move.name == "Throw":
            self.trees.append(Tree(move.player, 0, move.y1, move.x1))

@dataclass
class Move:
    player: int
    name: str
    new_size: int
    y0: int
    x0: int
    y1: int
    x1: int
    buy_cost: int

    def cost(self):
        if self.name=="Grow":
            return self.new_size
        elif self.name=="Harvest":
            return 4
        elif self.name=="Throw":
            return 1
        elif self.name=="Buy":
            return self.buy_cost

def print_hex_grid(tree_map):
    outstr=""
    for i in range(7):
        line = " " * (6-i) + str(i) + " "
        for j in range(7):
            #off=board
            if tree_map[i,j] == -3:
                line += "_"
            #potential seed-spot
            elif tree_map[i,j] == -2:
                line += "+"
            #empty space
            elif tree_map[i,j] == -1:
                line += "-"
            else:
                line += colors[int(tree_map[i,j]/4)]+str(tree_map[i,j]%4)+ENDCOLOR
            line += " "
        outstr += line  + "\n"
    print("\n----\n         0 1 2 3 4 5 6\n" + outstr + "\n----\n")

def get_moves(game, player_num):
    # for each tree, there is:grow, harvest, or throw a seed.
    trees = game.trees
    direction = game.direction
    player = game.players[player_num]
    moves: List[Move] = []
    light_map = game.get_light_map()
    tree_map = game.get_tree_map()
    moonlight = game.players[player_num].moonlight
    for size in range(4):

        if player.reserve.count[size]:
            cost = player.reserve.cost(size)
            if moonlight >= cost:
                move = Move(player_num, "Buy", size, -1,-1, -1,-1, cost)
                moves.append(move)

    for tree in trees:
        if tree.player == player_num and light_map[tree.y,tree.x]:
            if tree.size == 3:
                move = Move(player_num, "Harvest", -1, tree.y,tree.x, -1,-1, -1)
                if move.cost() <= moonlight:
                    moves.append(move)
            else:
                move = Move(player_num, "Grow", tree.size+1, tree.y,tree.x, -1,-1, -1)
                if move.cost() <= moonlight and player.available[tree.size+1]:
                    moves.append(move)
            if tree.size > 0 and player.available[SEED]:
                # throw-actions.
                # check open neighbor spaces of distance up to size,
                # and add any throwables.

                for y_dist_from_tree in range(-tree.size, tree.size + 1):
                    i = tree.y + y_dist_from_tree
                    if i<0 or i>6: continue
                    for j in range(max(0, tree.x - tree.size + max(0, y_dist_from_tree)), min(7, tree.x + tree.size + min(0, y_dist_from_tree) + 1)):
                        if light_map[i,j] and tree_map[i,j] == -1:
                            tree_map[i,j] = -2

                            move = Move(player_num, "Throw", 0, tree.y,tree.x, i,j, -1)
                            if move.cost() <= moonlight:
                                moves.append(move)

    print_hex_grid(tree_map)
    print(colors[player_num] + "Player " + str(player_num) + ENDCOLOR)
    print("Available:", player.available, ". Moonlight:", moonlight)
    print("Moves:")
    for ind in range(len(moves)):
        move = moves[ind]
        print(ind, " ("+str(move.cost())+"):", (move.y0, move.x0) if move.y0 >= 0 else "" , move.name, size_name(move.new_size), (move.y1, move.x1) if move.y1 >= 0 else "")
    return moves

'''

Making a gui?
Also the lists of VP tokens.
Also, when determining moves,
print the ascii board with colors!!! and dot sizes?

'''

def get_moonlight(trees, player, light_map):
    moonlight = 0
    for tree in trees:
        if tree.player == player and light_map[tree.y, tree.x]:
            moonlight+= tree.size
    return moonlight

num_players = 3
player_num = 0
turn_count = 0

game = Game.create_game(num_players)

while True:
    light_map = game.get_light_map()
    game.players[player_num].moonlight += get_moonlight(game.trees, player_num, light_map)
    player_taking_turn = True
    while player_taking_turn:
        moves = get_moves(game, player_num)
        print(["WEST", "NW", "NE", "EAST", "SE", "SW"][game.direction])
        print(colors[player_num] + "Player " + str(player_num) + ENDCOLOR,
            "\nwhich move? (by index; leave blank to end turn) " if moves else "(no moves; press enter)")
        response = input()
        if moves and response:
            index = int(response)
            if index >= len(moves):
                continue
            game.apply_move(moves[index])
        else:
            player_taking_turn = False
    player_num = (player_num+1) % 3
    turn_count += 1
    if turn_count % 3 == 0:
        game.direction = (game.direction+1) % 6
        player_num = (player_num+1) % 3

# Need to support purchasing from the reserve

# All of these operations / steps need names.

# apply move does the following:
#  - change the population of trees
#  - change the available pool
#  - change the reserve pool

# we have input (button.. +text? ) that executes whatever.
# and we have the text show the board state.
# This can at first look just like this terminal output, but better.
# Easy to make the text board have nice size, spacing, and color

