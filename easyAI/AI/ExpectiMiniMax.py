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

        for move in game.possible_moves():
            value = self.chance_value_after_move(game, move, self.depth - 1, alpha, beta, maximizing_player)

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)

        return best_move



    def evaluate(self, game, maximizing_player):
        pass

    def stochastic_successors(self, game, move):
        pass

    def chance_value_after_move(self, game, move, depth, alpha, beta, maximizing_player):
        if game.is_over() or depth == 0:
            return self.evaluate(game, maximizing_player)

        newGame = game.copy()

        # czy było zbicie?
        capt = newGame.make_move_simple(move)

        # ruch bez losowości
        if not capt:
            game.current_player = game.opponent_index
            if game.current_player == maximizing_player:
                return self.max_value(game, depth, alpha, beta, maximizing_player)
            else:
                return self.min_value(game, depth, alpha, beta, maximizing_player)
        # możliwe odrodzenia
        else:
            poss_reborn = len(game.removed_paws)
            """
            """







    # ruch należy do mnie, ide po drzewku i patrze co moge miec najwiekszego, to co pokazywał na tablicy
    def max_value(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_over():
            return self.evaluate(game, maximizing_player)

        value = -inf

        for move in game.possible_moves():
            leaf_val = self.chance_value_after_move(game, move, self.depth - 1, alpha, beta, maximizing_player)
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
            leaf_val = self.chance_value_after_move(game, move, self.depth - 1, alpha, beta, maximizing_player)
            value = min(value, leaf_val)
            beta = min(beta, value)

            if alpha >= beta:
                break
        return value