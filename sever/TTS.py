import time
import threading
import nls

URL = "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
TOKEN = ""  # 获取Token请参考：https://help.aliyun.com/document_detail/450255.html
APPKEY = ""  # 获取Appkey请前往控制台：https://nls-portal.console.aliyun.com/applist

def run_tts(text_file, pcm_file):
    # 读取文本文件内容
    with open(text_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # 打开文件以便写入PCM数据
    f = open(pcm_file, "wb")

    # 写入PCM文件的处理函数
    def on_data(data, *args):
        try:
            f.write(data)
        except Exception as e:
            print("Write data failed:", e)

    def on_error(message, *args):
        print("Error:", message)

    def on_completed(message, *args):
        print("Completed:", message)
        f.close()

    print("TTS session start")
    tts = nls.NlsSpeechSynthesizer(
        url=URL,
        token=TOKEN,
        appkey=APPKEY,
        on_data=on_data,
        on_completed=on_completed,
        on_error=on_error
    )

    result = tts.start(text, voice="ailun")
    print("TTS done with result:", result)

# 使用示例
#run_tts(text_file="input.txt", pcm_file="output.pcm")

