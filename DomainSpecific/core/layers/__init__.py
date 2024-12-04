from enum import Enum
from ..data import DataType

from .template_layer import template_layer

# Control layers
from .control import *

# Network (download/upload) layers
from .network import *

# IO (read/write) layers
from .io import *

# Extract layers
from .extract import *

# Transform layers
from .transform import *

class LayerType(Enum):
    Template                     = 0

    # Control
    Data_Sample                  = 1
    Data_Concat                  = 2
    Data_Order                   = 3
    Data_Partition               = 4
    Data_Filter                  = 5
    Data_Shuffle                 = 6

    # Network - download/upload
    Upload_File_To_Blob          = 101
    Upload_Bytes_To_Blob         = 102
    Download_File_From_Blob      = 103
    Download_Bytes_From_Blob     = 104
    Download_File_From_Internet  = 105
    Download_Bytes_From_Internet = 106
    Download_Url_List            = 107
    Download_Warc_Indice         = 108
    Download_Warc_File           = 109
    Download_Urls_From_Website   = 110
    Download_Image_From_Jsonl    = 111
    Download_StarCoder           = 112

    # IO - read/write
    To_Binary_File               = 201
    To_Line_File                 = 202
    To_Jsonl_File                = 203
    To_Parquet_File              = 204
    To_Index_File                = 205
    To_Warc_File                 = 206
    From_Binary_File             = 207
    From_Line_File               = 208
    From_Jsonl_File              = 209
    From_Parquet_File            = 210
    From_Index_File              = 211
    From_Wet_File                = 212
    From_Warc_File               = 213

    # Extract
    Extract_Article              = 301
    Build_Index                  = 302
    Search_Index                 = 303
    
    # Transform
    Tokenize_Article             = 401
    Ngrams                       = 402
    Minhash_Tokens               = 403
    LSH_Minhash                  = 404
    Warc_Filter                  = 405
    Warc_Encode                  = 406
    Warc_To_Wet                  = 407
    Wet_Decode                   = 408
    Text_Embedding               = 409
    Sentence_Embedding           = 410
    Sentence_Filter              = 411
    Code_Generation              = 412
    Url_To_Record                = 413
    Extract_Link_From_Warc       = 414
    Wet_To_Imageinfos            = 415
    Warc_To_Screenshot_MD        = 416
    MCQ_Filter                   = 417
    OpenQuestion_Filter          = 418
    Convert_PDF                  = 419
    Extract_HTML                 = 420
    MD_Filter                    = 421
    Cascaded_Filter              = 422
    Math_Filter                  = 423


