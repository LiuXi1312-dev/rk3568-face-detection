"""图片人脸检测：读图 → 检测 → 画框 → 保存并输出结果

用法：python detect_image.py --input samples/face.jpg --output outputs/result.jpg
"""
import argparse
import json
import os

import cv2

import config
from facedetector import FaceDetector


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="输入图片路径")
    ap.add_argument("--output", default="outputs/result.jpg", help="结果保存路径")
    ap.add_argument("--scale-factor", type=float, default=config.SCALE_FACTOR)
    ap.add_argument("--min-neighbors", type=int, default=config.MIN_NEIGHBORS)
    ap.add_argument("--min-size", type=int, default=config.MIN_SIZE[0])
    args = ap.parse_args()

    img = cv2.imread(args.input)
    if img is None:
        raise FileNotFoundError(f"读取失败：{args.input}")

    detector = FaceDetector(scale_factor=args.scale_factor,
                            min_neighbors=args.min_neighbors,
                            min_size=(args.min_size, args.min_size))
    boxes = detector.detect(img)
    detector.draw(img, boxes)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    cv2.imwrite(args.output, img)

    result = {"image": args.input, "faces": len(boxes),
              "boxes": [{"x": x, "y": y, "w": w, "h": h} for x, y, w, h in boxes],
              "detect_ms": round(detector.last_ms, 2)}
    print(json.dumps(result, ensure_ascii=False))
    print(f"结果已保存：{args.output}")


if __name__ == "__main__":
    main()
