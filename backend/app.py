from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import json
import base64
import os
import threading
from urllib.parse import unquote
from PIL import Image
from io import BytesIO
from Knowledge_Matching.GPT_process_CN import knowledge_keyword_gen, conv_gen, chat_gen, save_knowledge, get_book_discipline, gen_greet, answer_greet, generate_sum_conv, generate_sum_chat
from Text_Process.Text_Process import split_sentence
from Knowledge_Matching.Keyword_Matching_EN import keyword_matching
import asyncio

app = Flask(__name__, static_folder = './static')
app.secret_key = 'storytelling'

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

# Sample user data (replace with your actual user authentication mechanism)
users = [
    {'username': 'user1', 'password': 'pass1'},
    {'username': 'user2', 'password': 'pass2'},
    {'username': 'user3', 'password': 'pass3'},
    {'username': 'user4', 'password': 'pass4'},
    {'username': 'user5', 'password': 'pass5'},
    {'username': 'user6', 'password': 'pass6'},
    {'username': 'user7', 'password': 'pass7'},
    {'username': 'user8', 'password': 'pass8'},
    {'username': 'Emma', 'password': 'emma'},
    {'username': 'user', 'password': 'pass'}
]

'''
current_user = {
    'username': '',
    'password': ''
}
'''

LibraryBooks = [
    "amara and the bats",
    "oscar and the cricket",
    "penny, the engineering tail of the fourth little pig",
    "fairy science",
    "海边度假",
    "你想种什么"
]

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not os.path.isdir('../../frontend/static/files/' + username):
        os.makedirs('../../frontend/static/files/' + username)
    if not os.path.exists('../../frontend/static/files/' + username + '/dashboardData.json'):
        stat = {
            "reading": "", 
            "bookStat": {},
            "scienceStat": {
                "Discipline": {}, 
                "subDisc": {}
            }, 
            "readingRecord": {
                "date":{
                    "year": "",
                    "month": "",
                    "day": ""
                },
                "todayBook": [],
                "totalBook":[],
                "todayRead": 0, "todayTime": 0, "totalRead": 0, "totalTime": 0
            }, 
            "weekTime": {"Sun": 0, "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0}, 
            "upload": []
        }
        save_json('../../frontend/static/files/' + username + '/dashboardData.json', stat)
    if not os.path.exists('../../frontend/static/files/' + username + '/persona.json'):
        persona = {
            "isFill": 0,
            "age": "",
            "name": "",
            "interest": ""
        }
        save_json('../../frontend/static/files/' + username + '/persona.json', persona)
    session['username'] = username
    session['password'] = password
    # Check if the provided username and password are valid
    if any(user['username'] == username and user['password'] == password for user in users):
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/library')
def library():
    if 'username' in session:
        return render_template('library.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/bookRead')
def bookRead():
    if 'username' in session:
        return render_template('bookRead.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/bookDetail')
def bookDetail():
    if 'username' in session:
        return render_template('bookDetail.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/customize')
def customize():
    if 'username' in session:
        return render_template('customize.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/upload')
def upload():
    if 'username' in session:
        return render_template('upload.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/custBookDetail')
def custBookDetail():
    if 'username' in session:
        return render_template('custBookDetail.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/information')
def information():
    if 'username' in session:
        return render_template('information.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/greeting')
def greeting():
    if 'username' in session:
        return render_template('greeting.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/api/user', methods=['POST'])
def user():
    if 'username' in session:
        return jsonify({'username': session['username'], 'password': session['password']})
    
@app.route('/api/persona', methods=['POST'])
def persona():
    data = request.json
    user = data.get('username')
    persona_info = load_json('../../frontend/static/files/' + user + '/persona.json')
    return jsonify(persona_info)

@app.route('/api/personaUpdate', methods=['POST'])
def persona_update():
    data = request.json
    user = data.get('username')
    persona_info = data.get('persona')
    save_json('../../frontend/static/files/' + user + '/persona.json', persona_info)
    return jsonify('success')

@app.route('/api/gen', methods=['POST'])
async def generation1():
    data = request.json
    user = data.get('username')
    title = unquote(data.get('title'))
    print(title)
    isLibrary = True
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False
    print(title, isLibrary)
    gpt_gen = knowledge_keyword_gen(user, title, isLibrary)
    if not os.path.exists('../../frontend/static/files/' + user + '/' + title):
        os.makedirs('../../frontend/static/files/' + user + '/' + title)
    if not os.path.exists('../../frontend/static/files/' + user + '/' + title + '/conversation'):
        os.makedirs('../../frontend/static/files/' + user + '/' + title + '/conversation')
    if not os.path.exists('../../frontend/static/files/' + user + '/' + title + '/progress'):
        os.makedirs('../../frontend/static/files/' + user + '/' + title + '/progress') 
    if not os.path.exists('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json'):
        if isLibrary:
            save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', load_json('../../frontend/static/files/books/' + title + '/' + title + '_knowledge_dict.json'))
        else:
            save_knowledge(user, title, isLibrary)
    knowledge_dict = load_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    dashboard_data = load_json('../../frontend/static/files/' + user + '/dashboardData.json')
    
    dashboard_data['reading'] = title
    save_json('../../frontend/static/files/' + user + '/dashboardData.json', dashboard_data)

    return jsonify({
        'generation': gpt_gen,
        'answerProgress': knowledge_dict
    })

@app.route('/api/conv', methods=['POST'])
async def generation2():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False
    return jsonify(conv_gen(id, title, user, isLibrary))

@app.route('/api/chat', methods=['POST'])
async def generation3():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    response = data.get('response')
    answerProgress = load_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    answerProgress[id]['answer'] = True
    save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', answerProgress)
    return jsonify(chat_gen(id, title, user, response))

@app.route('/api/greet', methods=['POST'])
async def greet_intro():
    data = request.json
    user = data.get('username')
    title = data.get('title')
    return jsonify(gen_greet(user))

@app.route('/api/answer', methods=['POST'])
async def answer_intro():
    data = request.json
    user = data.get('username')
    response = data.get('response')
    id = data.get('id')
    title = data.get('title')
    isLibrary = True
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False

    return jsonify(answer_greet(user, response, id, title, isLibrary))

@app.route('/api/sum', methods=['POST'])
async def sum_conv():
    data = request.json
    user = data.get('username')
    title = data.get('title')
    isLibrary = True
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False
    return jsonify(generate_sum_conv(title, user, isLibrary))

@app.route('/api/answer_sum', methods=['POST'])
def sum_chat():
    data = request.json
    user = data.get('username')
    title = data.get('title')
    id = data.get('id')
    response = data.get('response')
    return jsonify(generate_sum_chat(user, title, id, response))

@app.route('/api/continue', methods=['POST'])
def save_progress():
    data = request.json
    user = data.get('username')
    id = str(data.get('id'))
    title = unquote(data.get('title'))
    html = data.get('html')
    isUpdate = data.get('dash_stat_flag')
    isEnd = data.get('end_flag')
    save_json('../../frontend/static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json', html)
    dash_stat = load_json('../../frontend/static/files/' + user + '/dashboardData.json')
    knowledge_dict = load_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    if knowledge_dict[id]['dash'] == False:
        knowledge_dict[id]['dash'] = True
        if title not in dash_stat["bookStat"]:
            if title.lower() in LibraryBooks:
                src = '.../../frontend/static/files/books/' + title + '/cover.jpg'
            else:
                src = '.../../frontend/static/files/' + user + '/' + title + 'cover.jpg'
            dash_stat["bookStat"][title] = {
                'coverSrc': src,
                'count': len(knowledge_dict),
                'records': {}
            }
        dash_stat["bookStat"][title]['records'][id] = {
            "concept": knowledge_dict[id]['keyword'],
            "knowledge": knowledge_dict[id]['knowledge'],
            "topic": knowledge_dict[id]['topic'],
            "progress": isEnd
        }
        if knowledge_dict[id]['discipline'] not in dash_stat["scienceStat"]['Discipline']:
            dash_stat["scienceStat"]['Discipline'][knowledge_dict[id]['discipline']] = 1
        else:
            dash_stat["scienceStat"]['Discipline'][knowledge_dict[id]['discipline']] += 1
        if knowledge_dict[id]['sub-disc'] not in dash_stat["scienceStat"]['subDisc']:
            dash_stat["scienceStat"]['subDisc'][knowledge_dict[id]['sub-disc']] = 1
        else:
            dash_stat["scienceStat"]['subDisc'][knowledge_dict[id]['sub-disc']] += 1
    else:
        dash_stat["bookStat"][title]['records'][id]['progress'] = isEnd
    
    save_json('../../frontend/static/files/' + user + '/dashboardData.json', dash_stat)
    save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', knowledge_dict)
    return jsonify("success")

@app.route('/api/review', methods=['POST'])
def send_html():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    if os.path.exists('../../frontend/static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json'):
        return jsonify(load_json('../../frontend/static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json'))
    else:
        return jsonify('knowledge not saved')

@app.route('/api/stat', methods=['POST'])
def send_stat():
    data = request.json
    user = data.get('username')
    return jsonify(load_json('../../frontend/static/files/' + user + '/dashboardData.json'))

@app.route('/api/uploadHistory', methods=['POST'])
def upload_history():
    data = request.json
    user = data.get('username')
    return jsonify(load_json('../../frontend/static/files/' + user + '/dashboardData.json')['upload'])

@app.route('/api/uploadCover', methods=['POST'])
def upload_cover():
    data = request.json
    user = data.get('username')
    cover = data.get('img')
    title = unquote(data.get('title'))

    _, encoded_data = cover.split(',', 1)
    image_data = base64.b64decode(encoded_data)

    image = Image.open(BytesIO(image_data))
    image = image.convert('RGB')

    if not os.path.isdir('../../frontend/static/files/' + user + '/' + title):
        os.mkdir('../../frontend/static/files/' + user + '/' + title)
    image.save('../../frontend/static/files/' + user + '/' + title + '/cover.jpg')

    return jsonify("success")

@app.route('/api/uploadPage', methods=['POST'])
def upload_page():
    data = request.json
    user = data.get('username')
    pages = data.get('pageData')
    title = unquote(data.get('title'))
    if not os.path.isdir('../../frontend/static/files/' + user + '/' + title + '/conversation'):
        os.mkdir('../../frontend/static/files/' + user + '/' + title + '/conversation')
    if not os.path.isdir('../../frontend/static/files/' + user + '/' + title + '/progress'):
        os.mkdir('../../frontend/static/files/' + user + '/' + title + '/progress')
    if not os.path.isdir('../../frontend/static/files/' + user + '/' + title + '/audio'):
        os.mkdir('../../frontend/static/files/' + user + '/' + title + '/audio')
    if not os.path.isdir('../../frontend/static/files/' + user + '/' + title + '/pages'):
        os.mkdir('../../frontend/static/files/' + user + '/' + title + '/pages')
    
    paragraphs = []
    sentences = []
    for i, page in enumerate(pages[1:]):
        para = page['text']
        sen = split_sentence(para)
        sentences.append(sen)
        paragraphs.append(para)
       
        _, encoded_data = page['img'].split(',', 1)
        image_data = base64.b64decode(encoded_data)

        image = Image.open(BytesIO(image_data))
        image = image.convert('RGB')
        image.save('../../frontend/static/files/' + user + '/' + title + '/pages/page' + str(i + 1) + '.jpg')

    save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '.json', paragraphs)
    save_json('../../frontend/static/files/' + user + '/' + title + '/' + title + '_sentence_split.json', sentences)

    # 1. match knowledge
    gen_result = keyword_matching(user, title, False)
    
    # 2. calculate knowledge stat
    save_knowledge(user, title, False)
    disciplines = get_book_discipline(user, title, False)

    # 3. update dashboard data
    dashboard_data = load_json('../../frontend/static/files/' + user + '/dashboardData.json')
    
    dashboard_data['upload'].append({
            "title": title,
            "cover": '../../frontend/static/files/' + user + '/' + title + '/cover.jpg',
            "tags": disciplines
        })
    save_json('../../frontend/static/files/' + user + '/dashboardData.json', dashboard_data)

    return jsonify(disciplines)


