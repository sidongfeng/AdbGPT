import re
import openai
import numpy as np
from loguru import logger

import cfgs

def find_identifier(text, identifier):
    m = []
    # https://regexr.com/78asm
    if identifier == "[]":
        m = re.findall(r'\[(.*?)\]', text)
    elif identifier == '""':
        m = re.findall(r'"(.*?)"', text)
    else:
        m = re.findall(r'({}\d+)'.format(identifier), text)
    return m

class ChatGPT():
    def __init__(self):
        openai.api_key = cfgs.OPENAI_TOKEN
        self.prompt = []
        self.initialize_chatgpt()

    def get_response_from_chatgpt(self, prompt):
        response = openai.ChatCompletion.create(
                            model=cfgs.MODEL,
                            messages=prompt,
                            # max_tokens=cfgs.MAX_TOKENS,
                            temperature=cfgs.TEMPERATURE,
                            frequency_penalty=cfgs.FREQUENCY_PENALTY,
                            presence_penalty=cfgs.PRESENCE_PENALTY)
        return response['choices'][0]['message']['content']

    def initialize_chatgpt(self):
        # self.prompt += [
        #     {"role": "system", "content": cfgs.INITIAL_SYSTEM_PROMPT},
        #     {"role": "user", "content": cfgs.INITIAL_USER_PROMPT}
        # ]
        # response = self.get_response_from_chatgpt(self.prompt)
        # self.prompt.append({"role": "assistant", "content": response})
        self.prompt += [
            {"role": "system", "content": cfgs.INITIAL_SYSTEM_PROMPT+cfgs.INITIAL_USER_PROMPT},
        ]

    def infer(self, question):
        logger.info(question)
        self.prompt.append({"role": "user", "content": question})
        response = self.get_response_from_chatgpt(self.prompt)
        self.prompt.append({"role": "assistant", "content": response})
        logger.info(response)
        return response

    def parse_numeric_outputs(self, response, identifier="[]"):
        output = []
        step = 1
        for line in response.split('\n'):
            # re.match(f"{step}. "+r'\[([A-Za-z0-9.^_]+)\]', line)
            line = line.strip()
            if re.match(f"{step}. ", line) is not None:
                m = find_identifier(line, identifier)
                print(step, m)
                step += 1
        return output

    def parse_list_outputs(self, response, identifier="[]"):
        output = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith("- "):
                m = find_identifier(line, identifier)
                print(line, m)
        return output
    
    def parse_identifier_outputs(self, response, identifier="[]"):
        output = []
        response = response.strip()
        m = find_identifier(response, identifier)
        return m

    def parse_outputs(self, response, identifier="[]"):
        parsed_numeric_output = self.parse_numeric_outputs(response, identifier=identifier)
        parsed_list_output = self.parse_list_outputs(response, identifier=identifier)
        # parsed_non_output = parse_non_outputs(output)

        parsed_output = [parsed_numeric_output, parsed_list_output][np.argmax([len(parsed_numeric_output), len(parsed_list_output)])]
        return parsed_output


if __name__ == '__main__':
    chatgpt = ChatGPT()

    question = """hello world"""
    chatgpt.infer(question)

    responese = """1. [num_test]
    2. [num_test]"""
    chatgpt.parse_outputs(responese, identifier="[]")

    responese = """- "list_test"
    - "list_test_1" "list_test_2" """
    chatgpt.parse_outputs(responese, identifier='""')