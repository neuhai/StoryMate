import openai
import json
import re
import os
from retry import retry
from sentence_transformers import SentenceTransformer, util
from Text_Process import split_para
from Keyword_Matching_EN import keyword_matching
from BaiDu_Audio_Generation import audio_gen
from openai import OpenAI
import shutil
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
    response = client.chat.completions.create(
        model= MODEL,
        messages=[{"role": "user", "content": each_input}],
        max_tokens=512,
        stop=stop,
    )
    return (response.choices[0].message.content).lower()

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
def conversation(message, stop=None):
    response = client.chat.completions.create(
        model = MODEL,
        messages = message,
        max_tokens = 512,
        stop = stop,
    )
    return (response.choices[0].message.content).lower()

def prompting_kg_matching(story):
  Instruction1 = f"""\
    I need you to match a story section with a piece of scientific knowledge.
    I will provide you with a short section of a story delimited by triple quotes, and a list of scientific knowledge.
    Please follow these steps:
    1. Read through the list of scientific knowledge provided.
    2. Read through the story section.
    3. Rank the knowledge list according to each knowledge's relevancy with the story narrative.
    If the story narrative, or a word or phrase in the story text is closely connected with a piece of knowledge, the piece of knowledge should rank higher.
    4. Return the most relevant piece of knowledge from the Scientific Knowledge List.

    [Scientific Knowledge List]:
    1. Pushes and pulls can have different strengths and directions.
    2. Pushing or pulling on an object can change the speed or direction of its motion and can start or stop it.
    3. When objects touch or collide, they push on one another and can change motion.
    4. A bigger push or pull makes things speed up or slow down more quickly.
    5. A situation that people want to change or create can be approached as a problem to be solved through engineering. Such problems may have many acceptable solutions.
    6. Sunlight warms Earth’s surface.
    7. All animals need food in order to live and grow. They obtain their food from plants or from other animals. Plants need water and light to live and grow.
    8. Weather is the combination of sunlight, wind, snow or rain, and temperature in a particular region at a particular time. People measure these conditions to describe and record the weather and to notice patterns over time.
    9. Plants and animals can change their environment.
    10. Things that people do to live comfortably can affect the world around them. But they can make choices that reduce their impacts on the land, water, air, and other living things.
    11. Living things need water, air, and resources from the land, and they live in places that have the things they need. Humans use natural resources for everything they do.
    12. Some kinds of severe weather are more likely than others in a given region. Weather scientists forecast severe weather so that the communities can prepare for and respond to these events.
    13. Asking questions, making observations, and gathering information are helpful in thinking about problems.
    14. Designs can be conveyed through sketches, drawings, or physical models. These representations are useful in communicating ideas for a problem’s solutions to other people.
    15. Sound can make matter vibrate, and vibrating matter can make sound.
    16. Objects can be seen if light is available to illuminate them or if they give off their own light.
    17. Some materials allow light to pass through them, others allow only some light through and others block all the light and create a dark shadow on any surface beyond them, where the light cannot reach. Mirrors can be used to redirect a light beam. (Boundary: The idea that light travels from place to place is developed through experiences with light sources, mirrors, and shadows, but no attempt is made to discuss the speed of light.)
    18. People also use a variety of devices to communicate (send and receive information) over long distances.
    19. All organisms have external parts. Different animals use their body parts in different ways to see, hear, grasp objects, protect themselves, move from place to place, and seek, find, and take in food, water and air. Plants also have different parts (roots, stems, leaves, flowers, fruits) that help them survive and grow.
    20. Adult plants and animals can have young. In many kinds of animals, parents and the offspring themselves engage in behaviors that help the offspring to survive.
    21. Animals have body parts that capture and convey different kinds of information needed for growth and survival. Animals respond to these inputs with behaviors that help them survive. Plants also respond to some external inputs.
    22. Young animals are very much, but not exactly like, their parents. Plants also are very much, but not exactly, like their parents.
    23. Individuals of the same kind of plant or animal are recognizable as similar but can also vary in many ways.
    24. Patterns of the motion of the sun, moon, and stars in the sky can be observed, described, and predicted.
    25. Seasonal patterns of sunrise and sunset can be observed, described, and predicted.
    26. Different kinds of matter exist and many of them can be either solid or liquid, depending on temperature. Matter can be described and classified by its observable properties.
    27. Different properties are suited to different purposes.
    28. A great variety of objects can be built up from a small set of pieces.
    29. Heating or cooling a substance may cause changes that can be observed. Sometimes these changes are reversible, and sometimes they are not.
    30. Plants depend on water and light to grow.
    31. Plants depend on animals for pollination or to move their seeds around.
    32. There are many different kinds of living things in any area, and they exist in different places on land and in water.
    33. Some events happen very quickly; others occur very slowly, over a time period much longer than one can observe.
    34. Wind and water can change the shape of the land.
    35. Maps show where things are located. One can map the shapes and kinds of land and water in any area.
    36. Water is found in the ocean, rivers, lakes, and ponds. Water exists as solid ice and in liquid form.
    37. Because there is always more than one possible solution to a problem, it is useful to compare and test designs.
    38. A situation that people want to change or create can be approached as a problem to be solved through engineering.
    39. Before beginning to design a solution, it is important to clearly understand the problem.

    For example,
    <Story narrative>:
    The little snowplow braced himself and PULLED.

    <Response>:
    Pushes and pulls can have different strengths and directions.

    <Story narrative>:
    '''
    {story}
    '''
    <Response>:
    """
  return Instruction1

