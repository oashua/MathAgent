import openai
import time
from dotenv import dotenv_values

def load_config():
    config = dotenv_values("env")
    openai.api_base = config['api_base']
    openai.api_key = config['api_key']
    openai.organization = config['organization']
    openai.proxy = config['proxy']

def requrest(model, prompt, max_len, temp, n=1):
    completion = openai.ChatCompletion.create(
        model=model,
        messages = prompt,
        max_tokens=max_len,
        temperature=temp,
        n = 1
    )
    return completion

def generate(prompt, sys = None, model = "gpt-3.5-turbo-0613", CoT = None, max_len = 1024, temp = 0):    
    prompt = [{"role":"user","content":prompt}]
    if CoT != None:
        for prmt in CoT:
            prompt = prmt + prompt    
    if sys:
        prompt = [{"role":"system","content":sys}] + prompt
    
    try:
        completion = requrest(model, prompt, max_len, temp)
    except:
        time.sleep(10)
        completion = requrest(model, prompt, max_len, temp)
    
    # greedy request
    result = completion["choices"][0]["message"]["content"]
    return result
