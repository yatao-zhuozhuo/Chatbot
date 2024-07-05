import os
import threading
import json
# 启动第二个线程

import threading
import time

from flask import Flask, request, send_file
from identify import run_with_nls # 引入用于语音识别的模块
from TongYi import call_with_messages,call_with_search  # 引入用于处理请求的模块
from TTS import run_tts  # 引入文本到语音的模块
from process_TongYi import  conclusion_messages
from embedding import prepare_data,get_embeddings,generate_embeddings

from MobileVLM.scripts.inference import inference_once



def picture_classify(image_file):
    model_path = ""  # MobileVLM V2
    prompt_str = "Summarize the content of the image\nsimply use several words."

    args = type('Args', (), {
        "model_path": model_path,
        "image_file": image_file,
        "prompt": prompt_str,
        "conv_mode": "v1",
        "temperature": 0,
        "top_p": None,
        "num_beams": 1,
        "max_new_tokens": 512,
        "load_8bit": False,
        "load_4bit": False,
    })()
    time.sleep(10)
    outputs = inference_once(args)
    
    # 创建识别结果的字典
    result = {"title": outputs}
    answer_file = "../process_data/answer.json"
    # 将结果写入 answer.json 文件
    if os.path.exists(answer_file):
        with open(answer_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(result)

    with open(answer_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def periodic_picture_classify(interval=30):
    count = 0
    while True:
        image_file = f"../picture_store/image_{count}.jpg"
        picture_classify(image_file)
        print(f"Processed {image_file}")
        count += 1
        time.sleep(interval)

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # 保存文件到本地指定路径
    filename = file.filename
    processed_filename = 'processed_' + filename
    file.save(os.path.join('process_data', filename))

    # 运行语音识别，将语音转换为文字存入input.txt
    run_with_nls(filename)
    print("语音转为文字存入input.txt")

    # 调用模型回答
    with open('../process_data/input.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        # 检查文件内容的前四个字符
        if content.startswith('网页搜索'):
            call_with_search()
        else:
            call_with_messages()
    print("通义千问已回答")

    # 将处理后的文本转换为语音文件
    run_tts("../process_data/output.txt", processed_filename)
    print("完成将文字output.txt转为语音output.pcm")

    return send_file(os.path.join('process_data', processed_filename), as_attachment=True)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    print("Received request for /upload_photo")  # 新增日志
    if 'file' not in request.files:
        print("No file part in request")
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return "No selected file", 400

    # 保存文件到本地指定路径
    filename = file.filename
    processed_filename = 'processed_' + filename
    file.save(os.path.join('picture_store', filename))

    # 这里可以添加处理照片的逻辑，例如图像识别、分析等
    print(f"照片 {filename} 已上传并保存")

    return f"Photo {filename} uploaded successfully", 200


@app.route('/process_inf', methods=['POST'])
def process_inf():
    print("Received request for /process_inf")  # 新增日志
    if 'file' not in request.files:
        print("No file part in request")
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return "No selected file", 400

    conclusion_messages()
    get_embeddings('../process_data/conclusion.json')
    

    # 保存文件到本地指定路径
    filename = file.filename
    processed_filename = 'processed_' + filename
    file.save(os.path.join('process_data', filename))


    return "The site log has changed", 200


if __name__ == '__main__':
    calculate_thread = threading.Thread(target=periodic_picture_classify)
    calculate_thread.daemon = True  # 设置为守护线程，使其随主线程退出
    calculate_thread.start()
    app.run(host='0.0.0.0', port=5000)
