#!/bin/bash

echo "🚀 Starting GeekGirl Visual System..."

python3 geekgirl_visual/generator/generate_meta_pack.py
python3 geekgirl_visual/generator/generate_link_pack.py
python3 geekgirl_visual/generator/generate_meta_print_sheet.py

ls -l assets/preview/v1.0-alpha/print_sheet_meta.svg

echo "✅ All systems ready for tomorrow's class!"

