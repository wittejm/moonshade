import numpy as np
from dataclasses import dataclass
from typing import Optional, List

# center space at (3,3)
# row indicated by y coord 0 to 6 (top to bot)
# top row has x coord 0 to 3
# middle row has x coord 0 to 6
# bottom row has x coord 3 to 6
# 0,0 is the upper-left
# 6,6 is the bottom-right
# 0,6 and 6,0 don't exist.
# the N/S axis is slanted to the upper-left / lower-right.

# Moon in position 1 thru 6:
# Having a direction of its shine/shade
# Starts in the east, shining west
# -1 +0 (W-facing)
# +0 -1 (NW-facing)
# +1 -1 (NE-facing)
# +1 +0 (E-facing)
# +0 +1 (SE-facing)
# -1 +1 (SW-facing)


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

@dataclass
class Tree:
    player: int
    size: int
    y: int
    x: int


available = np.asarray([
    [2,2,1,0],
    [2,2,1,0],
    [2,2,1,0],
    [2,2,1,0]
])

reserve = np.asarray([
    [2,2,1,0],
    [2,2,1,0],
    [2,2,1,0],
    [2,2,1,0]
])

class bcolors:
    #HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    #BOLD = '\033[1m'
    #UNDERLINE = '\033[4m'

colors = bcolors.OKGREEN, bcolors.FAIL, bcolors.WARNING
@dataclass
class Move:
    player: int
    name: str
    new_size: int
    y0: int
    x0: int
    y1: int = -1
    x1: int = -1
    # If x1 and y1 are given(as >=0), it's a throw-seed. otherwise it's a grow or harvest.
    # and if it's a grow/harvest but space y0/x0 is not occupied, it's not a legal move

# A tree is just a 4-tuple: the owner, size, x-coord, and y-coord.

# from th collection of all trees, compute shade.
# This is to start with full light and accumulate shade by walking trees.

# then get "tree is shaded" by checking the tree location against the shade grid.
# then

cast = ((0,-1),(-1,-1),(-1,0),(0,1),(1,1),(1,0))
#y-coord first)
# +0 -1 ( W-facing)
# -1 -1 (NW-facing)
# -1 0 (NE-facing)
# +0 +1 ( E-facing)
# +1 1 (SE-facing)
# +1 0 (SW-facing)

def get_lightmap(trees, direction):
    lightmap = np.ones((7,7), dtype=int)
    shadow_dir = cast[direction]

    for tree in trees:
        for i in range(1,tree.size+1):
            if (
                tree.y + (shadow_dir[0]*i) > 6 or
                tree.x + (shadow_dir[1]*i) > 6 or
                tree.y + (shadow_dir[0]*i) < 0 or
                tree.x + (shadow_dir[1]*i) < 0):
                    continue

            lightmap[tree.y+(shadow_dir[0]*i)][tree.x + (shadow_dir[1]*i)]=0

    #print_hex_grid(lightmap)
    return lightmap

def get_tree_map(trees):
    tree_map = -1 * np.ones((7,7), dtype=int)
    for tree in trees:
        tree_map[tree.y][tree.x] = tree.size + tree.player*4
    # hide the out-of-bounds spaces
    for y in range(3):
        for x in range(4+y,7):
            tree_map[y][x] = -3
    for y in range(4,7):
        for x in range(0,y-3):
            tree_map[y][x] = -3
    return tree_map

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
                line += colors[int(tree_map[i,j]/4)]+str(tree_map[i,j]%4)+bcolors.ENDC
            line += " "
        outstr += line  + "\n"
    print("\n----\n         0 1 2 3 4 5 6\n" + outstr + "\n----\n")
'''
trees = [
    Tree(0,1,0,0),
    Tree(0,1,6,6),
    Tree(0,0,3,6),
    Tree(0,1,3,5),
    Tree(0,2,3,4),
    Tree(0,3,3,3),
    Tree(0,2,5,6),
    Tree(0,0,1,2),
    Tree(0,0,4,6),
    Tree(0,2,2,2),
    Tree(0,3,0,3),
]
'''
trees = [
    Tree(0,1,0,0),
    Tree(0,1,0,3),
    Tree(1,1,3,0),
    Tree(1,1,6,3),
    Tree(2,1,6,6),
    Tree(2,1,3,6),

]

def moonlight(trees):
    # This is just the sum of your tree values masked by the shade map.
    # and it returns a value.
    return 0

