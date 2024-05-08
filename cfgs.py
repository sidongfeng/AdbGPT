from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# CHATGPT CONFIGURATIONS
OPENAI_TOKEN = <YOUR_OPENAI_KEY>
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.2
# MAX_TOKENS = 1000
FREQUENCY_PENALTY = 0.0
PRESENCE_PENALTY = 0.0
INITIAL_SYSTEM_PROMPT = "You are a senior bug report expert."
INITIAL_USER_PROMPT = "Please remember your duty is to understand the bug report and identifying the steps to reproduce the issue."
# PROMPT CONFIGURATIONS
ACTION_LISTS = ['tap', 'double tap', 'input', 'scroll', 'long tap']
RANDOM_INPUT_TEXT = "test"
# UI ENCODING CONFIGURATIONS
CLASS_MAPPING = {
    'TEXTVIEW': 'p',
    'BUTTON': 'button',
    'IMAGEBUTTON': 'button',
    'IMAGEVIEW': 'img',
    'EDITTEXT': 'input',
    'CHECKBOX': 'input',
    'CHECKEDTEXTVIEW': 'input',
    'TOGGLEBUTTON': 'button',
    'RADIOBUTTON': 'input',
    'SPINNER': 'select',
    'SWITCH': 'input',
    'SLIDINGDRAWER': 'input',
    'TABWIDGET': 'div',
    'VIDEOVIEW': 'video',
    'SEARCHVIEW': 'div'
}