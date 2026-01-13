import os
for root, dirs, files in os.walk("."):
    print(f"📡 探测到文件夹: {root}")
    for f in files:
        print(f"  📄 发现文件: {f}")