LayerType2Func = \
{
    LayerType.Template                     : (template_layer, [DataType.Mem_Any], [DataType.Mem_Any], True),

    # Control
    LayerType.Data_Sample                  : (data_sample_layer, [DataType.Mem_List], [DataType.Mem_List], True),
    LayerType.Data_Concat                  : (data_concat_layer, [DataType.Mem_List], [DataType.Mem_List], True),
    LayerType.Data_Order                   : (data_order_layer, [DataType.Mem_List], [DataType.Mem_List], True),
    LayerType.Data_Filter                  : (data_filter_layer, [DataType.Mem_List], [DataType.Mem_List], True),
    LayerType.Data_Partition               : (data_partition_layer, [DataType.Mem_List], [DataType.Mem_List], True),
    LayerType.Data_Shuffle                 : (data_shuffle_layer, [DataType.Mem_List], [DataType.Mem_List], True),

    # Network - download/upload
    LayerType.Upload_File_To_Blob          : (upload_file_to_blob_layer, [DataType.Mem_Str, DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Str], True),
    LayerType.Upload_Bytes_To_Blob         : (upload_bytes_to_blob_layer, [DataType.Mem_Binary, DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Str], True),
    LayerType.Download_File_From_Blob      : (download_file_from_blob_layer, [DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Str], True),
    LayerType.Download_Bytes_From_Blob     : (download_bytes_from_blob_layer, [DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Binary, DataType.Mem_Str], True),
    LayerType.Download_File_From_Internet  : (download_file_from_internet_layer, [DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Str], True),
    LayerType.Download_Bytes_From_Internet : (download_bytes_from_internet_layer, [DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Binary, DataType.Mem_Str], True),
    LayerType.Download_Url_List            : (download_url_list_layer, [DataType.Mem_Str], [DataType.Mem_StrList, DataType.Mem_StrList], True),
    LayerType.Download_Warc_File           : (download_warc_file_layer, [DataType.Mem_Str], [DataType.Mem_Str, DataType.Mem_Str], True),
    LayerType.Download_Warc_Indice         : (download_warc_indice_layer, [DataType.Mem_Str], [DataType.Mem_StrList, DataType.Mem_StrList], True),
    LayerType.Download_Urls_From_Website   : (download_urls_from_website_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.Download_StarCoder           : (download_starcoder_layer, [DataType.Mem_Str], [DataType.Mem_Int], True),

    # IO - read/write
    LayerType.To_Binary_File               : (to_binary_file_layer, [DataType.Mem_Binary, DataType.Mem_Str], [DataType.Mem_Str], True),
    LayerType.To_Line_File                 : (to_line_file_layer, [DataType.Mem_StrList, DataType.Mem_Str], [DataType.Mem_Str], True),
    LayerType.To_Jsonl_File                : (to_jsonl_file_layer, [DataType.Mem_DictList, DataType.Mem_Str], [DataType.Mem_Str], True),
    LayerType.To_Parquet_File              : (to_parquet_file_layer, [DataType.Mem_DictList, DataType.Mem_Str], [DataType.Mem_Str], True),
    LayerType.To_Index_File                : (to_index_file_layer, [DataType.Mem_Index, DataType.Mem_Str], [DataType.Mem_Str], True),
    LayerType.From_Binary_File             : (from_binary_file_layer, [DataType.Mem_Str], [DataType.Mem_Binary], True),
    LayerType.From_Line_File               : (from_line_file_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.From_Jsonl_File              : (from_jsonl_file_layer, [DataType.Mem_Str], [DataType.Mem_DictList], True),
    LayerType.From_Parquet_File            : (from_parquet_file_layer, [DataType.Mem_Str], [DataType.Mem_DictList], True),
    LayerType.From_Index_File              : (from_index_file_layer, [DataType.Mem_Str], [DataType.Mem_Index], True),
    LayerType.From_Wet_File                : (from_wet_file_layer, [DataType.Mem_Str], [DataType.Mem_DictList], True),
    LayerType.From_Warc_File               : (from_warc_file_layer, [DataType.Mem_Str], [DataType.Mem_DictList], True),

    # Extract
    LayerType.Extract_Article              : (extract_article_layer, [DataType.Mem_Warc], [DataType.Mem_Dict], True),
    LayerType.Build_Index                  : (build_index_layer, [DataType.Mem_VectorList], [DataType.Mem_Index], True),
    LayerType.Search_Index                 : (search_index_layer, [DataType.Mem_Index, DataType.Mem_VectorList], [DataType.Mem_VectorList, DataType.Mem_VectorList], True),
    
    # Transform
    LayerType.Tokenize_Article             : (tokenize_article_layer, [DataType.Mem_Dict], [DataType.Mem_StrList], True),
    LayerType.Ngrams                       : (ngrams_layer, [DataType.Mem_StrList], [DataType.Mem_StrList], True),
    LayerType.Minhash_Tokens               : (minhash_tokens_layer, [DataType.Mem_StrList], [DataType.Mem_StrList], True),
    LayerType.LSH_Minhash                  : (lsh_minhash_layer, [DataType.Mem_StrList], [DataType.Mem_StrList], True),
    LayerType.Warc_Filter                  : (warc_filter_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.Warc_Encode                  : (warc_encode_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.Warc_To_Wet                  : (warc_to_wet_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.Wet_Decode                   : (wet_decode_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.Math_Filter                  : (math_filter_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.OpenQuestion_Filter          : (openquestion_filter_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
    LayerType.MCQ_Filter                   : (mcq_filter_layer, [DataType.Mem_Str], [DataType.Mem_StrList], True),
}


__all__ = [
    "LayerType", 
    "LayerType2Func", 
    "template_layer", 
    "data_sample_layer", 
    "data_concat_layer", 
    "data_order_layer", 
    "data_partition_layer", 
    "data_filter_layer", 
    "data_shuffle_layer", 
    "upload_file_to_blob_layer", 
    "upload_bytes_to_blob_layer", 
    "download_file_from_blob_layer", 
    "download_bytes_from_blob_layer", 
    "download_file_from_internet_layer", 
    "download_bytes_from_internet_layer", 
    "download_url_list_layer", 
    "download_warc_file_layer", 
    "download_warc_indice_layer", 
    "download_urls_from_website_layer", 
    "download_starcoder_layer", 
    "to_binary_file_layer", 
    "to_line_file_layer", 
    "to_jsonl_file_layer", 
    "to_parquet_file_layer", 
    "to_index_file_layer", 
    "from_binary_file_layer", 
    "from_line_file_layer", 
    "from_jsonl_file_layer", 
    "from_parquet_file_layer", 
    "from_index_file_layer", 
    "from_wet_file_layer", 
    "from_warc_file_layer", 
    "extract_article_layer", 
    "build_index_layer", 
    "search_index_layer", 
    "tokenize_article_layer", 
    "ngrams_layer", 
    "minhash_tokens_layer", 
    "lsh_minhash_layer", 
    "warc_filter_layer", 
    "warc_encode_layer", 
    "warc_to_wet_layer", 
    "wet_decode_layer", 
    "math_filter_layer", 
    "openquestion_filter_layer", 
    "mcq_filter_layer", 
]
