#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
import faiss
import numpy as np
import traceback

def search_index_layer(index, query_vectors, variables=dict(), TOPK=1):
    ret = (None, None)
    try:
        query_vectors = np.array(query_vectors)
        D, I = index.search(query_vectors, TOPK)
        ret = (I, D)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return ret


if __name__ == '__main__':
    DIM = 4096
    CLUSTERS = 2
    base_vectors = np.random.random((100000, DIM)).astype('float32')
    base_vectors[:, 0] += np.arange(100000) / 1000.
    
    quantizer = faiss.IndexFlatL2(DIM)
    index = faiss.IndexIVFFlat(quantizer, DIM, CLUSTERS, faiss.METRIC_L2)

    assert not index.is_trained
    index.train(base_vectors)
    assert index.is_trained
    index.add(base_vectors)

    query_vectors = np.random.random((10000, DIM)).astype('float32')
    query_vectors[:, 0] += np.arange(10000) / 1000.

    I, D = search_index_layer(index, query_vectors, D=D)
    print(D[:1])
