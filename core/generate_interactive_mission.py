import os

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PEEL Workspace - {mid}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; margin: 0; color: #333; }}
        .main-wrapper {{
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        .main {{ 
            flex: 1; 
            flex-grow: 1;
            padding: 40px; 
            overflow-y: auto;
            transition: margin-right 0.3s ease;
        }}

        /* 可折叠侧边栏 */
        .sidebar-toggle {{
            position: fixed;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 50px;
            height: 50px;
            background: #1d3557;
            color: white;
            border: none;
            border-radius: 12px 0 0 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            z-index: 1000;
            box-shadow: -2px 0 8px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }}
        .sidebar-toggle:hover {{
            background: #457b9d;
            width: 55px;
        }}
        .sidebar-toggle.collapsed {{
            right: 0;
        }}
        .sidebar-toggle.expanded {{
            right: 380px;
        }}
        
        /* 右侧双窗口：上方知识区可滚动；下方 explainer-window 固定 */
        .sidebar {{
            width: 380px;
            height: 100vh;
            background: #fff;
            border-left: 1px solid #dee2e6;
            padding: 25px;
            box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-sizing: border-box;
            overflow-y: auto;
            margin-right: -380px;
            transition: margin-right 0.3s ease;
        }}
        .sidebar.expanded {{
            margin-right: 0;
        }}
        .sidebar-content {{
            flex: 1;
            overflow-y: auto;
            padding-right: 6px; /* 给滚动条留空间 */
        }}
        
        /* 侧边栏遮罩层 */
        .sidebar-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            z-index: 998;
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .sidebar-overlay.visible {{
            display: block;
            opacity: 1;
        }}
        .header {{ border-bottom: 3px solid #1d3557; margin-bottom: 25px; padding-bottom: 15px; }}
        .q-text {{ font-size: 20px; font-weight: 700; color: #1d3557; }}
        .nav-bar {{ margin-bottom: 25px; display: flex; gap: 10px; }}
        
        button {{ border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: 0.2s; }}
        .btn-save {{ background: #2a9d8f; color: white; padding: 10px 18px; }}
        .btn-export {{ background: #f4a261; color: white; padding: 10px 18px; }}
        
        /* 💡 显式按钮样式 */
        .tag-row {{ display: flex; align-items: center; gap: 5px; margin-bottom: 8px; }}
        .tag {{ flex: 1; padding: 8px; border-radius: 4px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; border-left: 4px solid #457b9d; text-align: left; }}
        .tag:hover {{ background: #f8f9fa; }}
        .explain-btn {{ background: #457b9d; color: white; padding: 8px; font-size: 12px; border-radius: 4px; width: 35px; }}
        
        .editor-box {{ margin-bottom: 15px; position: relative; }}
        .label {{ color: #e63946; font-size: 11px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }}
        textarea {{ 
            width: 100%; 
            height: 95px; 
            border: none; 
            border-radius: 8px; 
            padding: 12px; 
            font-size: 14px; 
            resize: none; 
            line-height: 1.5; 
            box-sizing: border-box;
            background: #fafafa;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: box-shadow 0.2s;
        }}
        textarea:focus {{
            outline: none;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }}
        
        /* 字数统计 */
        .word-count {{
            position: absolute;
            bottom: 8px;
            right: 12px;
            font-size: 11px;
            color: #6c757d;
            background: rgba(255,255,255,0.9);
            padding: 2px 6px;
            border-radius: 4px;
            pointer-events: none;
        }}
        
        /* 全局字数统计气泡 */
        .global-word-count {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1d3557;
            color: white;
            padding: 12px 20px;
            border-radius: 24px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 100;
            pointer-events: none;
        }}
        
        /* Focus 按钮 */
        .focus-btn {{
            background: none;
            border: none;
            color: #667eea;
            font-size: 16px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .focus-btn:hover {{
            background: #f0f0f0;
        }}
        
        /* Focus Modal */
        .focus-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 10000;
            display: none;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .focus-modal.visible {{
            display: flex;
            opacity: 1;
        }}
        .focus-modal-content {{
            background: #fff;
            border-radius: 12px;
            padding: 30px;
            width: 90%;
            max-width: 900px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        .focus-modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e1e4e8;
        }}
        .focus-modal-title {{
            font-size: 18px;
            font-weight: 700;
            color: #1d3557;
        }}
        .focus-modal-close {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
        }}
        .focus-modal-close:hover {{
            background: #5a6268;
        }}
        .focus-textarea {{
            width: 100%;
            flex: 1;
            min-height: 400px;
            border: none;
            border-radius: 8px;
            padding: 20px;
            font-size: 16px;
            line-height: 1.8;
            resize: none;
            background: #fafafa;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            font-family: inherit;
            box-sizing: border-box;
        }}
        .focus-textarea:focus {{
            outline: none;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }}
        .focus-modal-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #e1e4e8;
        }}
        .focus-word-count {{
            font-size: 13px;
            color: #6c757d;
            font-weight: 600;
        }}
        .focus-save-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
        }}
        .focus-save-btn:hover {{
            background: #5568d3;
        }}

        /* Essay constructor layout */
        #module-toolbar {{ display:flex; flex-wrap:wrap; gap:8px; margin: 8px 0 16px 0; }}
        .toolbar-btn {{ padding:8px 12px; border-radius:999px; border:none; background:#1d3557; color:#fff; font-size:13px; cursor:pointer; }}
        .toolbar-btn.secondary {{ background:#6c757d; }}
        .toolbar-btn:hover {{ opacity:0.9; transform:translateY(-1px); }}

        #essay-constructor {{ display:flex; flex-direction:column; gap:14px; }}
        .essay-module {{ 
            border: none; 
            border-radius:10px; 
            padding:12px 14px; 
            background:#fff; 
            max-width: 1000px; 
            width: 100%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        .main {{ max-width: 1000px; width: 90%; }}
        .module-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; gap:8px; }}
        .module-controls-left {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; }}
        .module-controls-right {{ display:flex; align-items:center; gap:6px; }}
        .module-tag {{ font-size:12px; font-weight:700; text-transform:uppercase; color:#1d3557; }}
        .move-btn {{ border:1px solid #ced4da; background:#f8f9fa; border-radius:4px; padding:2px 6px; font-size:11px; cursor:pointer; }}
        .move-btn:hover {{ background:#e9ecef; }}
        .mode-toggle {{ border:none; background:#f1faee; color:#1d3557; border-radius:999px; padding:4px 10px; font-size:11px; cursor:pointer; }}
        .mode-toggle:hover {{ background:#e0fbfc; }}
        .module-delete {{ border:none; background:#fff; color:#e63946; cursor:pointer; font-size:14px; }}
        .module-delete:hover {{ color:#b02a37; }}

        .free-hint {{ font-size:11px; color:#6c757d; margin-top:4px; line-height:1.4; }}

        #export-preview {{ display:none; margin-top:24px; border:1px solid #dee2e6; border-radius:10px; padding:16px; background:#fff; }}
        #export-essay {{ line-height:1.7; font-size:14px; }}
        
        /* 👨‍🏫 右侧讲解老师窗口 */
        #explainer-window {{
            position: sticky;
            bottom: 0;
            background: #1d3557; /* 蓝色窗口 */
            border-radius: 12px;
            padding: 14px 14px 12px 14px;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 10px 30px rgba(29,53,87,0.25);
        }}
        #explain-box {{ font-size: 13px; line-height: 1.6; color: #f1faee; min-height: 110px; white-space: pre-wrap; }}

        /* Toast 提示样式 */
        #toast-container {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
            pointer-events: none;
        }}
        .toast {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            font-weight: 600;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: toastSlideIn 0.3s ease-out, toastFadeOut 0.3s ease-in 2.7s forwards;
            max-width: 600px;
        }}
        @keyframes toastSlideIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes toastFadeOut {{
            to {{ opacity: 0; transform: translateY(-20px); }}
        }}
        .toast-icon {{
            font-size: 20px;
        }}

        /* 🚀 底部 AI Review 样式 */
        .review-actions {{ display: flex; gap: 12px; margin: 30px 0; }}
        .ai-review-trigger {{ background: #e63946; color: white; flex: 1; padding: 20px; font-size: 18px; box-shadow: 0 4px 15px rgba(230,57,70,0.3); }}
        .preview-btn {{ background: #457b9d; color: white; flex: 1; padding: 20px; font-size: 18px; box-shadow: 0 4px 15px rgba(69,123,157,0.3); }}
        
        /* Preview Modal */
        #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; overflow-y: auto; }}
        #preview-modal .modal-content {{ background: #fff; margin: 40px auto; max-width: 1000px; width: 90%; border-radius: 12px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); position: relative; }}
        .modal-header {{ font-size: 24px; font-weight: 700; color: #1d3557; margin-bottom: 20px; }}
        .modal-body {{ max-height: 60vh; overflow-y: auto; padding: 20px; background: #f8f9fa; border-radius: 8px; line-height: 1.8; white-space: pre-wrap; }}
        .modal-body p {{ margin: 0 0 16px 0; }}
        .modal-body p:last-child {{ margin-bottom: 0; }}
        .modal-footer {{ display: flex; gap: 12px; margin-top: 20px; justify-content: flex-end; }}
        .modal-btn {{ padding: 12px 24px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }}
        .modal-btn-secondary {{ background: #6c757d; color: white; }}
        .modal-btn-primary {{ background: #e63946; color: white; }}
        
        /* 批改视图：左右双栏布局（同屏对照修改） */
        #feedback-view {{ display: none; margin-top: 30px; }}
        .feedback-container {{ display: flex; gap: 20px; min-height: 500px; }}
        .feedback-left {{
            flex: 1;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            max-height: 80vh;
        }}
        .feedback-right {{
            flex: 1;
            background: #fff;
            border: 2px solid #e63946;
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            max-height: 80vh;
        }}
        .feedback-left h3 {{ color: #1d3557; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }}
        .feedback-right h3 {{ color: #e63946; margin-bottom: 15px; }}
        .view-mode-toggle {{
            background: #457b9d;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
        }}
        .view-mode-toggle:hover {{ opacity: 0.9; }}
        
        /* 呼吸灯高亮效果 */
        @keyframes breathe {{
            0%, 100% {{ box-shadow: 0 0 0 rgba(102, 126, 234, 0); }}
            50% {{ box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }}
        }}
        .essay-module.highlight {{
            animation: breathe 2s ease-in-out infinite;
            border: 2px solid #667eea !important;
        }}
        
        /* AI Review 联动高亮动画 */
        @keyframes activeGlow {{
            0% {{
                background-color: transparent;
                box-shadow: inset 0 0 0 rgba(224, 187, 228, 0);
            }}
            16.66% {{
                background-color: rgba(224, 187, 228, 0.3);
                box-shadow: inset 0 0 20px rgba(224, 187, 228, 0.5);
            }}
            33.33% {{
                background-color: transparent;
                box-shadow: inset 0 0 0 rgba(224, 187, 228, 0);
            }}
            50% {{
                background-color: rgba(224, 187, 228, 0.3);
                box-shadow: inset 0 0 20px rgba(224, 187, 228, 0.5);
            }}
            66.66% {{
                background-color: transparent;
                box-shadow: inset 0 0 0 rgba(224, 187, 228, 0);
            }}
            83.33% {{
                background-color: rgba(224, 187, 228, 0.3);
                box-shadow: inset 0 0 20px rgba(224, 187, 228, 0.5);
            }}
            100% {{
                background-color: transparent;
                box-shadow: inset 0 0 0 rgba(224, 187, 228, 0);
            }}
        }}
        .essay-module.active-glow {{
            animation: activeGlow 2s ease-in-out;
        }}
        
        /* AI 反馈卡片样式 */
        .ai-feedback-card {{
            background: #fff;
            border-left: 4px solid #e63946;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .locate-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 8px;
        }}
        .locate-btn:hover {{ opacity: 0.9; }}
        
        #ai-review-result {{ border: 2px solid #e63946; border-radius: 12px; background: white; margin-bottom: 40px; overflow: hidden; }}
        
        /* 模式标签样式 */
        .mode-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-left: 12px;
        }}
        .mode-badge.audit {{
            background: #fff3cd;
            color: #856404;
        }}
        .mode-badge.practice {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        /* Mission Lab 抽屉样式 */
        #mission-lab-drawer .mission-card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            border: 2px solid #e1e4e8;
            display: flex;
            flex-direction: column;
            min-height: 200px;
        }}
        #mission-lab-drawer .mission-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        #mission-lab-drawer .mid-tag {{
            background: #e1f5fe;
            color: #0288d1;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            align-self: flex-start;
            margin-bottom: 15px;
        }}
        #mission-lab-drawer .mission-card h3 {{
            margin: 10px 0;
            color: #2c3e50;
            font-size: 1.4rem;
        }}
        #mission-lab-drawer .question-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 12px;
            margin-top: auto;
            border-radius: 4px;
        }}
        #mission-lab-drawer .question-box p {{
            margin: 0;
            font-style: italic;
            color: #5f6368;
            font-size: 0.95rem;
        }}
        
        /* 计时器样式 */
        .timer-container {{
            position: relative;
        }}
        .timer-btn {{
            background: #1d3557;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: background 0.2s;
        }}
        .timer-btn:hover {{
            background: #457b9d;
        }}
        .timer-panel {{
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 8px;
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            min-width: 280px;
            z-index: 1000;
            display: none;
        }}
        .timer-panel.visible {{
            display: block;
        }}
        .timer-display {{
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            margin: 16px 0;
            font-family: 'Courier New', monospace;
            color: #1d3557;
            transition: color 0.3s;
        }}
        .timer-display.warning {{
            color: #e63946;
            animation: timerBlink 1s ease-in-out infinite;
        }}
        @keyframes timerBlink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .timer-controls {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .timer-control-btn {{
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            transition: opacity 0.2s;
        }}
        .timer-control-btn:hover {{
            opacity: 0.9;
        }}
        .timer-start-btn {{
            background: #2a9d8f;
            color: white;
        }}
        .timer-pause-btn {{
            background: #f4a261;
            color: white;
        }}
        .timer-reset-btn {{
            background: #6c757d;
            color: white;
        }}
        .timer-mode-select {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .timer-mode-btn {{
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background: #f8f9fa;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .timer-mode-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        .timer-countdown-input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 14px;
            margin-top: 8px;
            box-sizing: border-box;
        }}
        .timer-countdown-label {{
            font-size: 12px;
            color: #6c757d;
            margin-top: 8px;
        }}
    </style>
</head>

<body>
    <div class="main-wrapper">
    <div class="main">
        <div class="nav-bar">
            <button class="btn-workspace" onclick="backToWorkspace()" style="background: #6c757d; color: white; padding: 10px 18px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600;">← Workspace</button>
            <button class="btn-save" onclick="save()">💾 SAVE</button>
            <button class="btn-mission-lab" onclick="showMissionLab()" style="background: #764ba2; color: white; padding: 10px 18px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600;">📚 Mission Lab</button>
            <select id="language-setting" style="padding: 10px; border-radius: 6px; border: 1.5px solid #007bff;">
                <option value="dual" selected>🌓 Dual-Language</option>
                <option value="en">🇬🇧 English Only</option>
                <option value="zh">🇨🇳 Chinese Only</option>
            </select>
            <div class="timer-container">
                <button class="timer-btn" onclick="toggleTimerPanel()">⏱️ Timer</button>
                <div class="timer-panel" id="timer-panel">
                    <div class="timer-display" id="timer-display">00:00:00</div>
                    <div class="timer-controls">
                        <button class="timer-control-btn timer-start-btn" id="timer-start-btn" onclick="startTimer()">Start</button>
                        <button class="timer-control-btn timer-pause-btn" id="timer-pause-btn" onclick="pauseTimer()" style="display: none;">Pause</button>
                        <button class="timer-control-btn timer-reset-btn" onclick="resetTimer()">Reset</button>
                    </div>
                    <div class="timer-mode-select">
                        <button class="timer-mode-btn active" id="timer-mode-up" onclick="setTimerMode('up')">Count Up</button>
                        <button class="timer-mode-btn" id="timer-mode-down" onclick="setTimerMode('down')">Count Down</button>
                    </div>
                    <div id="timer-countdown-input-container" style="display: none;">
                        <label class="timer-countdown-label">Set countdown (minutes):</label>
                        <input type="number" class="timer-countdown-input" id="timer-countdown-input" value="45" min="1" max="180" placeholder="45">
                    </div>
                </div>
            </div>
            <button class="btn-export" onclick="exportDoc()">📥 EXPORT + FEEDBACK</button>
        </div>

        <!-- Mission Lab 抽屉 -->
        <div id="mission-lab-drawer" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 2000; overflow-y: auto;">
            <div style="background: #fff; margin: 40px auto; max-width: 1000px; border-radius: 12px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                    <h2 style="font-size: 28px; color: #1d3557;">📚 Mission Lab</h2>
                    <button onclick="closeMissionLab()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600;">✕ Close</button>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px;">
                    <div class="mission-card" onclick="location.href='assets/missions/CR_M1_workspace.html'">
                        <span class="mid-tag">Mission CR_M1</span>
                        <h3>Opposition in the 1950s</h3>
                        <div class="question-box"><p>"Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."</p></div>
                    </div>
                    <div class="mission-card" onclick="location.href='assets/missions/CR_M2_workspace.html'">
                        <span class="mid-tag">Mission CR_M2</span>
                        <h3>Success in the 1950s</h3>
                        <div class="question-box"><p>"Evaluate how successful the Civil Rights movement was in the 1950s."</p></div>
                    </div>
                    <div class="mission-card" onclick="location.href='assets/missions/CR_M3_workspace.html'">
                        <span class="mid-tag">Mission CR_M3</span>
                        <h3>Federal Institutions</h3>
                        <div class="question-box"><p>"Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."</p></div>
                    </div>
                    <div class="mission-card" onclick="location.href='assets/missions/CR_M4_workspace.html'">
                        <span class="mid-tag">Mission CR_M4</span>
                        <h3>NAACP Effectiveness</h3>
                        <div class="question-box"><p>"Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."</p></div>
                    </div>
                    <div class="mission-card" onclick="location.href='assets/missions/CR_M5_workspace.html'">
                        <span class="mid-tag">Mission CR_M5</span>
                        <h3>Federal vs Grassroots</h3>
                        <div class="question-box"><p>"'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view."</p></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="header" id="header-section">
            <div style="color:#6c757d; font-size:11px; margin-bottom:5px;">
                MISSION ID: {mid}
                <span id="mode-badge" class="mode-badge" style="display:none;"></span>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                <h1 class="q-text" id="question-title" contenteditable="true" spellcheck="false" style="outline:none; margin:0; flex:1;">{question}</h1>
                <span title="Click to edit the question" style="font-size:18px; color:#457b9d;">✏️</span>
            </div>
        </div>

        <div id="module-toolbar">
            <button class="toolbar-btn" onclick="addModule('intro')">+ Add Intro</button>
            <button class="toolbar-btn" onclick="addModule('body')">+ Add Body (PEEL)</button>
            <button class="toolbar-btn" onclick="addModule('conclusion')">+ Add Conclusion</button>
        </div>

        <div id="essay-constructor"></div>

        <div class="review-actions">
            <button class="ai-review-trigger" id="ai-btn" onclick="showPreviewView()">🚀 SUBMIT FOR AI TEACHER'S REVIEW</button>
        </div>

        <!-- Preview View (直接显示，不再用 Modal) -->
        <div id="preview-view" style="display: none;">
            <div style="background: #fff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 1000px; width: 100%;">
                <div style="font-size: 24px; font-weight: 700; color: #1d3557; margin-bottom: 20px;">📄 Essay Preview</div>
                <div id="preview-content" style="max-height: 60vh; overflow-y: auto; padding: 20px; background: #f8f9fa; border-radius: 8px; line-height: 1.8; white-space: pre-wrap; margin-bottom: 20px;"></div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button class="modal-btn modal-btn-secondary" onclick="backFromPreview()">← Back to Edit</button>
                    <button class="modal-btn modal-btn-primary" onclick="confirmSubmitFromPreview()">✓ Confirm & Submit for Review</button>
                </div>
        </div>
    </div>

        <!-- 批改视图：左右双栏（同屏对照修改） -->
        <div id="feedback-view">
            <div class="feedback-container">
                <div class="feedback-left">
                    <h3>
                        📝 Your Essay
                        <button class="view-mode-toggle" id="view-mode-toggle" onclick="toggleEditViewMode()">Switch to Text Mode</button>
                    </h3>
                    <div id="feedback-essay-editable"></div>
                </div>
                <div class="feedback-right">
                    <h3>🎯 Academic Review</h3>
                    <div id="ai-content" style="line-height: 1.8; font-size: 15px;">AI is analyzing...</div>
                </div>
            </div>
            <div style="margin-top: 20px; text-align: center;">
                <button class="ai-review-trigger" id="resubmit-btn" onclick="resubmitForReview()" style="display: none;">🔄 Re-submit for Improved Score</button>
            </div>
        </div>

        <div id="export-preview">
            <div style="font-weight:700; margin-bottom:8px;">📄 Essay Preview</div>
            <div id="export-essay"></div>
        </div>
    </div>
    
    <!-- 侧边栏切换按钮 -->
    <button class="sidebar-toggle collapsed" id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle Knowledge Hub">📚</button>
    
    <!-- 侧边栏遮罩层 -->
    <div class="sidebar-overlay" id="sidebar-overlay" onclick="closeSidebar()"></div>

    <!-- 可折叠侧边栏 -->
    <div class="sidebar" id="knowledge-sidebar">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <h3 style="margin:0; color:#1d3557;">Knowledge Hub</h3>
            <button onclick="closeSidebar()" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #6c757d; padding: 0; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">✕</button>
        </div>
        <div class="sidebar-content">
            <div class="kb-section">
                <div style="font-size:12px; font-weight:800; color:#1d3557; margin-bottom:10px; border-bottom:1px solid #eee;">⚖️ LEGAL MILESTONES</div>
                    <div class="tag-row"><div class="tag" onclick="add('Brown v. Board (1954)')">Brown v. Board</div><button class="explain-btn" onclick="getExplanation('Brown v. Board')">💡</button></div>
                    <div class="tag-row"><div class="tag" onclick="add('Civil Rights Act (1957)')">1957 CR Act</div><button class="explain-btn" onclick="getExplanation('Civil Rights Act 1957')">💡</button></div>
            </div>

            <div class="kb-section" style="margin-top:20px;">
                <div style="font-size:12px; font-weight:800; color:#1d3557; margin-bottom:10px; border-bottom:1px solid #eee;">✊ DIRECT ACTION</div>
                    <div class="tag-row"><div class="tag" onclick="add('Montgomery Bus Boycott (1955–56)')">Bus Boycott</div><button class="explain-btn" onclick="getExplanation('Montgomery Bus Boycott')">💡</button></div>
                    <div class="tag-row"><div class="tag" onclick="add('Little Rock Nine (1957)')">Little Rock 9</div><button class="explain-btn" onclick="getExplanation('Little Rock Nine')">💡</button></div>
                    <div class="tag-row"><div class="tag" onclick="add('Jim Crow laws')">Jim Crow</div><button class="explain-btn" onclick="getExplanation('Jim Crow laws')">💡</button></div>
                </div>
            </div>

            <div id="explainer-window">
                <div style="font-weight:800; color:#a8dadc; font-size:11px; margin-bottom:8px; display:flex; justify-content:space-between;">
                    <span>👨‍🏫 KNOWLEDGE EXPLORER</span>
                    <span style="cursor:pointer" onclick="document.getElementById('explain-box').innerText='Click the 💡 button for detailed context.'">Reset</span>
                </div>
                <div id="explain-box">Click the 💡 button for detailed context.</div>
            </div>
        </div>
    </div>
    </div>

    <!-- Toast 容器 -->
    <div id="toast-container"></div>
    
    <!-- 全局字数统计气泡 -->
    <div class="global-word-count" id="global-word-count">0 words</div>
    
    <!-- Focus Modal -->
    <div class="focus-modal" id="focus-modal" onclick="if(event.target===this) closeFocusMode()">
        <div class="focus-modal-content" onclick="event.stopPropagation()">
            <div class="focus-modal-header">
                <div class="focus-modal-title" id="focus-modal-title">Focus Mode</div>
                <button class="focus-modal-close" onclick="closeFocusMode()">✕ Close</button>
            </div>
            <textarea 
                class="focus-textarea" 
                id="focus-textarea"
                placeholder="Write your content here..."
                oninput="onFocusInput(); updateFocusWordCount();"
            ></textarea>
            <div class="focus-modal-footer">
                <div class="focus-word-count" id="focus-word-count">0 words</div>
                <button class="focus-save-btn" onclick="saveFocusMode()">Save & Close</button>
            </div>
        </div>
    </div>


    <script>
        const ID = "{mid}";

        // --- 0. 全局状态 ---
        let currentLanguageMode = document.getElementById('language-setting').value || 'dual';
        let modules = []; // {{ id, type: 'intro'|'body'|'conclusion', boxes: [] }}
        let activeTextarea = null;
        let workspaceMode = 'practice'; // 'audit' or 'practice'

        const STORAGE_KEY = `GGV1_STATE::${{ID}}`;
        let saveDebounceTimer = null;

        // --- 0.0 模式检测与初始化 ---
        function detectWorkspaceMode() {{
            const mode = localStorage.getItem('workspaceMode') || 'practice';
            workspaceMode = mode;
            
            // 显示模式标签
            const badge = document.getElementById('mode-badge');
            if (badge) {{
                if (mode === 'audit') {{
                    badge.className = 'mode-badge audit';
                    badge.innerText = 'Audit Mode';
                    badge.style.display = 'inline-block';
                }} else {{
                    badge.className = 'mode-badge practice';
                    badge.innerText = 'Practice Mode';
                    badge.style.display = 'inline-block';
                }}
            }}
            
            // Audit Mode：隐藏题目背景和 Knowledge Hub
            if (mode === 'audit') {{
                const header = document.getElementById('header-section');
                const sidebar = document.querySelector('.sidebar');
                const sidebarToggle = document.getElementById('sidebar-toggle');
                const toolbar = document.getElementById('module-toolbar');
                
                if (header) header.style.display = 'none';
                if (sidebar) sidebar.style.display = 'none';
                if (sidebarToggle) sidebarToggle.style.display = 'none';
                if (toolbar) toolbar.style.display = 'none';
            }}
            
            return mode;
        }}

        // --- 0.1 实用函数 ---
        function getLanguageConstraint() {{
            if (currentLanguageMode === 'en') return "Constraint: You must respond in 100% English. Do not use any Chinese characters.";
            if (currentLanguageMode === 'zh') return "约束：必须 100% 使用中文回答，即使问题是英文。";
            return "约束：使用双语回答。采用‘中文核心解释 + 括号内对应英文专业术语’的格式。";
        }}

        function getCurrentQuestion() {{
            const title = document.getElementById('question-title');
            const text = (title?.innerText || "").trim();
            return text || "{question}";
        }}

        function setActiveTextarea(el) {{
            activeTextarea = el;
        }}

        // --- 0.2 模块与占位符 ---
        function makeModuleId() {{
            return 'm_' + Math.random().toString(36).slice(2, 9) + Date.now().toString(36);
        }}

        function getBoxConfig(type) {{
            if (type === 'intro') {{
                return [
                    {{ label: "Intro Box 1", placeholder: "Define issue & background... (e.g., The issue of [topic] was significant...)" }},
                    {{ label: "Intro Box 2", placeholder: "Show debate... (e.g., Historians have debated...)" }},
                    {{ label: "Intro Box 3", placeholder: "Thesis statement... (e.g., This essay will argue that...)" }}
                ];
            }} else if (type === 'conclusion') {{
                return [
                    {{ label: "Conclusion Box 1", placeholder: "Direct answer (In conclusion...)" }},
                    {{ label: "Conclusion Box 2", placeholder: "Weighting judgement (Their impact was mainly...)" }},
                    {{ label: "Conclusion Box 3", placeholder: "Final evaluation (While [success], [limitation]...)" }}
                ];
            }} else {{
                return [
                    {{ label: "PEEL Box 1", placeholder: "Point (One important way...)" }},
                    {{ label: "PEEL Box 2", placeholder: "Evidence (This can be seen in...)" }},
                    {{ label: "PEEL Box 3", placeholder: "Explain (This was important because...)" }},
                    {{ label: "PEEL Box 4", placeholder: "Link back (Therefore, this shows...)" }}
                ];
            }}
        }}

        function createEmptyModule(type) {{
            const cfg = getBoxConfig(type);
            return {{
                id: makeModuleId(),
                type,
                boxes: new Array(cfg.length).fill(""),
                mode: 'guided',
                freeText: ""
            }};
        }}

        // --- 0.3 保存 / 恢复 ---
        function getState() {{
            return {{
                question: getCurrentQuestion(),
                language: currentLanguageMode,
                modules,
                updatedAt: Date.now()
            }};
        }}

        function saveToLocal() {{
            try {{
                localStorage.setItem(STORAGE_KEY, JSON.stringify(getState()));
            }} catch (e) {{}}
        }}

        function scheduleSave() {{
            if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
            saveDebounceTimer = setTimeout(() => saveToLocal(), 2000);
        }}

        function loadFromLocal() {{
            try {{
                const raw = localStorage.getItem(STORAGE_KEY);
                if (!raw) return;
                const s = JSON.parse(raw);
                if (s.question) document.getElementById('question-title').innerText = s.question;
                if (s.language) {{
                    currentLanguageMode = s.language;
                    document.getElementById('language-setting').value = s.language;
                }}
                if (Array.isArray(s.modules) && s.modules.length) {{
                    modules = s.modules;
                }}
            }} catch (e) {{}}
        }}

        // --- 1. 模块渲染与编辑 ---
        function renderModules() {{
            const container = document.getElementById('essay-constructor');
            if (!container) return;

            if (!modules.length) {{
                container.innerHTML = '<div style="color:#6c757d; font-size:13px;">Use the buttons above to add an Intro, Body paragraph, or Conclusion.</div>';
                return;
            }}

            let bodyIndex = 0;
            let introIndex = 0;
            let conclusionIndex = 0;
            const html = modules.map((m) => {{
                const cfg = getBoxConfig(m.type);
                const isFree = m.mode === 'free';
                let label = "";
                let blockId = "";
                if (m.type === 'intro') {{
                    introIndex += 1;
                    label = "Intro";
                    blockId = `intro-${{introIndex}}`;
                }} else if (m.type === 'conclusion') {{
                    conclusionIndex += 1;
                    label = "Conclusion";
                    blockId = `conclusion-${{conclusionIndex}}`;
                }} else {{
                    bodyIndex += 1;
                    label = "Body Paragraph " + bodyIndex;
                    blockId = `body-${{bodyIndex}}`;
                }}

                const modeLabel = isFree ? 'Free' : 'Guided';
                const modeIcon = isFree ? '📝' : '🧩';

                let bodyHtml = "";
                if (isFree) {{
                    const freeText = (m.freeText || (Array.isArray(m.boxes) ? m.boxes.join(" ") : ""));
                    const hintLines = getBoxConfig(m.type).map((c, i) => (i + 1) + '. ' + c.placeholder).join('<br>');
                    const wordCount = countWords(freeText);
                    bodyHtml = `
                        <div class="editor-box">
                            <div class="label">Freeform ${{label}}</div>
                            <textarea
                                data-module="${{m.id}}"
                                data-free="1"
                                placeholder="Write your ${{label.toLowerCase()}} in full sentences here..."
                                onfocus="setActiveTextarea(this)"
                                oninput="onFreeInput('${{m.id}}', this.value); updateWordCount(this);"
                            >${{freeText}}</textarea>
                            <div class="word-count">${{wordCount}} words</div>
                            <div class="free-hint">${{hintLines}}</div>
                        </div>
                    `;
                }} else {{
                    const boxesHtml = cfg.map((boxCfg, idx) => {{
                        const value = (m.boxes && typeof m.boxes[idx] === 'string') ? m.boxes[idx] : "";
                        const wordCount = countWords(value);
                        return `
                            <div class="editor-box">
                                <div class="label">${{boxCfg.label}}</div>
                                <textarea 
                                    data-module="${{m.id}}" 
                                    data-box="${{idx}}" 
                                    placeholder="${{boxCfg.placeholder}}"
                                    onfocus="setActiveTextarea(this)"
                                    oninput="onBoxInput('${{m.id}}', ${{idx}}, this.value); updateWordCount(this);"
                                >${{value}}</textarea>
                                <div class="word-count">${{wordCount}} words</div>
                            </div>
                        `;
                    }}).join("");
                    bodyHtml = boxesHtml;
                }}

                return `
                    <div class="essay-module" data-id="${{m.id}}" data-block-id="${{blockId}}">
                        <div class="module-header">
                            <div class="module-controls-left">
                                <button class="move-btn" onclick="moveModule('${{m.id}}', -1)">↑</button>
                                <button class="move-btn" onclick="moveModule('${{m.id}}', 1)">↓</button>
                                <span class="module-tag">${{label}}</span>
                            </div>
                            <div class="module-controls-right">
                                <button class="focus-btn" onclick="openFocusMode('${{m.id}}')" title="Focus Mode">🔍</button>
                                <button class="mode-toggle" onclick="toggleModuleMode('${{m.id}}')">${{modeIcon}} ${{modeLabel}}</button>
                                <button class="module-delete" onclick="confirmRemoveModule('${{m.id}}')">✕</button>
                            </div>
                        </div>
                        ${{bodyHtml}}
                    </div>
                `;
            }}).join("");

            container.innerHTML = html;
        }}

        function addModule(type) {{
            modules.push(createEmptyModule(type));
            renderModules();
            saveToLocal();
        }}

        function removeModule(id) {{
            modules = modules.filter(m => m.id !== id);
            renderModules();
            saveToLocal();
        }}

        function confirmRemoveModule(id) {{
            if (confirm('Delete this module? This action cannot be undone.')) {{
                removeModule(id);
            }}
        }}

        function onBoxInput(id, index, value) {{
            const m = modules.find(m => m.id === id);
            if (!m) return;
            if (!Array.isArray(m.boxes)) m.boxes = [];
            m.boxes[index] = value;
            scheduleSave();
            updateGlobalWordCount();
        }}
        
        function onFreeInput(id, value) {{
            const m = modules.find(m => m.id === id);
            if (!m) return;
            m.freeText = value;
            scheduleSave();
            updateGlobalWordCount();
        }}
        
        // --- 核心计算逻辑（与 DOM 解耦，便于迁移到小程序）---
        
        /**
         * 计算文本字数（纯函数，无 DOM 依赖）
         * @param {{string}} text - 待统计的文本
         * @returns {{number}} 字数
         */
        function countWords(text) {{
            if (!text || !text.trim()) return 0;
            return text.trim().split(/\\s+/).filter(w => w.length > 0).length;
        }}
        
        /**
         * 计算单个模块的字数（纯函数）
         * @param {{Object}} module - 模块对象
         * @returns {{number}} 该模块的字数
         */
        function calculateModuleWordCount(module) {{
            if (!module) return 0;
            if (module.mode === 'free') {{
                return countWords(module.freeText || '');
            }} else if (Array.isArray(module.boxes)) {{
                return module.boxes.reduce((total, box) => total + countWords(box || ''), 0);
            }}
            return 0;
        }}
        
        /**
         * 计算所有模块的总字数（纯函数）
         * @param {{Array}} modulesArray - 模块数组
         * @returns {{number}} 总字数
         */
        function calculateTotalWordCount(modulesArray) {{
            if (!Array.isArray(modulesArray)) return 0;
            return modulesArray.reduce((total, m) => total + calculateModuleWordCount(m), 0);
        }}
        
        /**
         * 分析 PEEL 结构（纯函数）
         * @param {{Array}} modulesArray - 模块数组
         * @returns {{Object}} 结构分析结果
         */
        function analyzePEELStructure(modulesArray) {{
            if (!Array.isArray(modulesArray)) return {{ intro: 0, body: 0, conclusion: 0, total: 0 }};
            
            const analysis = {{
                intro: 0,
                body: 0,
                conclusion: 0,
                total: modulesArray.length,
                modules: modulesArray.map(m => ({{
                    type: m.type,
                    wordCount: calculateModuleWordCount(m),
                    mode: m.mode || 'guided'
                }}))
            }};
            
            modulesArray.forEach(m => {{
                if (m.type === 'intro') analysis.intro++;
                else if (m.type === 'body') analysis.body++;
                else if (m.type === 'conclusion') analysis.conclusion++;
            }});
            
            return analysis;
        }}
        
        /**
         * 构建完整 Essay 文本（纯函数）
         * @param {{Array}} modulesArray - 模块数组
         * @returns {{string}} 完整的 Essay 文本
         */
        function buildEssayTextFromModules(modulesArray) {{
            if (!Array.isArray(modulesArray)) return '';
            
            const parts = [];
            modulesArray.forEach((m) => {{
                let text = "";
                if (m.mode === 'free') {{
                    text = (m.freeText || "").trim();
                }} else if (Array.isArray(m.boxes)) {{
                    text = m.boxes.map(b => (b || "").trim()).filter(Boolean).join(" ");
                }}
                if (!text) return;
                let prefix = "";
                if (m.type === 'intro') prefix = "[Intro] ";
                else if (m.type === 'conclusion') prefix = "[Conclusion] ";
                else prefix = "[Body] ";
                parts.push(prefix + text);
            }});
            return parts.join("\\n\\n");
        }}
        
        /**
         * 获取结构摘要（纯函数）
         * @param {{Array}} modulesArray - 模块数组
         * @returns {{Array}} 结构摘要数组
         */
        function getStructureSummaryFromModules(modulesArray) {{
            if (!Array.isArray(modulesArray)) return [];
            
            return modulesArray.map((m) => ({{
                type: m.type,
                text: m.mode === 'free'
                    ? (m.freeText || "").trim()
                    : (Array.isArray(m.boxes) ? m.boxes.join(" ").trim() : "")
            }}));
        }}
        
        // --- DOM 更新函数（依赖核心计算逻辑）---
        
        function updateWordCount(textarea) {{
            const wordCountEl = textarea.parentElement.querySelector('.word-count');
            if (wordCountEl) {{
                const count = countWords(textarea.value);
                wordCountEl.textContent = count + ' words';
            }}
        }}
        
        function updateGlobalWordCount() {{
            const globalCountEl = document.getElementById('global-word-count');
            if (!globalCountEl) return;
            
            const totalWords = calculateTotalWordCount(modules);
            globalCountEl.textContent = totalWords + ' words';
        }}
        
        // --- Focus Mode 功能 ---
        let currentFocusModuleId = null;
        
        function openFocusMode(moduleId) {{
            const m = modules.find(m => m.id === moduleId);
            if (!m) return;
            
            currentFocusModuleId = moduleId;
            const modal = document.getElementById('focus-modal');
            const textarea = document.getElementById('focus-textarea');
            const title = document.getElementById('focus-modal-title');
            
            if (!modal || !textarea || !title) return;
            
            // 确定标签
            let label = "";
            if (m.type === 'intro') label = "Intro";
            else if (m.type === 'conclusion') label = "Conclusion";
            else {{
                const bodyIdx = modules.filter(mm => mm.type === 'body' && modules.indexOf(mm) <= modules.indexOf(m)).length;
                label = "Body Paragraph " + bodyIdx;
            }}
            
            title.textContent = `Focus Mode: ${{label}}`;
            
            // 获取内容
            let content = "";
            if (m.mode === 'free') {{
                content = m.freeText || "";
            }} else if (Array.isArray(m.boxes)) {{
                content = m.boxes.map(b => (b || "").trim()).filter(Boolean).join("\\n\\n");
            }}
            
            textarea.value = content;
            updateFocusWordCount();
            
            modal.classList.add('visible');
            textarea.focus();
        }}
        
        function closeFocusMode() {{
            const modal = document.getElementById('focus-modal');
            if (modal) {{
                modal.classList.remove('visible');
            }}
            currentFocusModuleId = null;
        }}
        
        function onFocusInput() {{
            // Focus Mode 下的输入实时更新（但不立即保存到模块，等 Save 时再保存）
        }}
        
        function updateFocusWordCount() {{
            const textarea = document.getElementById('focus-textarea');
            const countEl = document.getElementById('focus-word-count');
            if (textarea && countEl) {{
                const count = countWords(textarea.value);
                countEl.textContent = count + ' words';
            }}
        }}
        
        function saveFocusMode() {{
            if (!currentFocusModuleId) return;
            
            const m = modules.find(m => m.id === currentFocusModuleId);
            const textarea = document.getElementById('focus-textarea');
            if (!m || !textarea) return;
            
            const content = textarea.value;
            
            if (m.mode === 'free') {{
                m.freeText = content;
            }} else {{
                // 如果是 Guided 模式，按段落拆分回 boxes
                const paragraphs = content.split(/\\n{{2,}}|\\n/).filter(p => p.trim());
                const cfg = getBoxConfig(m.type);
                m.boxes = new Array(cfg.length).fill("");
                for (let i = 0; i < cfg.length && i < paragraphs.length; i++) {{
                    m.boxes[i] = paragraphs[i];
                }}
            }}
            
            saveToLocal();
            renderModules();
            updateGlobalWordCount();
            closeFocusMode();
        }}

        function toggleModuleMode(id) {{
            // 致命 Bug 修复：切换前强制保存
            saveToLocal();
            
            const m = modules.find(m => m.id === id);
            if (!m) return;
            const cfg = getBoxConfig(m.type);
            if (!m.mode || m.mode === 'guided') {{
                const parts = Array.isArray(m.boxes) ? m.boxes.map(b => (b || '').trim()).filter(Boolean) : [];
                m.freeText = parts.join("\\n\\n");
                m.mode = 'free';
            }} else {{
                const maxBoxes = cfg.length;
                const src = (m.freeText || '').split(/\\n{{2,}}|\\n/).filter(Boolean);
                m.boxes = new Array(maxBoxes).fill("");
                for (let i = 0; i < maxBoxes; i++) {{
                    if (i < src.length - 1) {{
                        m.boxes[i] = src[i];
                    }} else if (i === maxBoxes - 1 && src.length) {{
                        m.boxes[i] = src.slice(i).join(' ');
                        break;
                    }}
                }}
                m.mode = 'guided';
            }}
            
            // 渲染新模式的 DOM
            renderModules();
            
            // 重新绑定事件监听器（确保字数统计等功能正常工作）
            setTimeout(() => {{
                updateGlobalWordCount();
                // 重新绑定所有 textarea 的 input 事件
                document.querySelectorAll('textarea[data-module]').forEach(textarea => {{
                    if (!textarea.hasAttribute('data-listener-bound')) {{
                        textarea.setAttribute('data-listener-bound', 'true');
                        textarea.addEventListener('input', () => {{
                            updateGlobalWordCount();
                            updateWordCount(textarea);
                        }});
                    }}
                }});
            }}, 100);
        }}

        function moveModule(id, direction) {{
            const idx = modules.findIndex(m => m.id === id);
            if (idx === -1) return;
            const next = idx + direction;
            if (next < 0 || next >= modules.length) return;
            const tmp = modules[idx];
            modules[idx] = modules[next];
            modules[next] = tmp;
            renderModules();
            saveToLocal();
        }}

        // --- 2. 全文构建（使用核心计算逻辑）---
        function buildEssayText() {{
            return buildEssayTextFromModules(modules);
        }}

        function getStructureSummary() {{
            return getStructureSummaryFromModules(modules);
        }}

        function buildEssayHtml() {{
            const parts = [];
            let bodyIndex = 0;
            modules.forEach((m) => {{
                let title = "";
                if (m.type === 'intro') title = "Introduction";
                else if (m.type === 'conclusion') title = "Conclusion";
                else {{
                    bodyIndex += 1;
                    title = "Body Paragraph " + bodyIndex;
                }}
                let text = "";
                if (m.mode === 'free') {{
                    text = (m.freeText || "").trim();
                }} else if (Array.isArray(m.boxes)) {{
                    text = m.boxes.map(b => (b || "").trim()).filter(Boolean).join(" ");
                }}
                if (!text) return;
                const safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
                parts.push(
                    `<h4 style="margin:8px 0 4px 0;">${{title}}</h4>` +
                    `<p style="margin:0 0 8px 0;">${{safe}}</p>`
                );
            }});
            return parts.join('');
        }}

        // --- 3. 语言与自动保存事件 ---
        document.getElementById('language-setting').addEventListener('change', (e) => {{
            currentLanguageMode = e.target.value;
            saveToLocal();
        }});

        document.getElementById('question-title').addEventListener('blur', () => saveToLocal());

        // --- 4. 知识 Hub 插入：针对当前激活 textarea ---
        function add(text) {{
            if (!activeTextarea) return;
            const start = activeTextarea.selectionStart ?? activeTextarea.value.length;
            const end = activeTextarea.selectionEnd ?? start;
            const v = activeTextarea.value;
            activeTextarea.value = v.substring(0, start) + text + " " + v.substring(end);
            activeTextarea.focus();

            const mId = activeTextarea.getAttribute('data-module');
            const idxStr = activeTextarea.getAttribute('data-box');
            const idx = idxStr ? parseInt(idxStr, 10) : NaN;
            if (mId && !Number.isNaN(idx)) {{
                onBoxInput(mId, idx, activeTextarea.value);
            }}
        }}

        // --- 5. 侧边栏讲解老师 ---
        async function getExplanation(topic) {{
            const box = document.getElementById('explain-box');
            const lang = currentLanguageMode;
            const constraint = getLanguageConstraint();
            const essay_question = getCurrentQuestion();
            box.innerHTML = `<i style="color:#666">🔍 Searching...</i>`;
            try {{
                const response = await fetch('/api/explain', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ 
                        topic,
                        language: lang,
                        essay_question,
                        structure: getStructureSummary(),
                        constraint
                    }})
                }});
                const result = await response.json();
                box.innerText = result.explanation || "No explanation found.";
            }} catch (e) {{ box.innerText = "⚠️ Connection error."; }}
        }}

        // --- 6. 预览视图逻辑（精简流程：直接显示，无 Modal） ---
        function showPreviewView() {{
            const previewView = document.getElementById('preview-view');
            const content = document.getElementById('preview-content');
            if (!previewView || !content) return;
            
            const essayText = buildEssayText();
            if (!essayText.trim()) {{
                alert('Please write something before previewing.');
                return;
            }}
            
            // 格式化文本：按段落清晰排版
            const formatted = essayText
                .split('\\n\\n')
                .map(p => p.trim())
                .filter(p => p.length > 0)
                .join('\\n\\n');
            
            content.innerText = formatted;
            
            // 隐藏编辑区，显示预览视图
            document.getElementById('essay-constructor').style.display = 'none';
            document.getElementById('module-toolbar').style.display = 'none';
            document.querySelector('.review-actions').style.display = 'none';
            previewView.style.display = 'block';
            previewView.scrollIntoView({{ behavior: 'smooth' }});
        }}

        function backFromPreview() {{
            const previewView = document.getElementById('preview-view');
            const constructor = document.getElementById('essay-constructor');
            const toolbar = document.getElementById('module-toolbar');
            const actions = document.querySelector('.review-actions');
            
            if (previewView) previewView.style.display = 'none';
            if (constructor) constructor.style.display = 'block';
            if (toolbar) toolbar.style.display = 'flex';
            if (actions) actions.style.display = 'flex';
            
            constructor.scrollIntoView({{ behavior: 'smooth' }});
        }}

        function confirmSubmitFromPreview() {{
            // 直接提交，无需关闭预览
            submitReview();
        }}

        // --- 7. 底部批改：整篇 Essay 级别（同屏对照修改） ---
        let isResubmit = false;
        let previousReview = "";
        
        async function submitReview(isResubmitFlag = false) {{
            isResubmit = isResubmitFlag;
            const btn = document.getElementById('ai-btn');
            const feedbackView = document.getElementById('feedback-view');
            const editableArea = document.getElementById('feedback-essay-editable');
            const contentDiv = document.getElementById('ai-content');
            const resubmitBtn = document.getElementById('resubmit-btn');
            const essay_question = getCurrentQuestion();
            const constraint = getLanguageConstraint();
            const essay_full = buildEssayText();
            const structure = getStructureSummary();

            const data = {{ 
                essay_question,
                essay_full,
                structure,
                language: currentLanguageMode,
                constraint,
                is_resubmit: isResubmit,
                previous_review: previousReview
            }};
            
            // 隐藏编辑区，显示批改视图
            document.getElementById('essay-constructor').style.display = 'none';
            document.getElementById('module-toolbar').style.display = 'none';
            document.querySelector('.review-actions').style.display = 'none';
            feedbackView.style.display = 'block';
            
            // 左侧显示可编辑的模块（PEEL 格子模式）
            renderEditableModules(editableArea);
            
            btn.innerText = "⌛ Teacher is grading..."; btn.disabled = true;
            contentDiv.innerText = "AI is analyzing your essay...";
            if (resubmitBtn) resubmitBtn.style.display = 'none';

            try {{
                const response = await fetch('/api/review', {{ 
                    method: 'POST', 
                    headers: {{ 'Content-Type': 'application/json' }}, 
                    body: JSON.stringify(data) 
                }});
                const result = await response.json();
                previousReview = result.review || "";
                renderAIFeedback(contentDiv, previousReview);
                if (resubmitBtn) resubmitBtn.style.display = 'block';
            }} catch (e) {{ contentDiv.innerText = "⚠️ Connection failed."; }}
            finally {{ 
                btn.innerText = "🚀 SUBMIT FOR AI TEACHER'S REVIEW"; 
                btn.disabled = false;
                feedbackView.scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // 渲染可编辑模块（在 Review 页面左侧）
        function renderEditableModules(container) {{
            if (!container) return;
            let bodyIndex = 0;
            let introIndex = 0;
            let conclusionIndex = 0;
            const html = modules.map((m) => {{
                const cfg = getBoxConfig(m.type);
                let label = "";
                let blockId = "";
                if (m.type === 'intro') {{
                    introIndex += 1;
                    label = "Intro";
                    blockId = `intro-${{introIndex}}`;
                }} else if (m.type === 'conclusion') {{
                    conclusionIndex += 1;
                    label = "Conclusion";
                    blockId = `conclusion-${{conclusionIndex}}`;
                }} else {{
                    bodyIndex += 1;
                    label = "Body Paragraph " + bodyIndex;
                    blockId = `body-${{bodyIndex}}`;
                }}
                
                if (m.mode === 'free') {{
                    const freeText = (m.freeText || "").trim();
                    return `
                        <div class="essay-module" data-id="${{m.id}}" data-type="${{m.type}}" data-block-id="${{blockId}}">
                            <div class="module-header">
                                <span class="module-tag">${{label}}</span>
                            </div>
                            <div class="editor-box">
                                <textarea 
                                    data-module="${{m.id}}"
                                    data-free="1"
                                    style="width:100%; min-height:120px; padding:12px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.5;"
                                    oninput="onFreeInput('${{m.id}}', this.value)"
                                >${{freeText}}</textarea>
                            </div>
                        </div>
                    `;
                }} else {{
                    const boxesHtml = cfg.map((boxCfg, idx) => {{
                        const value = (m.boxes && typeof m.boxes[idx] === 'string') ? m.boxes[idx] : "";
                        return `
                            <div class="editor-box">
                                <div class="label">${{boxCfg.label}}</div>
                                <textarea 
                                    data-module="${{m.id}}" 
                                    data-box="${{idx}}" 
                                    style="width:100%; height:95px; padding:12px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.5;"
                                    oninput="onBoxInput('${{m.id}}', ${{idx}}, this.value)"
                                >${{value}}</textarea>
                            </div>
                        `;
                    }}).join("");
                    return `
                        <div class="essay-module" data-id="${{m.id}}" data-type="${{m.type}}" data-block-id="${{blockId}}">
                            <div class="module-header">
                                <span class="module-tag">${{label}}</span>
                            </div>
                            ${{boxesHtml}}
                        </div>
                    `;
                }}
            }}).join("");
            container.innerHTML = html;
        }}

        // 切换编辑视图模式（PEEL 格子 / 纯文本）
        let editViewMode = 'peel'; // 'peel' or 'text'
        function toggleEditViewMode() {{
            const container = document.getElementById('feedback-essay-editable');
            const toggleBtn = document.getElementById('view-mode-toggle');
            if (!container) return;
            
            editViewMode = editViewMode === 'peel' ? 'text' : 'peel';
            
            if (editViewMode === 'text') {{
                // 切换到纯文本模式
                const essayText = buildEssayText();
                container.innerHTML = `
                    <textarea 
                        id="essay-text-editor"
                        style="width:100%; min-height:400px; padding:20px; border:1.5px solid #ced4da; border-radius:8px; font-size:14px; line-height:1.8; font-family:inherit;"
                        oninput="onTextEditorInput(this.value)"
                    >${{essayText}}</textarea>
                `;
                if (toggleBtn) toggleBtn.innerText = 'Switch to PEEL Mode';
            }} else {{
                // 切换回 PEEL 格子模式
                renderEditableModules(container);
                if (toggleBtn) toggleBtn.innerText = 'Switch to Text Mode';
            }}
        }}

        function onTextEditorInput(value) {{
            // 纯文本模式下的输入同步到 modules（简单实现：按段落拆分）
            const paragraphs = value.split('\\n\\n').map(p => p.trim()).filter(p => p.length > 0);
            // 这里可以更智能地匹配到现有模块，暂时简单处理
            scheduleSave();
        }}

        // 渲染 AI 反馈（带 Locate 功能）
        function renderAIFeedback(container, reviewText) {{
            if (!container) return;
            
            // 解析 AI 反馈，查找 block_id 标记（格式：[block_id: intro-1], [block_id: body-2], [block_id: conclusion-1]）
            const blockIdPattern = /\\[block_id:\\s*([a-z]+-\\d+)\\]/gi;
            
            // 同时支持旧格式的 Body 段落引用（向后兼容）
            const bodyPattern = /Body\\s+(?:Paragraph\\s+)?(\\d+)/gi;
            
            // 将反馈分段，为每个提到 block_id 的段落添加 Locate 按钮
            let html = '<div class="ai-feedback-card">';
            const paragraphs = reviewText.split('\\n\\n').filter(p => p.trim());
            
            paragraphs.forEach(para => {{
                // 查找 block_id 标记
                const blockIdMatches = [...para.matchAll(blockIdPattern)];
                const blockIds = [...new Set(blockIdMatches.map(m => m[1]))];
                
                // 查找 Body 段落引用（向后兼容）
                const paraMatches = [...para.matchAll(bodyPattern)];
                const paraBodyRefs = [...new Set(paraMatches.map(m => parseInt(m[1])))];
                
                // 移除 block_id 标记后显示文本
                const displayText = para.replace(/\\[block_id:[^\\]]+\\]/gi, '').trim();
                html += `<p style="margin:0 0 12px 0; line-height:1.8;">${{displayText}}</p>`;
                
                // 为每个 block_id 添加 Locate 按钮
                if (blockIds.length > 0) {{
                    blockIds.forEach(blockId => {{
                        const displayName = blockId.replace('-', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        html += `<button class="locate-btn" onclick="locateIssue('${{blockId}}')">📍 Locate ${{displayName}}</button> `;
                    }});
                }}
                
                // 向后兼容：为 Body 段落添加 Locate 按钮
                if (paraBodyRefs.length > 0 && blockIds.length === 0) {{
                    paraBodyRefs.forEach(bodyNum => {{
                        html += `<button class="locate-btn" onclick="locateIssue('body-${{bodyNum}}')">📍 Locate Body ${{bodyNum}}</button> `;
                    }});
                }}
            }});
            
            html += '</div>';
            container.innerHTML = html;
        }}

        // Locate 功能：高亮对应模块（通用函数，支持所有 block 类型）
        function locateIssue(blockId) {{
            if (!blockId) return;
            
            // 查找对应的 DOM 元素
            const moduleEl = document.querySelector(`[data-block-id="${{blockId}}"]`);
            
            if (moduleEl) {{
                // 移除之前的高亮
                document.querySelectorAll('.essay-module').forEach(el => {{
                    el.classList.remove('highlight');
                    el.classList.remove('active-glow');
                }});
                
                // 滚动到目标元素
                moduleEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                
                // 添加高亮动画
                moduleEl.classList.add('active-glow');
                
                // 2 秒后移除高亮（动画时长）
                setTimeout(() => {{
                    moduleEl.classList.remove('active-glow');
                }}, 2000);
            }} else {{
                // 如果找不到，尝试向后兼容的 locateBodyParagraph
                const match = blockId.match(/body-(\\d+)/);
                if (match) {{
                    const bodyNum = parseInt(match[1], 10);
                    locateBodyParagraph(bodyNum);
                }}
            }}
        }}
        
        // 向后兼容：Locate Body 段落（保留旧函数）
        function locateBodyParagraph(bodyNum) {{
            locateIssue(`body-${{bodyNum}}`);
        }}

        // Re-submit 逻辑
        async function resubmitForReview() {{
            await submitReview(true);
        }}

        // --- 11. Mission Lab 抽屉 ---
        function showMissionLab() {{
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) drawer.style.display = 'block';
        }}

        function closeMissionLab() {{
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) drawer.style.display = 'none';
        }}

        // 点击抽屉外部关闭
        document.addEventListener('DOMContentLoaded', () => {{
            const drawer = document.getElementById('mission-lab-drawer');
            if (drawer) {{
                drawer.onclick = (e) => {{
                    if (e.target === drawer) closeMissionLab();
                }};
            }}
        }});
        
        // --- 12. 侧边栏折叠/展开控制 ---
        function toggleSidebar() {{
            const sidebar = document.getElementById('knowledge-sidebar');
            const toggle = document.getElementById('sidebar-toggle');
            const overlay = document.getElementById('sidebar-overlay');
            
            if (!sidebar || !toggle) return;
            
            const isExpanded = sidebar.classList.contains('expanded');
            
            if (isExpanded) {{
                closeSidebar();
            }} else {{
                sidebar.classList.add('expanded');
                toggle.classList.remove('collapsed');
                toggle.classList.add('expanded');
                overlay.classList.add('visible');
            }}
        }}
        
        function closeSidebar() {{
            const sidebar = document.getElementById('knowledge-sidebar');
            const toggle = document.getElementById('sidebar-toggle');
            const overlay = document.getElementById('sidebar-overlay');
            
            if (!sidebar || !toggle) return;
            
            sidebar.classList.remove('expanded');
            toggle.classList.remove('expanded');
            toggle.classList.add('collapsed');
            overlay.classList.remove('visible');
        }}
        
        // 检查 URL 参数，如果是 view-hub 模式，自动展开侧边栏
        window.addEventListener('load', () => {{
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('view') === 'hub') {{
                setTimeout(() => {{
                    toggleSidebar();
                }}, 300);
            }}
        }});
        
        // --- 13. 计时器功能 ---
        let timerInterval = null;
        let timerSeconds = 0;
        let timerMode = 'up'; // 'up' or 'down'
        let timerCountdownMinutes = 45;
        let timerIsRunning = false;
        let timerStartTime = null;
        
        function toggleTimerPanel() {{
            const panel = document.getElementById('timer-panel');
            if (panel) {{
                panel.classList.toggle('visible');
            }}
        }}
        
        function setTimerMode(mode) {{
            timerMode = mode;
            const upBtn = document.getElementById('timer-mode-up');
            const downBtn = document.getElementById('timer-mode-down');
            const inputContainer = document.getElementById('timer-countdown-input-container');
            
            if (upBtn && downBtn) {{
                if (mode === 'up') {{
                    upBtn.classList.add('active');
                    downBtn.classList.remove('active');
                    if (inputContainer) inputContainer.style.display = 'none';
                }} else {{
                    upBtn.classList.remove('active');
                    downBtn.classList.add('active');
                    if (inputContainer) inputContainer.style.display = 'block';
                }}
            }}
            
            // 如果切换模式时计时器正在运行，需要重置
            if (timerIsRunning) {{
                resetTimer();
            }} else {{
                updateTimerDisplay();
            }}
        }}
        
        function startTimer() {{
            if (timerIsRunning) return;
            
            timerIsRunning = true;
            timerStartTime = Date.now();
            
            const startBtn = document.getElementById('timer-start-btn');
            const pauseBtn = document.getElementById('timer-pause-btn');
            
            if (startBtn) startBtn.style.display = 'none';
            if (pauseBtn) pauseBtn.style.display = 'block';
            
            // 如果是倒计时模式，读取设置的分钟数
            if (timerMode === 'down') {{
                const input = document.getElementById('timer-countdown-input');
                if (input) {{
                    const minutes = parseInt(input.value, 10);
                    if (minutes > 0 && minutes <= 180) {{
                        timerCountdownMinutes = minutes;
                        timerSeconds = minutes * 60;
                    }}
                }}
            }}
            
            timerInterval = setInterval(() => {{
                if (timerMode === 'up') {{
                    timerSeconds++;
                }} else {{
                    timerSeconds--;
                    if (timerSeconds <= 0) {{
                        timerSeconds = 0;
                        pauseTimer();
                        // 时间到，可以添加提示
                        showToast('⏰ Time is up! Please finish your conclusion.');
                    }}
                }}
                
                updateTimerDisplay();
            }}, 1000);
            
            updateTimerDisplay();
        }}
        
        function pauseTimer() {{
            if (!timerIsRunning) return;
            
            timerIsRunning = false;
            
            if (timerInterval) {{
                clearInterval(timerInterval);
                timerInterval = null;
            }}
            
            const startBtn = document.getElementById('timer-start-btn');
            const pauseBtn = document.getElementById('timer-pause-btn');
            
            if (startBtn) startBtn.style.display = 'block';
            if (pauseBtn) pauseBtn.style.display = 'none';
        }}
        
        function resetTimer() {{
            pauseTimer();
            
            if (timerMode === 'up') {{
                timerSeconds = 0;
            }} else {{
                const input = document.getElementById('timer-countdown-input');
                if (input) {{
                    const minutes = parseInt(input.value, 10);
                    if (minutes > 0 && minutes <= 180) {{
                        timerCountdownMinutes = minutes;
                        timerSeconds = minutes * 60;
                    }} else {{
                        timerSeconds = timerCountdownMinutes * 60;
                    }}
                }} else {{
                    timerSeconds = timerCountdownMinutes * 60;
                }}
            }}
            
            updateTimerDisplay();
        }}
        
        function updateTimerDisplay() {{
            const display = document.getElementById('timer-display');
            if (!display) return;
            
            let hours = Math.floor(timerSeconds / 3600);
            let minutes = Math.floor((timerSeconds % 3600) / 60);
            let seconds = timerSeconds % 60;
            
            const timeString = 
                String(hours).padStart(2, '0') + ':' +
                String(minutes).padStart(2, '0') + ':' +
                String(seconds).padStart(2, '0');
            
            display.textContent = timeString;
            
            // 倒计时模式：剩余 5 分钟时变红并闪烁
            if (timerMode === 'down' && timerSeconds > 0 && timerSeconds <= 300) {{
                display.classList.add('warning');
                if (timerSeconds === 300) {{
                    showToast('⚠️ 5 minutes remaining! Time to write your conclusion.');
                }}
            }} else {{
                display.classList.remove('warning');
            }}
        }}
        
        // 点击外部关闭计时器面板
        document.addEventListener('click', (e) => {{
            const panel = document.getElementById('timer-panel');
            const btn = document.querySelector('.timer-btn');
            if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {{
                panel.classList.remove('visible');
            }}
        }});
        
        // --- 14. 返回 Workspace ---
        function backToWorkspace() {{
            // 确保当前内容已保存
            saveToLocal();
            // 跳转回首页
            window.location.href = '../index.html';
        }}

        // 传统 SAVE / EXPORT 适配整篇 essay
        function save() {{
            saveToLocal();
            alert("Work Saved!");
        }}

        function exportDoc() {{
            const aiContent = document.getElementById('ai-content').innerText;
            const essayText = buildEssayText();
            const content = `WORK: ${{ID}}\\nQUESTION: ${{getCurrentQuestion()}}\\n\\n[ESSAY]\\n${{essayText}}\\n\\n[AI FEEDBACK]\\n${{aiContent}}`;
            const blob = new Blob([content], {{ type: 'text/plain' }});
            const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `Submission_${{ID}}.txt`; a.click();

            const preview = document.getElementById('export-preview');
            const container = document.getElementById('export-essay');
            if (preview && container) {{
                container.innerHTML = buildEssayHtml();
                preview.style.display = 'block';
                preview.scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        // --- 9. Toast 提示函数 ---
        function showToast(message) {{
            const container = document.getElementById('toast-container');
            if (!container) return;
            
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `<span class="toast-icon">✅</span><span>${{message}}</span>`;
            
            container.innerHTML = '';
            container.appendChild(toast);
            
            // 3 秒后自动移除
            setTimeout(() => {{
                if (toast.parentNode) {{
                    toast.parentNode.removeChild(toast);
                }}
            }}, 3000);
        }}

        // --- 10. 自动拆解投喂逻辑 ---
        function processQuickAuditData() {{
            // 检查是否有 Quick Audit 的待处理数据
            const pendingIntro = localStorage.getItem('pendingIntro');
            const pendingConclusion = localStorage.getItem('pendingConclusion');
            const pendingBodiesRaw = localStorage.getItem('pendingBodies');
            
            if (!pendingIntro && !pendingConclusion && !pendingBodiesRaw) {{
                return false; // 没有待处理数据
            }}
            
            // 清空现有模块（确保清除所有输入框）
            modules = [];
            
            let moduleCount = 0;
            
            // 创建 Intro 模块（如果有）
            if (pendingIntro) {{
                const introMod = createEmptyModule('intro');
                introMod.mode = 'free';
                introMod.freeText = pendingIntro;
                modules.push(introMod);
                moduleCount++;
            }}
            
            // 创建 Body 模块（根据 pendingBodies 的长度自动生成）
            if (pendingBodiesRaw) {{
                try {{
                    const bodies = JSON.parse(pendingBodiesRaw);
                    if (Array.isArray(bodies) && bodies.length > 0) {{
                        bodies.forEach(bodyText => {{
                            if (bodyText && bodyText.trim()) {{
                                const bodyMod = createEmptyModule('body');
                                bodyMod.mode = 'free';
                                bodyMod.freeText = bodyText.trim();
                                modules.push(bodyMod);
                                moduleCount++;
                            }}
                        }});
                    }}
                }} catch (e) {{
                    console.error('Failed to parse pendingBodies:', e);
                }}
            }}
            
            // 创建 Conclusion 模块（如果有）
            if (pendingConclusion) {{
                const conclMod = createEmptyModule('conclusion');
                conclMod.mode = 'free';
                conclMod.freeText = pendingConclusion;
                modules.push(conclMod);
                moduleCount++;
            }}
            
            // 清除 localStorage 中的待处理数据（防止下次打开页面误触发）
            localStorage.removeItem('pendingIntro');
            localStorage.removeItem('pendingConclusion');
            localStorage.removeItem('pendingBodies');
            
            // 保存到当前任务的状态
            saveToLocal();
            
            // 渲染模块
            renderModules();
            
            // 显示 Toast 反馈提示
            showToast("Audit Complete: We've split your text into PEEL blocks. Review the logic below!");
            
            // Audit Mode：自动提交批改
            if (workspaceMode === 'audit') {{
                setTimeout(() => {{
                    showPreviewView();
                    setTimeout(() => {{
                        confirmSubmitFromPreview();
                    }}, 500);
                }}, 1000);
            }}
            
            return true; // 成功处理
        }}

        // 初始恢复 + 默认 body 模块 + Quick Audit 数据导入
        window.addEventListener('load', () => {{
            // 首先检测模式
            detectWorkspaceMode();
            
            // 优先处理 Quick Audit 数据
            const hasQuickAuditData = processQuickAuditData();
            
            if (!hasQuickAuditData) {{
                // 如果没有 Quick Audit 数据，正常加载本地保存的状态
                loadFromLocal();
            }}
            
            // 如果没有模块，创建默认 body 模块（仅在 Practice Mode）
            if (!modules.length && workspaceMode === 'practice') {{
                modules.push(createEmptyModule('body'));
            }}
            
            renderModules();
            updateGlobalWordCount();
            
            // 监听所有 textarea 的输入，实时更新全局字数
            document.addEventListener('input', (e) => {{
                if (e.target.tagName === 'TEXTAREA' && e.target.hasAttribute('data-module')) {{
                    updateGlobalWordCount();
                }}
            }});
        }});
    </script>
</body>
</html>"""


def create_page(mid, question):
    html = HTML_TEMPLATE.format(mid=mid, question=question)
    with open(f"assets/missions/{mid}_workspace.html", "w", encoding="utf-8") as f:
        f.write(html)

missions = [
    ("CR_M1", "Assess the reasons for the opposition to the Civil Rights movement in the Southern states in the 1950s."),
    ("CR_M2", "Evaluate how successful the Civil Rights movement was in the 1950s."),
    ("CR_M3", "Assess the impact of federal institutions on civil rights in the late 1940s and 1950s."),
    ("CR_M4", "Analyse the effectiveness of the NAACP in promoting civil rights in the late 1940s and 1950s."),
    ("CR_M5", "'Progress towards greater civil rights in the 1950s was mainly brought about by federal institutions.' Evaluate this view.")
]

for m_id, q in missions:
    create_page(m_id, q)
    print(f">>> Updated: {m_id}")