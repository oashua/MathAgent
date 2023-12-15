from src.generate import generate
from src.utils import return_json
from src.prompts import TASK_DICT, template_dict, prompts_dict
from src.config import *

import copy

class InferNode:
    def __init__(self, funcs, logger, conditions, memories, question, top_level, inf_level, model):
        self.logger = logger
        self.conditions = conditions
        self.memories = memories
        self.question = question
        self.funcs = funcs

        self.failure = []
        self.fail_count = 0

        self.top_level = top_level
        self.inf_level = inf_level
        self.model = model
        
    def logging(self, info):
        print(info)
        self.logger = self.logger + info + '\n\n'
        
    def act_gen(self, forbid=[]): 
        self.forbid = forbid
        select_func = self.funcs['select']
        
        # When the system has reached max depths, forbid to create new branchs.
        if self.top_level >= MAX_LAYER:
            self.forbid = list(set(forbid + ['negate', 'induce', 'classify']))
            
        memory = '. '.join(self.memories).strip()
        action = select_func(self.question, self.conditions, self.model, memories=memory, forbid=self.forbid)
        self.action = action.lower()
        self.logging(f'Action selection: {action}.')
        
        # we will only execute select once in one node.
        # the check mechanism will retry the same action
        # the summarize machanism will start another action in a new infernode
        final_output = self.act()
        return self.logger, final_output
    
    def act(self):
        assert self.action in TASK_DICT.keys()
        action = self.action
        
        # basic execution
        exec_func = self.funcs['act']
        memory = '. '.join(self.memories).strip() if len(self.memories) else None
        failure = '.\n'.join(self.failure).strip() if len(self.failure) else None
        output = exec_func(self.question, self.conditions, action, self.model, memory, failure)
        self.logging(f'Action: {action} (Level {self.top_level})\nOutput: {output}')
                
        if action in ['induce', 'classify', 'negate']:
            output = return_json(output)
            if action == 'negate':
                output = [output]
            
            next_nodes_outputs = []
            for step in output:
                step_goal = step['Goal']#.replace("\\\\", "\\")
                
                if action == 'induce':
                    step_induce_type = step['Type']
                    step_goal += f". Please only prove this {step_induce_type}."
                    step_type = f'{step_induce_type} of a induction'
                    
                elif action == 'classify':
                    step_type = 'classification discussion'
                else:
                    step_type = 'contradiction'
                    step_goal = prompts_dict['branch']['negate_goal'].format(step_negate_goal=step_goal)
                
                step_cond = step['Conditions']#.replace("\\\\", "\\")
                temp_condition = copy.deepcopy(self.conditions)
                temp_condition.append(prompts_dict['branch']['cond'].format(step_type=step_type, step_cond=step_cond))
                
                # the required context of memories were converted into sub_conditions and sub_goals
                next_node = InferNode(self.funcs, self.logger, temp_condition, [], step_goal, self.top_level+1, 0, self.model)
                node_logger, node_out = next_node.act_gen([action])
                next_nodes_outputs.append(node_out)
                # replace the original logger as we execute the actions sequentely
                self.logger = node_logger
               
            branch_outputs = '. '.join(next_nodes_outputs)
            final_output = self.summarize(branch_outputs)
            
            self.logging(f'Action: conclude/induce (Level {self.top_level})\nOutput: {final_output}')
        else:
            final_output = self.check(output)
            
        return final_output
        
    def check(self, output):
        exec_func = self.funcs['check']
        memory = '. '.join(self.memories).strip() if len(self.memories) else None
        output_check = exec_func(output, self.question, self.conditions, self.model, memories = memory)
        self.logging(f'Check output: {output_check}.')

        if output_check['Correctness'].lower() == 'wrong':
            self.failure.append(output_check['Summary'])
            self.fail_count += 1

            if self.fail_count < MAX_FAILURE_COUNT_IN_ONE_NODE:
                # Retry the same action
                return self.act()
            
        return self.summarize(output)
        
    def summarize(self, output):
        exec_func = self.funcs['summary']
        memory = '. '.join(self.memories).strip() if len(self.memories) else None
        output_sum = exec_func(output, self.question, self.conditions, self.model, memories = memory)

        self.logging(f'Summarize output: {output_sum}.')
        if output_sum['Solved'].lower() == 'no':
            if self.inf_level >= MAX_TRY_IN_ONE_LAYER:
                return "Can't finish the target: " + self.question
            temp_memories = copy.deepcopy(self.memories)
            temp_memories.append(output_sum['Summary'])
            # cannot be solved in one node
            next_node = InferNode(self.funcs, self.logger, self.conditions, temp_memories, self.question, self.top_level,
                                  self.inf_level + 1, self.model)
            
            node_logger, node_output = next_node.act_gen(self.forbid + [self.action])
            self.logger = node_logger
            return node_output
        else:
            return output_sum['Summary']