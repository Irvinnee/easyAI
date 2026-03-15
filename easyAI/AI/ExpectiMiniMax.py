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


    def chance_value_after_move(self, game, move, depth, alpha, beta, maximizing_player):
        if game.is_over() or depth == 0:
            return self.evaluate(game, maximizing_player)

        newGame = game.copy()

        # czy było zbicie?
        capt = newGame.make_move_simple(move)

        # ruch bez losowości
        if not capt:
            newGame.current_player = newGame.opponent_index
            if newGame.current_player == maximizing_player:
                return self.max_value(newGame, depth, alpha, beta, maximizing_player)
            else:
                return self.min_value(newGame, depth, alpha, beta, maximizing_player)
        # możliwe odrodzenia
        else:
            removed_id =  newGame.removed_pawns[newGame.opponent_index]
            available_start_pos = list(newGame.players[0].pawns.values()) + list(newGame.players[1].pawns.values())
            possible_reborn = []
            for id in removed_id:
                start_pos = newGame.start_positions[newGame.opponent_index][id]
                if start_pos in available_start_pos:
                    possible_reborn.append(id)

            if not possible_reborn:
                newGame.current_player = newGame.opponent_index
                if game.current_player == maximizing_player:
                    return self.max_value(newGame, depth, alpha, beta, maximizing_player)
                else:
                    return self.min_value(newGame, depth, alpha, beta, maximizing_player)

            expected_value = 0.0


            # żaden pionek sie nie odradza
            no_reborn_game = newGame.copy()

            no_reborn_game.current_player = no_reborn_game.opponent_index
            if no_reborn_game.current_player == maximizing_player:
                no_reborn_val = self.max_value(no_reborn_game, depth, alpha, beta, maximizing_player)
            else:
                no_reborn_val = self.min_value(no_reborn_game, depth, alpha, beta, maximizing_player)

            expected_value += (1 - newGame.chance) * no_reborn_val

            # jeden pionek sie odradza

            removed_poss = newGame.chance / len(possible_reborn)

            for id in possible_reborn:
                removed_game = newGame.copy()
                start_pos = removed_game.start_positions[removed_game.opponent_index][id]

                removed_game.opponent.pawns[id] = start_pos
                removed_game.removed_pawns[removed_game.opponent_index].remove(id)

                removed_game.current_player = removed_game.opponent_index
                if no_reborn_game.current_player == maximizing_player:
                    reborn_val = self.max_value(removed_game, depth, alpha, beta, maximizing_player)
                else:
                    reborn_val = self.min_value(removed_game, depth, alpha, beta, maximizing_player)

                expected_value += removed_poss * reborn_val

        return expected_value



    # ruch należy do mnie, ide po drzewku i patrze co moge miec najwiekszego, to co pokazywał na tablicy
    def max_value(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.is_over():
            return self.evaluate(game, maximizing_player)

        value = -inf

        for move in game.possible_moves():
            leaf_val = self.chance_value_after_move(game, move, self.depth, alpha, beta, maximizing_player)
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
            leaf_val = self.chance_value_after_move(game, move, self.depth, alpha, beta, maximizing_player)
            value = min(value, leaf_val)
            beta = min(beta, value)

            if alpha >= beta:
                break
        return value