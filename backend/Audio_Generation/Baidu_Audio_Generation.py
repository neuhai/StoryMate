from aip import AipSpeech
import os
import json

APP_ID = os.environ["APP_ID"]
ak = os.environ["CLOUD_SDK_AK"]           
sk = os.environ["CLOUD_SDK_SK"] 

client = AipSpeech(APP_ID, ak, sk)

def audio_gen(text, path):
    synth_context = client.synthesis(text,'zh',1,{
        'spd' : 5,  #语速(0-9)
        'vol' : 5,  #音量(0-9)
        'pit' : 5,  #音调(0-9)
        'per' : 5,  #发音人：度丫丫
    })
    # 确定合成内容已生成，因为生成错误会返回字典类型报错
    if not isinstance(synth_context, dict):
        with open(path, 'wb') as f:
            f.write(synth_context)
        return 0
    else:
        return -1

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data


def audio_story_gen(user, title, text, para, sec, isLibrary):
    if os.path.exists("./static/files/books/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"):
        return
    if isLibrary:
        path = "./static/files/books/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"
    else:
        path = "./static/files/" + user + "/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"
    if text != '':
        print(audio_gen(text, path))

def CN_story_audio(user, title, isLibrary):
    if isLibrary:
        story = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    else:
        story = load_json('./static/files/' + user + '/' + title + '/' + title + '_sentence_split.json')
    for i, para in enumerate(story):
        for j, sec in enumerate(para):
            audio_story_gen(user, title, sec, i, j, isLibrary)

# CN_story_audio("user", "你想种什么", True)