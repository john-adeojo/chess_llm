import os
import json
import requests
import yaml
import logging
import time
import re
import ast

# config_path = './api_keys.yaml'

config_path = os.path.join(os.path.dirname(__file__), '..', 'llm_agents', 'api_keys.yaml')


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

load_config(config_path)


def get_llm_response_openai(json_mode, system_prompt, model='gpt-4o', temperature=0):

    model_endpoint = 'https://api.openai.com/v1/chat/completions'
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
                    "model": model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": "Now it's your turn to play a move."
                        }
                    ],
                    "stream": False,
                    "temperature": temperature,
                }
    
    if json_mode == False:
        payload.pop('response_format')
        
    response_dict = requests.post(model_endpoint, headers=headers, data=json.dumps(payload))
    # logging.debug(response_dict.json())
    response_json = response_dict.json()

    if json_mode == False:
        response = response_json['choices'][0]['message']['content']

    else:
        response = json.loads(response_json['choices'][0]['message']['content'])

    return response 

def get_llm_response_groq(json_mode, system_prompt, model=None, temperature=0):

    model_endpoint = 'https://api.groq.com/openai/v1/chat/completions'
    api_key = os.getenv('GROQ_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
                    "model": model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "user",
                            "content": f"system: {system_prompt}\n\n user: Now it's your turn to play a move."
                        },
                    ],
                    "stream": False,
                    "temperature": temperature,
                }
    
    if json_mode == False:
        payload.pop('response_format')

    # To avoid rate limit errors on the GROQ API
    time.sleep(5)    
    response_dict = requests.post(model_endpoint, headers=headers, data=json.dumps(payload))
    # logging.debug(response_dict.json())
    response_json = response_dict.json()

    if json_mode == False:
        response = response_json['choices'][0]['message']['content']

    else:
        response = json.loads(response_json['choices'][0]['message']['content'])

    return response 



def get_llm_response_claude(json_mode, system_prompt, model=None, temperature=0):

    model_endpoint = 'https://api.anthropic.com/v1/messages'
    api_key = os.getenv('CLAUD_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version':'2023-06-01'
    }

    payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"system: {system_prompt}\n\n user: Now it's your turn to play a move."
                        },
                    ],
                    "temperature": temperature,
                    "max_tokens": 2024,

                }
    
    if json_mode:
        payload['messages'][0]['content'] += "Return the specified JSON, do not prepend your response with anything."

    response_dict = requests.post(model_endpoint, headers=headers, data=json.dumps(payload))
    logging.debug(response_dict.json())
    response_json = response_dict.json()

    if json_mode == False:
        response = response_json['content'][0]['text']
    else:
        response = response_json['content'][0]['text']
        response = json.loads(response)

    return response