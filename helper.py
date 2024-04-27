from Constants import *
from os import system, name

def set_bit(bitboard: int, square: int) -> int:
    return bitboard | (1 << square)

def get_bit(bitboard: int, square: int) -> int:
    return (bitboard >> square) & 1

def bits_count(bitboard: int) -> int:
    count = 0
    while bitboard:
        count += 1
        bitboard &= (bitboard - 1)
    return count

def get_rm_bit1_idx(bitboard: int):
    if bitboard:
        return bits_count((bitboard & -bitboard) - 1)
    else:
        return -1
                
def mask_pawn_attack(square: int, is_white: bool) -> int:
    """
    function to calculate pawn attack\n
    parameter:
    + square: int
    + is_white: bool
    """
    attack_mask = 0
    bitboard = set_bit(0, square)
    if is_white:
        if (attack := bitboard << 9) & NOT_H_FILE:
            attack_mask |= attack
        if (attack := bitboard << 7) & NOT_A_FILE:
            attack_mask |= attack
    else:
        if (attack := bitboard >> 9) & NOT_A_FILE:
            attack_mask |= attack
        if (attack := bitboard >> 7) & NOT_H_FILE:
            attack_mask |= attack

    return attack_mask

def mask_knight_attack(square: int) -> int:
    """
    function to calculate knight attack
    """
    attack_mask = 0
    bitboard = set_bit(0, square)
    if (attack := bitboard << 17) & NOT_H_FILE:
        attack_mask |= attack
    if (attack := bitboard << 15) & NOT_A_FILE:
        attack_mask |= attack
    if (attack := bitboard << 10) & NOT_GH_FILE:
        attack_mask |= attack
    if (attack := bitboard << 6) & NOT_AB_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 17) & NOT_A_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 15) & NOT_H_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 10) & NOT_AB_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 6) & NOT_GH_FILE:
        attack_mask |= attack
    
    return attack_mask

def mask_king_attack(square: int) -> int:
    """
    function to calculate king attack
    """
    bitboard = set_bit(0, square)
    attack_mask = bitboard >> 8
    attack_mask |= ((bitboard << 8) & 0xffffffffffffffff)
    if (attack := bitboard << 1) & NOT_H_FILE:
        attack_mask |= attack
    if (attack := bitboard << 9) & NOT_H_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 7) & NOT_H_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 1) & NOT_A_FILE:
        attack_mask |= attack
    if (attack := bitboard >> 9) & NOT_A_FILE:
        attack_mask |= (bitboard >> 9)
    if (attack := bitboard << 7) & NOT_A_FILE:
        attack_mask |= attack
    return attack_mask

def mask_bishop_attack(square: int) -> int:
    """
    masking relevant bishop occupancy bits
    """
    i_fixed = square // 8
    j_fixed = square % 8
    
    attack_mask = 0
    for i, j in zip(range(i_fixed - 1, 0, -1), range(j_fixed - 1, 0, -1)):
        attack_mask = set_bit(attack_mask, i * 8 + j)
    for i, j in zip(range(i_fixed - 1, 0, -1), range(j_fixed + 1, 7, +1)):
        attack_mask = set_bit(attack_mask, i * 8 + j)
    for i, j in zip(range(i_fixed + 1, 7, +1), range(j_fixed - 1, 0, -1)):
        attack_mask = set_bit(attack_mask, i * 8 + j)
    for i, j in zip(range(i_fixed + 1, 7, +1), range(j_fixed + 1, 7, +1)):
        attack_mask = set_bit(attack_mask, i * 8 + j)

    return attack_mask