@app.route('/api/timer', methods=['POST'])
def update_time():
    data = request.json
    print(data)
    user = data.get('username')
    duration = data.get('duration')
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    title = data.get('title')
    dashboard_stat = load_json('../../frontend/static/files/' + user + '/dashboardData.json')
    new_day_flag = 0
    if year != dashboard_stat['readingRecord']['date']['year']:
        dashboard_stat['readingRecord']['date']['year'] = year
        new_day_flag = 1
    if month != dashboard_stat['readingRecord']['date']['month']:
        dashboard_stat['readingRecord']['date']['month'] = month
        new_day_flag = 1
    if day != dashboard_stat['readingRecord']['date']['day']:
        dashboard_stat['readingRecord']['date']['day'] = day
        new_day_flag = 1
    if new_day_flag == 0:
        dashboard_stat['readingRecord']['todayTime'] += duration
        if title not in dashboard_stat['readingRecord']['todayBook']:
            dashboard_stat['readingRecord']['todayBook'].append(title)
    elif new_day_flag == 1:
        dashboard_stat['readingRecord']['todayTime'] = int(duration)
        dashboard_stat['readingRecord']['todayBook'] = [title]
    dashboard_stat['readingRecord']['totalTime'] += int(duration)
    if title not in dashboard_stat['readingRecord']['totalBook']:
        dashboard_stat['readingRecord']['totalBook'].append(title)
    dashboard_stat['readingRecord']['todayRead'] = len(dashboard_stat['readingRecord']['todayBook'])
    dashboard_stat['readingRecord']['totalRead'] = len(dashboard_stat['readingRecord']['totalBook'])
    save_json('../../frontend/static/files/' + user + '/dashboardData.json', dashboard_stat)
    return jsonify('success')

if __name__ == '__main__':        
    app.run(host='0.0.0.0', port=5500)