def prompting_kword(story, knowledge):
  Instruction2 = f"""\
    Please identify a key word from a short story section.
    You'll be provided with a short story section enclosed in triple quotes and a piece of scientific knowledge.

    Here are the steps to follow:
    1. Read the story section provided.
    2. Review the scientific knowledge provided.
    3. From all the words in the story text, identify a word from the story text that is semantically related to the provided scientific knowledge.
    The chosen word should be suitable for educating children aged 3 to 6 about the related knowledge.
    4. Check if the identified word is from the story text. If not, repeat step 3.
    5. For the identified word, generate a short explanation of the word in one sentence. The explanation should be friendly to preschoolers aged 3 to 6. The explanation should follow this format: [key word] means [explanation]
    6. Return the identified word and explanation. If there is no word that meets the criteria, respond with 'not identified.'

    For example,
    <Story Text>:
    '''The little snowplow braced himself and PULLED.'''

    <Knowledge>:
    Pushes and pulls can have different strengths and directions.
    
    <Response>:
    PULLED
    Pull means to use your hands or strength to bring something closer to you.
    
    <Story Text>:
    '''
    {story}
    '''

    <Knowledge>: {knowledge}

    <Response>:
    """
  return Instruction2

def prompt_greeting():
    Instruction = f"""\
现在你是一个与5-8岁儿童互动的对话的友善的伙伴，名叫智星，你现在需要给小朋友介绍自己，和接下来的互动讲故事活动，并通过互动来得到小朋友的背景信息。
你和孩子将轮流进行对话，每轮你说话后，等待小朋友的回复，再进行下一轮。
你一共需要进行三轮对话，每一轮对话问一个问题，请你就按照我提供的这三个问题进行问话：
问题1: 小朋友你好！我叫智星，是你的学习伙伴。我可以给你讲很多有趣的故事哦。你可以告诉我你的名字吗？
问题2: 你好[小朋友的名字]，非常高兴认识你！你今年几岁了呀？
问题3: [对小朋友的回答做出肯定、积极的回复]你有什么喜欢的话题吗？比如太空、公主、恐龙或者是汽车呢？

请遵循以下的步骤：
1. 问出问题1
2. 问出问题2
3. 回复小朋友并问出问题3
4. 认同小朋友所说的喜欢的话题，但不要和小朋友说我们会阅读和他/她感兴趣的内容相关的故事，因为选择的故事不一定和小朋友感兴趣的内容相关。结束互动，并向小朋友介绍接下来的互动讲故事活动：我们接下来会进入故事阅读模式，你可以通过点击屏幕右下角的按钮切换到学习模式。在学习模式里，我们会一起探索科学知识，你可以通过点击屏幕上的按钮回答自己的答案，准备好了吗？开始阅读吧！

如果小朋友不愿意回答相关的信息，不用继续问。
每次生成一个问题，如果互动没有结束，请按照以下json格式，注意json字典里key和value应使用双引号：
{{
    "greeting_content": [你和小朋友的互动，包括你对小朋友问题的回复，或者新的问题]
}}

如果互动结束，请在生成最后一个问题或反馈的时候，按照以下json格式返回信息，注意json字典里key和value应使用双引号：
{{
    "name": [小朋友的名字，格式为字符串，如果没有，就返回空字符串""],
    "age": [小朋友的年龄，一个数字，比如‘5’，格式为字符串，如果没有，就返回空字符串""],
    "interest": [小朋友感兴趣的东西，格式为字符串，如果没有，就返回空字符串""],
    "greeting_content": [你最终的回复，格式为字符串],
    "end": [值为true，确定你和小朋友的互动结束]
}}
现在，开始对话：
"""
    return Instruction

