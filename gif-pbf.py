import subprocess
import os
import sys
import shutil
import glob

DEFAULT_DURATION = 3
FPS = 10
HEIGHT = 360
IMG_DIR = "img"

if len(sys.argv) < 2:
    print("请在命令行指定视频文件名（带后缀）")
    sys.exit(1)

VIDEO_FILE = sys.argv[1]
if not os.path.isfile(VIDEO_FILE):
    print(f"未找到视频文件: {VIDEO_FILE}")
    sys.exit(1)

basename, _ = os.path.splitext(VIDEO_FILE)
print(f"使用视频文件: {VIDEO_FILE}")

PBF_FILE = f"{basename}.pbf"
if not os.path.isfile(PBF_FILE):
    print(f"书签文件 {PBF_FILE} 不存在！")
    sys.exit(1)

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

user_input = input(f"请输入 GIF 秒数（默认 {DEFAULT_DURATION} 秒，回车使用默认）: ").strip()
try:
    duration = float(user_input) if user_input else DEFAULT_DURATION
except ValueError:
    print("输入无效，使用默认值")
    duration = DEFAULT_DURATION

OUTPUT_DIR = basename
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"GIF 将生成在目录: {OUTPUT_DIR}")

# ===== PyInstaller 打包后访问内置 exe =====
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

FFMPEG_EXE = os.path.join(base_path, "ffmpeg.exe")
GIFSKI_EXE = os.path.join(base_path, "gifski.exe")

for index, sec in enumerate(bookmarks):
    if os.path.exists(IMG_DIR):
        shutil.rmtree(IMG_DIR)
    os.makedirs(IMG_DIR, exist_ok=True)

    ffmpeg_cmd = [
        FFMPEG_EXE, "-y", "-v", "warning",
        "-ss", str(sec),
        "-t", str(duration),
        "-i", VIDEO_FILE,
        "-vf", f"fps={FPS},scale=-1:{HEIGHT}",
        os.path.join(IMG_DIR, "%03d.png")
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    png_files = sorted(glob.glob(os.path.join(IMG_DIR, "*.png")))
    output_gif = os.path.join(OUTPUT_DIR, f"{basename}_clip_{index:03d}.gif")

    gifski_cmd = [
        GIFSKI_EXE,
        "--fps", str(FPS),
        "--height", str(HEIGHT),
        "--quality", "100",
        "--output", output_gif
    ] + png_files
    subprocess.run(gifski_cmd, check=True)
    print(f"生成文件：{output_gif}")

shutil.rmtree(IMG_DIR)
print("全部 GIF 已生成完成！")
