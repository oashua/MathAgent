# prompts for planner
ACTION_DISP = '''Actions Description:
# Principle
In general, the exploration/reasoning is conducted by agent models, forming individual nodes of both chain and tree-like structures.
# Main categories of Actions
Inference, Observation, Association.
## Inference
Purpose: generate new rationales with known conditions to promote an exploration.
Actions: ['negate', 'derive', 'induce', 'classify', 'infer'].
Explanation: 'negate' involves negation or counterproof, 'derive' focues on calculation or formula derivation, 'induce' is using mathematical induction, 'classify' is using classification discussion with finite cases, and 'infer' is general text-based reasoning when other actions are not applicable.
## Observation
Purpose: provide discussion or analysis to evaluate an exploration for guiding the next action.
Actions: ['analyze', 'rethink'].
Explanation: 'analyze' guides the exploration via discussion or analysis, 'rethink' means think outside the box.
## Association
Purpose: connecting and introducing external knowledge to aid or start an exploration.
Actions: ['associate', 'construct'].
Explanation: 'associate' seeks applicable theorems and formulas, 'construct' designs auxiliary conditions or variables.
'''

TASK_DICT = {
    'negate': "'negate' involves negation or counterproof",
    'derive': "'derive' focues on calculation or formula derivation",
    'induce': "'induce' is using mathematical induction",
    'classify': "'classify' is using classification discussion with finite cases",
    'infer': "'infer' is general text-based reasoning when other actions are not applicable",
    'analyze': "'analyze' guides the exploration via discussion or analysis",
    'rethink': "'rethink' means think outside the box",
    'associate': "'associate' seeks applicable theorems and formulas",
    'construct': "'construct' designs auxiliary conditions or variables"
}

## Split the Problem
prepocess_prp = {
    'question': "Only extract the question to be reasoned or the conclusion to be proven in '{problem}' without any conditions.",
    'conditions': "Extract all known conditions in the theory proving problem of '{problem}' and list them in a list format. There is no need to prefix each condition with a sequence number."
}

branch_temp = {
    'cond': "In {step_type} scheme, you can use the following conditions directly: {step_cond}",
    'negate_goal': "You need to show that in a case of contradiction, the known condition contradicts the following goal: {step_negate_goal}"
}

roles = {
    # the planner
    'select': 'You are a AI planner specialized in choosing an action and designing the task/guidance. Please read the given context and choose an action that could be helpful for solving the problem. Then an special AI agent who is only capable of one action will be called to finish it by completing the task or following the guidance.',
    # mathematical and auxilary actions
    ## create new branches
    'negate': "You are an AI planner specialized in solving mathematical problems by contradiction. Please read the given context and devise a contradiction scheme.",
    'induce': "You are an AI planner specialized in devising a scheme with mathematical induction method to solve math problems.Please read the given context and devise an induction scheme.",
    'classify': "You are an AI planner specialized in devising a classification discussion scheme to solve math problems. Please read the given context and devise a classification discussion scheme.",
    ## no more branches
    'derive': "You are an AI mathematician specialized in using calculation or formula derivation for promoting the exploration and advancing the reasoning/proving. Please read the given context and promote the proof.",
    'infer': "You are an AI mathematician specialized in promoting the exploration and advance the reasoning/proving. Please read the given context and promote the proof.",
    'analyze': "You are an AI mathematician specialized in providing an analysis/discussion for further decision-making. Please read the given context and promote the proof.",
    'rethink': "You are an AI mathematician specialized in thinking outside the box or finding useful pattarns for further decision-making. Please read the given context and promote the proof.",
    'associate': "You are an AI mathematician specialized in Seeking (external) applicable theorems and formulas to aid or start an exploration. Please read the given context and promote the proof.",
    'construct': "You are an AI mathematician specialized in constructing auxiliary conditions/variables to aid or start an exploration. Please read the given context and promote the proof.",
    # always called, no need for selection
    'check': "You are an AI mathematician who is good at checking proofs and summarizing them. Please read the given context and make your judgement.\n",
    'summary': "You are an AI mathematician who is good at summarizing the proof. Please read the given context and make your summary."
}

prompts_dict = {'prepocess': prepocess_prp, 'branch': branch_temp, 'roles': roles}

template_dict = {
    'general': 'Now, your target is to infer that:\n[{qst}]\nThe conditions you know:\n[{cond}]\n{mem}{fail}',
    'memory': 'Before, you have completed the following steps:\n[{mem}]\n',
    'failure': 'And You can learn from the following failed attempts:\n[{fail}]\n',
    # instructions
    'select': 'Please choose one action based on following instructions:\n{act_desp}\nPlease only output your action choice without any other information.',
    'negate': 'Please design a contradiction scheme in the JSON list format of "{\'Conditions\': C, \'Goal\': G}". C is all conditions assumed in proof by contradiction (including the necessary original conditions), and G is the target that is intended to be disproved in the proof by contradiction.',
    'induce': 'Please divide the problem into two subproblems in the JSON list format of "[{\'Type\': "base step", \'Conditions\': C1, \'Goal\': G1}, {\'Type\': "induction step", \'Conditions\': C2, \'Goal\': G2}]". C1 and C2 are the new conditions of the base step and the induction step, respectly. G1 and G2 are the targets of the two step.',
    'classify': 'Please divide the problem into some subproblems in the JSON list format of "[{\'Conditions\': ST, \'Goal\': SG}, and so forth.]". ST is the new conditions of one subproblem and SG is the target of it.',
    'check': 'The proof which needs to be check and summary is that:\n[{output}]\nYou need to check whether the proof processing is right. If you believe the proof is wrong, please output in the JSON format:\n"{{"Correctness":"wrong","Summary":R}}". R is the reason why you think the proof is wrong, and should be shorter and clearer in three sentences or less. Otherwise, if you think it\'s right, please output in the JSON format: "{{"Correctness":"right"}}".', 
    'summary': 'The proof which needs to be summarized is that:\n[{output}]\nYou need to check whether the final target is solved. Please output in the JSON format:\n"{{"Solved":S1,"Summary":S2}}". S1 is yes/no whether the final target is solved, S2 is your summary of this proof.\nPay attention: S2 should be shorter and clearer in three sentences or less, and you don\'t need to judge the correctness of the proof.',
    # other actions
    'failure_wo_branch': 'Besides, in a previous attempt, someone made the following incorrect deduction and you should avoid similar mistakes:\n[{fail}]',
    'other_action': "Remember, the only action you are capable of is defined as: \n{inst}."
}