def prompt_conv(title, story, info):
    Instruction4 = f"""\
现在你是一个与3-8岁儿童一起阅读故事书的对话的友善的伙伴，名叫智星，你需要通过提问和提供回应来与孩子互动，培养他/她对故事内容的阅读理解能力。
以下是孩子的个人信息：
{info}

请遵循以下要求与孩子进行互动：
1. 你和孩子将轮流对话，每轮生成一个问题，总问题数不超过三个。如果孩子对知识有很好理解，应减少问题数量。
2. 你的问题和回复需匹配孩子的年龄，风格亲切、生活化。对5-6岁的孩子，语言应简单易懂、生动有趣，避免使用复杂词汇和冗长解释。提问时自然些，不要让孩子觉得是在完成任务。
3. 问题和回复应包含孩子感兴趣的话题。
4. 当孩子回应时，请做出回复。回复应包括：1). 判断回答的正确性，2). 友好、鼓励的反馈，3). 对前一个问题答案的解释，4). 如果对话未结束，转向下一个问题。
5. 如果孩子回答不正确，用引导方法启发他们思考。如果孩子没有回应，可简单回复“没关系，你需要更多时间思考”并解释，或“我没听清你的回答”并重复问题。
6. 保持回应简洁，每部分不超过15个字，尽量使用简单词汇，避免使用专业的词汇，比如‘液态’，‘可逆’等，如果你必须提到专业词汇，请务必用通俗、有趣的语言解释这个词汇，保证孩子可以听懂你在说什么。

对于你生成的第一个问题，请按照以下json格式，注意json字典里key和value应使用双引号：
{{
    "greeting": [介绍自己，（我是智星/我的名字是智星）向孩子问好并开始对话，例如‘你好呀！’，格式为字符串],
    "question": [第一个问题。只包含一个问题。格式为字符串]
}}

如果不是第一个问题，你的回应格式应按照以下json格式，注意json字典里key和value应使用双引号：
{{
    "judgement": [对孩子回答的判断：correct/not correct/partially correct。格式为字符串],
    "feedback": [对孩子回答的反馈，应友好且具有鼓励性，例如‘做得好！’，‘你说的完全正确’，‘没关系！’等。格式为字符串],
    "explanation": [根据孩子的回答对前一个问题的相关知识进行简单易懂的解释，不超过15个字，格式为字符串],
    "transition": [从解释到问题或结束对话的转折，例如‘让我们继续读！’等。不要在transition中问问题。格式为字符串],
    "question": [新问题，只包含一个问题。如果是最后一个反馈，那么这个字符串应该为空。格式为字符串],
    "end": [是否是最后一个问题：true/false]
}}
如果对话结束，你在提供最后的反馈而不再问新问题时，请将'question'部分留空（""），并将'end'部分设为'true'。
请注意，当'feedback'、'explanation'、'transition'和'question'的文本结合在一起时，应成为一个流畅的回复。

请注意，故事文本的内容是关于故事情节的，和小朋友的自身经历不一定相关。例如，故事中提到去海边玩耍，是故事的情节，而不是小朋友本人去到了海边玩耍。

<故事标题>: {title}
<故事文本>:
```
{story}
```

现在，开始对话：
"""

    return Instruction4


def prompt_sum1(story):
    Instruction1 = f"""\
请你根据一则故事，总结出这段故事的主要内容。总结的内容需要贴近故事情节，并且要有能够教育5-8岁小朋友的道理，字数长度不超过100字。
当你完成内容总结后，根据这部分内容，匹配一则可以培养小朋友科学思维的科学知识。

让我们来一步步思考，首先请根据故事文本生成你的总结
<故事文本>: ```
{story}
```
<总结>: 
"""
    return Instruction1

def prompt_sum2(sum, science):
    Instruction2 = f"""\
这是你基于故事内容生成的总结: {sum}
现在，在你生成的故事内容总结的基础上，有以下的科学知识：
{science}

请你从以上的科学知识中选择一则最贴近故事总结/要教小朋友道理的知识，这个科学知识需要能够结合你的总结来培养小朋友一些科学思维的能力。
<知识>: 
"""
    return Instruction2

