import hashlib

import numpy as np
from datasketch.lsh import _optimal_param

DEFAULT_MER = 2**61 - 1
DEFAULT_SEED = 1


def gen_lsh_param(num_perm, lsh_threshold):
    return _optimal_param(lsh_threshold, num_perm, 0.5, 0.5)


class CalcMinhash:
    def __init__(self, num_perm, seed=DEFAULT_SEED, mer=DEFAULT_MER):
        self.mer = mer
        self.num_perm = num_perm

        self.gen = np.random.RandomState(seed)
        self.a = self.gen.randint(1, self.mer, (self.num_perm,), dtype="u8")
        self.b = self.gen.randint(0, self.mer, (self.num_perm,), dtype="u8")

    def _sha1_hash(self, val):
        val = int.from_bytes(hashlib.sha1(val).digest()[:8], "little")
        val &= self.mer
        return np.uint64(val)

    def hash(self, sequence: list[str]) -> np.ndarray:
        res = np.ones(self.num_perm, dtype="u8") * self.mer
        for token in sequence:
            hash0 = self._sha1_hash(token.encode("utf8"))
            hash_vec = hash0 * self.a + self.b
            hash_vec %= self.mer
            res = np.minimum(res, hash_vec)
        return res


class CalcLsh:
    def __init__(self, b, r):
        self.b = b
        self.r = r
        self.hashranges = [(i * r, (i + 1) * r) for i in range(b)]

    def gen_lsh(self, minhash) -> list[bytearray]:
        return [bytearray(minhash[start:end]) for start, end in self.hashranges]


class CalcMinhashLsh:
    def __init__(self, b, r, seed=DEFAULT_SEED, mer=DEFAULT_MER):
        num_perm = b * r
        self.minhash = CalcMinhash(num_perm, seed, mer)
        self.lsh = CalcLsh(b, r)

    def hash(self, tokens) -> list[bytearray]:
        minhash = self.minhash.hash(tokens)
        lsh = self.lsh.gen_lsh(minhash)
        return lsh


class LocalMinhashLshDedup:
    def __init__(self, b, r, seed=DEFAULT_SEED, mer=DEFAULT_MER):
        self.calc_minhash_lsh = CalcMinhashLsh(b, r, seed, mer)
        self.data = []
        self.b = b

    def add(self, id, tokens):
        hval = self.calc_minhash_lsh.hash(tokens)
        self.data.append((id, hval))

    def dedup(self):
        self.data.sort(key=lambda x: x[0])
        dedup_set = [set() for _ in range(self.b)]
        exclude = []
        for line_id, hash_list in self.data:
            flag_dup = False
            for i, hval in hash_list:
                if hval in dedup_set[i]:
                    flag_dup = True
                else:
                    dedup_set[i].add(hval)

            if flag_dup:
                exclude.append(line_id)

        return exclude
