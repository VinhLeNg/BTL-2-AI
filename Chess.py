from Constants import *
from helper import get_bit, get_rm_bit1_idx, encoder, decoder, get_bishop_attack, get_rook_attack, get_queen_attack, clear_screen, bits_count
from colorama import Style
from enum import Enum
from re import match
from random import choice, random

def print_bitboard(bitboard: int) -> None:
    square = 63
    for i in range(8, 0, -1):
        print(i, end= " ")
        for _ in range(8):
            print(get_bit(bitboard, square), end= " ")
            square -= 1
        print()
    print(f"  a b c d e f g h\nBitboard: {bitboard}")

class Chess:
    def __init__(self) -> None:
        pass

    def _is_attacked(self, square: int) -> bool:
        """
        check whether square is attacked
        """
        opponent = 1 if self._side_to_move == 0 else 0
        for piece in pieces[opponent]:
            bitboard = self._bitboards[piece]
            while bitboard:
                src_square = get_rm_bit1_idx(bitboard)

                if piece.upper() == "P" and get_bit(pawn_attacks[src_square, opponent], square):
                    return True
                elif piece.upper() == "N" and get_bit(knight_attacks[src_square], square):
                    return True
                elif piece.upper() == "K" and get_bit(king_attacks[src_square], square):
                    return True
                elif piece.upper() == "B" and get_bit(get_bishop_attack(src_square, self._occupancy[2]), square):
                    return True
                elif piece.upper() == "R" and get_bit(get_rook_attack(src_square, self._occupancy[2]), square):
                    return True
                elif piece.upper() == "Q" and get_bit(get_queen_attack(src_square, self._occupancy[2]), square):
                    return True

                bitboard ^= (1 << src_square)
        return False
    
    def reset_board(self) -> None:
        # castling right
        self._castle = { (0, "K"): True, (0, "Q"): True, (1, "K"): True, (1, "Q"): True }
        # which side to move
        self._side_to_move = 0
        # en passant
        self._en_passant = None
        # bitboards
        self._bitboards = {
            "K": 0, "Q": 0, "R": 0, "B": 0, "N": 0, "P": 0,
            "k": 0, "q": 0, "r": 0, "b": 0, "n": 0, "p": 0
        }
        # occupancy
        self._occupancy = {
            0: 0xffff, # white occupancy indices
            1: 0xffff000000000000, # black occupancy indices
            2: 0xffff00000000ffff # both side
        }
        # king
        self._set_bit("K", 3)
        self._set_bit("k", 59)
        # queen
        self._set_bit("Q", 4)
        self._set_bit("q", 60)
        # rook
        self._set_bit("R", 7)
        self._set_bit("R", 0)
        self._set_bit("r", 63)
        self._set_bit("r", 56)
        # bishop
        self._set_bit("B", 5)
        self._set_bit("B", 2)
        self._set_bit("b", 61)
        self._set_bit("b", 58)
        # knight
        self._set_bit("N", 6)
        self._set_bit("N", 1)
        self._set_bit("n", 62)
        self._set_bit("n", 57)
        # white pawn
        for square in range(8, 16):
            self._set_bit("P", square)
        # black pawn
        for square in range(48, 56):
            self._set_bit("p", square)
        # fifty moves rule
        self._fifty = 0

    def _set_bit(self, piece: str, square: int) -> None:
        self._bitboards[piece] |= (1 << square)

    def _pop_bit(self, piece: str, square: int) -> None:
        self._bitboards[piece] ^= (1 << square)
    
    def get_at_square(self, square: int) -> str | None:
        for k, v in self._bitboards.items():
            if (v >> square) & 1:
                return k
        return None

    def print(self):
        for i in range(7, -1, -1):
            print(Style.RESET_ALL, end="")
            background = False if i & 1 else True
            print(i + 1, end=" ")
            for j in range(7, -1, -1):
                if (k := self.get_at_square(i * 8 + j)) != None:
                    print(color[background] + unicode_chars[k], end=" ")
                else:
                    print(color[background] + "  ", end="")
                
                background = not background

            print(Style.RESET_ALL)
        print(f"  a b c d e f g h")
        print("---White" if self._side_to_move == 0 else "---Black", "to move---")
        # print("En passant:", self._en_passant)
        # print(f'Castling right:\nWhite: {self._castle[0, "K"]}, {self._castle[0, "Q"]}\nBlack: {self._castle[1, "K"]}, {self._castle[1, "Q"]}')

    def generate_move(self):
        """
        generating pseudo legal moves
        """
        side = self._side_to_move
        opponent = 1 if side == 0 else 0
        lst = [] # move list
        
        for piece in pieces[side]:
            bitboard = self._bitboards[piece]
            piece = encode_piece[piece]
            r = piece % 6
            while bitboard:
                src_square = get_rm_bit1_idx(bitboard)
                # if is pawn
                if r == 5:
                    # 1. quiet pawn move
                    des_square = src_square + 8 if side == 0 else src_square - 8
                    seventh_rank_a, seventh_rank_h = (Sqr["a7"], Sqr["h7"]) if side == 0 else (Sqr["a2"], Sqr["h2"])
                    second_rank_a, second_rank_h = (Sqr["a2"], Sqr["h2"]) if side == 0 else (Sqr["a7"], Sqr["h7"])

                    if get_bit(self._occupancy[2], des_square) == 0:
                        # 1.1. promotion
                        if src_square >= seventh_rank_h and src_square <= seventh_rank_a:
                            promotion = [1, 2, 3, 4] if side == 0 else [7, 8, 9, 10]
                            for promoted_piece in promotion:
                                lst.append(encoder(src_square, des_square, piece, promoted_piece, 0, 0, 0, 0))
                        # 1.2. pawn push
                        else:
                            lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        # 1.3. double pawn push
                        if src_square >= second_rank_h and src_square <= second_rank_a:
                            des_square = src_square + 16 if side == 0 else src_square - 16
                            if get_bit(self._occupancy[2], des_square) == 0:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 1, 0, 0))
                    # 2. pawn capture
                    attacks = pawn_attacks[src_square, side] & self._occupancy[opponent]
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        # 2.1. Promotion
                        if src_square >= seventh_rank_h and src_square <= seventh_rank_a:
                            promotion = [1, 2, 3, 4] if side == 0 else [7, 8, 9, 10]
                            for promoted_piece in promotion:
                                lst.append(encoder(src_square, des_square, piece, promoted_piece, 1, 0, 0, 0))
                        # 2.2. Normal capture
                        else:
                            lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                        attacks ^= (1 << des_square)
                    # 3. en passant
                    if self._en_passant != None:
                        if get_bit(pawn_attacks[src_square, side], self._en_passant):
                            lst.append(encoder(src_square, self._en_passant, piece, 0, 1, 0, 1, 0))
                # if is knight
                elif r == 4:
                    attacks = knight_attacks[src_square]
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        if get_bit(self._occupancy[side], des_square) == 0:
                            # capture move
                            if get_bit(self._occupancy[opponent], des_square):
                                lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                            # normal move
                            else:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        attacks ^= (1 << des_square)
                # if is king
                elif r == 0:
                    # king move
                    attacks = king_attacks[src_square]
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        if get_bit(self._occupancy[side], des_square) == 0 and not self._is_attacked(des_square):
                            if get_bit(self._occupancy[opponent], des_square):
                                lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                            else:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        attacks ^= (1 << des_square)
                    # castle
                    if not self._is_attacked(src_square):
                        f, g, c, d, b = (Sqr["f1"], Sqr["g1"], Sqr["c1"], Sqr["d1"], Sqr["b1"]) if side == 0 else (Sqr["f8"], Sqr["g8"], Sqr["c8"], Sqr["d8"], Sqr["b8"])
                        if self._castle[side, "K"] and not self._is_attacked(f) and not self._is_attacked(g) and get_bit(self._occupancy[2], f) == 0 and get_bit(self._occupancy[2], g) == 0:
                            lst.append(encoder(src_square, g, piece, 0, 0, 0, 0, 1))
                        if self._castle[side, "Q"] and not self._is_attacked(d) and not self._is_attacked(c) and get_bit(self._occupancy[2], c) == 0 and get_bit(self._occupancy[2], d) == 0 and get_bit(self._occupancy[2], b) == 0:
                            lst.append(encoder(src_square, c, piece, 0, 0, 0, 0, 1))
                # if is bishop
                elif r == 3:
                    attacks = get_bishop_attack(src_square, self._occupancy[2])
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        if get_bit(self._occupancy[side], des_square) == 0:
                            if get_bit(self._occupancy[opponent], des_square):
                                lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                            else:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        attacks ^= (1 << des_square)
                # if is rook
                elif r == 2:
                    attacks = get_rook_attack(src_square, self._occupancy[2])
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        if get_bit(self._occupancy[side], des_square) == 0:
                            if get_bit(self._occupancy[opponent], des_square):
                                lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                            else:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        attacks ^= (1 << des_square)
                # if is queen
                else:
                    attacks = get_queen_attack(src_square, self._occupancy[2])
                    while attacks:
                        des_square = get_rm_bit1_idx(attacks)
                        if get_bit(self._occupancy[side], des_square) == 0:
                            if get_bit(self._occupancy[opponent], des_square):
                                lst.append(encoder(src_square, des_square, piece, 0, 1, 0, 0, 0))
                            else:
                                lst.append(encoder(src_square, des_square, piece, 0, 0, 0, 0, 0))
                        attacks ^= (1 << des_square)
                bitboard ^= (1 << src_square)

        return lst
    
    def copy_state(self):
        """
        Save a copy of current state
        """
        castle = self._castle.copy()
        side = self._side_to_move
        en_passant = self._en_passant
        bitboards = self._bitboards.copy()
        occupancy = self._occupancy.copy()
        fifty_move = self._fifty
        return bitboards, occupancy, side, en_passant, castle, fifty_move

    def undo_move(self, old_state: tuple) -> None:
        self._bitboards, self._occupancy, self._side_to_move, self._en_passant, self._castle, self._fifty = old_state
        
    def make_move(self, move: int):
        src, des, piece, promotion, capture, dpush, ep, castle = decoder(move)

        old_state = self.copy_state()

        self._pop_bit(decode_piece[piece], src)
        self._set_bit(decode_piece[piece], des)

        self._occupancy[self._side_to_move] |= (1 << des)
        self._occupancy[self._side_to_move] ^= (1 << src)

        opponent = 1 if self._side_to_move == 0 else 0

        if capture:
            for opponent_piece in pieces[opponent]:
                if get_bit(self._bitboards[opponent_piece], des):
                    self._pop_bit(opponent_piece, des)
                    self._occupancy[opponent] ^= (1 << des)

                    if opponent_piece == "r":
                        if des == 56:
                            self._castle[1, "K"] = False
                        elif des == 63:
                            self._castle[1, "Q"] = False

                    elif opponent_piece == "R":
                        if des == 56:
                            self._castle[0, "K"] = False
                        elif des == 7:
                            self._castle[0, "Q"] = False
                        
                    break
            self._fifty = 0

        elif piece == 5 or piece == 11: # pawn move
            self._fifty = 0
        else:
            self._fifty += 1

        if promotion:
            self._pop_bit(decode_piece[piece], des)
            self._set_bit(decode_piece[promotion], des)
        
        if ep:
            self._pop_bit("p", des - 8) if self._side_to_move == 0 else self._pop_bit("P", des + 8)
            self._occupancy[opponent] ^= (1 << des)
            
        self._en_passant = None

        if dpush:
            self._en_passant = des - 8 if self._side_to_move == 0 else des + 8
        
        elif castle:
            if des % 8 == 1: # g column
                rook_des = des + 1
                rook_src = src - 3
            else: # c column
                rook_des = des - 1
                rook_src = src + 4

            rook = "R" if self._side_to_move == 0 else "r"
            self._castle[self._side_to_move, "K"] = self._castle[self._side_to_move, "Q"] = False

            self._pop_bit(rook, rook_src)
            self._set_bit(rook, rook_des)

            self._occupancy[self._side_to_move] |= (1 << rook_des)
            self._occupancy[self._side_to_move] ^= (1 << rook_src)
        
        # castling rights
        if piece == 0:
            self._castle[0, "K"] = self._castle[0, "Q"] = False
        elif piece == 6:
            self._castle[1, "K"] = self._castle[1, "Q"] = False
        elif piece == 2:
            side = "K" if src == 0 else "Q"
            self._castle[0, side] = False
        elif piece == 8:
            side = "K" if src == 56 else "Q"
            self._castle[1, side] = False
        # update occupancy
        self._occupancy[2] = self._occupancy[0] | self._occupancy[1]
        # check whether king is under attack
        king = "K" if self._side_to_move == 0 else "k"
        king_square = get_rm_bit1_idx(self._bitboards[king])
        if self._is_attacked(king_square):
            self.undo_move(old_state)
            return None
        # switch side
        self._side_to_move ^= 1
        # return
        return old_state
    
    def play(self, plr1, plr2):
        while True:
            if (ret := plr1()) != None:
                return -1 if ret == 1 else 0
            if plr2() != None:
                return 1 if ret == 1 else 0
    
    def get_legal_move(self) -> list[int]:
        """from the list of pseudo legal moves, get legal moves"""
        move_lst = []
        for move in self.generate_move():
            if (old_state := self.make_move(move)) != None:
                move_lst.append(move)
                self.undo_move(old_state)
        return move_lst
    
    def is_goal_state(self):
        """Use this function if there is no legal move"""
        king = "K" if self._side_to_move == 0 else "k"
        king_square = get_rm_bit1_idx(self._bitboards[king])
        if self._is_attacked(king_square):
            return 1 # checkmate
        else:
            return 0 # draw by stalemate
    
    # human's turn
    def human_turn(self) -> int | None:
        # clear_screen()
        self.print()

        if self._fifty == 100:
            print("Drawn by fifty moves rule")
            return 0

        lst = self.get_legal_move()

        if len(lst) == 0:
            ret = self.is_goal_state()
            if ret == 0:
                print("Drawn by stalemate")
            else:
                print("Black" if self._side_to_move == 0 else "White", "won by checkmate")
            return ret

        while True:
            inp = input("Input move: ")

            if inp.upper() == "RESIGN":
                print("Black" if self._side_to_move == 0 else "White", "won by resignation")
                return self._side_to_move ^ 1
        
            side = self._side_to_move
            if match(promotion_pattern, inp):
                piece = 5 if side == 0 else 11
                src, des, promoted = inp.split()
                # promoted = encode_piece[promoted] if side == 0 else encode_piece[promoted.lower()]
                src, des = Sqr[src], Sqr[des]
            elif inp == "O-O":
                piece = 0 if side == 0 else 6
                src, des = [3, 1] if side == 0 else [59, 57]
            elif inp == "O-O-O":
                piece = 0 if side == 0 else 6
                src, des = [3, 5] if side == 0 else [59, 61]
            elif match(other_pattern, inp):
                inp = inp.split()
                if len(inp) == 2:
                    piece, src, des = "P", inp[-2], inp[-1]
                else:
                    piece, src, des = inp
                piece = piece.lower() if side == 1 else piece
                piece = encode_piece[piece]
                src, des = Sqr[src], Sqr[des]
            else:
                print("Invalid input")
                continue

            for move in lst:
                decoded_move = decoder(move)
                if src == decoded_move[0] and des == decoded_move[1] and piece == decoded_move[2]:
                    self.make_move(move)
                    return None
            
            clear_screen()
            print("Illegal move")
            self.print()

    # for engine
    def play_random_move(self):
        # clear_screen()
        self.print()

        if self._fifty == 100:
            print("Drawn by fifty moves rule")
            return 0

        lst = self.get_legal_move()

        if len(lst) == 0:
            ret = self.is_goal_state()
            if ret == 0:
                print("Drawn by stalemate")
            else:
                print("Black" if self._side_to_move == 0 else "White", "won by checkmate")
            return ret

        self.make_move(choice(self.get_legal_move()))
        return None
    
    # eval 1
    def simple_eval(self) -> int:
        score = 0
        for piece in pieces[0]:
            score += bits_count(self._bitboards[piece]) * piece_value[piece]
        for piece in pieces[1]:
            score -= bits_count(self._bitboards[piece]) * piece_value[piece.upper()]
        return score
    
    def eval_v2(self) -> float:
        score = {0: 0, 1: 0}
        for side in [0, 1]:
            for piece in pieces[side]:
                bitboard = self._bitboards[piece]
                piece = piece.upper()
                val = piece_value[piece]
                while bitboard:
                    score[side] += val
                    square = get_rm_bit1_idx(bitboard)
                    if piece == "K":
                        atk_mask = 0.0
                    elif piece == "N":
                        atk_mask = knight_attacks[square]
                    elif piece == "P":
                        atk_mask = pawn_attacks[square, side]
                    elif piece == "R":
                        atk_mask = get_rook_attack(square, self._occupancy[2])
                    elif piece == "B":
                        atk_mask = get_bishop_attack(square, self._occupancy[2])
                    else:
                        atk_mask = get_queen_attack(square, self._occupancy[2])
                    bitboard ^= (1 << square)
                    score[side] += bits_count(atk_mask) / 1000.0
        return score[0] - score[1]
    
    def alphabeta(self, depth, alpha, beta, eval_func):
        if depth == 0:
            return eval_func(), None
        elif self._fifty == 100:
            return 0, None

        if self._side_to_move == 1: # minimize
            val, best_move = 10001, None
            for move in self.generate_move():
                if(old_state := self.make_move(move)):
                    child_val, _ = self.alphabeta(depth - 1, alpha, beta, eval_func)
                    self.undo_move(old_state)

                    if val > child_val:
                        val = child_val
                        best_move = move
                    elif abs(val - child_val) < 0.2 and random() > .5:
                        best_move = move

                    if val < alpha:
                        break # alpha cutoff
                                            
                    beta = min(beta, val)
        
        else:
            val, best_move = -10001, None
            for move in self.generate_move():
                if(old_state := self.make_move(move)):
                    child_val, _ = self.alphabeta(depth - 1, alpha, beta, eval_func)
                    self.undo_move(old_state)

                    if val < child_val:
                        val = child_val
                        best_move = move
                    elif abs(val - child_val) < 0.2 and random() > .5:
                        best_move = move

                    if val > beta:
                        break # beta cutoff

                    alpha = max(alpha, val)

        if best_move == None:
            if self.is_goal_state() == 1:
                val = 10000 if self._side_to_move == 1 else -10000
            else:
                val = 0
            
        return val, best_move
    
    def bot_turn_v1(self, depth: int) -> int:
        # clear_screen()
        self.print()

        if self._fifty == 100:
            print("Draw by fifty moves rule")
            return 0

        print("Bot is thinking...")
        eval, best_move = self.alphabeta(depth * 2, -10001, 10001, lambda: self.simple_eval())
        print(f"Eval score: {eval}")
        
        if best_move == None:
            if eval == 0:
                print("Draw by stalemate")
                return 0
            if eval > 0:
                print("White won by checkmate")
            else:
                print("Black won by checkmate")
            return 1

        self.make_move(best_move)
        return None
    
    def bot_turn_v2(self, depth: int) -> int:
        # clear_screen()
        self.print()

        if self._fifty == 100:
            print("Draw by fifty moves rule")
            return 0

        print("Bot is thinking...")
        eval, best_move = self.alphabeta(depth * 2, -10001, 10001, lambda: self.eval_v2())
        print(f"Eval score: {eval}")
        
        if best_move == None:
            if eval == 0:
                print("Draw by stalemate")
                return 0
            if eval > 0:
                print("White won by checkmate")
            else:
                print("Black won by checkmate")
            return 1

        self.make_move(best_move)
        return None
    
    def main(self):
        self.reset_board()
        clear_screen()
        inp = int(input("CHESS\n1/PvP\n2/PvE\n3/Bot vs Random move\nChoose mode: "))
        clear_screen()
        if inp == 1:
            self.play(plr1 = lambda: self.human_turn(), plr2 = lambda: self.human_turn())
        elif inp == 2:
            clear_screen()
            inp = int(input("You chose PvE mode!\nLv 0\nLvl 1\nLvl 2\nLvl 3\nLvl 4\nLvl 5\nDifficulty? "))
            if inp == 0:
                plr2 = lambda: self.play_random_move()
            elif inp == 1:
                plr2 = lambda: self.bot_turn_v1(2)
            elif inp == 2:
                print("Warning: Bot takes a very long time to think")
                plr2 = lambda: self.bot_turn_v1(3)
            elif inp == 3:
                print("Warning: Bot takes a very long time to think")
                plr2 = lambda: self.bot_turn_v1(5)
            elif inp == 4:
                print("Warning: Bot takes a very long time to think")
                plr2 = lambda: self.bot_turn_v2(5)
            elif inp == 5:
                print("Ehehehehhe I am stockfish")
                print("Warning: Bot takes a very long time to think")
                plr2 = lambda: self.bot_turn_v2(17)
            else:
                print("Invalid input")
                exit()

            inp = int(input("1/White\n2/Black\nYou play as: "))
            if inp == 1:
                self.play(plr1 = lambda: self.human_turn(), plr2 = plr2)
            elif inp == 2:
                self.play(plr1 = lambda: plr2, plr2 = lambda: self.human_turn())
        elif inp == 3:
            inp = int(input("Easy mode bot vs random move\n1/White\n2/Black\nBot play as: "))
            if inp == 1:
                self.play(plr1 = lambda: self.bot_turn_v1(2), plr2 = lambda: self.play_random_move())
            elif inp == 2:
                self.play(plr1 = lambda: self.play_random_move(), plr2 = lambda: self.bot_turn_v1(2))
            else:
                print("Invalid input")
        else:
            print("Invalid input")