def prompt_sum_conv(info, title, sum, knowledge):
    Instruction3 = f"""\
现在你是一个与5-8岁儿童互动的对话的友善的伙伴，你需要通过提问和提供回应来与孩子互动，现在小朋友已经阅读完书本的内容了，你需要围绕故事大纲和对应的科学思维知识，来将这则知识与故事大纲和孩子感兴趣的东西教给他。
以下是孩子的个人信息：
{info}

请遵循以下的要求：
1. 你和孩子将轮流进行对话，每轮生成一个问题。在对话中，用适合孩子语言的问题序列进行提问。总问题数不应超过三个。如果孩子表现出对知识的很好理解，应减少问题数量。
2. 你的问题与回复需要与孩子信息中的年龄相匹配，你的对话风格需要亲切，生活化。对于年纪越小的小朋友，问题与回复要更加简单，字数需要更少，能让对应年龄的小朋友听懂，语言要更加生动，有趣。比如，对于3-5岁的小朋友，你的语言要简单易懂，不能使用复杂的词汇和冗长的解释。另外，在提问题时，尽量自然，不要让小朋友觉得是在完成任务，你可以表述为和小朋友一起探索科学的世界。
3. 你的问题与回复需要包含孩子个人信息中感兴趣的东西/话题。比如，如果小朋友提到喜欢老虎，你可以在问题或回复中包含老虎的形象，例如‘假如一只老虎来到了海滩，你觉得他会看见什么样的动物或植物呢？’，来吸引小朋友。
4. 当孩子回应时，请对他们作出回复。你的回复应包括：1. 判断孩子的回答是正确、不正确或部分正确，2. 对孩子回答进行友好、鼓励性的反馈，3. 对前一个问题答案的解释，以及4. 如果对话未结束，则转向下一个问题。
5. 如果孩子的回答不正确，使用引导方法启发他们的思考。如果孩子没有回应，仅简单地回复类似“没关系，你需要更多时间思考”加上解释，或“我没听清你的回答”并重复问题。
6. 保持你的回应和问题简洁，每部分不超过15个字为宜。

对于你生成的第一个问题，请按照以下json格式，注意json字典里key和value应使用双引号：
{{
    "greeting": [介绍自己，（我是智星/我的名字是智星）向孩子问好并开始对话，例如‘你好呀！你真棒，读完了这一个故事，让我们一起来思考一下这则故事吧’，格式为字符串],
    "question": [第一个问题。只包含一个问题。需要包含对故事的总结。格式为字符串]
}}

如果不是第一个问题，你的回应格式应按照以下json格式，注意json字典里key和value应使用双引号：
{{
    "judgement": [对孩子回答的判断：correct/not correct/partially correct。格式为字符串],
    "feedback": [对孩子回答的反馈，应友好且具有鼓励性，例如‘做得好！’，‘你说的完全正确’，‘没关系！’等。格式为字符串],
    "explanation": [根据孩子的回答对前一个问题的相关知识进行解释，格式为字符串],
    "transition": [从解释到问题或结束对话的转折，例如‘让我们一起来探索一下这个现象/问题：’，‘让我们继续读！’等。不要在transition中问问题。格式为字符串],
    "question": [新问题，尽量在问题中包含孩子感兴趣的东西/话题。只包含一个问题。如果是最后一个反馈，那么这个字符串应该为空。格式为字符串],
    "end": [是否是最后一个问题：true/false]
}}
如果对话结束，你在提供最后的反馈而不再问新问题时，请将'question'部分留空（""），并将'end'部分设为'true'。
请注意，当'feedback'、'explanation'、'transition'和'question'的文本结合在一起时，应成为一个流畅的回复。

我会给你提供这则故事的大纲，以及匹配的科学思维知识

<故事标题>: {title}
<故事大纲>:
```
{sum}
```
<科学思维知识>: {knowledge}

现在，开始对话：   
"""
    return Instruction3


def generate_persona(user):

    persona_dict = load_json('./static/files/' + user + '/persona.json')

    prompt = ""

    if persona_dict['isFill'] == 0:
        prompt = "这是一位3-8岁的小朋友"
        print(prompt)
        return prompt
    
    # 添加小朋友名字
    if "name" in persona_dict and persona_dict["name"]:
        prompt += f"这位小朋友名叫{persona_dict['name']}"

    if prompt != "":
            prompt += "，"
    # 添加小朋友年龄
    if "age" in persona_dict and persona_dict["age"]:
        if prompt == "":
            prompt += "这位小朋友"
        prompt += f"今年{persona_dict['age']}岁"

    if prompt != "":
            prompt += "，"
    # 添加对科学知识感兴趣程度
    if "interest" in persona_dict and persona_dict["interest"]:
        if prompt == "":
            prompt += "这位小朋友"
        prompt += f"感兴趣的东西/话题是：{persona_dict['interest']}"

    '''if prompt != "":
            prompt += "，"
    # 添加对科学知识了解程度
    if "science" in persona_dict and persona_dict["science"]:
        if prompt == "":
            prompt += "这位小朋友"
        prompt += f"对科学知识的了解程度是：{persona_dict['science']}。"
    '''
    print(prompt)
    return prompt

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
statements_dict = load_json("./NGSS_statements_CN.json")

def generate_sum(text):
    sum = evaluate(prompt_sum1(text))
    print(sum)
    science_list = [value for d in statements_dict.values() for p in d.values() for q in p.values() for value in q.values()]
    message = [
        {"role": "system", "content": prompt_sum1(text)},
        {"role": "assistant", "content": sum},
        {"role": "system", "content": prompt_sum2(sum, science_list)}
    ]
    science_kg = conversation(message)
    return sum, science_kg

