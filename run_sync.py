import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 定义当你修改代码时要执行的动作
class RebuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # 只要 core 目录下的 Python 文件或模板变动，就重新生成 HTML
        if event.src_path.endswith(".py"):
            print(f"🚀 检测到变化: {event.src_path}，正在自动重新生成...")
            print("✅ 任务列表已同步更新！")

if __name__ == "__main__":
    path = "core"  # 监听 core 文件夹
    event_handler = RebuildHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    
    print(f"👀 正在监听 '{path}' 目录下的变动...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
