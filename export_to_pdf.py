import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def convert_svg_to_pdf(svg_path, pdf_path):
    """将 SVG 转换为物理尺寸精确的 PDF"""
    print(f"正在转换: {svg_path} -> {pdf_path}")
    
    drawing = svg2rlg(svg_path)
    c = canvas.Canvas(pdf_path, pagesize=A4)

    # 绘制到页面左上角
    renderPDF.draw(drawing, c, 0, A4[1] - drawing.height)

    c.showPage()
    c.save()

def build_v1_print_package():
    version_dir = "assets/preview/v1.0-alpha/civil_rights"
    output_dir = "assets/dist/v1.0-alpha"
    os.makedirs(output_dir, exist_ok=True)
    
    files_to_convert = {
        "sheet_1.svg": "stickers_print_v1.pdf",
        "peel_template.svg": "board_print_v1.pdf"
    }
    
    for svg_name, pdf_name in files_to_convert.items():
        svg_path = os.path.join(version_dir, svg_name)
        pdf_path = os.path.join(output_dir, pdf_name)
        
        if os.path.exists(svg_path):
            convert_svg_to_pdf(svg_path, pdf_path)
        else:
            print(f"⚠️ 跳过: 找不到文件 {svg_path}")

if __name__ == "__main__":
    build_v1_print_package()