def generate_sum_conv(title, user, isLibrary):
    if os.path.exists('./static/files/' + user  + '/' + title +  '/sum_message.json'):
        sum_message = load_json('./static/files/' + user  + '/' + title + '/sum_message.json')
        return json.loads(sum_message[1]['content'])
    
    if isLibrary:
        book_list = load_json("./static/files/books/" + title + "/" + title + '.json')
    else:
        book_list = load_json("./static/files/" + user + "/" + title + '/' + title + '.json')
    book_str = ''
    for sec_list in book_list:
        book_str += sec_list[0]
    sum, kg = generate_sum(book_str)

    persona_info = load_json('./static/files/' + user + '/persona.json')
    input = prompt_sum_conv(persona_info, title, sum, kg)
    first_sum = evaluate(input)
    print(first_sum)

    if not os.path.exists('./static/files/' + user  + '/' + title +  '/sum_message.json'):
        save_json('./static/files/' + user  + '/' + title +  '/sum_message.json', [])
    sum_message = load_json('./static/files/' + user  + '/' + title + '/sum_message.json')
    start_index = first_sum.find('{')
    end_index = first_sum.rfind('}') + 1
    first_sum= first_sum[start_index:end_index]
    print(first_sum)
    first_sum_dict = json.loads(first_sum)
    sum_message = [
        {"role": "system", "content": input},
        {"role": "assistant", "content": first_sum}
    ]

    if not os.path.exists("./static/files/" + user  + '/' + title +  "/sum_audio"):
        os.makedirs("./static/files/" + user  + '/' + title +  "/sum_audio")
    audio_gen(first_sum_dict['greeting'] + first_sum_dict['question'], "./static/files/" + user  + '/' + title +  "/sum_audio/q_1.mp3")
    save_json('./static/files/' + user + '/' + title +  '/sum_message.json', sum_message)
    return first_sum_dict

def generate_sum_chat(user, title, id, response):
    sum_message = load_json('./static/files/' + user + '/' + title + '/sum_message.json')
    if response == '':
        response = "[No Response]"
    sum_message.append(
        {"role": "user", "content": response}
    )
    feedback = conversation(sum_message)
    start_index = feedback.find('{')
    end_index = feedback.rfind('}') + 1
    feedback = feedback[start_index:end_index]
    print(feedback)
    
    feedback_dict = json.loads(feedback)
    feedback_dict['feedback'] = feedback_dict['feedback']
    feedback_dict['explanation'] = feedback_dict['explanation']
    feedback_dict['transition'] = feedback_dict['transition']
    feedback_dict['question'] = feedback_dict['question']
    if not ("end" in feedback_dict):
        if feedback_dict['question'] != '':
            feedback_dict['end'] = False
        else:
            feedback_dict['end'] = True

    sum_message.append(
        {"role": "assistant", "content": feedback}
    )
    audio_gen(feedback_dict['feedback'] + feedback_dict['explanation'] + feedback_dict['transition'] + feedback_dict['question'], "./static/files/" + user  + '/' + title + "/sum_audio/q_" + str(id) + ".mp3")

    save_json('./static/files/' + user + '/' + title + '/sum_message.json', sum_message)

    return feedback_dict


def is_format(input_string):
    pattern = re.compile(r'^\d+\.\s.*$')
    return bool(pattern.match(input_string))

def evaluate_knowledge(input):
    if is_format(input):
        input = input.split('. ')[1]
    if input.lower() in knowledge_list:
        return input.lower()
    else:
        return 'not matched'

def capitalize_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    capitalized_sentences = [sentence.capitalize() for sentence in sentences]
    
    capitalized_text = ' '.join(capitalized_sentences)
    
    return capitalized_text

def evaluate_kword(section, input):
    if input.lower() in section.lower():
        return input.lower()
    else:
        return 'not identified'

def get_similarity(word, knowledge):
  sim_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
  #Compute embedding for both lists
  embedding_1= sim_model.encode(word, convert_to_tensor=True)
  embedding_2 = sim_model.encode(knowledge, convert_to_tensor=True)
  return util.pytorch_cos_sim(embedding_1, embedding_2)[0].numpy()[0]

def knowledge_matching(input):
    output = {}
    for i, section in enumerate(input):
        each_output = evaluate(prompting_kg_matching(section)).split('\n')[0]
        knowledge = evaluate_knowledge(each_output)
        if i not in output:
            output[i] = {
                'section': section,
                'knowledge': knowledge,
                'keyword': '',
                'use': 0,
                'explanation': ''
            }
    return output

def keyword_identifying(title, input):
    all_knowledge = {}
    sen_split = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    id = 0
    for key, value in input.items():
        section = value['section']
        knowledge = value['knowledge']
        each_output = evaluate(prompting_kword(section, knowledge)).split('\n')
        candidate_word = each_output[0]
        exp = each_output[1]
        key_word = evaluate_kword(section, candidate_word)
        sim = get_similarity(key_word, knowledge)
        if (knowledge not in all_knowledge) or (knowledge in all_knowledge and all_knowledge[knowledge]['sim'] < sim):
          if key_word != 'not identified':
            all_knowledge[knowledge] = {
                'sim': sim,
                'section': id,
                'keyword': key_word
            }
        input[id]['section'] = sen_split[id]
        input[id]['explanation'] = exp
        id += 1

    for kg, value in all_knowledge.items():
        input[value['section']]['keyword'] = value['keyword']
        keyword_list = value['keyword'].split(' ')
        split_word = []
        match_flag = 0
        for sen in input[value['section']]['section']:
            split_sen = split_para(sen)
            for i in range(len(split_sen) - len(keyword_list) + 1):
                if all(split_sen[i + j]['word'].lower() == keyword_list[j] for j in range(len(keyword_list))) and match_flag == 0:
                    for j in range(len(keyword_list)):
                        split_sen[i + j]['keyword'] = 1
                    match_flag = 1
                    input[value['section']]['use'] = 1
            split_word.append(split_sen)         
        input[value['section']]['section'] = split_word
       
    return input

