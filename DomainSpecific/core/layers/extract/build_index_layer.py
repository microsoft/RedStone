#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import sys
import faiss
import numpy as np
import traceback

def build_index_layer(base_vectors, variables=dict(), SEED=1, DIM=4096, CLUSTERS=100):
    ret = None
    try:
        np.random.seed(SEED)

        quantizer = faiss.IndexFlatL2(DIM)
        index = faiss.IndexIVFFlat(quantizer, DIM, CLUSTERS, faiss.METRIC_L2)

        assert not index.is_trained
        base_vectors = np.array(base_vectors)
        index.train(base_vectors)
        assert index.is_trained

        index.add(base_vectors)
        ret = index
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    D = 64
    base_vectors = np.random.random((100000, D)).astype('float32')
    base_vectors[:, 0] += np.arange(100000) / 1000.
    index = build_index_layer(base_vectors, D=D)
    print(index)
