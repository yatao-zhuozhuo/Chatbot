# -*- coding: utf8 -*-
import time
import json
import nls

URL = "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
TOKEN = "" #每次需要获取临时token
APPKEY = ""

def run_with_nls(test_file):
    def loadfile(filename):
        with open(filename, "rb") as f:
            return f.read()

    def test_on_sentence_begin(message, *args):
        print("test_on_sentence_begin:{}".format(message))

    def test_on_sentence_end(message, *args):
        print("test_on_sentence_end:{}".format(message))
        result_content = json.loads(message)["payload"]["result"]
        with open("../process_data/input.txt", "w", encoding="utf-8") as f:
            f.write(result_content)

    def test_on_start(message, *args):
        print("test_on_start:{}".format(message))

    def test_on_error(message, *args):
        print("on_error args=>{}".format(args))

    def test_on_close(*args):
        print("on_close: args=>{}".format(args))

    def test_on_result_chg(message, *args):
        print("test_on_chg:{}".format(message))

    def test_on_completed(message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))

    data = loadfile(test_file)
    sr = nls.NlsSpeechTranscriber(
        url=URL,
        token=TOKEN,
        appkey=APPKEY,
        on_sentence_begin=test_on_sentence_begin,
        on_sentence_end=test_on_sentence_end,
        on_start=test_on_start,
        on_result_changed=test_on_result_chg,
        on_completed=test_on_completed,
        on_error=test_on_error,
        on_close=test_on_close,
        callback_args=[]
    )

    r = sr.start(aformat="pcm",
                 enable_intermediate_result=True,
                 enable_punctuation_prediction=True,
                 enable_inverse_text_normalization=True)

    slices = zip(*(iter(data),) * 640)
    for i in slices:
        sr.send_audio(bytes(i))
        time.sleep(0.01)

    sr.ctrl(ex={"test": "tttt"})
    time.sleep(1)

    r = sr.stop()

# 使用示例
#run_with_nls(test_file="input.pcm")

