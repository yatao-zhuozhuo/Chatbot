import json
import dashscope
from http import HTTPStatus
from dashscope import Generation

from dashscope import TextEmbedding
from dashvector import Client, Doc
from search import search_so


def generate_embeddings(news):
    rsp = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v1,
        input=news
    )
    embeddings = [record['embedding'] for record in rsp.output['embeddings']]
    return embeddings if isinstance(news, list) else embeddings[0]


def search_relevant_news(question):
    # 初始化 dashvector client
    client = Client(
        api_key='',  # 此api为向量库api，不要搞错
        endpoint=''
    )

    # 获取刚刚存入的集合
    try:
        collection = client.get('HCI_collection')
        if not collection:
            raise Exception("Failed to get collection")
    except Exception as e:
        print(f"Error getting collection: {e}")
        exit(1)

    # 向量检索：指定 topk = 1
    rsp = collection.query(generate_embeddings(question), output_fields=['title'],
                           topk=5)
    assert rsp
    return rsp.output[0].fields['title']


def call_with_search():
    dashscope.api_key = ''  # 使用实际的API密钥
    with open('../process_data/input.txt', 'r', encoding='utf-8') as file:
        inputQuestions = file.readlines()
    inputQuestions = '\n'.join(inputQuestions)
    inputQuestions=inputQuestions[4:]

    search_so(inputQuestions)
    with open('../process_data/search.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    if data:
        pre_conversation = [f'Content: {entry["content"]}' for entry in data]
        pre_conversation = ' '.join(pre_conversation)
        data_count = len(data)
    else:
        pre_conversation = ''
        data_count = 0

    final_questions = pre_conversation+"总结上述网页的信息，使用“这些内容……”的形式"

    messages = [{'role': 'user', 'content': final_questions}]

    gen = Generation()
    response = gen.call(
        Generation.Models.qwen_turbo,
        messages=messages,
        result_format='message',
    )

    if response.status_code == HTTPStatus.OK:
        model_response = response.output.choices[0]['message']['content']
        model_response = f"为您找到{data_count}条相关的内容，{model_response}，已为您保存网站地址方便您的访问"
        print(model_response)
        with open('../process_data/output.txt', 'w', encoding='utf-8') as output_file:
            output_file.write(model_response)
    else:
        print(
            f"Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}")


def call_with_messages():
    dashscope.api_key = ''  # 使用实际的API密钥

    #用户最新的prompt
    with open('../process_data/input.txt', 'r', encoding='utf-8') as file:
        inputQuestions = file.readlines()
    inputQuestions='\n'.join(inputQuestions)

    #相关的历史记录
    history = search_relevant_news(inputQuestions)

    #图片识别结果
    with open('../process_data/answer.json', 'r') as file:
        data = json.load(file)
    # 检查data是否为空
    if data:
        picture_questions = [entry['title'] + '\n' for entry in data]
        picture_questions = ' '.join(picture_questions)
    else:
        picture_questions = ''  # 如果data为空，则设置为一个空字符串

    #本轮次的对话记录
    with open('../process_data/answers.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    if data:
        pre_conversation = [f'{entry["role"]}:{entry["content"]}' for entry in data]
        pre_conversation = ' '.join(pre_conversation)
    else:
        pre_conversation = ''

    #最终prompt
    final_questions = "这是你已知的信息："+pre_conversation + "\n这是你能看到的情景:"+picture_questions + "\n这是我们刚刚的聊天记录:"+history + "\n注意："+inputQuestions
    print(final_questions)
    messages = [{'role': 'user', 'content': final_questions}]

    gen = Generation()
    response = gen.call(
        Generation.Models.qwen_turbo,
        messages=messages,
        result_format='message',
    )

    #打印模型回复，并将回复写入output.txt
    if response.status_code == HTTPStatus.OK:
        model_response = response.output.choices[0]['message']['content']
        print(model_response)
        with open('../process_data/output.txt', 'w', encoding='utf-8') as output_file:
            output_file.write(model_response)
    else:
        print(
            f"Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}")
    
    #将信息加入到本次聊天历史记录中
    try:
        with open('../process_data/answers.json', 'r', encoding='utf-8') as json_file:
            history = json.load(json_file)
    except FileNotFoundError:
        history = []

    history.append({'role': 'user', 'content': inputQuestions})
    history.append({'role': 'assistant', 'content':model_response})

    with open('../process_data/answers.json', 'w', encoding='utf-8') as json_file:
        json.dump(history, json_file, ensure_ascii=False, indent=4)


#if __name__ == '__main__':
#    call_with_messages()

