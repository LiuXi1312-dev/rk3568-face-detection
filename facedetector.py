"""人脸检测器封装

默认使用 OpenCV 自带 Haar 级联（离线、无需模型文件、适合嵌入式）。
如需更高精度，把 mode 换成 "dnn" 并放入 res10_300x300_ssd 模型即可。
"""
import os
import time

import cv2

import config


class FaceDetector:
    def __init__(self, mode: str = "haar",
                 scale_factor: float = config.SCALE_FACTOR,
                 min_neighbors: int = config.MIN_NEIGHBORS,
                 min_size: tuple[int, int] = config.MIN_SIZE):
        self.mode = mode
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.last_ms = 0.0

        if mode == "haar":
            path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            self.cascade = cv2.CascadeClassifier(path)
            if self.cascade.empty():
                raise RuntimeError(f"级联分类器加载失败：{path}")
        elif mode == "dnn":
            proto = "deploy.prototxt"
            model = "res10_300x300_ssd_iter_140000.caffemodel"
            if not (os.path.exists(proto) and os.path.exists(model)):
                raise FileNotFoundError("DNN 模式需要 deploy.prototxt 与 .caffemodel 模型文件")
            self.net = cv2.dnn.readNetFromCaffe(proto, model)
        else:
            raise ValueError(f"不支持的模式：{mode}")

    def detect(self, frame):
        """返回 [(x, y, w, h), ...]，同时记录本次检测耗时(ms)。"""
        t0 = time.perf_counter()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.equalizeHist(gray, dst=gray)        # 提升低照度下的检出率

        if self.mode == "haar":
            faces = self.cascade.detectMultiScale(
                gray, scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors, minSize=self.min_size)
            boxes = [tuple(map(int, f)) for f in faces]
        else:
            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                         (300, 300), (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            det = self.net.forward()
            boxes = []
            for i in range(det.shape[2]):
                conf = float(det[0, 0, i, 2])
                if conf > 0.6:
                    x1, y1, x2, y2 = (det[0, 0, i, 3:7] * [w, h, w, h]).astype(int)
                    boxes.append((int(x1), int(y1), int(x2 - x1), int(y2 - y1)))

        self.last_ms = (time.perf_counter() - t0) * 1000
        return boxes

    @staticmethod
    def draw(frame, boxes):
        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          config.BOX_COLOR, config.BOX_THICKNESS)
            cv2.putText(frame, "face", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX,
                        config.FONT_SCALE, config.BOX_COLOR, 2)
        return frame
