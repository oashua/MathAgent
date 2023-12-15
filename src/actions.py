from src.utils import return_json
from src.prompts import ACTION_DISP, TASK_DICT, prompts_dict, template_dict
from src.generate import generate
import json

def load_history(memory, failure, isSelect=False):
    if isSelect:
        fail_temp = template_dict['failure_wo_branch']
    else:
        fail_temp = template_dict['failure']
    
    return_mem, return_fail = '', ''
    if memory:
        return_mem = template_dict['memory'].format(mem=memory)
    
    if failure:
        return_fail = fail_temp.format(fail=failure)
        
    return return_mem, return_fail

def prepocess(problem, model):
    '''This function requests the GPTs to split the problem into conditions and question.
    Params: 
    problem - the original problem
    
    Return: the splited question and conditions.
    '''    
    prepocess_prp = prompts_dict['prepocess']
    
    # request seperately
    qst_inq = prepocess_prp['question'].format(problem=problem)
    question = generate(qst_inq, model)
    cond_inq = prepocess_prp['conditions'].format(problem=problem)
    conditions = generate(cond_inq, model)

    # avoid format errors
    conditions = conditions.replace("\n\n", "\n").replace("- ", '').split("\n")
    return question, conditions

def select(question, conditions, model, memories=None, failure=None, forbid=[]):
    '''This function requests the GPTs to determine current action and corresponding guidance.
    Params: ...    
    
    Return: the splited question and conditions.
    '''
    # generate role
    select_prp = prompts_dict['roles']['select']
    # generate general input
    memory, failure = load_history(memories, failure, True)
    inq = template_dict['general'].format(qst=question, cond=conditions, mem=memory, fail=failure)
    # add action description (maybe forbid some actions)
    action_desriptions = gen_act_disp(forbid)
    inq = inq + template_dict['select'].format(act_desp=action_desriptions)
    # request
    result = generate(inq, select_prp, model = model)
    return result

def act(question, conditions, action, model, memories=None, failure=None):
    '''This function requests the GPTs to execute most Reasoner's actions.
    Params: ...
    
    Return: generations of GPTs
    '''
    # generate role
    prp = prompts_dict['roles'][action]
    
    # for different actions, add different instruction
    if action in ['induce', 'classify', 'negate']: # branch actions
        memories, failure = load_history(memories, None)
        inq = template_dict['general'].format(qst=question, cond=conditions, mem=memories, fail=failure)
        inq = inq + template_dict[action]
    else:
        memories, failure = load_history(memories, failure)
        inq = template_dict['general'].format(qst=question, cond=conditions, mem=memories, fail=failure)
        inq = inq + template_dict['other_action'].format(inst=TASK_DICT[action])
    # request
    result = generate(inq, prp, model = model)
    
    # simplify the expression format to avoid the confusion of LLM when the context is too long.
    result = result.replace('\n', ' ').replace('  ', ' ')
    return result

def summary(outputs, question, conditions, model, memories=None):
    '''This function requests the GPTs to summarize current outputs.
    Params: ...
    
    Return: the summarization and stopflag.
    '''
    prp = prompts_dict['roles']['summary']
    
    memories, failure = load_history(memories, None)
    inq = template_dict['general'].format(qst=question, cond=conditions, mem=memories, fail=failure)
    inq = inq + template_dict['summary'].format(output=outputs)
    # request
    result = generate(inq, prp, model = model)
    result = return_json(result)
    return result

def check(outputs, question, conditions, model, memories=None):
    '''This function requests the GPTs to summarize current outputs.
    Params: ...
    
    Return: the summarization and stopflag.
    '''
    prp = prompts_dict['roles']['check']
    
    memories, failure = load_history(memories, None)
    inq = template_dict['general'].format(qst=question, cond=conditions, mem=memories, fail=failure)
    inq = inq + template_dict['check'].format(output=outputs)
    # request
    result = generate(inq, prp, model = model)
    result = return_json(result)
    return result

def gen_act_disp(forbid_act):
    '''helper function that filter out the available actions
    Params:
    forbid_act - list, the actions that should not be selected.
    
    Return
    action_disp - the definitions of actions that given to the LM'''
    
    if len(forbid_act) == 0:
        return ACTION_DISP
    
    action_disp = '''Actions Description:
# Principle
In general, the exploration/reasoning is conducted by agent models, forming individual nodes of both chain and tree-like structures.
# Main categories of Actions
Inference, Observation, Association.
## Inference
Purpose: generate new rationales with known conditions to promote an exploration.
Actions: '''
    inference_act = ['negate', 'derive', 'induce', 'classify', 'infer']
    for act in forbid_act:
        if act in inference_act:
            inference_act.remove(act)
    action_disp += json.dumps(inference_act)
    action_disp += ".\nExplanation: " + ", ".join(TASK_DICT[key] for key in inference_act) + '''.
## Observation
Purpose: provide discussion or analysis to evaluate an exploration for guiding the next action.
Actions: '''
    observation_act = ['analyze', 'rethink']
    for act in forbid_act:
        if act in observation_act:
            observation_act.remove(act)
    action_disp += json.dumps(observation_act)
    action_disp += ".\nExplanation: " + ", ".join(TASK_DICT[key] for key in observation_act) + '''.
## Association
Purpose: connecting and introducing external knowledge to aid or start an exploration.
Actions: '''
    association_act = ['associate', 'construct']
    for act in forbid_act:
        if act in association_act:
            association_act.remove(act)
    action_disp += json.dumps(association_act)
    action_disp += ".\nExplanation: " + ", ".join(TASK_DICT[key] for key in association_act) + '.\n'
    return action_disp

action_funcs = {'select': select, 'act': act, 'summary': summary, 'check': check}