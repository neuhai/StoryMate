import json, openai
from retry import retry
from sentence_transformers import SentenceTransformer, util
from Text_Process.Text_Process import split_para_CN, split_CN_sentences
from Audio_Generation.Baidu_Audio_Generation import audio_gen
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
        json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()

knowledge_dict = load_json("./NGSS_DCI_CN.json")
knowledge_list = [kg for kg in knowledge_dict.keys()]

'''If replaec sim dict with cosine similarity, replace all the Similarity_Dict.json files with CosSimilarity_Dict.json'''
sim_dict = load_json('./Similarity_Dict.json')
sim_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def prompting_explanation(word, knowledge):
  Instruction = f"""\
请你为3到8岁的儿童提供一个对科学概念的简短解释。我会提供给你这个科学概念以及与之相关的科学知识。
你提供的解释应该专注于这一个科学概念，并且这个解释需要清晰、简短、易于儿童的理解，解释的句子长度不超过40个字。
请确保解释中出现的概念与我提供的概念的词语是一致的。

例如，
<概念>: 拉
<知识>: 推和拉可以有不同的力量和方向。
<回答>: 拉是指用你的手或力量把东西拉近你。

<概念>: {word}
<知识>: {knowledge}
<回答>:
"""
  
  # print(Instruction)
  return Instruction

def prompting_matching(word, knowledge):
  Instruction = f"""\
请你判断给定的一个概念（词语）和一个科学知识是否相关。
我会给你一个概念，和一个对应的科学知识，概念和知识可能是相关的，但也可能没有关系。
1. 如果这个概念的词语不是第一层词汇或第二层词汇(tier 1 or tier 2 vocabulary)，且不是一个具体的名词，动词，形容词，并且对于3-8岁的儿童来说不常见， 直接在回答中输出‘0’
2. 如果这个概念和知识相关，回答中输出‘1’，反之则输出‘0’

例如，
<概念>: 拉
<知识>: 推和拉可以有不同的力量和方向。
<回答>: 1

<概念>: 地说
<知识>: 风和水可以改变地形
<回答>: 0

<概念>: 落日余晖
<知识>: 可以观察、描述和预测日出和日落的季节性模式。
<回答>: 1

<概念>: 哈哈大笑
<知识>: 更大的推力或拉力会使物体更加快速或减速
<回答>: 0

<概念>: 关子
<知识>: 植物依靠动物传粉或传播他们的种子
<回答>: 0

<概念>: 种
<知识>: 同一种植物或动物的个体在许多方面可以被识别为相似，但也会有很多不同。
<回答>: 0

<概念>: 一块
<知识>: 可以用一小套零件构建出多种不同的物体。
<回答>: 0

<概念>: {word}
<知识>: {knowledge}
<回答>:
"""
  
  # print(Instruction)
  return Instruction

def get_similarity(word, knowledge):
  #Compute embedding for both lists
  embedding_1= sim_model.encode(word, convert_to_tensor=True)
  embedding_2 = sim_model.encode(knowledge, convert_to_tensor=True)
  return util.pytorch_cos_sim(embedding_1, embedding_2)[0].numpy()[0]

def calculate_similarity(word):
    if word in sim_dict:
        return float(sim_dict[word]['similarity']), sim_dict[word.lower()]['knowledge'], knowledge_dict[sim_dict[word.lower()]['knowledge']]["Statements"][0].split('-')[0]
    else:
        max_sim = -1
        matched_kg = ''
        matched_level = ''
        for knowledge in knowledge_dict:
            similarity = get_similarity(word, knowledge)
            if similarity > max_sim:
                max_sim = similarity
                matched_kg = knowledge
                matched_level = knowledge_dict[knowledge]["Statements"][0].split('-')[0]
        sim_dict[str(word)] = {
            "similarity": str(max_sim),
            "knowledge": matched_kg,
            "level": matched_level
        }
        return max_sim, matched_kg, matched_level

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


    if not os.path.exists('../../frontend/static/files/books/' + title + '/exp_audio/'):
        os.makedirs('../../frontend/static/files/books/' + title + '/exp_audio/')

    for i, para in enumerate(story_content):
        text_tokens = []
        best_sim = 0.6
        best_level = ''
        keyword = ''
        best_kg = ''
        for sen in sen_split[i]:
            split_sen = split_para_CN(sen)
            for token in split_sen:
                if token['stopword']:
                    continue
                similarity, knowledge, level = calculate_similarity(token['word'].lower())
                if similarity > best_sim:
                    best_sim = similarity
                    best_level = level
                    best_kg = knowledge
                    keyword = token['word']
            text_tokens.append(split_sen)
        # print(keyword, best_kg, best_sim)
        if (best_kg != '') and (best_kg not in all_knowledge) or (best_kg in all_knowledge and best_sim > all_knowledge[best_kg]['sim']):
            if evaluate(prompting_matching(keyword, best_kg)) == '1':
                all_knowledge[best_kg] = {
                    'sim': best_sim,
                    'level': best_level,
                    'sec_id': i,
                    'keyword': keyword,
                    'cog': 0
                }
        gen_result[i] = {
            'section': text_tokens,
            'section_text': sen_split[i],
            'knowledge': '',
            'keyword': '',
            'use': 0,
            'sim': 0,
            'level': '',
            'cog': 1,
            'explanation': ''
        }

    sorted_all_knowledge = sorted(all_knowledge.items(), key=lambda x: x[1]['sim'], reverse=True)
    
    third = len(sorted_all_knowledge) // 3

    for i, (key, value) in enumerate(sorted_all_knowledge):
        if i < third:
            all_knowledge[key]['cog'] = 1
        elif i < 2 * third:
            all_knowledge[key]['cog'] = 2
        else:
            all_knowledge[key]['cog'] = 3

    for kg, value in all_knowledge.items():
        gen_result[value['sec_id']]['keyword'] = value['keyword']
        gen_result[value['sec_id']]['knowledge'] = kg
        gen_result[value['sec_id']]['use'] = 1
        gen_result[value['sec_id']]['sim'] = value['sim']
        gen_result[value['sec_id']]['level'] = value['level']
        gen_result[value['sec_id']]['cog'] = value['cog']
        gen_result[value['sec_id']]['explanation'] = evaluate(prompting_explanation(value['keyword'], kg))
        audio_gen(gen_result[value['sec_id']]['explanation'], '../../frontend/static/files/books/' + title + '/exp_audio/exp_audio' + str(value['sec_id']) + '.mp3')
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

    save_json('./Similarity_Dict.json', sim_dict)
    if (isLibrary):
        save_json('../../frontend/static/files/books/' + title + '/' + title + ' Gen.json', gen_result)  
    else:
        save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + ' Gen.json', gen_result)  
    return gen_result

# keyword_matching('user', "海边度假", True)

def save_split_CN_sentence(title):
    story_content = load_json('../../frontend/static/files/books/' + title + '/' + title + '.json')
    sentences = []
    for para in story_content:
        sen = split_CN_sentences(para[0])
        sentences.append(sen)
    save_json('../../frontend/static/files/books/' + title + '/' + title + '_sentence_split.json', sentences)

# save_split_CN_sentence("你想种什么")

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


# label_gen('Amara and the Bats')
