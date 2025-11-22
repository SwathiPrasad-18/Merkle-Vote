import hashlib

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

class MerkleTree:
    def __init__(self, leaves_hex):
        self.leaves = leaves_hex[:]
        self.levels = []
        if self.leaves:
            self.build_tree()

    def build_tree(self):
        current = [bytes.fromhex(x) for x in self.leaves]
        self.levels = [current]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i+1] if i+1 < len(current) else left
                parent = hashlib.sha256(left + right).digest()
                next_level.append(parent)
            current = next_level
            self.levels.append(current)

    def get_root(self):
        if not self.levels:
            return None
        return self.levels[-1][0].hex()
