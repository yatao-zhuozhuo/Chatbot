import requests
from record_music import record_audio_with_keyboard_control
import pyaudio
import langchain


# 发送文件到服务器的函数
def send_file(url, filename):
    with open(filename, 'rb') as f:
        files = {'file': (filename, f)}
        response = requests.post(url, files=files) # 发送文件到指定的 URL

    if response.status_code == 200:
        with open('returned_' + filename, 'wb') as f:
            f.write(response.content) # 保存返回的文件
        print(f"Processed file saved as 'returned_{filename}'")
    else:
        print("Failed to process file", response.status_code) # 如果请求失败，打印错误信息


if __name__ == "__main__":
    #先播放问候语
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
    with open("begin.pcm", "rb") as f:
        stream.write(f.read())
        stream.stop_stream()
        stream.close()
        p.terminate()

    record=1
    while record==1:
        record_audio_with_keyboard_control("input.pcm") # 控制录音
        send_file('http://your_ip/upload', 'input.pcm')  # 将录音文件发送到服务器
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
        with open("returned_input.pcm", "rb") as f:
            stream.write(f.read()) # 播放返回的音频
        stream.stop_stream()
        stream.close()
        p.terminate()
        record=int(input("Press 1 to continue...")) # 根据输入决定是否继续录音

    #结束之后播放结束语
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
    with open("end.pcm", "rb") as f:
        stream.write(f.read())
        stream.stop_stream()
        stream.close()
        p.terminate()
