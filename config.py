"""检测参数集中管理：PC 调试与板子部署各一套，改这里即可。"""

# Haar 级联检测参数
SCALE_FACTOR = 1.15      # 图像金字塔缩放步长，越大越快、越容易漏检
MIN_NEIGHBORS = 4        # 候选框邻居数阈值，越大误检越少
MIN_SIZE = (40, 40)      # 最小人脸尺寸(像素)，按拍摄距离调整

# 实时流参数
FRAME_SCALE = 0.5        # 送入检测前的缩放比例，嵌入式性能开关
FRAME_SKIP = 2           # 每 N 帧检测一次，中间帧复用上次结果
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# 绘制
BOX_COLOR = (0, 255, 0)
BOX_THICKNESS = 2
FONT_SCALE = 0.6
