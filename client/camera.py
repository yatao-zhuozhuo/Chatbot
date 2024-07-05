import os
import cv2
import time

import cv2
import time
import os

def catch_picture():
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    try:
        count = 0
        while True:
            # 读取一帧
            ret, frame = cap.read()

            if not ret:
                print("无法接收帧 (stream end?). Exiting ...")
                break

            # 生成保存图片的完整路径
            filename = f'image_{count}.jpg'
            cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            print(f'Saved {filename}')

            count += 1

            # 每30秒拍摄一次
            time.sleep(10)

    finally:
        # 释放摄像头资源
        cap.release()
        cv2.destroyAllWindows()

#catch_picture()