def bishop_attack_on_the_fly(square: int, occupancy: int) -> int:
    i_fixed = square // 8
    j_fixed = square % 8
    
    attack_mask = 0
    for i, j in zip(range(i_fixed - 1, -1, -1), range(j_fixed - 1, -1, -1)):
        square = set_bit(0, i * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break
    for i, j in zip(range(i_fixed - 1, -1, -1), range(j_fixed + 1, +8, +1)):
        square = set_bit(0, i * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break
    for i, j in zip(range(i_fixed + 1, +8, +1), range(j_fixed - 1, -1, -1)):
        square = set_bit(0, i * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break
    for i, j in zip(range(i_fixed + 1, +8, +1), range(j_fixed + 1, +8, +1)):
        square = set_bit(0, i * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break

    return attack_mask

def mask_rook_attack(square: int) -> int:
    """
    masking relevant rook occupancy bits
    """
    i_fixed = square // 8
    j_fixed = square % 8
    
    attack_mask = 0
    for i in range(i_fixed - 1, 0, -1):
        attack_mask = set_bit(attack_mask, i * 8 + j_fixed)
    for i in range(i_fixed + 1, 7, +1):
        attack_mask = set_bit(attack_mask, i * 8 + j_fixed)
    for j in range(j_fixed - 1, 0, -1):
        attack_mask = set_bit(attack_mask, i_fixed * 8 + j)
    for j in range(j_fixed + 1, 7, +1):
        attack_mask = set_bit(attack_mask, i_fixed * 8 + j)

    return attack_mask

def rook_attack_on_the_fly(square: int, occupancy: int) -> int:
    i_fixed = square // 8
    j_fixed = square % 8
    
    attack_mask = 0
    for i in range(i_fixed - 1, -1, -1):
        square = set_bit(0, i * 8 + j_fixed)
        attack_mask |= square
        if square & occupancy:
            break
    for i in range(i_fixed + 1, +8, +1):
        square = set_bit(0, i * 8 + j_fixed)
        attack_mask |= square
        if square & occupancy:
            break
    for j in range(j_fixed - 1, -1, -1):
        square = set_bit(0, i_fixed * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break
    for j in range(j_fixed + 1, +8, +1):
        square = set_bit(0, i_fixed * 8 + j)
        attack_mask |= square
        if square & occupancy:
            break

    return attack_mask

def set_occupancy(idx: int, bit_count: int, attack_mask: int) -> int:
    occupancy = 0

    for count in range(bit_count):
        square = get_rm_bit1_idx(attack_mask)
        attack_mask ^= (1 << square)
        # occupancy is on board
        if (idx & (1 << count)):
            # populate occupancy map
            occupancy |= (1 << square)

    return occupancy

def init_leapers_attack() -> None:
    for square in range(64):
        king_attacks[square] = mask_king_attack(square)
        knight_attacks[square] = mask_knight_attack(square)
        pawn_attacks[square, 0] = mask_pawn_attack(square, True)
        pawn_attacks[square, 1] = mask_pawn_attack(square, False)

def init_sliders_attack() -> None:
    for square in range(64):
        bishop_masks[square] = mask_bishop_attack(square)
        rook_masks[square] = mask_rook_attack(square)

    for square in range(64):
        attack_mask = bishop_masks[square]
        relevant_bits = bits_count(attack_mask)
        occupancies_idx = 1 << relevant_bits

        for idx in range(occupancies_idx):
            occupancy = set_occupancy(idx, relevant_bits, attack_mask)
            magic_idx = (occupancy * bishop_magic_number[square]) >> (64 - relevant_bits)
            bishop_attacks[square, magic_idx] = bishop_attack_on_the_fly(square, occupancy)

    for square in range(64):
        attack_mask = rook_masks[square]
        relevant_bits = bits_count(attack_mask)
        occupancies_idx = 1 << relevant_bits
        for idx in range(occupancies_idx):
            occupancy = set_occupancy(idx, relevant_bits, attack_mask)
            magic_idx = (occupancy * rook_magic_number[square]) >> (64 - relevant_bits)
            rook_attacks[square, magic_idx] = rook_attack_on_the_fly(square, occupancy)

def init_all():
    print("Initializing...")
    init_leapers_attack()
    init_sliders_attack()
# move encoder
def encoder(src: int, des: int, piece: int, promotion: int, capture: int, dpush: int, ep: int, castle: int) -> int:
    return src | (des << 6) | (piece << 12) | (promotion << 16) | (capture << 20) | (dpush << 21) | (ep << 22) | (castle << 23)
# move decoder
def decoder(move: int) -> tuple[int, int, int, int, int, int, int, int]:
    src = move & 0x3f
    des = (move & 0xfc0) >> 6
    piece = (move & 0xf000) >> 12
    promotion = (move & 0xf0000) >> 16
    capture = (move & 0x100000) >> 20
    dpush = (move & 0x200000) >> 21
    ep = (move & 0x400000) >> 22
    castle = (move & 0x800000) >> 23
    return src, des, piece, promotion, capture, dpush, ep, castle

def get_bishop_attack(square: int, occupancy: int):
    occupancy &= bishop_masks[square]
    occupancy *= bishop_magic_number[square]
    occupancy >>= (64 - bishop_relevant_bits[square])
    return bishop_attacks[square, occupancy]

def get_rook_attack(square: int, occupancy: int):
    occupancy &= rook_masks[square]
    occupancy *= rook_magic_number[square]
    occupancy >>= (64 - rook_relevant_bits[square])
    return rook_attacks[square, occupancy]

def get_queen_attack(square: int, occupancy: int):
    return get_bishop_attack(square, occupancy) | get_rook_attack(square, occupancy)

def clear_screen():
    if name == "nt": # window
        system("cls")
    else:
        system("clear")
