import subprocess
import sys
import os

def run_step(command, description):
    print(f"\n--- 🚀 正在执行: {description} ---")
    try:
        result = subprocess.run([sys.executable] + command.split(), check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 步骤失败: {description}")
        return False

def main():
    # 确保 PYTHONPATH 包含当前目录
    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

    # 1. 自动化质检
    if not run_step("-m geekgirl_visual.generator.validation_check", "数据质量校验 (Validation)"):
        print("\n🚨 质检未通过，生产已终止。请修正 JSON 数据后重试。")
        sys.exit(1)

    # 2. 生成单个贴纸资源
    run_step("run_sync.py", "生成贴纸资源 (Individual SVG Generation)")

    # 3. 自动化拼版 (A4)
    run_step("-m geekgirl_visual.generator.tiling_generator", "自动化 A4 拼版 (Tiling)")

    # 4. 生成 PEEL 背景板（可选）
    if os.path.exists("geekgirl_visual/generator/generate_peel_boards.py"):
        run_step("-m geekgirl_visual.generator.generate_peel_boards", "生成 PEEL 交互背景板 (Template)")

    print("\n" + "🎉"*10)
    print("  生产任务全部圆满完成！")
    print("  请检查 assets/preview/ 目录查看成果。")
    print("🎉"*10)

if __name__ == "__main__":
    main()
