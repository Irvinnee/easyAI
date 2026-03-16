from copy import deepcopy

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
        self.undo_stack = []
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

        undo_move = {
            "player_index": self.current_player,
            "pawn_index": ind,
            "source": source,
            "target": target,
            "captured_id": captured_id,
            "respawned_id": None,
        }

        self.player.pawns[ind] = target  # zmiana pozycji pionka na planszy

        if captured_id is not None:  # czy było bicie?
            del self.opponent.pawns[captured_id]
            self.removed_pawns[self.opponent_index].append(captured_id)

        # losowe odrodzenie po ruchu
        if self.removed_pawns[self.opponent_index] and random.random() < self.chance:
            pawn_id = random.choice(self.removed_pawns[self.opponent_index])
            start_pos = self.start_positions[self.opponent_index][pawn_id]
            self.opponent.pawns[pawn_id] = start_pos
            self.removed_pawns[self.opponent_index].remove(pawn_id)
            undo_move["respawned_id"] = pawn_id

        self.undo_stack.append(undo_move)

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

    def unmake_move(self, move):
        move = self.undo_stack.pop()
        player_index = move["player_index"]
        pawn_index = move["pawn_index"]
        source = move["source"]
        target = move["target"]
        captured_id = move["captured_id"]
        respawned_id = move["respawned_id"]

        self.players[player_index - 1].pawns[pawn_index] = source

        if respawned_id is not None:
            del self.opponent.pawns[respawned_id]
            self.removed_pawns[self.opponent_index].append(respawned_id)

        if captured_id is not None:
            self.opponent.pawns[captured_id] = target
            self.removed_pawns[self.opponent_index].remove(captured_id)

        


    def _progress(self, player):
        M, _ = self.size
        return sum(i if player.direction == 1 else M - 1 - i for i, _ in player.pawns.values())

    def scoring(self):
        if self.lose():
            return -1000
        curr_progress = self._progress(self.player)
        opp_progress = self._progress(self.opponent)

        curr_num_pawns = len(self.player.pawns)
        opp_num_pawns = len(self.opponent.pawns)

        curr_moves = len(self.possible_moves())

        return 10 * (curr_progress - opp_progress) + 100 * (curr_num_pawns - opp_num_pawns) + 5 * curr_moves



if __name__ == "__main__":
    from easyAI import AI_Player, Human_Player, Negamax
    from easyAI.AI.ExpectiMiniMax import ExpectiMiniMax
    times = []

    scores = [0,0]
    avg_time = 0.0
    for depth, cond in product([3,7], [True, False]):
        ai= Negamax(depth, cond=cond)

        pruning_label = "z alfa-beta" if cond else "bez alfa-beta"
        print(f'\nNegamax ({pruning_label}), głębokość {ai.depth}')
        for chance in [0.1, 0.0]:
            scores = [0,0]
            starter_wins = 0
            second_wins = 0
            avg_time = 0.0
            variant = "deterministyczna" if chance == 0.0 else "probabilistyczna"
            print(f"wariant: {variant} (chance={chance})")
            for i in range(100):
                g = Octospawn([AI_Player(ai), AI_Player(ai)], chance)

                starter = i % 2 + 1
                g.current_player = starter
                _, time_per_game = g.play()
                avg_time += time_per_game
                scores[g.opponent_index -1] += 1
                if g.opponent_index == starter:
                    starter_wins += 1
                else:
                    second_wins += 1

            print(f"{scores[0]} : {scores[1]}  (zaczynający: {starter_wins}, drugi: {second_wins})  śr. czas: {avg_time/100:.4f}s")
            times.append(f"Negamax ({pruning_label}), głębokość {depth}, {variant}, czas {avg_time/100:.4f}s, P1:{scores[0]} P2:{scores[1]}, zaczyn:{starter_wins} drugi:{second_wins})")

    for depth in [3, 7]:
        ai = ExpectiMiniMax(depth)

        print(f'\nExpectiMiniMax, głębokość {depth}')
        scores = [0,0]
        starter_wins = 0
        second_wins = 0
        avg_time = 0.0
        chance = 0.1
        print(f"wariant: probabilistyczna (chance={chance})")
        for i in range(100):
            g = Octospawn([AI_Player(ai), AI_Player(ai)], chance)

            starter = i % 2 + 1
            g.current_player = starter
            _, time_per_game = g.play()
            avg_time += time_per_game
            scores[g.opponent_index -1] += 1
            if g.opponent_index == starter:
                starter_wins += 1
            else:
                second_wins += 1

        print(f"{scores[0]} : {scores[1]}  (zaczynający: {starter_wins}, drugi: {second_wins})  śr. czas: {avg_time/100:.4f}s")
        times.append(f"ExpectiMiniMax, głębokość {depth}, probabilistyczna, czas {avg_time/100:.4f}s, P1:{scores[0]} P2:{scores[1]}, zaczyn:{starter_wins} drugi:{second_wins})")

    chance = 0.1
    asymmetric_configs = [
        ("Negamax(d=3,ab) vs Negamax(d=7,ab)",
         Negamax(3, cond=True), Negamax(7, cond=True)),
        ("Negamax(d=3,ab) vs ExpectiMiniMax(d=3)",
         Negamax(3, cond=True), ExpectiMiniMax(3)),
        ("Negamax(d=7,ab) vs ExpectiMiniMax(d=7)",
         Negamax(7, cond=True), ExpectiMiniMax(7)),
    ]

    for label, ai1, ai2 in asymmetric_configs:
        print(f"\n{label} (chance={chance})")
        scores = [0, 0]
        starter_wins = 0
        second_wins = 0
        avg_time = 0.0
        for i in range(100):
            g = Octospawn([AI_Player(ai1), AI_Player(ai2)], chance)
            starter = i % 2 + 1
            g.current_player = starter
            _, time_per_game = g.play()
            avg_time += time_per_game
            scores[g.opponent_index - 1] += 1
            if g.opponent_index == starter:
                starter_wins += 1
            else:
                second_wins += 1
        print(f"{scores[0]} :{scores[1]} (zaczynający: {starter_wins}, drugi: {second_wins})  śr. czas: {avg_time/100:.4f}s")
        times.append(f"{label}, chance={chance}, czas {avg_time/100:.4f}s, P1:{scores[0]} P2:{scores[1]}, zaczyn:{starter_wins} drugi:{second_wins})")

    print("\nPODSUMOWANIE=")
    for t in times:
        print(t)
