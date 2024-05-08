import re
from loguru import logger

from ChatGPT import ChatGPT
import cfgs


class STEP():
    def __init__(self, step_text):
        self.step_text = step_text
        self.action, self.target, self.input = self.step_parse()

    def step_parse(self):
        m = re.findall(r'\[(.*?)\]', self.step_text)
        if not self.is_step(m):
            print(f'Error: No actions found: {self.step_text}')
            return None

        action = None
        target = None
        input = None

        # Considering cases:
        # - [Tap] "home"
        # - [Tap] ["home"]
        # - [Input] ["home", "1"]
        # - [Input] ["home"]
        # NOT considering case:
        # - [Tap] ["home"] or [Tap] [button]
        # - 1. [Input] ["key", "shop"] \n [Input] ["value", "*"]
        if len(m) == 1:
            action = m[0]
            target = self.step_text.split(f"[{m[0]}]")[-1].strip()
        elif len(m) >= 2:
            if 'input' not in m[0].lower():
                action = m[0]
                target = m[1]
            else:
                action = m[0]
                target = m[1].strip()
                
                if len(m) > 2: 
                    input = m[2].strip()
                else:
                    input = cfgs.RANDOM_INPUT_TEXT

        return action, target, input

    def is_step(self, list_of_variable):
        for v in list_of_variable:
            if v.lower() in cfgs.ACTION_LISTS:
                return True
        return False




class Extract_Steps():
    def __init__(self):
        self.chatgpt = ChatGPT()
        self.chatgpt.initialize_chatgpt()

    def infer(self, question):
        response = self.chatgpt.infer(question)
#         response = """The action sequence can be converted as follows:
# 1. [Input] ["key", "shop"]
#    [Input] ["value", "*"]
#    [Input] ["max. age", "0"]
# 2. [Tap] ["DONE"]
#    [Tap] ["back"] (assuming this goes back to the main screen)"""

        output = []
        step = 1
        for line in response.split('\n'):
            line = line.strip()
            if re.match(f"{step}. "+r'\[([A-Za-z0-9.^_]+)\]', line) is not None:
                s = STEP(line.split(f"{step}. ",1)[-1])
                logger.info('\n{} \n  >>>> STEP-{}: [{}] [{}] [{}]'.format(
                                        line, step, s.action, s.target, s.input))
                output.append(s)
                step += 1
        return output




if __name__ == '__main__':
    action_prompt = """Here is a list of operations: [tap, input, scroll, double tap, long tap]\n"""
    primtive_prompt = """An action is defined as [operation] [location], for example, [tap] ["OK"].\n"""
    example_prompt = """Question: Convert the action sequence to "I attempt to take a photo when viewing the preference, swipe to the bottom, input a value of "1" in the photo, and click the OK button or CANCEL button in the circle."\n"""
    cot_prompt = """Answer: The possible first step will be [Open] [the "preference" view], however, there is no explicit [Open] operation in the list, so we parse it into the closest operation [Tap]. As a result, the first step will be [Tap] ["preference"]. \nOverall, the action sequence is:\n1. [Tap] ["preference"]\n2. [Scroll] ["down"]\n3. [Input] ["photo", "1"]\n4. [Tap] ["OK"] or [Tap] ["Cancel"]\n"""
    
    bug = """Navigate to reader or post, tap on comment icon and expand comment editor."""
    bug = """1. Set key \"shop\" and value to \"*\", max. age to \"0\"\n2. Press DONE and go back to the main screen."""
    bug = """Go to gyms page. Crashes within a few seconds """
    question_prompt = """Question: Convert the action sequence to "{}"\n Answer: """.format(bug)
    
    prompt = action_prompt + primtive_prompt + example_prompt + cot_prompt + question_prompt
    # prompt = action_prompt + primtive_prompt + question_prompt
    prompt = prompt.strip()

    es = Extract_Steps()
    output = es.infer(prompt)