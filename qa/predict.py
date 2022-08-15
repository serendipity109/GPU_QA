import os
import sys
sys.path.insert(1, os.path.dirname(__file__))
import torch
import logging
import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from core import to_bert_ids, use_model


def init_logging():
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s %(processName)s --- [%(threadName)s] %(name)s : %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    logger_level = logging.INFO
    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    handlers = [ch]
    logging.basicConfig(level=logger_level, handlers=handlers)

init_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

logger.info('Init model.')
pkl_file = open('qa/trained_model/data_features.pkl', 'rb')
data_features = pickle.load(pkl_file)
answer_dic = data_features['answer_dic'] 
model_setting = {
    "model_name":"bert", 
    "config_file_path":"qa/trained_model/config.json", 
    "model_file_path":"qa/trained_model/pytorch_model.bin", 
    "vocab_file_path":"qa/bert-base-chinese-vocab.txt",
    "num_labels":149  # 分幾類 
}  
model, tokenizer = use_model(**model_setting)
model.eval()

class request_body(BaseModel):
    question : str = 'GeForce RTX 3060 GAMING Z TRIO 12G 的晶片'

@app.post("/predict")
async def predict(args : request_body):
    q_input = args.question
    bert_ids = to_bert_ids(tokenizer,q_input)
    assert len(bert_ids) <= 512
    input_ids = torch.LongTensor(bert_ids).unsqueeze(0)
    # predict
    outputs = model(input_ids)
    predicts = outputs[:2]
    predicts = predicts[0]
    max_val = torch.max(predicts)
    label = (predicts == max_val).nonzero().numpy()[0][1]
    ans_label = answer_dic.to_text(label)
    return (q_input, ans_label)

# if __name__ == "__main__":    
#     # load and init
#     pkl_file = open('trained_model/data_features.pkl', 'rb')
#     data_features = pickle.load(pkl_file)
#     answer_dic = data_features['answer_dic']
        
#     # BERT
#     model_setting = {
#         "model_name":"bert", 
#         "config_file_path":"trained_model/config.json", 
#         "model_file_path":"trained_model/pytorch_model.bin", 
#         "vocab_file_path":"bert-base-chinese-vocab.txt",
#         "num_labels":149  # 分幾類 
#     }    

#     #
#     model, tokenizer = use_model(**model_setting)
#     model.eval()

#     #
#     q_inputs = ['GeForce RTX 3060 GAMING Z TRIO 12G 的晶片','TUF Gaming GeForce RTX3060 V2 OC 超頻版 12GB GDDR6 適用於','RTX 3080 SUPRIM X 12G LHR 的價格是', 'GeForce RTX 3080 Ti GAMING OC 12G的保固期']
#     for q_input in q_inputs:
        # bert_ids = to_bert_ids(tokenizer,q_input)
        # assert len(bert_ids) <= 512
        # input_ids = torch.LongTensor(bert_ids).unsqueeze(0)

        # # predict
        # outputs = model(input_ids)
        # predicts = outputs[:2]
        # predicts = predicts[0]
        # max_val = torch.max(predicts)
        # label = (predicts == max_val).nonzero().numpy()[0][1]
        # ans_label = answer_dic.to_text(label)
        
        # print(q_input)
        # print(ans_label)
