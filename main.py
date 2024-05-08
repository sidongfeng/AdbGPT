import os
from loguru import logger
import uiautomator2 as u2
import time

from extract_step import Extract_Steps
from guided_replay import UI
from guided_replay import Guided_Replay
import adb

#### VERY IMPORTANT: Change the xml_screen_size in config to your device size

if __name__ == '__main__':
    save_path = "test"
    logger.add(os.path.jpon(save_path, "loguru.log"))
    bug_description = """1. Go to settings\n2. Click support project (either paypal or bitcoin)"""

    # action_prompt = """Here is a list of operations: [tap, input, scroll, double tap, long tap]\n"""
    # primtive_prompt = """An action is defined as [operation] [location], for example, [tap] ["OK"].\n"""
    # example_prompt = """Question: Convert the action sequence to "I attempt to take a photo when viewing the preference, swipe to the bottom, input a value of "1" in the photo, and click the OK button or CANCEL button in the circle."\n"""
    # cot_prompt = """Answer: The possible first step will be [Open] [the "preference" view], however, there is no explicit [Open] operation in the list, so we parse it into the closest operation [Tap]. As a result, the first step will be [Tap] ["preference"]. \nOverall, the action sequence is:\n1. [Tap] ["preference"]\n2. [Scroll] ["down"]\n3. [Input] ["photo"] ["1"]\n4. [Tap] ["OK"] or [Tap] ["Cancel"]\n"""
    # question_prompt = """Question: Convert the action sequence to "{}"\n Answer: """.format(bug)
    
    action_prompt = """Available actions: [tap, input, scroll, double tap, long tap]\n"""
    primtive_prompt ="""Action primitives: [Tap] [Component], [Scroll] [Direction], [Input] [Component] [Value], [Double-tap] [Component], [Long-tap] [Component]\n"""
    example_prompt = """Question: Extract the entity from the following ->
    "1. Open bookmark 
    2. Tap "add new bookmark" and create a name with "a" 
    3. Create another one with name "b" 
    4. Click "a" 
    5. Go back to bookmark after changing name "a" to "b" 
    6. App crash"\n"""
    cot_prompt = """Answer: 
    1st step is "Open bookmark". The action is "open" and the target component is "bookmark". However, there is no explicit "open" in the Available actions list. Therefore, we select the closest semantic action "tap". Following the Action primitives, the entity of the step is [Tap] ["bookmark"].
    2nd step is "Tap 'add new bookmark' and create a name with 'a'". Due to the conjunction word "and", this step can be separated into two sub-steps, "Tap 'add new bookmark'" and "create a name with 'a'". For the first sub-step, following the Action primitives, the entity is [Tap] ["add new bookmark"]. For the second sub-step, there is no explicit "create" in the Available actions list. Therefore, we select the closest semantic action "input". Following the Action primitives, the entity of the sub-step is [Input] ["name"] ["a"].
    3rd step is "Create another one with name 'b'". Due to its semantic meaning, this step is meant to repeat the previous steps to add another bookmark with name "b". Therefore, it should actually be the 2nd step, that is [Tap] ["add new bookmark"] and [Input] ["name"] ["b"].
    4th step is "Click 'a'". The action is "click" and the target component is "a". However, there is no explicit "click" in the Available actions list. Therefore, we select the closest semantic action "tap". Following the Action primitives, the entity of the step is [Tap] ["a"].
    5th step is "Go back to bookmark after changing name 'a' to 'b'". Due to the conjunction word "after", this step can be separated into two sub-steps, "Go back to bookmark" and "change name 'a' to 'b'". The conjunction word "after" also alters the temporal order of the sub-steps, that "change name 'a' to 'b'" should be executed first, followed by "go back to bookmark". For the first sub-step, there is no explicit "change" in the Available actions list. Therefore, we select the closest semantic action "input". Following the Action primitives, the entity of the sub-step is [Input] ["name"] ["b"]. For the second sub-step, there is no explicit "go back" in the Available actions list. Therefore, we select the closest semantic action "tap". Following the Action primitives, the entity of the sub-step is [Tap] ["back"].
    6th step is "App crash". This step does not have any operations.
    Overall, the extracted S2R entities are: 
    1. [Tap] ["bookmark"]
    2. [Tap] ["add new bookmark"]
    3. [Input] ["name"] ["a"]
    4. [Tap] ["add new bookmark"]
    5. [Input] ["name"] ["b"]
    6. [Tap] ["a"]
    7. [Input] ["name"] ["b"]
    8. [Tap] ["back"]\n
    """

    bug = bug_description
    question_prompt = """Question: Extract the entity from the following -> "{}"\n Answer: """.format(bug)

    prompt = action_prompt + primtive_prompt + example_prompt + cot_prompt + question_prompt
    prompt = prompt.strip()

    es = Extract_Steps()
    step_outputs = es.infer(prompt)

    d = u2.connect()
    print(d.info)

    step_i = 0
    missing_i = 0
    gr = Guided_Replay()
    start_time = time.time()
    while step_i < len(step_outputs):
        logger.debug(step_outputs[step_i].step_text)
        
        page_source = d.dump_hierarchy(compressed=True, pretty=True)
        xml_file = open(os.path.join(save_path, f'step_{step_i}_hierarchy.xml'), 'w', encoding='utf-8')
        xml_file.write(page_source)
        xml_file.close()
        adb.screen_shot(f'step_{step_i}', save_path)

        if step_outputs[step_i].action.lower() != "scroll":
            ui =  UI(os.path.join(save_path, f'step_{step_i}_hierarchy.xml'))
            html_code = ui.encoding()
            title_prompt = """Question:\n"""
            
            with open('utils/gui-1.xml', 'r') as f:
                example_ui = f.read()
            example_ui_prompt_1 = """GUI screen: \n{}\n\n""".format(example_ui)
            example_question_prompt_1 = """If I need to [Tap] ["Sign in"], which component id should I operate on the GUI? ->\n"""
            example_cot_prompt_1 = """Answer: There is no explicit "Sign in" component in the current GUI screen. However, there is a semantic closest component "Log in" button. The id attribute of "Log in" component is 6. So, we could potentially operate on [id=6] in the screen.\n"""

            example_ui_prompt_2 = """GUI screen: \n{}\n\n""".format(example_ui)
            example_question_prompt_2 = """If I need to [Tap] ["Settings"], which component id should I operate on the GUI? ->\n"""
            example_cot_prompt_2 = """Answer: There is no explicit and semantic similar "Settings" component in the current GUI screen, so it appears a [MISSING] step. However, "Settings" could be related to the "drawer" button in the screen. The id attribute of "drawer" component is 0. So, we could potentially operate on [id=0] component in the screen.\n"""

            if step_outputs[step_i].action.lower() == "input":
                step = "[{}] [{}] [{}]".format(step_outputs[step_i].action, step_outputs[step_i].target, step_outputs[step_i].input)
            else:
                step = "[{}] [{}]".format(step_outputs[step_i].action, step_outputs[step_i].target)
            ui_prompt = """GUI screen: \n{}\n\n""".format(html_code)
            question_prompt = """If I need to {}, which component id should I operate on the GUI? ->\nAnswer:""".format(step)
            
            prompt = title_prompt + example_ui_prompt_1 + example_question_prompt_1 + example_cot_prompt_1 \
                        + title_prompt + example_ui_prompt_2 + example_question_prompt_2 + example_cot_prompt_2 \
                        + title_prompt + ui_prompt + question_prompt
            prompt = prompt.strip()

            recursive_flag, target_id = gr.infer(prompt)
            logger.info("""Operate on id={} in the GUI screen.""".format(target_id))
            if target_id is None:
                adb.back()
                logger.info("No component found!")
                os.rename(os.path.join(save_path, f'step_{step_i}_hierarchy.xml'), os.path.join(save_path, f'step_{step_i}_missing_{missing_i}_hierarchy.xml'))
                os.rename(os.path.join(save_path, f'screenshot-step_{step_i}.png'), os.path.join(save_path, f'screenshot-step_{step_i}_missing_{missing_i}.png'))
                missing_i += 1
                continue

            # Excute the action
            bounds = [ui.elements[target_id].bounding_box.x1, \
                        ui.elements[target_id].bounding_box.y1, \
                        ui.elements[target_id].bounding_box.x2, \
                        ui.elements[target_id].bounding_box.y2]
            if step_outputs[step_i].action.lower() == "tap":
                adb.click(bounds)
            elif step_outputs[step_i].action.lower() == "double tap":
                adb.double_click(bounds)
            elif step_outputs[step_i].action.lower() == "long tap":
                adb.long_click(bounds)
            elif step_outputs[step_i].action.lower() == "input":
                adb.input_text(bounds, step_outputs[step_i].input)
        
            if recursive_flag:
                logger.info("There is a MISSING step!")
                os.rename(os.path.join(save_path, f'step_{step_i}_hierarchy.xml'), os.path.join(save_path, f'step_{step_i}_missing_{missing_i}_hierarchy.xml'))
                os.rename(os.path.join(save_path, f'screenshot-step_{step_i}.png'), os.path.join(save_path, f'screenshot-step_{step_i}_missing_{missing_i}.png'))
                missing_i += 1
            else:
                adb.screen_shot(f'step_{step_i}', save_path)
                step_i += 1
        else:
            direction = 'up' if 'up' in step_outputs[step_i].target else 'down'
            adb.scroll(direction)
            step_i += 1

        time.sleep(1)

    time_spend = time.time() - start_time
    print("Prcessing time", time_spend)