def get_moves(trees, player, direction, moonlight):
    # for each tree, there is:grow, harvest, or throw a seed.
    moves: List[Move] = []
    lightmap = get_lightmap(trees, direction)
    tree_map = get_tree_map(trees)
    #print_hex_grid(tree_map)

    for tree in trees:
        #print("===", tree.y, tree.x, "===, (size " , tree.size, ")")
        if tree.player == player and lightmap[tree.y,tree.x]:
            if tree.size == 3:
                move = Move(player, "Harvest", -1, tree.y,tree.x, -1,-1)
                if move_cost(move) <= moonlight[player]:
                    moves.append(move)
            else:
                move = Move(player, "Grow", tree.size+1, tree.y,tree.x, -1,-1)
                if move_cost(move) <= moonlight[player] and available[player][tree.size+1]:
                    moves.append(move)
            if tree.size > 0 and available[player][0]:
                # check open neighbor spaces of distance up to size,
                # and add any throwables.

                for y_dist_from_tree in range(-tree.size, tree.size + 1):
                    i = tree.y + y_dist_from_tree
                    if i<0 or i>6: continue
                    for j in range(max(0, tree.x - tree.size + max(0, y_dist_from_tree)), min(7, tree.x + tree.size + min(0, y_dist_from_tree) + 1)):
                        if lightmap[i,j] and tree_map[i,j] == -1:
                            tree_map[i,j] = -2

                            move = Move(player, "Throw", 0, tree.y,tree.x, i,j)
                            if move_cost(move) <= moonlight[player]:
                                moves.append(move)

    print_hex_grid(tree_map)
    print("Available:", available[player], ". Moonlight:", moonlight[player])
    print("Moves:")
    for ind in range(len(moves)):
        move = moves[ind]
        print(ind, " ("+str(move_cost(move))+"):", (move.y0, move.x0) , move.name, move.new_size, (y if (y:= move.y1)>=0 else ""), (x if (x:= move.x1)>=0 else ""))
    return moves
    #print(tree_map)

# How to specify a move:
# "the tree at location (x,y)"



def move_cost(move):
    if move.name=="Grow":
        return move.new_size
    elif move.name=="Harvest":
        return 4
    elif move.name=="Throw":
        return 1

def apply_move(trees, move, moonlight):
    moonlight[move.player] -= move_cost(move)
    if move.name == "Harvest":
        reserve[move.player,3] += 1
    elif move.name == "Grow":
        reserve[move.player, move.new_size-1] += 1
        available[move.player, move.new_size] -= 1
    elif move.name == "Throw":
        available[move.player, 0] -= 1
    for ind in range(len(trees)):
            tree=trees[ind]
            if tree.y == move.y0 and tree.x == move.x0:
                tree_index = ind
                break
    if move.name=="Grow":
            tree=trees[tree_index]
            if tree.y == move.y0 and tree.x == move.x0:
                tree.size+=1
    elif move.name == "Harvest":
        trees = trees[:tree_index] + trees[tree_index+1:]
    elif move.name == "Throw":
        trees.append(Tree(move.player, 0, move.y1, move.x1))
    return trees
'''

Making a gui?
Also the lists of VP tokens.
Also, when determining moves,
print the ascii board with colors!!! and dot sizes?

'''

def get_moonlight(trees, player, lightmap):
    moonlight = 0
    for tree in trees:
        if tree.player == player and lightmap[tree.y, tree.x]:
            moonlight+= tree.size
    return moonlight

num_players = 3
player = 0
direction = 0
direction_counter = 0
moonlight=[0,0,0]
while True:
    lightmap = get_lightmap(trees, direction)
    moonlight[player] += get_moonlight(trees, player, lightmap)
    player_taking_turn = True
    while player_taking_turn:
        moves = get_moves(trees, player, direction, moonlight)
        print(["WEST", "NW", "NE", "E", "SE", "SW"][direction])
        print(colors[player] + "Player " + str(player) + bcolors.ENDC,
            "\nwhich move? (by index; leave blank to end turn) " if moves else "(no moves; press enter)")
        response = input()
        if moves and response:
            index = int(response)
            if index >= len(moves):
                continue
            trees = apply_move(trees, moves[index], moonlight)
        else:
            player_taking_turn = False
    player = (player+1) % 3
    direction_counter = direction_counter + 1
    if direction_counter == 3:
        direction = (direction+1) % 6
        player = (player+1) % 3
        direction_counter = 0

# Need to support purchasing from the reserve
# and planting from and the AVAILABLE pool.
# the reserve and AP are both:
# length 4 integer tuples.

# All of these operations / steps need names.

# apply move does the following:
#  - change the population of trees
#  - change the available pool
#  - change the reserve pool

# Is it time to make this OO?
# and JS?
# we have input (button.. +text? ) that executes whatever.
# and we have the text show the board state.
# This can at first look just like this terminal output, but better.
# Easy to make the text board have nice size, spacing, and color
