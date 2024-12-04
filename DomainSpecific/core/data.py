#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
from enum import Enum

class DataType(Enum):
    # Memory Data
    Mem_Any          = 0
    Mem_Binary       = 1
    Mem_Int          = 2
    Mem_Float        = 3
    Mem_Str          = 4
    Mem_Warc         = 5
    Mem_Dict         = 6
    Mem_Index        = 7
    Mem_Vector       = 8
    Mem_Record       = 9
    Mem_List         = 10
    Mem_BinaryList   = 11
    Mem_IntList      = 12
    Mem_FloatList    = 13
    Mem_StrList      = 14
    Mem_WarcList     = 15
    Mem_DictList     = 16
    Mem_IndexList    = 17
    Mem_VectorList   = 18
    Mem_RecordList   = 19

    # Disk Data (Deprecated)
    File_Any         = 100
    File_Binary      = 101
    File_Text        = 102
    File_Warc        = 103
    File_Parquet     = 104
    File_Json        = 105
    File_Index       = 106
    File_Vector      = 107
    File_AnyLines    = 110
    File_TextLines   = 111
    File_JsonLines   = 112
    File_VectorLines = 113

    @staticmethod
    def belong(a, b):
        if not isinstance(a, DataType) or not isinstance(b, DataType):
            return False
        return a == b or \
               (b.value % 10 == 0 and 0 <= a.value - b.value < 10) or \
               (b == DataType.Mem_Any and a.value < 100) or \
               (b == DataType.File_Any and a.value >= 100)

class Data:
    """
    Data class (Deprecated).
    """
    def __init__(self, type=DataType.Mem_Any, value=None):
        self.type = type if isinstance(type, DataType) else DataType[type]
        self.value = value


if __name__ == "__main__":
    data = Data()
    print(data)
