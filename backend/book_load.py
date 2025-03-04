import json
import os
from Knowledge_Matching.GPT_process_EN import save_knowledge
from Knowledge_Matching.Keyword_Matching_EN import keyword_matching
from Audio_Generation.Openai_Audio_Generation import save_sen_split, story_audio


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


# you should have the book text organized in a json file, with each paragraph as a list of strings
def load_book(title):
    if os.path.exists('../../frontend/static/files/books/' + title + '/' + title + '.json'):
        book = load_json('../../frontend/static/files/books/' + title + '/' + title + '.json')

        # step 1: text process and generate audio narration
        # if you are using English, you can use the following code
        save_sen_split('user', title, True)
        story_audio('user', title, True)
        # if you are using Chinese, you can use the following code
        # save_CN_sen_split(title)
        # CN_story_audio('user', title, True)

        # step 2: knowledge matching
        # if you are using English, you can use the following code
        knowledge_list = keyword_matching(title)
        save_knowledge('user', title, True)
        # if you are using Chinese, import the keyword_matching_CN.py and use the following code
        # knowledge_list = keyword_matching(title)
        # save_knowledge('user', title, True)
    else:
        return None



    
# load_book('Amara and the Bats')