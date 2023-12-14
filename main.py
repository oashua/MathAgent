from dotenv import load_dotenv
import os
from src.infer_node import InferNode
from src.actions import prepocess, action_funcs
import argparse
import json
# add openai_api_key of .env file into environment variable
load_dotenv()
print(os.getenv('OPENAI_API_KEY'))
def load_data(dataset,split,topic):
    prefix = os.path.join('data',dataset)
    if dataset == 'miniF2F':
        prefix = os.path.join(prefix,'informal')
    if dataset == "MATH":
        assert split in ['train','test'], "MATH don't have split {}".format(split)
    if dataset == "miniF2F":
        assert split in ['test','valid'], "miniF2F don't have split {}".format(split)
    datapath = os.path.join(prefix,split)
    problem_list = []
    for root,dirs,files in os.walk(datapath):
        for file in files:
                problem_list.append(os.path.join(root,file))
    problem_topic_list = [item for item in problem_list if topic in item]
    assert len(problem_topic_list) != 0,"Load 0 data. Please check the correspondence between dataset and topic"
    return problem_topic_list

def get_question(problem_file,data_class):
    with open(problem_file, encoding="utf-8") as f:
        problem_dict = json.load(f)
    if data_class == 'MATH':
        problem_key = 'problem'
    elif data_class == 'miniF2F':
        problem_key = 'informal_statement'
    return problem_dict[problem_key]
def get_answer(q,model):
    question, conditions = prepocess(q, model)
    solver = InferNode(action_funcs, '', conditions, [], question, top_level=0, inf_level=0, model=model)
    logger, out = solver.act_gen()
    return logger,out

def save_answers(logger_dict,args,flag):
    file_name = '{}_{}_{}'.format(args.dataset,args.split,args.topic)
    if flag==1:
        file_name += '_nc.json'
    else:
        file_name += '.json'
    with open(file_name,'w') as f:
        json.dump(logger_dict,f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--dataset', type=str, default='MATH',help='dataset need to test')
    parser.add_argument('-s', '--split', type=str,default='test',help='spit of dataset')
    parser.add_argument('-t', '--topic', type=str,default='algebra',help='topic of MATH or filter of miniF2F, default to all data in split')

    args = parser.parse_args()

    assert args.dataset in ['MATH','miniF2F'], "dataset must be MATH or miniF2F."

    problem_filelist = load_data(args.dataset,args.split,args.topic)
    model = 'gpt-4-0613'
    loggers_dict = dict()
    flag = 0
    for problem_file in problem_filelist[:2]:
        qst = get_question(problem_file,data_class=args.dataset)
        try:
            logger,out = get_answer(qst,model)
            loggers_dict[problem_file] = logger
        except:
            print('Interrupt at {}:{}'.format(len(loggers_dict.keys()),problem_file))
            loggers_dict[problem_file] = 'None'
            flag = 1
    save_answers(loggers_dict,args,flag)
        
        