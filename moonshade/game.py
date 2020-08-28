from typing import List, Tuple, Iterator

import numpy as np

from moonshade.models import Game, Move, SEED, Player, Tree, Direction
from moonshade.printer import Printer

# center space at (3,3)
# row indicated by y coord 0 to 6 (top to bot)
# top row has x coord 0 to 3
# middle row has x coord 0 to 6
# bottom row has x coord 3 to 6
# 0,0 is the upper-left
# 6,6 is the bottom-right
# 0,6 and 6,0 don't exist.
# the N/S axis is slanted to the upper-right / lower-left.
"""
       1  1  1  1  0  0  0
      1  1  1  1  1  0  0
     1  1  1  1  1  1  0
    1  1  1  X  1  1  1
   0 1  1  1  1  1  1
  0 0 1  1  1  1  1
 0 0 0 1  1  1  1
"""

# actions:
# from a chosen tree, place a seed; or, grow or harvest that tree.
# if a chosen tree is shaded, it can't be used.

# so, best way to track a player's possible moves is through their set
# of trees on the board.

# There's also the AVAILABLE pool pieces; and the reserve.

# From any board state (locations of trees, seeds, and moon) we get
# the shade map. and use trees+shade to determine permitted moves.

# game setup: select 1 of the 18 edge spaces; then repeat for 2 x #players


def get_throwable_range(tree: Tree) -> Iterator[Tuple[int, int]]:
    for y_dist_from_tree in range(-tree.size, tree.size + 1):
        i = tree.y + y_dist_from_tree
        if 0 <= i <= 6:
            for j in range(
                tree.x - tree.size + max(0, y_dist_from_tree), tree.x + tree.size + min(0, y_dist_from_tree) + 1,
            ):
                if 0 <= j <= 6:
                    yield i, j


def get_moves(game: Game, player_num: int, touched_trees: List[Tree]) -> Tuple[List[Move], np.ndarray]:
    # for each tree, there is: grow, harvest, or throw a seed.
    trees: List[Tree] = game.trees
    player: Player = game.players[player_num]
    light_map: np.ndarray = game.get_light_map()
    tree_map: np.ndarray = game.get_tree_map()
    moves: List[Move] = []
    for size in range(4):
        if player.reserve.count[size]:
            cost = player.reserve.cost(size)
            move = Move(player_num, "Buy", new_size=size, source_tree=None, y_throw=-1, x_throw=-1, buy_cost=cost)
            moves.append(move)
    for tree in trees:
        if tree.player == player_num and light_map[tree.y, tree.x] and tree not in touched_trees:
            if tree.size == 3:
                move = Move(player_num, "Harvest", new_size=-1, source_tree=tree, y_throw=-1, x_throw=-1, buy_cost=-1)
                moves.append(move)
            elif player.available[tree.size + 1]:
                move = Move(
                    player_num, "Grow", new_size=tree.size + 1, source_tree=tree, y_throw=-1, x_throw=-1, buy_cost=-1
                )
                moves.append(move)
            if tree.size > 0 and player.available[SEED]:
                # throw-actions.
                # check open neighbor spaces of distance up to size,
                # and add any throwables.
                for i, j in get_throwable_range(tree):
                    if light_map[i, j] and tree_map[i, j] == -1:
                        tree_map[i, j] = -2
                        move = Move(
                            player_num, "Throw", new_size=0, source_tree=tree, y_throw=i, x_throw=j, buy_cost=-1
                        )
                        moves.append(move)
    moonlight = player.moonlight
    valid_moves = [move for move in moves if move.cost() <= moonlight]
    return valid_moves, tree_map


def get_moonlight(trees, player, light_map):
    moonlight = 0
    for tree in trees:
        if tree.player == player and light_map[tree.y, tree.x]:
            moonlight += tree.size
    return moonlight


num_players = 3
player_num = 0
turn_count = 0
rounds = 1

game = Game.create_game(num_players)

while rounds <= 3:
    light_map = game.get_light_map()
    game.players[player_num].moonlight += get_moonlight(game.trees, player_num, light_map)
    player_taking_turn = True
    touched_trees: List[Tree] = []
    while player_taking_turn:
        moves, tree_map = get_moves(game, player_num, touched_trees)
        player = game.players[player_num]
        Printer.print_hex_grid(tree_map)
        Printer.print_moves(player, player_num, moves)
        Printer.print_prompt(game.direction, player_num, moves)
        response = input()
        if moves and response:
            index = int(response)
            if 0 <= index < len(moves):
                move = moves[index]
                new_tree = game.apply_move(move)
                if new_tree:
                    touched_trees.append(new_tree)
                touched_trees.append(move.source_tree)
        else:
            player_taking_turn = False
    player_num = (player_num + 1) % 3
    turn_count += 1
    if turn_count % 3 == 0:
        if game.direction == Direction.SW:
            rounds += 1
        game.direction = game.direction.next()
        player_num = (player_num + 1) % 3


# All of these operations / steps need names.

# apply move does the following:
#  - change the population of trees
#  - change the available pool
#  - change the reserve pool

# we have input (button.. +text? ) that executes whatever.
# and we have the text show the board state.
# This can at first look just like this terminal output, but better.
# Easy to make the text board have nice size, spacing, and color


"""

Making a gui?
Also the lists of VP tokens.
Also, when determining moves,
print the ascii board with colors!!! and dot sizes?

"""
