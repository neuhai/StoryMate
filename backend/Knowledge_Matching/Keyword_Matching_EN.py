import json, openai
from retry import retry
from sentence_transformers import SentenceTransformer, util
from Text_Process.Text_Process import split_para, split_sentence
from Audio_Generation.Openai_Audio_Generation import audio_gen
import os
from openai import OpenAI
from dotenv import load_dotenv
    
load_dotenv()

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)
MODEL = "gpt-4"

@retry(
    (
        openai.APIError,
        openai.RateLimitError,
        openai.Timeout,
        # openai.ServiceUnavailableError,
        openai.APIConnectionError,
    ),
    tries=50,
    delay=2,
    backoff=2,
    max_delay=20,
)
def evaluate(each_input, stop=None):
    response = openai.chat.completions.create(
        model= MODEL,
        messages=[{"role": "user", "content": each_input}],
        max_tokens=128,
        stop=stop,
    )
    return (response.choices[0].message.content).lower()


def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()

knowledge_dict = load_json(os.path.join(os.path.dirname(__file__), "NGSS_DCI_EN.json"))
knowledge_list = [kg for kg in knowledge_dict.keys()]
sim_dict = load_json(os.path.join(os.path.dirname(__file__), "Similarity_Dict_EN.json"))
# the similarity model can be changed to other models, such as the bge-large-en-v1.5
sim_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def prompting_explanation(word, knowledge):
  Instruction = f"""\
    I need you to provide a short sentence of explanation of a concept for prschoolers aged 3 to 8. 
    I will provide you the concept and the scientific knowldge it related to.
    The explanation should be clear, short and easy to understand.

    For example,
    <Concept>: pull

    <Knowledge>: Pushes and pulls can have different strengths and directions.
    
    <Response>: Pull means to use your hands or strength to bring something closer to you.
    
    <Concept>: {word}

    <Knowledge>: {knowledge}

    <Response>:
    """
  return Instruction

def get_similarity(word, knowledge):
  #Compute embedding for both lists
  embedding_1= sim_model.encode(word, convert_to_tensor=True)
  embedding_2 = sim_model.encode(knowledge, convert_to_tensor=True)
  return util.pytorch_cos_sim(embedding_1, embedding_2)[0].numpy()[0]

def calculate_similarity(word):
    if word.lower() in sim_dict:
        return float(sim_dict[word.lower()]['similarity']), sim_dict[word.lower()]['knowledge']
    else:
        max_sim = -1
        machted_kg = ''
        for knowledge in knowledge_dict:
            similarity = get_similarity(word, knowledge)
            if similarity > max_sim:
                max_sim = similarity
                machted_kg = knowledge
        sim_dict[str(word.lower())] = {
            "similarity": str(max_sim),
            "knowledge": machted_kg
        }
        return max_sim, machted_kg

def knowledge_matching(word):
    sim = 0
    kg = ''
    for knowledge in knowledge_list:
        cur_sim = get_similarity(word, knowledge)
        if cur_sim > sim:
            sim = cur_sim
            kg = knowledge
    return sim, kg

