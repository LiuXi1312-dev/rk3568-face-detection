"""摄像头 / 本地视频流实时人脸检测

用法：
  python detect_video.py --source 0                  # 摄像头
  python detect_video.py --source test.mp4 --save out.avi
按 q 退出。
"""
import argparse
import os
import time

import cv2

import config
from facedetector import FaceDetector


def parse_source(src: str):
    """设备号字符串转 int，视频路径保持字符串。"""
    return int(src) if src.isdigit() else src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(config.CAMERA_INDEX), help="摄像头设备号或视频路径")
    ap.add_argument("--scale", type=float, default=config.FRAME_SCALE, help="检测前缩放比例")
    ap.add_argument("--skip", type=int, default=config.FRAME_SKIP, help="每 N 帧检测一次")
    ap.add_argument("--save", default="", help="保存输出视频的路径，留空则不保存")
    ap.add_argument("--no-display", action="store_true", help="无界面环境(板子)下使用")
    args = ap.parse_args()

    cap = cv2.VideoCapture(parse_source(args.source))
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频源：{args.source}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    detector = FaceDetector()
    writer = None
    last_boxes: list = []
    frame_id = 0
    fps_t0, fps_frames = time.perf_counter(), 0
    fps = 0.0
    scale_up = 1.0 / max(args.scale, 0.05)

    print("开始检测，按 q 退出 ...")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_id += 1

        # 嵌入式优化 1：缩帧检测，结果坐标放大回原尺寸
        small = cv2.resize(frame, None, fx=args.scale, fy=args.scale)
        # 嵌入式优化 2：跳帧检测，中间帧复用上次结果
        if frame_id % args.skip == 0 or not last_boxes:
            boxes = detector.detect(small)
            last_boxes = [(int(x * scale_up), int(y * scale_up),
                           int(w * scale_up), int(h * scale_up)) for x, y, w, h in boxes]
        detector.draw(frame, last_boxes)

        fps_frames += 1
        if fps_frames >= 30:
            fps = fps_frames / (time.perf_counter() - fps_t0)
            fps_t0, fps_frames = time.perf_counter(), 0

        cv2.putText(frame, f"FPS {fps:.1f} | faces {len(last_boxes)} | {detector.last_ms:.0f}ms",
                    (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if args.save:
            if writer is None:
                os.makedirs(os.path.dirname(args.save) or ".", exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                writer = cv2.VideoWriter(args.save, fourcc, 20.0,
                                         (frame.shape[1], frame.shape[0]))
            writer.write(frame)

        if not args.no_display:
            cv2.imshow("face detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print(f"结束：共处理 {frame_id} 帧")


if __name__ == "__main__":
    main()