def knowledge_keyword_gen(user, title, isLibrary):
    if isLibrary:
        return load_json('./static/files/books/' + title + '/' + title + ' Gen.json')

    if os.path.exists('./static/files/' + user + '/' + title + '/' + title + ' Gen.json'):
        return load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')
    else:
      knowledge_gen = keyword_matching(user, title, isLibrary)
      save_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json', knowledge_gen)  
    return knowledge_gen

def gen_greet(user):
    if os.path.exists('./static/files/' + user + '/greet_message.json'):
        greet_message = load_json('./static/files/' + user + '/greet_message.json')
        return json.loads(greet_message[1]['content'])['greeting_content']
    input = prompt_greeting()
    first_greet = '{"greeting_content": "小朋友你好！我叫智星，是你的学习伙伴。我可以给你讲很多有趣的故事哦。你可以告诉我你的名字吗？"}'
    if not os.path.exists('./static/files/' + user + '/greet_message.json'):
        save_json('./static/files/' + user + '/greet_message.json', [])
    greet_message = load_json('./static/files/' + user + '/greet_message.json')
    first_greet_dict = {
        "greeting_content": "小朋友你好！我叫智星，是你的学习伙伴。我可以给你讲很多有趣的故事哦。你可以告诉我你的名字吗？"
    }
    greet_message = [
        {"role": "system", "content": input},
        {"role": "assistant", "content": first_greet}
    ]

    if not os.path.exists("./static/files/" + user + "/greet_audio"):
        os.makedirs("./static/files/" + user + "/greet_audio")
    audio_gen(first_greet_dict['greeting_content'], "./static/files/" + user + "/greet_audio/q_1.mp3")
    save_json('./static/files/' + user + '/greet_message.json', greet_message)
    return first_greet_dict['greeting_content']
    
def answer_greet(user, response, id, title, isLibrary):
    greet_message = load_json('./static/files/' + user + '/greet_message.json')
    if response == '':
        response = "[No Response]"
    greet_message.append(
        {"role": "user", "content": response}
    )
    feedback = conversation(greet_message)
    start_index = feedback.find('{')
    end_index = feedback.rfind('}') + 1
    feedback = feedback[start_index:end_index]
    print(feedback)
    feedback_dict = json.loads(feedback)

    # feedback_dict['greeting_content'] = capitalize_sentences(feedback_dict['greeting_content'])
    if 'end' in feedback_dict:
        '''feedback_dict['name'] = capitalize_sentences(feedback_dict['name'])
        feedback_dict['age'] = capitalize_sentences(feedback_dict['age'])
        feedback_dict['interest'] = capitalize_sentences(feedback_dict['interest'])'''

        persona_info = load_json('./static/files/' + user + '/persona.json')
        persona_info['name'] = feedback_dict['name']
        persona_info['age'] = feedback_dict['age']
        persona_info['interest'] = feedback_dict['interest']
        persona_info['isFill'] = 1
        save_json('./static/files/' + user + '/persona.json', persona_info)
        update_age_cog(user, title, isLibrary)

    greet_message.append(
        {"role": "assistant", "content": feedback}
    )
    audio_gen(feedback_dict['greeting_content'], "./static/files/" + user + "/greet_audio/q_" + str(id) + ".mp3")

    save_json('./static/files/' + user + '/greet_message.json', greet_message)

    return feedback_dict

def get_level(age):
    if age < 6:
        return 'k'
    elif age < 7:
        return '1'
    elif age <= 8:
        return '2'
    

def update_age_cog(user, title, isLibrary):
    persona_info = load_json('./static/files/' + user + '/persona.json')
    if persona_info['age'] != '':
        age = int(persona_info['age'])
    else:
        age = 6
    level = get_level(age)
    if (isLibrary):
        gen_result =  load_json('./static/files/books/' + title + '/' + title + ' Gen.json')  
    else:
        gen_result =  load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')  
    for key, value in gen_result.items():
        if value['use'] == 1:
            if value['level'] == level:
                value['cog'] = 1
    save_json('./static/files/books/' + title + '/' + title + ' Gen.json', gen_result)

