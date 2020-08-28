from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List, Optional

import numpy as np

SEED = 0
SMALL = 1
MEDIUM = 2
LARGE = 3


class Direction(str, Enum):
    W = "West facing"
    NW = "Northwest facing"
    NE = "Northeast facing"
    E = "East facing"
    SE = "Southeast facing"
    SW = "Southwest facing"

    def cast(self):
        return {
            Direction.W: (0, -1),
            Direction.NW: (-1, -1),
            Direction.NE: (-1, 0),
            Direction.E: (0, 1),
            Direction.SE: (1, 1),
            Direction.SW: (1, 0),
        }[self]

    # Adapted from https://stackoverflow.com/a/35905666/2750819
    def next(self):
        klass = self.__class__
        members: List = list(klass)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def __str__(self):
        return self


@dataclass
class Tree:
    # includes Seed, which has size 0
    player: int
    size: int
    y: int
    x: int


class Reserve:
    costs = ((1, 1, 2, 2), (2, 2, 3, 3), (3, 3, 4), (4, 5))
    count = [4, 4, 3, 2]
    MAX = 4, 4, 3, 2

    def cost(self, size):
        return self.costs[size][self.MAX[size] - self.count[size]]


@dataclass
class Player:
    available: List[int]
    reserve: Reserve
    moonlight: int
    victory_tokens: List[int]

    @staticmethod
    def initial():
        return Player(available=[2, 4, 1, 0], reserve=Reserve(), moonlight=0, victory_tokens=[])


@dataclass
class Move:
    player: int
    name: str
    new_size: int
    source_tree: Optional[Tree]
    y_throw: int
    x_throw: int
    buy_cost: int

    def cost(self):
        if self.name == "Grow":
            return self.new_size
        elif self.name == "Harvest":
            return 4
        elif self.name == "Throw":
            return 1
        elif self.name == "Buy":
            return self.buy_cost


@dataclass
class Game:
    players: Tuple[Player, ...]
    trees: List[Tree]
    direction: Direction

    @staticmethod
    def create_game(num_players):
        game = Game(
            players=tuple([Player.initial() for _ in range(num_players)]),
            trees=[
                Tree(0, 1, 0, 0),
                Tree(0, 1, 0, 3),
                Tree(1, 1, 3, 0),
                Tree(1, 1, 6, 3),
                Tree(2, 1, 6, 6),
                Tree(2, 1, 3, 6),
            ],  # assume 3 players
            direction=Direction.W,
        )
        return game

    def get_light_map(self) -> np.ndarray:
        light_map = np.ones((7, 7), dtype=int)
        shadow_dir = self.direction.cast()
        for tree in self.trees:
            for i in range(1, tree.size + 1):
                if (
                    tree.y + (shadow_dir[0] * i) > 6
                    or tree.x + (shadow_dir[1] * i) > 6
                    or tree.y + (shadow_dir[0] * i) < 0
                    or tree.x + (shadow_dir[1] * i) < 0
                ):
                    continue  # off-board.
                light_map[tree.y + (shadow_dir[0] * i)][tree.x + (shadow_dir[1] * i)] = 0
        return light_map

    def get_tree_map(self) -> np.ndarray:
        """
        From the set of trees, make the array whose values represent all the tree data
        -1 is empty space
        0-15 are pieces.
        -2 is a reserved value for visualizing valid seed spots.
        -3 is off-board (upper-right, lower-left corner regions)
        """

        tree_map = -1 * np.ones((7, 7), dtype=int)
        for tree in self.trees:
            tree_map[tree.y][tree.x] = tree.size + tree.player * 4
        # mark the out-of-bounds spaces
        for y in range(3):
            for x in range(4 + y, 7):
                tree_map[y][x] = -3
        for y in range(4, 7):
            for x in range(0, y - 3):
                tree_map[y][x] = -3
        return tree_map

    def apply_move(self, move: Move) -> Optional[Tree]:
        player = self.players[move.player]
        player.moonlight -= move.cost()
        if move.name == "Grow":
            move.source_tree.size += 1
            player.reserve.count[move.new_size - 1] = min(
                Reserve.MAX[move.new_size - 1], player.reserve.count[move.new_size - 1] + 1
            )
            player.available[move.new_size] -= 1
        elif move.name == "Harvest":
            self.trees = [tree for tree in self.trees if tree != move.source_tree]
            player.reserve.count[LARGE] += 1
        elif move.name == "Throw":
            new_tree = Tree(move.player, 0, move.y_throw, move.x_throw)
            self.trees.append(new_tree)
            player.available[SEED] -= 1
            return new_tree
        elif move.name == "Buy":
            player.available[move.new_size] += 1
            player.reserve.count[move.new_size] -= 1
        return None
