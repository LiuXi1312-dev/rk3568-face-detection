# RK3568 人脸检测

> 简历对应经历：2025.11–2025.12　广州粤嵌通信科技股份有限公司实习
> 基于 RK3568 开发板，Python + OpenCV 实现图片人脸识别、摄像头/本地视频流实时人脸检测

## 功能

- 图片人脸检测：读取本地图片 → 检测 → 绘制人脸框 → 输出检测结果（坐标、置信度、耗时）
- 摄像头 / 本地视频流实时检测：支持 `0` 设备号或视频文件路径
- 嵌入式环境参数调优：分辨率缩放、跳帧、检测参数（scaleFactor / minNeighbors / minSize）
- 检测结果输出：画面绘制 + 控制台日志 + 可保存为视频文件

## 快速开始（PC 上先跑通）

```bash
pip install -r requirements.txt

python detect_image.py --input samples/face.jpg --output outputs/result.jpg
python detect_video.py --source 0                      # 摄像头
python detect_video.py --source test.mp4 --save out.avi # 本地视频
```

按 `q` 退出实时画面。

## 参数怎么调（板子上最关键的一课）

| 参数 | 作用 | 嵌入式建议 |
|---|---|---|
| `--scale` | 送入检测前把帧按比例缩小 | RK3568 上 0.5 起，帧率不够继续降 |
| `--skip` | 每 N 帧检测一次，中间帧沿用上次结果 | 实时流建议 2–3 |
| `--scaleFactor` | 金字塔缩放步长 | 1.1 精度高但慢，1.2–1.3 更快 |
| `--minNeighbors` | 候选框邻居数阈值 | 3–5，越大误检越少但可能漏检 |
| `--minSize` | 最小人脸尺寸 | 按实际拍摄距离设，能显著减少候选窗口 |

## 目录结构

```
03-face-detection-rk3568/
├─ facedetector.py       # 检测器封装（Haar 级联，参数可调）
├─ detect_image.py       # 图片检测
├─ detect_video.py       # 摄像头 / 视频流实时检测
├─ config.py             # 默认参数集中管理
├─ deploy_rk3568.md      # RK3568 部署与调优记录
└─ requirements.txt
```

## 说明

- 使用 OpenCV 自带的 `haarcascade_frontalface_default.xml`，无需额外下载模型，便于在板子上离线运行。
- 需要更高精度时可替换为 DNN 模型（如 `res10_300x300_ssd`），`facedetector.py` 已预留切换入口。
- 仓库中不含任何真实人脸图片，请自行放入 `samples/` 目录测试。
