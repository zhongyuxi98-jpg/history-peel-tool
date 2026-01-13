import os

def generate_print_sheet():
    output_path = "assets/preview/v1.0-alpha/print_sheet_meta.svg"
    meta_dir = "assets/preview/v1.0-alpha/meta_logic"
    
    files = [f for f in os.listdir(meta_dir) if f.endswith('.svg')]
    files.sort()

    page_w, page_h = 210, 297
    margin = 15
    current_x = margin
    current_y = margin
    row_height = 0
    
    svg_elements = []

    for file in files:
        file_path = os.path.join(meta_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            start = content.find('>') + 1
            end = content.rfind('</svg>')
            inner_content = content[start:end]
            
            if "LK" in file:
                w, h = 60, 15
            else:
                w, h = 60, 30
            
            if current_x + w > page_w - margin:
                current_x = margin
                current_y += row_height + 5
                row_height = 0
            
            wrapped_content = f'<g transform="translate({current_x}, {current_y})">{inner_content}</g>'
            svg_elements.append(wrapped_content)
            
            current_x += w + 5
            row_height = max(row_height, h)

    full_svg = f'''<svg width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{page_w}" height="{page_h}" fill="white" />
    <text x="{margin}" y="10" font-family="Arial" font-size="5" font-weight="bold" fill="#333">GeekGirl Visual PEEL: Meta Logic Set (v1.0)</text>
    {''.join(svg_elements)}
    </svg>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_svg)
    print(f"🎉 拼版完成！文件位于: {output_path}")

if __name__ == "__main__":
    generate_print_sheet()
0

