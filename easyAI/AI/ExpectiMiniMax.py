import time

inf = float("infinity")

class ExpectiMiniMax:
    def __init__(self, depth):
        self.depth = depth

    def __call__(self, game):
        maximizing_player = game.current_player
        best_move = None
        best_value = -inf
        alpha = -inf
        beta = inf

        start_time = time.time()
        for move in game.possible_moves():
            value = self.chance_value_after_move(game, move, self.depth - 1, alpha, beta, maximizing_player)

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)

        end_time = time.time()
        return best_move, end_time - start_time



    def evaluate(self, game, maximizing_player):
        score = game.scoring()
        if game.current_player == maximizing_player:
            return score
        return -score


    def chance_value_after_move(self, game, move, depth, alpha, beta, maximizing_player):

        newGame = game.copy()

        # czy było zbicie?
        capt = newGame.make_move_simple(move)

        if capt:
            # zbite pionki przeciwnika (przed switch_player, opponent_index = ten kogo zbito)
            removed_id = list(newGame.removed_pawns[newGame.opponent_index])

        newGame.switch_player()

        if newGame.is_over():
            return self.evaluate(newGame, maximizing_player)

        # nie było bicia
        if not capt:
            if depth == 0:
                return self.evaluate(newGame, maximizing_player)
            if newGame.current_player == maximizing_player:
                return self.max_value(newGame, depth, alpha, beta, maximizing_player)
            else:
                return self.min_value(newGame, depth, alpha, beta, maximizing_player)

        expected_value = 0.0

        # żaden pionek sie nie odradza
        
        no_reborn_game = newGame.copy()
        if depth == 0:
            no_reborn_val = self.evaluate(no_reborn_game, maximizing_player)
        elif no_reborn_game.current_player == maximizing_player:
            no_reborn_val = self.max_value(no_reborn_game, depth, alpha, beta, maximizing_player)
        else:
            no_reborn_val = self.min_value(no_reborn_game, depth, alpha, beta, maximizing_player)

        expected_value += (1 - game.chance) * no_reborn_val

        # jeden pionek sie odradza (po switch_player current_player = ten którego zbito)

        reborn_prob = game.chance / len(removed_id)

        for pid in removed_id:
            reborn_game = newGame.copy()
            start_pos = reborn_game.start_positions[reborn_game.current_player][pid]

            reborn_game.player.pawns[pid] = start_pos
            reborn_game.removed_pawns[reborn_game.current_player].remove(pid)

            if depth == 0:
                reborn_val = self.evaluate(reborn_game, maximizing_player)
            elif reborn_game.current_player == maximizing_player:
                reborn_val = self.max_value(reborn_game, depth, alpha, beta, maximizing_player)
            else:
                reborn_val = self.min_value(reborn_game, depth, alpha, beta, maximizing_player)

            expected_value += reborn_prob * reborn_val

        return expected_value



    # ruch należy do mnie, ide po drzewku i patrze co moge miec najwiekszego, to co pokazywał na tablicy
    def max_value(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_over():
            return self.evaluate(game, maximizing_player)

        value = -inf

        for move in game.possible_moves():
            leaf_val = self.chance_value_after_move(game, move, depth - 1, alpha, beta, maximizing_player)
            value = max(value, leaf_val)
            alpha = max(alpha, value)

            if alpha >= beta:
                break
        return value

    # ruch należy do mnie, ide po drzewku i patrze co moge miec najmniejszego, to co pokazywał na tablicy
    def min_value(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_over():
            return self.evaluate(game, maximizing_player)

        value = +inf

        for move in game.possible_moves():
            leaf_val = self.chance_value_after_move(game, move, depth - 1, alpha, beta, maximizing_player)
            value = min(value, leaf_val)
            beta = min(beta, value)

            if alpha >= beta:
                break
        return value