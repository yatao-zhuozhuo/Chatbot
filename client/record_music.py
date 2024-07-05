import pyaudio
import wave
import keyboard
import time

def record_audio_with_keyboard_control(filename, format=pyaudio.paInt16, channels=1, rate=16000, chunk=1024):
    # 创建PyAudio对象
    audio = pyaudio.PyAudio()

    # 打开音频流
    stream = audio.open(format=format, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)

    print("按 's' 键开始录音，再次按 's' 键停止录音...")

    frames = []
    recording = False

    # 等待开始录音的按键
    keyboard.wait('s')
    print("开始录音...")
    recording = True
    start_time = time.time()

    # 持续录音直到再次按下's'键
    while True:
        if keyboard.is_pressed('s') and time.time() - start_time > 1:  # 检测是否按下停止键并确保已经录音至少1秒
            if recording:
                print("录音结束.")
                break
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    # 停止录音并关闭音频流
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 将录音数据写入PCM文件
    with open(filename, "wb") as pcm_file:
        for frame in frames:
            pcm_file.write(frame)

    print(f"录音数据已保存到 {filename}")

# 确保安装keyboard库：pip install keyboard
# 请以管理员权限运行此脚本以允许键盘监听
#record_audio_with_keyboard_control("input.pcm")

#record_audio_with_keyboard_control("input.pcm")