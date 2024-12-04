#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import faiss
import traceback
import util

def to_index_file_layer(index, file_path, variables=dict(), STORAGE_PATH=None):
    ret = None
    try:
        file_path = util.to_real_path(file_path, variables)
        util.create_folder_by_file_path(file_path)

        faiss.write_index(index, file_path)

        if STORAGE_PATH is not None:
            util.upload_file_to_blob(STORAGE_PATH, file_path, file_path)

        ret = file_path
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return (ret,)


if __name__ == '__main__':
    D = 64
    NLIST = 100
    base_vectors = np.random.random((100000, D)).astype('float32')
    base_vectors[:, 0] += np.arange(100000) / 1000.
    
    quantizer = faiss.IndexFlatL2(D)
    index = faiss.IndexIVFFlat(quantizer, D, NLIST, faiss.METRIC_L2)

    assert not index.is_trained
    index.train(base_vectors)
    assert index.is_trained
    index.add(base_vectors)

    file_path = "index.faiss"
    file_path = to_index_file_layer(index, file_path)
    print(file_path)
