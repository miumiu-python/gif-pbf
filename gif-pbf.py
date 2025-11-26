import subprocess
import os
import sys
import shutil
import glob

# ===== 配置 =====
DEFAULT_DURATION = 3  # 默认 GIF 秒数
FPS = 10
HEIGHT = 360
IMG_DIR = "img"

# ===== 命令行参数 =====
if len(sys.argv) < 2:
    print("请在命令行指定视频文件名（带后缀）")
    sys.exit(1)

VIDEO_FILE = sys.argv[1]

if not os.path.isfile(VIDEO_FILE):
    print(f"未找到视频文件: {VIDEO_FILE}")
    sys.exit(1)

basename, _ = os.path.splitext(VIDEO_FILE)
print(f"使用视频文件: {VIDEO_FILE}")

# ===== 自动识别书签文件 =====
PBF_FILE = f"{basename}.pbf"
if not os.path.isfile(PBF_FILE):
    print(f"书签文件 {PBF_FILE} 不存在！")
    sys.exit(1)

# ===== 读取书签 =====
bookmarks = []
with open(PBF_FILE, "r", encoding="utf-16") as f:
    for line in f:
        line = line.strip()
        if "=" in line and "*" in line:
            try:
                time_ms = line.split("=")[1].split("*")[0]
                bookmarks.append(int(time_ms) / 1000.0)
            except ValueError:
                print(f"跳过无法解析的书签行: {line}")

# ===== 统一设置 GIF 秒数 =====
duration = DEFAULT_DURATION  # 固定默认值，也可以改成命令行参数再传入

# ===== GIF 输出目录 = 输入文件名 =====
OUTPUT_DIR = basename
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"GIF 将生成在目录: {OUTPUT_DIR}")

# ===== 循环生成 GIF =====
for index, sec in enumerate(bookmarks):
    # 创建临时 PNG 文件夹
    if os.path.exists(IMG_DIR):
        shutil.rmtree(IMG_DIR)
    os.makedirs(IMG_DIR, exist_ok=True)

    # ===== FFmpeg 生成 PNG 序列 =====
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-v", "warning",
        "-ss", str(sec),
        "-t", str(duration),
        "-i", VIDEO_FILE,
        "-vf", f"fps={FPS},scale=-1:{HEIGHT}",
        os.path.join(IMG_DIR, "%03d.png")
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    # ===== 获取 PNG 文件 =====
    png_files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))

    # ===== gifski 生成 GIF =====
    output_gif = os.path.join(OUTPUT_DIR, f"{basename}_clip_{index:03d}.gif")
    gifski_cmd = [
        "gifski",
        "--fps", str(FPS),
        "--height", str(HEIGHT),
        "--quality", "100",
        "--output", output_gif
    ] + png_files

    subprocess.run(gifski_cmd, check=True)
    print(f"生成文件：{output_gif}")

# ===== 清理 =====
shutil.rmtree(IMG_DIR)
print("全部 GIF 已生成完成！")
