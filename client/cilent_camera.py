import time
import requests
import threading
from camera import catch_picture

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

# 主函数
def main():
    url = 'http://your_ip/upload'  # 修改为你的服务器 URL
    count=0
    while True:
        filename = f'image_{count}.jpg'
        catch_picture()  # 拍摄照片
        send_file(url, filename)  # 发送照片到服务器
        time.sleep(10)  # 每隔10秒拍摄并发送一次照片
        count+=1

if __name__ == "__main__":
    # 创建并启动一个新线程来运行main函数
    photo_thread = threading.Thread(target=main)
    photo_thread.start()
