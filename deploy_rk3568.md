# RK3568 部署与调优记录

实习期间在 RK3568 开发板（4×A55 @1.8GHz，Debian/Ubuntu 系）上的落地过程与踩坑记录。

## 1. 环境准备

```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv
python3 -m pip install -U pip numpy
```

优先装系统包 `python3-opencv`（自带 NEON 优化）；用 pip 装 `opencv-python` 在部分系统上会缺少
GTK 依赖，导致 `cv2.imshow` 不可用——此时加 `--no-display` 参数运行，或用 `opencv-python-headless`。

## 2. 摄像头设备确认

```bash
ls /dev/video*
v4l2-ctl --list-formats-ext -d /dev/video0
```

rk3568 走 V4L2，OpenCV 打开 `0` 通常即可；若报 `VIDEOIO ERROR`，检查用户是否在 `video` 组：

```bash
sudo usermod -aG video $USER   # 重新登录后生效
```

## 3. 参数调优过程（640×480 输入）

| 配置 | 处理耗时/帧 | 实测帧率 | 说明 |
|---|---|---|---|
| 原始尺寸 + 全帧检测 | ~85 ms | ~11 FPS | 卡顿明显 |
| scale=0.5 | ~30 ms | ~25 FPS | 小脸检出率下降 |
| scale=0.5 + skip=2 | ~30 ms(摊薄 ~15 ms) | ~33 FPS | 画面流畅，可接受 |
| scale=0.5 + skip=2 + minSize=(40,40) | ~22 ms | ~35 FPS | 误检明显减少 |

结论：优先降分辨率与跳帧，其次才动检测参数；`minNeighbors` 从 3 提到 5 会明显减少误检，
但侧脸容易漏，实时场景建议 4。

## 4. 运行

```bash
python3 detect_video.py --source 0 --scale 0.5 --skip 2 --no-display --save out.avi
```

## 5. 踩过的坑

- **温度与降频**：连续跑 10 分钟后帧率下降，是 SoC 温控降频，加装散热片后稳定。
- **USB 摄像头带宽**：同时接两个摄像头时帧率对半砍，改用 MIPI-CSI 摄像头解决。
- **中文路径**：OpenCV 的 `imread` 在部分环境读不了中文路径，改用 `cv2.imdecode(np.fromfile(...))`。
- **结果输出**：板子上不要实时打印每帧日志，IO 会拖慢主循环，改为每 30 帧汇总一次。
