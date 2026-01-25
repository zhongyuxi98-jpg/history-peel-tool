/**
 * Visual Audit V3.0 - 右侧浮窗模式
 * 创建 fixed 定位的右侧浮窗，将评审数据渲染到浮窗中
 */

// A-Level AO 定义（支持两种键名格式：AO1 和 AO1_Knowledge）
const AO_DEFINITIONS = {
    'AO1': '对经济学概念、理论和事实的准确理解与掌握',
    'AO2': '将经济学知识应用到具体情境和案例中的能力',
    'AO3': '分析经济问题，识别因果关系，构建逻辑论证的能力',
    'AO4': '评估不同观点、论据和结论，做出判断和结论的能力',
    // 兼容后端返回的带下划线格式
    'AO1_Knowledge': '对经济学概念、理论和事实的准确理解与掌握',
    'AO2_Application': '将经济学知识应用到具体情境和案例中的能力',
    'AO3_Analysis': '分析经济问题，识别因果关系，构建逻辑论证的能力',
    'AO4_Evaluation': '评估不同观点、论据和结论，做出判断和结论的能力'
};

// 防止递归死循环的标志
let isRendering = false;
let auditPanel = null;

/**
 * 创建右侧浮窗面板
 * @returns {HTMLElement} 创建的浮窗元素
 */
