import _init_paths
from loguru import logger

from ChatGPT import ChatGPT
import cfgs
import config
import view_hierarchy
import utils

class UI():
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.elements = {}

    def encoding(self):
        logger.info('reading hierarchy tree from {} ...'.format(self.xml_file.split('/')[-1]))
        with open(self.xml_file, 'r', encoding='utf-8') as f:
            vh_data = f.read().encode()
        vh = view_hierarchy.ViewHierarchy(
                    screen_width=config.XML_SCREEN_WIDTH,
                    screen_height=config.XML_SCREEN_HEIGHT)
        vh.load_xml(vh_data)
        view_hierarchy_leaf_nodes = vh.get_leaf_nodes()
        utils.sortchildrenby_viewhierarchy(view_hierarchy_leaf_nodes, 'bounds')

        logger.info('encoding the ui elements in hierarchy tree...')
        codes = ''
        for _id, ele in enumerate(view_hierarchy_leaf_nodes):
            obj_type = ele.uiobject.obj_type.name
            text = ele.uiobject.text
            text = text.replace('\n', ' ')
            resource_id = ele.uiobject.resource_id
            content_desc = ele.uiobject.content_desc
            html_code = self.element_encoding(_id, obj_type, text, content_desc, resource_id)
            codes += html_code
            self.elements[_id] = ele.uiobject
        codes = "<html>\n" + codes + "</html>"

        # logger.info('Encoded UI\n' + codes)
        return codes

    def element_encoding(self, _id, _obj_type, _text, _content_desc, _resource_id):
        _class = _resource_id.split('id/')[-1].strip()
        _text = _text.strip()
        assert _obj_type in cfgs.CLASS_MAPPING.keys(), print(_obj_type)
        tag = cfgs.CLASS_MAPPING[_obj_type]
        
        if _obj_type in ['CHECKBOX', 'CHECKEDTEXTVIEW', 'SWITCH']:
            code = f'  <input id={_id} type="checkbox" name="{_class}">\n'
            code += f'  <label for={_id}>{_text}</label>\n'
        elif _obj_type == 'RADIOBUTTON':
            code = f'  <input id={_id} type="radio" name="{_class}">\n'
            code += f'  <label for={_id}>{_text}</label>\n'
        elif _obj_type == 'SPINNER':
            code = f'  <label for={_id}>{_text}</label>\n'
            code += f'  <select id={_id} name="{_class}"></select>\n'
        elif _obj_type == 'IMAGEVIEW':
            if _class == "":
                code = f'  <img id={_id} alt="{_content_desc}" />\n'
            else:
                code = f'  <img id={_id} class="{_class}" alt="{_content_desc}" />\n'
        else:
            if _class == "":
                _text = _content_desc if _text == "" else _text
                code = f'  <{tag} id={_id}">{_text}</{tag}>\n'
            else:
                _text = _content_desc if _text == "" else _text
                code = f'  <{tag} id={_id} class="{_class}">{_text}</{tag}>\n'
        return code

class Guided_Replay():
    def __init__(self):
        self.chatgpt = ChatGPT()
        self.chatgpt.initialize_chatgpt()

    def infer(self, question):
        response = self.chatgpt.infer(question)

        target_id = None
        recursive_flag = False
        outputs = self.chatgpt.parse_identifier_outputs(response)
        outputs = [o for o in outputs if "id=" in o or "missing" in o]
        if len(outputs) == 0:
            outputs = self.chatgpt.parse_identifier_outputs(response, 'id=')
        if "missing" in outputs:
            recursive_flag = True

        target_id = [o.split("id=")[-1] for o in outputs if "id=" in o]
        # assert len(target_id) > 0, "Error: No target found!"
        if len(target_id) > 0:
            target_id = int(target_id[0])
        else:
            target_id = None
        return recursive_flag, target_id




if __name__ == '__main__':
    ui =  UI('test/step_0_hierarchy.xml')
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
    
    step = """[Tap] ["Settings"]"""
    ui_prompt = """GUI screen: \n{}\n\n""".format(html_code)
    question_prompt = """If I need to {}, which component id should I operate on the GUI? ->\nAnswer:""".format(step)
    
    prompt = title_prompt + example_ui_prompt_1 + example_question_prompt_1 + example_cot_prompt_1 \
                + title_prompt + example_ui_prompt_2 + example_question_prompt_2 + example_cot_prompt_2 \
                + title_prompt + ui_prompt + question_prompt
    prompt = prompt.strip()
    logger.info(prompt)

    gr = Guided_Replay()
    recursive_flag, target_id = gr.infer(prompt)

    logger.info("""The step "{}" infers to the id={} in the GUI screen.""".format( \
        step.strip(), \
        target_id))
    
    """ Visualize"""
    # with open('test/step_1_missing_0_hierarchy.xml', 'r', encoding='utf-8') as f:
    #     vh_data = f.read().encode()
    # vh = view_hierarchy.ViewHierarchy(
    #             screen_width=config.XML_SCREEN_WIDTH,
    #             screen_height=config.XML_SCREEN_HEIGHT)
    # vh.load_xml(vh_data)
    # view_hierarchy_leaf_nodes = vh.get_leaf_nodes()

    # # Visualize the bounding box
    # import cv2
    # img = cv2.imread('test/screenshot-step_1_missing_0.png')
    # img = cv2.resize(img, (config.XML_SCREEN_WIDTH, config.XML_SCREEN_HEIGHT))
    # vis_img = img.copy()
    # for ele in view_hierarchy_leaf_nodes:
    #     x1 = ele.uiobject.bounding_box.x1
    #     y1 = ele.uiobject.bounding_box.y1
    #     x2 = ele.uiobject.bounding_box.x2
    #     y2 = ele.uiobject.bounding_box.y2
    #     utils.draw_label(vis_img, [x1,y1,x2,y2], color=(0, 165, 255), put_text=False)
    # cv2.imwrite(f'vis.jpg', vis_img)
