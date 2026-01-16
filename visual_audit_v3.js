/**
 * Visual Audit V3.0 - 手术级视觉诊断系统
 * Agent-03 评审引擎专家实现
 */

// A-Level AO 定义
const AO_DEFINITIONS = {
    'AO1': '对经济学概念、理论和事实的准确理解与掌握',
    'AO2': '将经济学知识应用到具体情境和案例中的能力',
    'AO3': '分析经济问题，识别因果关系，构建逻辑论证的能力',
    'AO4': '评估不同观点、论据和结论，做出判断和结论的能力'
};

/**
 * 主渲染函数：根据 Agent-04 提供的 JSON 数据渲染 Visual Audit V3.0
 * @param {Object} data - 包含 overall, criteria, paragraphs, actions, model_essay 的 JSON 对象
 */
function renderVisualAuditV3(data) {
    if (!data) {
        console.error('No data provided to renderVisualAuditV3');
        return;
    }

    // 隐藏其他视图
    const essayConstructor = document.getElementById('essay-constructor');
    const moduleToolbar = document.getElementById('module-toolbar');
    const reviewActions = document.querySelector('.review-actions');
    const feedbackView = document.getElementById('feedback-view');
    
    if (essayConstructor) essayConstructor.style.display = 'none';
    if (moduleToolbar) moduleToolbar.style.display = 'none';
    if (reviewActions) reviewActions.style.display = 'none';
    if (feedbackView) feedbackView.style.display = 'none';
    
    // 显示 V3.0 视图
    const reviewOverlay = document.getElementById('review-overlay');
    if (reviewOverlay) {
        reviewOverlay.style.display = 'block';
    }
    
    // 渲染各个卡片组件
    renderOverallScoreCard(data.overall);
    renderCriteriaMatrix(data.criteria);
    renderActionChecklist(data.actions);
    renderSegmentSurgery(data.paragraphs);
    renderModelEssay(data.model_essay);
}

/**
 * [总分卡片] Overall Score Card
 * 渲染 overall.score, overall.grade, overall.summary
 * 使用环形进度条或仪表盘视觉
 */
function renderOverallScoreCard(overall) {
    if (!overall) return;
    
    const gradeEl = document.getElementById('overall-grade');
    const scoreEl = document.getElementById('overall-score-text');
    const summaryEl = document.getElementById('overall-summary');
    const progressRing = document.getElementById('progress-ring');
    
    if (gradeEl) {
        gradeEl.textContent = overall.grade || '-';
    }
    
    if (scoreEl) {
        scoreEl.textContent = overall.score || '-';
    }
    
    if (summaryEl) {
        summaryEl.textContent = overall.summary || '暂无全局诊断结论';
    }
    
    // 计算环形进度条
    if (progressRing && overall.score) {
        const score = parseFloat(overall.score);
        let percentage = 0;
        
        // 如果是数字分数（0-100），直接使用
        if (!isNaN(score) && score <= 100) {
            percentage = score;
        } else {
            // 如果是等级（A*-E），转换为百分比
            const gradeMap = {
                'A*': 95, 'A': 85, 'B': 75, 'C': 65, 'D': 55, 'E': 45
            };
            percentage = gradeMap[overall.grade] || 50;
        }
        
        const circumference = 2 * Math.PI * 54; // r = 54
        const offset = circumference - (percentage / 100) * circumference;
        progressRing.style.strokeDashoffset = offset;
    }
}

/**
 * [各项评分卡片] Criteria Matrix
 * 将 criteria 映射为 4 个横向进度条：AO1, AO2, AO3, AO4
 */
