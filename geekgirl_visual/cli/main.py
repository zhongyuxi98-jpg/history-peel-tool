import click
import os
import json
from geekgirl_visual.generator.sticker_generator import generate_svg

@click.group()
def cli():
    pass

@cli.command()
@click.option("--path", default="knowledge_base", help="知识库根目录")
def sync(path):
    """【极客同步】一键将所有 JSON 笔记转换为视觉贴纸"""
    click.secho("🔄 启动知识库同步流...", fg="cyan", bold=True)
    count = 0
    
    # 递归遍历 knowledge_base 文件夹
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".json"):
                # 读取笔记内容
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                    title = data.get("title", "UNTITLED")
                    level = data.get("level", "L2")
                    
                    # 生成存储路径
                    output_path = os.path.join("assets", "svg", f"{level}_{title}.svg")
                    
                    # 调用生成器画图
                    generate_svg(level, title, output_path)
                    click.echo(f"  📦 转换完成: {title} ({level})")
                    count += 1
                    
    click.secho(f"🚀 同步成功！共处理 {count} 个知识点。", fg="green", bold=True)

if __name__ == "__main__":
    cli()