def conv_gen(id, title, user, isLibrary):
    if not os.path.exists('./static/files/' + user + '/' + title + "/conversation/"):
        os.makedirs('./static/files/' + user + '/' + title + "/conversation/")
    if isLibrary and os.path.exists("./static/files/books/" + title + "/conv_audio/") and not os.path.exists("./static/files/" + user + "/" + title + "/conv_audio/"):
        os.makedirs("./static/files/" + user + "/" + title + "/conv_audio/")
    if not os.path.exists("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json") and os.path.exists("./static/files/books/" + title + "/conversation/get_conv_sec_" + id + ".json"):
        save_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json", load_json("./static/files/books/" + title + "/conversation/get_conv_sec_" + id + ".json"))
        shutil.copy("./static/files/books/" + title + "/conv_audio/sec_" + str(id) + "_q_1.mp3", "./static/files/" + user + "/" + title + "/conv_audio/sec_" + str(id) + "_q_1.mp3")
    
    if os.path.exists("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json"):
        return json.loads(load_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json")[1]['content'])
    if isLibrary:
        sec_dict = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/books/' + title + '/' + title + '.json')[int(id)]
    else:
        sec_dict = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/' + user + '/' + title + '/' + title + '.json')[int(id)]
    chatHistory = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    
    keyword = sec_dict['keyword']
    if keyword == '':
        return 
    knowledge = sec_dict['knowledge'].lower()
    linked_statements = knowledge_dict[knowledge]["Statements"]
    statements = ''
    for sts_id in linked_statements:
        char = sts_id.split('-')
        if statements != '':
            statements += '\n'
        statements += statements_dict[char[0]][char[1]][char[2]][char[3]]
    input = prompt_conv(title, section, generate_persona(user))
    first_conv = evaluate(input)
    start_index = first_conv.find('{')
    end_index = first_conv.rfind('}') + 1
    first_conv = first_conv[start_index:end_index]
    first_conv_dict = json.loads(first_conv)
    first_conv_dict['greeting'] = capitalize_sentences(first_conv_dict['greeting'])
    first_conv_dict['question'] = capitalize_sentences(first_conv_dict['question'])
    messages = [
        {"role": "system", "content": input},
        {"role": "assistant", "content": first_conv}
    ]

    chatHistory[id]['conversation'].append({
        'question': first_conv_dict['question'],
        'answer': '',
        'correct': '',
        'explanation': ''
    })

    # if not os.path.exists("./static/files/" + user + "/" + title + "/conv_audio"):
    #     os.makedirs("./static/files/" + user + "/" + title + "/conv_audio")
    # audio_gen(first_conv_dict['greeting'] + first_conv_dict['question'], './static/files/' + user + '/' + title + "/conv_audio/sec_" + str(id) + "_q_1.mp3")

    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', chatHistory)
    save_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)
    # save_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json', chatHistory)
    # save_json("./static/files/books/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)
    return first_conv_dict
    
def gen_first_conv(title):
    story = load_json('./static/files/books/' + title + '/' + title + '.json')
    for sec_id in range(len(story)):
        conv_gen(str(sec_id), title, 'reading', True)

gen_first_conv("海边度假")

def label_conv_gen(id, title, user, isLibrary):
    # if os.path.exists("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json"):
    #     return json.loads(load_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json")[1]['content'])
    if not os.path.exists('./static/files/books/' + title + "/conversation/"):
         os.makedirs('./static/files/books/' + title + "/conversation/")
    if isLibrary:
        sec_dict = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/books/' + title + '/' + title + '.json')[int(id)]
    else:
        sec_dict = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/' + user + '/' + title + '/' + title + '.json')[int(id)]
    
    chatHistory = load_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json')

    label = load_json('./static/files/books/' + title + '/' + 'label.json')

    keyword = sec_dict['keyword']
    knowledge = sec_dict['knowledge'].lower()
    statements = label[id]['statement']
    
    input = prompt_conv(title, section, keyword, knowledge, statements, generate_persona(user))
    first_conv_dict = {
         "greeting": "Hi there! Let's talk about something fun in " + title + '!',     
         "question": label[id]['question']
         # "question": label[id]['question'][0]
    }
    messages = [
        {"role": "system", "content": input},
        {"role": "assistant", "content": json.dumps(first_conv_dict)}
    ]

    chatHistory[id]['conversation'].append({
        'question': first_conv_dict['question'],
        'answer': '',
        'correct': '',
        'explanation': ''
    })

    if not os.path.exists("./static/files/books/" + title + "/conv_audio"):
        os.makedirs("./static/files/books/" + title + "/conv_audio")
    audio_gen(first_conv_dict['greeting'] + first_conv_dict['question'], "./static/files/books/" + title + "/conv_audio/sec_" + str(id) + "_q_1.mp3")

    save_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json', chatHistory)
    save_json("./static/files/books/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)
    return first_conv_dict

# conv_gen("2", 'The Little Snowplow', 'user')
def gen_first_conv_label(title):
    label = load_json('./static/files/books/' + title + '/' + 'label.json')
    for sec_id, val in label.items():
        label_conv_gen(str(sec_id), title, 'user', True)

# gen_first_conv_label('Amara and the Bats')

def chat_gen(id, title, user, response):
    messages = load_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json")
    chatHistory = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    if response == '':
        response = "[No Response]"
    messages.append(
        {"role": "user", "content": response}
    )
    feedback = conversation(messages)
    start_index = feedback.find('{')
    end_index = feedback.rfind('}') + 1
    feedback = feedback[start_index:end_index]
    feedback_dict = json.loads(feedback)
    
    feedback_dict['feedback'] = capitalize_sentences(feedback_dict['feedback'])
    feedback_dict['explanation'] = capitalize_sentences(feedback_dict['explanation'])
    feedback_dict['transition'] = capitalize_sentences(feedback_dict['transition'])
    feedback_dict['question'] = capitalize_sentences(feedback_dict['question'])
    if not ("end" in feedback_dict):
        if feedback_dict['question'] != '':
            feedback_dict['end'] = False
        else:
            feedback_dict['end'] = True

    messages.append(
        {"role": "assistant", "content": feedback}
    )
    save_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)

    chatHistory[id]['conversation'][-1]['answer'] = response
    chatHistory[id]['conversation'][-1]['correct'] = feedback_dict['judgement']
    chatHistory[id]['conversation'][-1]['explanation'] = feedback_dict['explanation']

    chatHistory[id]['conversation'].append({
        'question': feedback_dict['question'],
        'answer': '',
        'correct': '',
        'explanation': ''
    })
    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', chatHistory)

    feedback_dict['q_id'] = len(chatHistory[id]['conversation'])
    print(feedback_dict)

    audio_gen(feedback_dict['feedback'] + feedback_dict['explanation'] + feedback_dict['transition'] + feedback_dict['question'], "./static/files/" + user + "/" + title + "/conv_audio/sec_" + str(id) + "_q_" + str(len(chatHistory[id]['conversation'])) + ".mp3")

    return {
        "response_dict": feedback_dict,
        "QA_pair": chatHistory[id]['conversation'][-2]
    }

