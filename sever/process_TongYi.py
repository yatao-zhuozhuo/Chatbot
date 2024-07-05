import json
import dashscope

from http import HTTPStatus
from dashscope import Generation


def conclusion_messages():
    dashscope.api_key = ''  # 使用实际的API密钥

    #图片识别结果
    with open('../process_data/answer.json', 'r') as file:
        data = json.load(file)
    picture_questions = [entry['title'] + '\n' for entry in data]
    picture_questions = ' '.join(picture_questions)

    #本轮次的对话记录
    with open('../process_data/answers.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    pre_conversation = [f'{entry["role"]}:{entry["content"]}' for entry in data]
    pre_conversation = ' '.join(pre_conversation)

    #最终prompt
    final_questions = pre_conversation+picture_questions+"简略总结上述所有信息,以当前时间、地点、人物、事物的格式"
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
    else:
        print(
            f"Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}")

    print(model_response)
    #将信息加入到本次聊天历史记录中
    try:
        with open('../process_data/conclusion.json', 'r', encoding='utf-8') as json_file:
            history = json.load(json_file)
    except FileNotFoundError:
        history = []

    history.append({'title': model_response})
    with open('../process_data/conclusion.json', 'w', encoding='utf-8') as json_file:
        json.dump(history, json_file, ensure_ascii=False, indent=4)

