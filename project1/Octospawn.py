from copy import deepcopy

from sympy.abc import alpha

from easyAI import TwoPlayerGame
from itertools import product
import time

import copy

import random
inf = float("infinity")

# Convert D7 to (3,6) and back...
to_string = lambda move: " ".join(
    ["ABCDEFGHIJ"[move[i][0]] + str(move[i][1] + 1) for i in (0, 1)]
)
to_tuple = lambda s: ("ABCDEFGHIJ".index(s[0]), int(s[1:]) - 1)


class Octospawn(TwoPlayerGame):
    """
    A nice game whose rules are explained here:
    http://fr.wikipedia.org/wiki/Hexapawn
    """

    def __init__(self, players, chance, size=(4, 4)):
        self.size = M, N = size
        self.chance = chance
        p = [[(i, j) for j in range(N)] for i in [0, M - 1]]



        for i, d, goal, pawns in [(0, 1, M - 1, p[0]), (1, -1, 0, p[1])]:
            players[i].direction = d  # gracz 1 ma direction = 1, gracz 2 ma direction = -1 ( góra doł)
            players[i].goal_line = goal
            players[i].pawns = {x: pawns[x] for x in range(len(pawns))}


        self.players = players
        self.current_player = 1
        self.removed_pawns = {1: [], 2: []} # klucze to index gracza, wartosc to index pionka
        self.start_positions = {
            1: {x: p[0][x] for x in range(len(p[0]))},
            2: {x: p[1][x] for x in range(len(p[1]))},
        }

    def possible_moves(self):
        moves = []
        d = self.player.direction
        M, N = self.size

        own_pawns = set(self.player.pawns.values())
        opponent_pawns = set(self.opponent.pawns.values())

        for i, j in self.player.pawns.values():
            # ruch do przodu
            ni, nj = i + d, j
            if 0 <= ni < M and 0 <= nj < N:
                if (ni, nj) not in own_pawns and (ni, nj) not in opponent_pawns:
                    moves.append(((i, j), (ni, nj)))

            # bicie po skosie w prawo
            ni, nj = i + d, j + 1
            if 0 <= ni < M and 0 <= nj < N:
                if (ni, nj) in opponent_pawns:
                    moves.append(((i, j), (ni, nj)))

            # bicie po skosie w lewo
            ni, nj = i + d, j - 1
            if 0 <= ni < M and 0 <= nj < N:
                if (ni, nj) in opponent_pawns:
                    moves.append(((i, j), (ni, nj)))

        return [to_string(m) for m in moves]

    def make_move(self, move):

        move = list(map(to_tuple, move.split(" ")))  # zamieniamy A1 na współrzędne

        source = move[0]
        target = move[1]

        ind = None
        for idx, pos in self.player.pawns.items():
            if pos == source:
                ind = idx
                break

        captured_id = None

        for idx, pos in list(self.opponent.pawns.items()):
            if pos == target:
                captured_id = idx
                break

        self.player.pawns[ind] = target  # zmiana pozycji pionka na planszy

        if captured_id is not None:  # czy było bicie?
            del self.opponent.pawns[captured_id]
            self.removed_pawns[self.opponent_index].append(captured_id)

            # losujemy 10% tylko po zbiciu
            if self.removed_pawns[self.opponent_index] and random.random() < self.chance:
                pawn_id = random.choice(self.removed_pawns[self.opponent_index])
                start_pos = self.start_positions[self.opponent_index][pawn_id]

                # sprawdzamy, czy pole startowe jest wolne

                self.opponent.pawns[pawn_id] = start_pos
                self.removed_pawns[self.opponent_index].remove(pawn_id)





    def lose(self):
        return any([i == self.opponent.goal_line for i, j in self.opponent.pawns.values()]) or (  # spreawdzamy czy aktualny gracz przegrał
            self.possible_moves() == []
        )

    def is_over(self):
        return self.lose()

    def show(self): # wyświetlanie planszy w terminalu
        f = (
            lambda x: "1"
            if x in self.players[0].pawns.values()
            else ("2" if x in self.players[1].pawns.values() else ".")
        )
        print(
            "\n".join(
                [
                    " ".join([f((i, j)) for j in range(self.size[1])])
                    for i in range(self.size[0])
                ]
            )
        )
        print(self.players[0].pawns)
        print(self.players[1].pawns)
        print(self.removed_pawns)

    def copy(self):
        return copy.deepcopy(self)

    def make_move_simple(self, move):
        move = list(map(to_tuple, move.split(" ")))
        source = move[0]
        target = move[1]

        ind = None
        for idx, pos in self.player.pawns.items():
            if pos == source:
                ind = idx
                break

        captured_id = None
        for idx, pos in list(self.opponent.pawns.items()):
            if pos == target:
                captured_id = idx
                break

        self.player.pawns[ind] = target

        if captured_id is not None:
            del self.opponent.pawns[captured_id]
            self.removed_pawns[self.opponent_index].append(captured_id)

        return captured_id is not None









if __name__ == "__main__":
    from easyAI import AI_Player, Human_Player, Negamax

    scoring = lambda game: -100 if game.lose() else 0
    times = []

    scores = [0,0]
    avg_time = 0.0
    for depth, cond in product([5,10], [True, False]):
        ai= Negamax(depth, scoring, cond=cond)

        print(f'głębokość {ai.depth}, pruning: {ai.cond}')
        for chance in [0.1, 0.0]:
            scores = [0,0]
            avg_time = 0.0
            print(f"szansunia {chance}")
            for i in range(100):
                g = Octospawn([AI_Player(ai), AI_Player(ai)], chance)

                g.current_player = i % 2 + 1
                _, time_per_game = g.play()
                avg_time += time_per_game
                scores[g.opponent_index -1] += 1
                print("player %d wins after %d turns " % (g.opponent_index, g.nmove))
                print(time_per_game)


            print(scores)
            print(avg_time/100)
            times.append(f"głębokość {depth}, szansa {chance}, pruning {cond} czas {avg_time/100}")