def save_knowledge(user, title, isLibrary):
    if (isLibrary):
        gen_data = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')
    else:
        gen_data = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')
    gpt_data = {}
    for key, value in gen_data.items():
        if value['use'] == 1:
            gpt_data[key] = {
                'keyword': value['keyword'],
                'explanation': value['explanation'],
                'level': value['level'],
                'cog': value['cog'],
                'knowledge': value['knowledge'],
                'discipline': knowledge_dict[value['knowledge'].lower()]['Discipline'],
                'sub-disc': knowledge_dict[value['knowledge'].lower()]['SubDiscipline'],
                'topic': knowledge_dict[value['knowledge'].lower()]['Topic'],
                'answer': False,
                'dash': False,
                'conversation': []
            }
    if (isLibrary):
        save_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json', gpt_data)
    else:
        save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', gpt_data)

def save_label_knowledge(user, title, isLibrary):
    if (isLibrary):
        gen_data = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')
    else:
        gen_data = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')
    gpt_data = {}
    for key, value in gen_data.items():
        if value['use'] == 1:
            gpt_data[key] = {
                'keyword': value['keyword'],
                'explanation': value['explanation'],
                'knowledge': value['knowledge'],
                'discipline': '',
                'sub-disc': '',
                'topic': '',
                'answer': False,
                'dash': False,
                'conversation': []
            }
    if (isLibrary):
        save_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json', gpt_data)
    else:
        save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', gpt_data)


# save_label_knowledge('user', 'Amara and the Bats', True)

def get_book_discipline(user, title, isLibrary):
    if (isLibrary):
        gpt_data = load_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json')
    else:
        gpt_data = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    disc = {}
    sub_dis = {}
    for key, value in gpt_data.items():
        dis = knowledge_dict[value['knowledge']]['Discipline']
        sub = knowledge_dict[value['knowledge']]['SubDiscipline']
        if dis not in disc:
            disc[dis] = 1
        else:
            disc[dis] += 1
        if sub not in sub_dis:
            sub_dis[sub] = 1
        else:
            sub_dis[sub] += 1
    disc = sorted(disc.items(), key=lambda x:x[1])
    sub_dis = sorted(sub_dis.items(), key=lambda x:x[1])
    topic = {
        "discipline": disc,
        "sub-discipline": sub_dis
    }
    print(topic)
    return topic



# save_knowledge('user', "海边度假", True)
# get_book_discipline('user', "Why Do Sunflowers Love the Sun?", True)
# knowledge_keyword_gen('user', "Why Do Sunflowers Love the Sun", True)

def update_lib():
    lib_book = [
        "Amara and the Bats",
        "Fairy Science",
        # "Oscar and the CRICKET",
        "PENNY, the Engineering Tail of the Fourth Little Pig"
    ]
    for b in lib_book:
        save_knowledge('user', b, True)
        knowledge_keyword_gen('user', b, True)

def gen_conv_lib():
    lib_book = [
        "Amara and the Bats",
        "Fairy Science",
        "Oscar and the CRICKET",
        "PENNY, the Engineering Tail of the Fourth Little Pig"
    ]
    for b in lib_book:
        kg_dict = load_json('./static/files/books/' + b + '/' + b + '_knowledge_dict.json')
        for key, val in kg_dict.items():
            conv_gen(key, b, 'user', True)

# update_lib()
# gen_conv_lib()
