from Chess import *
from helper import mask_bishop_attack, mask_rook_attack, bishop_attack_on_the_fly, set_occupancy, rook_attack_on_the_fly, bits_count

class Random:
    random_state = 1804289383

    def rand() -> int:
        """
        Generate 32-bit pseudo-random number
        """
        num =  Random.random_state
    
        num ^= (num << 13 & 0xffffffff)
        num ^= (num >> 17 & 0xffffffff)  
        num ^= (num << 5 & 0xffffffff)

        Random.random_state = num

        return num
    
    def random_seed(num :int) -> None:
        Random.random_state = num & 0xffffffff

    def rand_u64() -> int:
        num1 = Random.rand() & 0xffff
        num2 = Random.rand() & 0xffff
        num3 = Random.rand() & 0xffff
        num4 = Random.rand() & 0xffff
        return num1 | (num2 << 16) | (num3 << 32) | (num4 << 48)
    
def generate_magic_number() -> int:
    """
    Generate magic number candidates
    """
    return Random.rand_u64() & Random.rand_u64() & Random.rand_u64()

def find_magic_number(square: int, relevant_bits: int, is_bishop: bool):
    occupancies = dict()
    attacks = dict()

    attack_mask = mask_bishop_attack(square) if is_bishop else mask_rook_attack(square)
    occupancies_index = 1 << relevant_bits
    
    for idx in range(occupancies_index):
        occupancies[idx] = set_occupancy(idx, relevant_bits, attack_mask)
        attacks[idx] = bishop_attack_on_the_fly(square, occupancies[idx]) if is_bishop else rook_attack_on_the_fly(square, occupancies[idx])

    for _ in range(100000000):
        candidate = generate_magic_number()
        if bits_count((candidate * attack_mask) & 0xff00000000000000) < 6:
            continue

        used_attack = dict()
        idx, fail = 0, False

        while idx < occupancies_index and not fail:
            magic_idx = ((candidate * occupancies[idx]) >> (64 - relevant_bits)) & 0xffffffff

            if magic_idx not in used_attack:
                used_attack[magic_idx] = attacks[idx]
            
            elif used_attack[magic_idx] != attacks[idx]:
                fail = True

            idx += 1

        if not fail:
            return candidate
        
    print("Failed")
    return 0

def init_magic_number() -> None:
    print("-----------------BISHOP-----------------")
    with open("bishop_magic.txt", "wt") as f:
        for square in range(63, -1, -1):
            magic_number = find_magic_number(square, bishop_relevant_bits[square], True)
            print(magic_number)
            f.write(str(square) + ": " + str(magic_number) + ", ")
    print("------------------ROOK------------------")
    with open("rook_magic.txt", "wt") as f:
        for square in range(63, -1, -1):
            magic_number = find_magic_number(square, rook_relevant_bits[square], False)
            print(magic_number)
            f.write(str(square) + ": " + str(magic_number) + ", ")

init_magic_number()