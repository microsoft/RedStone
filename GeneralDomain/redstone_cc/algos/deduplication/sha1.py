import hashlib

from .utils import ccnet_normalize

DEFAULT_HASH_SIZE = 8


def sha1_hash(line, hash_size=DEFAULT_HASH_SIZE) -> bytes:
    line = ccnet_normalize(line)

    return hashlib.sha1(bytes(line, encoding="utf-8")).digest()[:hash_size]


class LocalSha1Dedup:
    def __init__(self, hash_size):
        self.hash_size = hash_size

        self.data = []

    def add_line(self, line_id, line):
        hval = sha1_hash(line, self.hash_size)
        self.data.append((line_id, hval))

    def add_hashes(self, line_id, hval):
        assert isinstance(hval, bytes) and len(hval) == self.hash_size
        self.data.append((line_id, hval))

    def dedup(self):
        self.data.sort(key=lambda item: item[0])
        dedup_set = set()
        exclude = []
        for line_id, hval in self.data:
            if hval in dedup_set:
                exclude.append(line_id)
            else:
                dedup_set.add(hval)
        return exclude
