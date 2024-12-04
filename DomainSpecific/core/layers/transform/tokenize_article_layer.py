#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
import os
import sys
os.sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/..")
import traceback
import sentencepiece as spm


tokenizer = None

def tokenize_article_layer(article, variables=dict(), SPM_MODEL_PATH="./dependency/models/sentencepiece.bpe.model"):
    ret = None
    try:
        global tokenizer
        if tokenizer is None:
            tokenizer = spm.SentencePieceProcessor(SPM_MODEL_PATH)
        tokens = tokenizer.encode(article, out_type=str)
        ret = tokens
    except KeyboardInterrupt:
        sys.exit()
    except Exception as ex:
        traceback.print_exc()
    return ret


if __name__ == "__main__":
    article = "2021-12-03 记者： 来源：中国网地产\n\n杭州市1日对外发布《杭州市共有产权保障住房管理办法》，其中明确，共有产权保障住房面向符合条件的市区户籍和稳定就业的非市区户籍家庭供应，购买共有产权保障住房享有与购买商品住房同等的公共服务权益。\n\n根据办法，市区户籍家庭要在符合限购政策前提下同时满足户籍、住房等相关条件，非市区户籍家庭需满足居住证、住房以及累计缴纳社保或个税年限等相关条件。\n\n办法明确，共有产权保障住房销售基准价按同地段、同类型商品住房市场价格合理优惠后确定。单套销售价格按照销售基准价及其浮动幅度确定，在售房阶段向社会公布。划拨土地共有产权保障住房，购房家庭可根据支付能力在50%至80%范围内选择产权份额比例，按照单套销售价格对应的不同比例支付购房款。出让土地共有产权保障住房，购房家庭产权份额为土地出让时已确定的份额比例，按照单套销售价格对应的产权比例支付购房款。\n\n在使用管理方面，杭州提出共有产权保障住房购房家庭取得不动产权证满5年的，可向代持机构提出一次性增购政府份额的申请，增购后住房性质转为商品住房，划拨土地权利性质调整为出让。取得不动产权证满10年后，方可通过买卖等方式上市交易。"
    tokens = tokenize_article_layer(article)
    print(tokens)
