from typing import List
from moonshade.models import Direction, Move, Player


def size_name(size):
    return ["SEED", "SMALL", "MEDIUM", "LARGE"][size]


class Printer:
    COLORS = "\033[92m", "\033[91m", "\033[93m", "\033[96m"
    END_COLOR = "\033[0m"

    @staticmethod
    def print_hex_grid(tree_map):
        outstr = ""
        for i in range(7):
            line = " " * (6 - i) + str(i) + " "
            for j in range(7):
                # off=board
                if tree_map[i, j] == -3:
                    line += "_"
                # potential seed-spot
                elif tree_map[i, j] == -2:
                    line += "+"
                # empty space
                elif tree_map[i, j] == -1:
                    line += "-"
                else:
                    line += Printer.COLORS[int(tree_map[i, j] / 4)] + str(tree_map[i, j] % 4) + Printer.END_COLOR
                line += " "
            outstr += line + "\n"
        print("\n----\n         0 1 2 3 4 5 6\n" + outstr + "\n----\n")

    @staticmethod
    def print_moves(player: Player, player_num: int, moves: List[Move]):
        print(Printer.COLORS[player_num] + "Player " + str(player_num) + Printer.END_COLOR)
        print("Available:", player.available, ". Moonlight:", player.moonlight)
        print("Moves:")
        for i, move in enumerate(moves):
            print(
                i,
                " (" + str(move.cost()) + "):",
                (move.source_tree.y, move.source_tree.x) if move.source_tree else "",
                move.name,
                size_name(move.new_size),
                (move.y_throw, move.x_throw) if move.y_throw >= 0 else "",
            )

    @staticmethod
    def print_prompt(direction: Direction, player_num: int, moves: List[Move]):
        print(direction)
        print(
            Printer.COLORS[player_num] + "Player " + str(player_num) + Printer.END_COLOR,
            "\nwhich move? (by index; leave blank to end turn) " if moves else "(no moves; press enter)",
        )