function createAuditPanel() {
    // 如果已存在，先移除
    const existing = document.getElementById('visual-audit-panel');
    if (existing) {
        existing.remove();
    }
    
    // 清理残留的遮罩层
    const existingOverlay = document.getElementById('audit-panel-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // 创建浮窗容器
    const panel = document.createElement('div');
    panel.id = 'visual-audit-panel';
    panel.style.cssText = `
        position: fixed;
        top: 0;
        right: 0;
        width: 420px;
        height: 100vh;
        background: #fff;
        box-shadow: -5px 0 20px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        border-left: 1px solid #e2e8f0;
    `;

    // 创建头部
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 20px;
        border-bottom: 2px solid #1e293b;
        background: linear-gradient(135deg, #1e293b 0%, #4F46E5 100%);
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
    `;
    header.innerHTML = `
        <h2 style="margin: 0; font-size: 20px; font-weight: 800;">📊 Visual Audit</h2>
        <button id="audit-panel-close" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center;">✕</button>
    `;

    // 创建内容容器
    const content = document.createElement('div');
    content.id = 'audit-panel-content';
    content.style.cssText = `
        flex: 1;
        padding: 24px;
        overflow-y: auto;
    `;

    // 组装
    panel.appendChild(header);
    panel.appendChild(content);
    document.body.appendChild(panel);

    // 绑定关闭按钮
    const closeBtn = document.getElementById('audit-panel-close');
    if (closeBtn) {
        closeBtn.onclick = () => {
            panel.style.display = 'none';
        };
    }

    // 添加遮罩层（可选）
    const overlay = document.createElement('div');
    overlay.id = 'audit-panel-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.3);
        z-index: 9999;
        display: block;
    `;
    overlay.onclick = () => {
        panel.style.display = 'none';
        overlay.style.display = 'none';
    };
    document.body.appendChild(overlay);

    auditPanel = panel;
    return panel;
}

/**
 * 主渲染函数：根据 Agent-04 提供的 JSON 数据渲染 Visual Audit V3.0
 * @param {Object} rawData - 包含 overall, criteria, paragraphs, actions, model_essay 的 JSON 对象
 */
function renderVisualAuditV3(rawData) {
    // 防止递归死循环：如果正在渲染，直接返回
    if (isRendering) {
        console.warn('⚠️ renderVisualAuditV3 正在执行中，跳过重复调用');
        return;
    }
    
    // 设置渲染标志
    isRendering = true;
    
    try {
        console.log('--- 收到原始数据 ---', rawData);

        // 1. 数据脱壳：兼容直接数据和带 structured 的数据
        const data = rawData.structured ? rawData.structured : rawData;
        
        if (!data || !data.overall) {
            console.error('❌ 数据脱壳失败或格式错误，无法渲染。请检查控制台数据结构。');
            return;
        }

        console.log('✅ 脱壳成功，开始分发渲染:', data);

        // 2. 创建或获取浮窗
        if (!auditPanel || !document.getElementById('visual-audit-panel')) {
            createAuditPanel();
        }
        const contentEl = document.getElementById('audit-panel-content');
        if (!contentEl) {
            console.error('❌ 无法找到浮窗内容容器');
            return;
        }

        // 显示浮窗和遮罩
        auditPanel.style.display = 'flex';
        const overlay = document.getElementById('audit-panel-overlay');
        if (overlay) overlay.style.display = 'block';

        // 3. 清空内容并渲染
        contentEl.innerHTML = '';

        // 渲染各个组件
        if (typeof renderOverallScoreCard === 'function') {
            renderOverallScoreCard(data.overall, contentEl);
        }
        if (typeof renderCriteriaMatrix === 'function') {
            renderCriteriaMatrix(data.criteria, contentEl);
        }
        if (typeof renderActionChecklist === 'function') {
            renderActionChecklist(data.actions || [], contentEl);
        }
        if (typeof renderSegmentSurgery === 'function') {
            renderSegmentSurgery(data.paragraphs || [], contentEl);
        }
        if (typeof renderModelEssay === 'function') {
            renderModelEssay(data.model_essay || '', contentEl);
        }
        
        console.log('✅ 所有组件渲染完成');
        
    } catch (err) {
        console.error('❌ 渲染组件时出错:', err);
    } finally {
        // 重置渲染标志
        isRendering = false;
    }
}

/**
 * [总分卡片] Overall Score Card
 * 渲染 overall.score, overall.grade, overall.summary
 */
function renderOverallScoreCard(overall, container) {
    if (!overall || !container) return;
    
    const card = document.createElement('div');
    card.style.cssText = `
        background: linear-gradient(135deg, #1e293b 0%, #4F46E5 100%);
        color: white;
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    `;
    
    const grade = overall.grade || '-';
    const score = overall.score || '-';
    const summary = overall.summary || '暂无全局诊断结论';
    
    card.innerHTML = `
        <div style="font-size: 48px; font-weight: 800; margin-bottom: 12px;">${grade}</div>
        <div style="font-size: 24px; font-weight: 700; margin-bottom: 16px; opacity: 0.9;">${score}</div>
        <div style="font-size: 14px; line-height: 1.6; opacity: 0.95;">${escapeHtml(summary)}</div>
    `;
    
    container.appendChild(card);
}

/**
 * [各项评分卡片] Criteria Matrix
 * 将 criteria 映射为 4 个横向进度条：AO1, AO2, AO3, AO4
 */
function renderCriteriaMatrix(criteria, container) {
    if (!criteria || !container) return;
  
    // 统一成数组结构：[{ao:'AO1', score: 3}, ...]
    let list = [];
  
    if (Array.isArray(criteria)) {
        list = criteria.map(c => ({
            ao: c.ao || c.key || '',
            score: c.score ?? c.value ?? 0
        }));
    } else if (typeof criteria === 'object') {
        list = Object.entries(criteria).map(([k, v]) => ({
            ao: k,
            score: v
        }));
    } else {
        return;
    }
  
    // 映射函数：将后端返回的键名（如 AO1_Knowledge）转换为标准格式（AO1）
    const normalizeAoKey = (key) => {
        if (!key) return '';
        // 如果已经是 AO1, AO2 格式，直接返回
        if (/^AO[1-4]$/.test(key)) return key;
        // 如果是 AO1_Knowledge 格式，提取 AO1
        const match = key.match(/^(AO[1-4])_/);
        return match ? match[1] : key;
    };
  
    const criteriaMap = {
        AO1: 'AO1: Knowledge',
        AO2: 'AO2: Application',
        AO3: 'AO3: Analysis',
        AO4: 'AO4: Evaluation',
        // 兼容后端返回的带下划线格式
        AO1_Knowledge: 'AO1: Knowledge',
        AO2_Application: 'AO2: Application',
        AO3_Analysis: 'AO3: Analysis',
        AO4_Evaluation: 'AO4: Evaluation'
    };
  
    const card = document.createElement('div');
    card.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    `;
    
    card.innerHTML = `
        <h3 style="font-size: 18px; font-weight: 800; color: #1e293b; margin: 0 0 20px 0;">评分维度</h3>
        <div style="display: flex; flex-direction: column; gap: 16px;">
            ${list.map(({ ao, score }) => {
                // 标准化 AO 键名，用于显示和帮助函数
                const normalizedAo = normalizeAoKey(ao);
                const label = criteriaMap[ao] || criteriaMap[normalizedAo] || ao;
                const percentage = calculateCriteriaPercentage(score);
                const isLow = percentage < 60;
                
                return `
                    <div style="background: #f8fafc; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <span style="font-size: 14px; font-weight: 700; color: #1e293b;">${label}</span>
                            ${isLow ? `<span style="cursor: pointer; font-size: 16px;" onclick="showCriteriaHelp('${normalizedAo}')">❓</span>` : ''}
                        </div>
                        <div style="width: 100%; height: 10px; background: #e2e8f0; border-radius: 5px; overflow: hidden;">
                            <div style="height: 100%; width: ${percentage}%; background: linear-gradient(90deg, #4F46E5 0%, #1e293b 100%); border-radius: 5px; transition: width 0.8s ease-out;"></div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    container.appendChild(card);
}

/**
 * 计算 Criteria 百分比
 */
function calculateCriteriaPercentage(score) {
    const n = Number(score);
    if (!isNaN(n)) return Math.max(0, Math.min(100, n * 10));
    return 0;
}

/**
 * [修改任务卡片] Action Checklist
 * 将 actions 数组渲染为带复选框的列表
 */
function renderActionChecklist(actions, container) {
    if (!actions || !Array.isArray(actions) || !container) return;
    
    const card = document.createElement('div');
    card.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    `;
    
    card.innerHTML = `
        <h3 style="font-size: 18px; font-weight: 800; color: #1e293b; margin: 0 0 20px 0;">修改任务</h3>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            ${actions.map((action, index) => {
                const text = action.text || action || '';
                return `
                    <div class="action-item" id="action-item-${index}" style="display: flex; align-items: flex-start; gap: 12px; padding: 12px; background: #f8fafc; border-radius: 8px;">
                        <input 
                            type="checkbox" 
                            class="action-checkbox" 
                            id="action-checkbox-${index}"
                            onchange="toggleAction(${index})"
                            style="width: 20px; height: 20px; margin-top: 2px; cursor: pointer; accent-color: #4F46E5;"
                        >
                        <label for="action-checkbox-${index}" class="action-text" style="flex: 1; font-size: 14px; line-height: 1.6; color: #1e293b; cursor: pointer;">${escapeHtml(text)}</label>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    container.appendChild(card);
}

/**
 * 切换 Action 完成状态
 */
function toggleAction(index) {
    const checkbox = document.getElementById(`action-checkbox-${index}`);
    const item = document.getElementById(`action-item-${index}`);
    
    if (checkbox && item) {
        if (checkbox.checked) {
            item.classList.add('completed');
            item.style.textDecoration = 'line-through';
            item.style.opacity = '0.5';
        } else {
            item.classList.remove('completed');
            item.style.textDecoration = 'none';
            item.style.opacity = '1';
        }
    }
}

/**
 * [分段手术对比卡片] Segment Surgery
 * 遍历 paragraphs 数组，渲染每个段落卡片
 */
function renderSegmentSurgery(paragraphs, container) {
    if (!paragraphs || !Array.isArray(paragraphs) || !container) return;
    
    const card = document.createElement('div');
    card.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    `;
    
    card.innerHTML = `
        <h3 style="font-size: 18px; font-weight: 800; color: #1e293b; margin: 0 0 20px 0;">段落诊断</h3>
        <div style="display: flex; flex-direction: column; gap: 16px;">
            ${paragraphs.map((para, index) => {
                const type = para.type || 'Body';
                const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
                const peelCheck = para.peel_check || {};
                const issues = para.issues || [];
                const exampleRevision = para.example_revision || '';
                
                // PEEL 状态灯
                const peelStatus = renderPeelStatus(peelCheck);
                
                // Issues 标签
                const issuesHtml = issues.map(issue => 
                    `<span style="display: inline-block; background: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 6px; margin-bottom: 6px;">${escapeHtml(issue)}</span>`
                ).join('');
                
                return `
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <span style="font-size: 14px; font-weight: 700; color: #4F46E5; text-transform: uppercase; padding: 6px 12px; background: #eef2ff; border-radius: 6px;">${typeLabel}</span>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                ${peelStatus}
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
                            <div style="background: #FFF5F5; border-left: 4px solid #F56565; padding: 16px; border-radius: 8px;">
                                <div style="font-size: 12px; font-weight: 700; color: #F56565; text-transform: uppercase; margin-bottom: 12px;">Issues</div>
                                ${issuesHtml || '<span style="color:#64748b; font-size:12px;">无问题</span>'}
                            </div>
                            <div style="background: #F0FFF4; border-left: 4px solid #48BB78; padding: 16px; border-radius: 8px;">
                                <div style="font-size: 12px; font-weight: 700; color: #48BB78; text-transform: uppercase; margin-bottom: 12px;">Example Revision</div>
                                <div style="font-size: 13px; line-height: 1.6; color: #1e293b; white-space: pre-wrap;">${escapeHtml(exampleRevision) || '暂无修改建议'}</div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    container.appendChild(card);
}

/**
 * 渲染 PEEL 状态灯
 */
function renderPeelStatus(peelCheck) {
    const peelLabels = ['P', 'E', 'E', 'L'];
    const status = [
        peelCheck.point || false,
        peelCheck.evidence || false,
        peelCheck.explanation || false,
        peelCheck.link || false
    ];
    
    return status.map((isValid, index) => {
        const className = isValid ? 'valid' : 'invalid';
        const color = isValid ? '#48BB78' : '#F56565';
        return `
            <div style="width: 8px; height: 8px; border-radius: 50%; background: ${color};" title="${peelLabels[index]}: ${isValid ? 'Valid' : 'Missing'}"></div>
        `;
    }).join('') + '<span style="margin-left: 8px; font-size: 12px; font-weight: 700; color: #1e293b;">PEEL</span>';
}

/**
 * [范文卡片] Model Essay
 * 默认折叠，提供 "Reveal Model Essay" 按钮
 */
function renderModelEssay(modelEssay, container) {
    if (!modelEssay || !container) return;
    
    const card = document.createElement('div');
    card.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    `;
    
    // 生成唯一 ID：使用 timestamp + 随机数确保唯一性
    const uniqueId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const contentId = 'model-essay-content-' + uniqueId;
    const buttonId = 'reveal-model-btn-' + uniqueId;
    
    card.innerHTML = `
        <button id="${buttonId}" onclick="toggleModelEssay('${contentId}', '${buttonId}')" style="width: 100%; padding: 16px; background: linear-gradient(135deg, #4F46E5 0%, #1e293b 100%); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.3s;">
            📖 Reveal Model Essay
        </button>
        <div id="${contentId}" style="display: none; margin-top: 20px; padding: 20px; background: #f8fafc; border-radius: 8px; line-height: 1.8; font-size: 14px; color: #1e293b; white-space: pre-wrap;">${escapeHtml(modelEssay)}</div>
    `;
    
    container.appendChild(card);
}

/**
 * 切换范文显示/隐藏
 * @param {string} contentId - 内容区域的唯一 ID
 * @param {string} buttonId - 按钮的唯一 ID
 */
function toggleModelEssay(contentId, buttonId) {
    const content = document.getElementById(contentId);
    const btn = document.getElementById(buttonId);
    
    if (content && btn) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            btn.textContent = '📖 Hide Model Essay';
        } else {
            content.style.display = 'none';
            btn.textContent = '📖 Reveal Model Essay';
        }
    }
}

/**
 * 显示 AO 定义帮助
 * @param {string} aoKey - AO 键名（支持 AO1 或 AO1_Knowledge 格式）
 */
function showCriteriaHelp(aoKey) {
    if (!aoKey) return;
    
    // 标准化键名：将 AO1_Knowledge 转换为 AO1
    const normalizedKey = /^AO[1-4]$/.test(aoKey) 
        ? aoKey 
        : aoKey.match(/^(AO[1-4])_/)?.[1] || aoKey;
    
    // 优先使用标准化键名查找，如果找不到再尝试原始键名
    const definition = AO_DEFINITIONS[normalizedKey] || AO_DEFINITIONS[aoKey] || '暂无定义';
    alert(`${normalizedKey}: ${definition}`);
}

/**
 * HTML 转义函数（性能优化版本）
 * 使用纯字符串操作，避免 DOM 操作，提升大规模文本处理性能
 */
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    
    // 对于小文本，使用简单的字符串替换（更快）
    if (text.length < 1000) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
    
    // 对于大文本，使用更高效的批量替换
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    
    return text.replace(/[&<>"']/g, (char) => map[char]);
}

// 导出函数供全局使用 - 确保在 window 对象上挂载
if (typeof window !== 'undefined') {
    window.renderVisualAuditV3 = renderVisualAuditV3;
    window.createAuditPanel = createAuditPanel;
    window.toggleAction = toggleAction;
    window.toggleModelEssay = toggleModelEssay;
    window.showCriteriaHelp = showCriteriaHelp;
    console.log('✅ visual_audit_v3.js 已加载，renderVisualAuditV3 和 createAuditPanel 函数已挂载到 window 对象');
} else {
    console.error('❌ window 对象不存在，无法挂载 renderVisualAuditV3');
}