def keyword_matching(user, title, isLibrary):
    if (isLibrary):
        story_content = load_json('../../frontend/static/files/books/' + title + '/' + title + '.json')
        sen_split = load_json('../../frontend/static/files/books/' + title + '/' + title + '_sentence_split.json')
    else:
        story_content = load_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '.json')
        sen_split = load_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_sentence_split.json')
    
    all_knowledge = {}
    gen_result = {}
    for i, para in enumerate(story_content):
        text_tokens = []
        best_sim = 0.27
        keyword = ''
        best_kg = ''
        for sen in sen_split[i]:
            split_sen = split_para(sen)
            for token in split_sen:
                if token['stopword']:
                    continue
                similarity, knowledge = calculate_similarity(token['word'].lower())
                if similarity > best_sim:
                    best_sim = similarity
                    best_kg = knowledge
                    keyword = token['word']
            text_tokens.append(split_sen)
        # print(keyword, best_kg, best_sim)
        if (best_kg != '') and (best_kg not in all_knowledge) or (best_kg in all_knowledge and best_sim > all_knowledge[best_kg]['sim']):
            all_knowledge[best_kg] = {
                'sim': best_sim,
                'sec_id': i,
                'keyword': keyword
            }
        gen_result[i] = {
            'section': text_tokens,
            'section_text': sen_split[i],
            'knowledge': '',
            'keyword': '',
            'use': 0,
            'explanation': ''
        }

    for kg, value in all_knowledge.items():
        gen_result[value['sec_id']]['keyword'] = value['keyword']
        gen_result[value['sec_id']]['knowledge'] = kg
        gen_result[value['sec_id']]['use'] = 1
        gen_result[value['sec_id']]['explanation'] = evaluate(prompting_explanation(value['keyword'], kg))
        match_flag = False
        for i, sen in enumerate(gen_result[value['sec_id']]['section']):
            if (match_flag):
                break
            for j, token in enumerate(sen):
                if token['word'] == value['keyword']:
                    gen_result[value['sec_id']]['section'][i][j]['keyword'] = 1
                    match_flag = True
                    break
    
    '''for key, value in gen_result.items():
        if value['use'] == 0:
            gen_result[key]['section'] = story_content[int(key)]'''

    save_json(os.path.join(os.path.dirname(__file__), "Similarity_Dict_EN.json"), sim_dict)
    if (isLibrary):
        save_json('../../frontend/static/files/books/' + title + '/' + title + ' Gen.json', gen_result)  
    else:
        save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + ' Gen.json', gen_result)  
    return gen_result

def save_split_sentence(title):
    story_content = load_json('../../frontend/static/files/books/' + title + '/' + title + '.json')
    sentences = []
    for para in story_content:
        sen = split_sentence(para[0])
        sentences.append(sen)
    save_json('../../frontend/static/files/books/' + title + '/' + title + '_sentence_split.json', sentences)

def label_gen(title):
    label = load_json('../../frontend/static/files/books/' + title + '/' + 'label.json')
    story_content = load_json('../../frontend/static/files/books/' + title + '/' + title + '.json')
    sen_split = load_json('../../frontend/static/files/books/' + title + '/' + title + '_sentence_split.json')

    gen_result = {}
    for i, para in enumerate(story_content):
        text_tokens = []
        keyword = ''
        best_kg = ''
        for sen in sen_split[i]:
            split_sen = split_para(sen)
            for token in split_sen:
                if token['stopword']:
                    continue
            text_tokens.append(split_sen)
        gen_result[i] = {
            'section': text_tokens,
            'section_text': sen_split[i],
            'knowledge': '',
            'keyword': '',
            'use': 0,
            'explanation': ''
        }
    if not os.path.exists('../../frontend/static/files/books/' + title + '/exp_audio/'):
         os.makedirs('../../frontend/static/files/books/' + title + '/exp_audio/')

    for sec_id, val in label.items():
        gen_result[int(sec_id)]['keyword'] = val['keyword']
        gen_result[int(sec_id)]['knowledge'] = val['DCI']
        gen_result[int(sec_id)]['use'] = 1
        if val['keyword'] != "":
            gen_result[int(sec_id)]['explanation'] = evaluate(prompting_explanation(val['keyword'], val['DCI']))
            audio_gen(gen_result[int(sec_id)]['explanation'], '../../frontend/static/files/books/' + title + '/exp_audio/exp_audio' + sec_id + '.mp3')
        else:
            gen_result[int(sec_id)]['explanation'] = ""
        match_flag = False
        for i, sen in enumerate(gen_result[int(sec_id)]['section']):
            if (match_flag):
                break
            for j, token in enumerate(sen):
                if token['word'] == val['keyword']:
                    gen_result[int(sec_id)]['section'][i][j]['keyword'] = 1
                    match_flag = True
                    break

    save_json('../../frontend/static/files/books/' + title + '/' + title + ' Gen.json', gen_result)  


def gen_sent_split():
    lib_book = [
        "Amara and the Bats",
        "Fairy Science",
        "Oscar and the CRICKET",
        "PENNY, the Engineering Tail of the Fourth Little Pig"
    ]
    for b in lib_book:
        save_split_sentence(b)


# gen_sent_split()

# label_gen('Amara and the Bats')
# save_split_sentence("Water Cycle Earth Science")
# keyword_matching('user', "Water Cycle Earth Science", True)