function renderCriteriaMatrix(criteria) {
    if (!criteria || !Array.isArray(criteria)) return;
    
    const gridEl = document.getElementById('criteria-grid');
    if (!gridEl) return;
    
    const criteriaMap = {
        'AO1': 'AO1: Knowledge',
        'AO2': 'AO2: Application',
        'AO3': 'AO3: Analysis',
        'AO4': 'AO4: Evaluation'
    };
    
    const html = criteria.map(criterion => {
        const aoKey = criterion.ao || '';
        const label = criteriaMap[aoKey] || aoKey;
        const score = criterion.score || 0;
        const percentage = calculateCriteriaPercentage(score);
        const isLow = percentage < 60; // 低于 60% 显示问号
        
        return `
            <div class="criterion-item">
                <div class="criterion-header">
                    <span class="criterion-label">${label}</span>
                    ${isLow ? '<span class="help-icon" onclick="showCriteriaHelp(\'' + aoKey + '\')">❓</span>' : ''}
                </div>
                <div class="criterion-progress-bar">
                    <div class="criterion-progress-fill" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }).join('');
    
    gridEl.innerHTML = html;
}

/**
 * 计算 Criteria 百分比
 */
function calculateCriteriaPercentage(score) {
    if (typeof score === 'number') {
        return Math.min(100, Math.max(0, score));
    }
    
    // 如果是等级，转换为百分比
    const gradeMap = {
        'A*': 95, 'A': 85, 'B': 75, 'C': 65, 'D': 55, 'E': 45
    };
    return gradeMap[score] || 50;
}

/**
 * [修改任务卡片] Action Checklist
 * 将 actions 数组渲染为带复选框的列表
 * 点击复选框时，文字呈现删除线并降低透明度
 */
function renderActionChecklist(actions) {
    if (!actions || !Array.isArray(actions)) return;
    
    const listEl = document.getElementById('action-list');
    if (!listEl) return;
    
    const html = actions.map((action, index) => {
        const text = action.text || action || '';
        return `
            <div class="action-item" id="action-item-${index}">
                <input 
                    type="checkbox" 
                    class="action-checkbox" 
                    id="action-checkbox-${index}"
                    onchange="toggleAction(${index})"
                >
                <label for="action-checkbox-${index}" class="action-text">${escapeHtml(text)}</label>
            </div>
        `;
    }).join('');
    
    listEl.innerHTML = html;
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
        } else {
            item.classList.remove('completed');
        }
    }
}

/**
 * [分段手术对比卡片] Segment Surgery
 * 遍历 paragraphs 数组，渲染每个段落卡片
 */
function renderSegmentSurgery(paragraphs) {
    if (!paragraphs || !Array.isArray(paragraphs)) return;
    
    const containerEl = document.getElementById('paragraph-cards');
    if (!containerEl) return;
    
    const html = paragraphs.map((para, index) => {
        const type = para.type || 'Body';
        const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
        const peelCheck = para.peel_check || {};
        const issues = para.issues || [];
        const exampleRevision = para.example_revision || '';
        
        // PEEL 状态灯
        const peelStatus = renderPeelStatus(peelCheck);
        
        // Issues 标签
        const issuesHtml = issues.map(issue => 
            `<span class="issue-tag">${escapeHtml(issue)}</span>`
        ).join('');
        
        return `
            <div class="paragraph-card">
                <div class="paragraph-header">
                    <span class="paragraph-type">${typeLabel}</span>
                    <div class="peel-status">
                        ${peelStatus}
                    </div>
                </div>
                <div class="comparison-window">
                    <div class="issues-box">
                        <div class="issues-label">Issues</div>
                        ${issuesHtml || '<span style="color:#64748b; font-size:12px;">无问题</span>'}
                    </div>
                    <div class="revision-box">
                        <div class="revision-label">Example Revision</div>
                        <div class="revision-text">${escapeHtml(exampleRevision) || '暂无修改建议'}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    containerEl.innerHTML = html;
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
        return `
            <div class="peel-dot ${className}" title="${peelLabels[index]}: ${isValid ? 'Valid' : 'Missing'}"></div>
        `;
    }).join('') + '<span class="peel-label">PEEL</span>';
}

/**
 * [范文卡片] Model Essay
 * 默认折叠，提供 "Reveal Model Essay" 按钮
 */
function renderModelEssay(modelEssay) {
    if (!modelEssay) return;
    
    const contentEl = document.getElementById('model-essay-content');
    if (contentEl) {
        contentEl.textContent = modelEssay;
    }
}

/**
 * 切换范文显示/隐藏
 */
function toggleModelEssay() {
    const btn = document.getElementById('reveal-model-btn');
    const content = document.getElementById('model-essay-content');
    
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
 */
function showCriteriaHelp(aoKey) {
    const modal = document.getElementById('criteria-help-modal');
    if (modal) {
        modal.style.display = 'flex';
        
        // 如果指定了 AO，高亮显示
        if (aoKey) {
            // 可以添加高亮逻辑
        }
    }
}

/**
 * 关闭 AO 定义帮助
 */
function closeCriteriaHelp() {
    const modal = document.getElementById('criteria-help-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * HTML 转义函数
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 导出函数供全局使用
window.renderVisualAuditV3 = renderVisualAuditV3;
window.toggleAction = toggleAction;
window.toggleModelEssay = toggleModelEssay;
window.showCriteriaHelp = showCriteriaHelp;
window.closeCriteriaHelp = closeCriteriaHelp;

