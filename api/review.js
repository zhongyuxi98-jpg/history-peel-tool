// 导入考纲配置和 Command Words 识别
import { RUBRICS, getRubricDescription, getDimensionNames, getCommandWordPrompt } from '../src/configs.js';

export default async function handler(req, res) {
  // 仅允许 POST 请求
  if (req.method !== 'POST') return res.status(405).json({ review: "Method Not Allowed" });

  // 接收：写作内容 + 动态题目 + 段落类型 + 语言约束 + Re-submit 标志 + 考试类型
  const {
    point,
    evidence1,
    evidence2,
    link,
    language,
    essay_question,
    section_type,
    constraint,
    essay_full,
    structure,
    is_resubmit,
    previous_review,
    currentExamType = 'AL_ECON' // 默认 A-Level，兼容旧版本
  } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  // 标准化考试类型：将前端可能传入的 'ielts'/'alevel' 转换为 'IELTS'/'AL_ECON'
  let examType = currentExamType.toUpperCase();
  if (examType === 'IELTS' || examType === 'IELTS_ACADEMIC') {
    examType = 'IELTS';
  } else if (examType === 'ALEVEL' || examType === 'A-LEVEL' || examType === 'AL_ECON') {
    examType = 'AL_ECON';
  } else {
    // 默认使用 AL_ECON
    examType = 'AL_ECON';
  }

  // 获取对应考纲的评分维度描述
  let rubricDescription = '';
  let dimensionNames = [];
  try {
    rubricDescription = getRubricDescription(examType);
    dimensionNames = getDimensionNames(examType);
  } catch (error) {
    console.error('Error loading rubric:', error);
    // 降级处理：使用默认的 AL_ECON
    examType = 'AL_ECON';
    rubricDescription = getRubricDescription(examType);
    dimensionNames = getDimensionNames(examType);
  }

  // 2. [新增] 动态生成语言风格指令
  let languageDirective = "";
  if (language === 'zh') {
    languageDirective = "请完全使用【中文】进行批改。你现在是一位严厉但负责的『中教老师』，重点检查史实细节。";
  } else if (language === 'en') {
    languageDirective = "Please respond strictly in 【English】. Act as a 'Native British/American Examiner'. Focus on academic phrasing, tone, and logical flow.";
  } else {
    // 默认双语模式
    languageDirective = "请使用【双语】批改：核心评价用英文；具体的改进指导和史实分析用中文，确保学生能精准理解如何改进。";
  }

  const strictConstraint = constraint
    ? `\n\n${constraint}`
    : "\n\nConstraint: Follow the selected language mode strictly.";

  const sectionType = (section_type || "multi").toLowerCase();
  const sectionRubric =
    sectionType === "intro"
      ? "Section Type: Intro. Focus on thesis clarity, line of argument, and signposting."
      : sectionType === "conclusion"
      ? "Section Type: Conclusion. Focus on summarising key points and linking back to the question (no new evidence)."
      : sectionType === "body"
      ? "Section Type: Body (PEEL). Diagnose Point–Evidence–Explanation–Link coherence; check evidence specificity and causal logic."
      : "Section Type: Full essay (Intro + Body paragraphs + Conclusion). Evaluate overall argument, paragraph balance, and how well the essay answers the question.";

  // [Agent-04] Command Words 识别
  const commandWordPrompt = essay_question ? getCommandWordPrompt(essay_question) : "";

  // [Agent-04] 考纲隔离：严格确保 A-Level 模式下不会出现雅思维度
  const examTypeGuard = examType === 'AL_ECON' 
    ? `⚠️ 考纲隔离警告：当前是 A-Level 模式，绝对禁止使用以下雅思评分维度：
- Task Response
- Coherence & Cohesion
- Lexical Resource
- Grammatical Range & Accuracy

你必须且只能使用 A-Level 的四个维度：${dimensionNames.join(', ')}`
    : examType === 'IELTS'
    ? `⚠️ 考纲隔离警告：当前是 IELTS 模式，绝对禁止使用以下 A-Level 评分维度：
- AO1 Knowledge
- AO2 Application
- AO3 Analysis
- AO4 Evaluation

你必须且只能使用 IELTS 的四个维度：${dimensionNames.join(', ')}`
    : "";

  // [Agent-04 骨架] 根据考试类型确定输出格式
  // 对于 A-Level，使用新的 JSON Schema
  const isALevel = examType === 'AL_ECON';
  
  const outputFormat = isALevel ? `你只能输出一个合法的 JSON 对象，严禁任何解释性文字、Markdown 代码块标签（如 \`\`\`json）或其他格式。

JSON Schema（必须严格遵守）:
{
  "overall": {
    "score": 数字 0-100,
    "grade": "A*|A|B|C|D|E|U",
    "summary": "针对 A-Level 考官口味的学术性总结（200-300字）"
  },
  "criteria": {
    "AO1_Knowledge": 数字 0-10,
    "AO2_Application": 数字 0-10,
    "AO3_Analysis": 数字 0-10,
    "AO4_Evaluation": 数字 0-10
  },
  "paragraphs": [
    {
      "type": "introduction|body|conclusion",
      "peel_check": {
        "point": true|false,
        "evidence": true|false,
        "explain": true|false,
        "link": true|false
      },
      "issues": ["学术逻辑痛点1", "学术逻辑痛点2"],
      "example_revision": "针对该段落的学术化改写样例（完整段落）"
    }
  ],
  "actions": ["行动导向的改进建议1", "行动导向的改进建议2", "行动导向的改进建议3"],
  "model_essay": "一篇符合该题目 A* 标准的范文思考（完整文章，800-1200字）"
}

⚠️ 输出规范（绝对禁止）:
- 禁止输出 \`\`\`json 或 \`\`\` 等 Markdown 代码块标签
- 禁止输出任何解释性文字（如 "这是评审结果："、"JSON 如下："等）
- 禁止在 JSON 前后添加任何文本
- 只输出纯净的 JSON 字符串，以便前端 JSON.parse() 直接调用

✅ 正确示例（只输出这个）:
{"overall":{"score":75,"grade":"B","summary":"..."},"criteria":{...},"paragraphs":[...],"actions":[...],"model_essay":"..."}` 
    : `You MUST return a valid JSON object with the following structure:
{
  "overall": "总体评分或等级（${RUBRICS[examType].scoringRange}）",
  "dimension_scores": {
    "${dimensionNames[0]}": ${RUBRICS[examType].scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[1]}": ${RUBRICS[examType].scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[2]}": ${RUBRICS[examType].scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[3]}": ${RUBRICS[examType].scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'}
  },
  "justification": "详细的评分理由和改进建议",
  "feedback_loops": [
    {
      "original_segment": "学生原文中的问题段落",
      "diagnosis": "诊断说明",
      "improved_segment": "改进后的版本"
    }
  ]
}

CRITICAL REQUIREMENTS:
1. 你必须严格按照 ${examType} 考纲的四个维度打分：${dimensionNames.join(', ')}
2. ${examTypeGuard}
3. 返回的必须是有效的 JSON，不要包含任何额外的文本或格式`;

  try {
    // 调用阿里云百炼接口
    const response = await fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "qwen-plus",
        messages: [
          {
            role: "system",
            content: isALevel 
              ? `Role: 你是 A-Level 写作专家。请严格按以下 JSON 格式输出评审结果，严禁任何解释性文字。

${commandWordPrompt ? `\n${commandWordPrompt}\n` : ""}

${languageDirective}
${strictConstraint}

批改准则：
1. 态度检测：如果输入是 '123' 或乱码，请毒舌且严厉地训诫学生，要求其端正学术态度。
2. 考纲对齐：${rubricDescription}
3. ${examTypeGuard}
4. Structure alignment: ${sectionRubric}
5. Fact-check: correct or flag weak/incorrect claims; encourage specific events (e.g. Brown v. Board, Montgomery Bus Boycott, Little Rock Nine) when relevant.
6. Command Word 对齐：${commandWordPrompt ? '确保学生的回答符合题目中识别到的 Command Word 要求。' : '仔细分析题目要求。'}

${outputFormat}`
              : `你是 [Agent-04 考纲逻辑专家]。你的任务是完善后端 system_prompt 和数据协议。

${commandWordPrompt ? `\n${commandWordPrompt}\n` : ""}

You are a professional ${examType === 'IELTS' ? 'IELTS Academic Writing' : 'A-Level'} examiner and academic writing coach. ${languageDirective}
${strictConstraint}

Task:
- Grade and diagnose the student's writing according to ${examType} standards.
- Align feedback with the selected section type and rubric.
- ${commandWordPrompt ? 'Ensure the response matches the Command Word requirements identified in the question.' : 'Analyze the question requirements carefully.'}
            
批改准则：
1. 态度检测：如果输入是 '123' 或乱码，请毒舌且严厉地训诫学生，要求其端正学术态度。
2. 考纲对齐：${rubricDescription}
3. ${examTypeGuard}
4. Structure alignment: ${sectionRubric}
5. Fact-check: correct or flag weak/incorrect claims; encourage specific events (e.g. Brown v. Board, Montgomery Bus Boycott, Little Rock Nine) when relevant.
6. Command Word 对齐：${commandWordPrompt ? '确保学生的回答符合题目中识别到的 Command Word 要求。' : '仔细分析题目要求。'}

${outputFormat}`
          },
          {
            role: "user",
            content: is_resubmit && previous_review
              ? `这是学生的修改稿。请对比上次的评价，重点指出进步点和仍需改进的地方。

上次评价：
${previous_review}

当前 Essay Question: ${essay_question || "(not provided)"}

当前 Essay Structure (JSON-like, modules in order): 
${JSON.stringify(structure || [], null, 2)}

当前 Full essay text:
${essay_full || `
Point: ${point || "(legacy)"} 
Evidence 1: ${evidence1 || "(legacy)"} 
Evidence 2: ${evidence2 || "(legacy)"} 
Link: ${link || "(legacy)"}
`}

请给出改进后的 Review，重点关注：
1. 相比上次评价，哪些地方有进步？
2. 还有哪些地方需要继续改进？
3. 给出具体的修改建议。

Block ID Mapping (for your reference when adding [block_id: ...] markers):
${(() => {
                let introCount = 0, bodyCount = 0, conclusionCount = 0;
                const mapping = [];
                if (Array.isArray(structure)) {
                  structure.forEach((m) => {
                    if (m.type === 'intro') {
                      introCount++;
                      mapping.push(`- ${m.type} #${introCount} → block_id: intro-${introCount}`);
                    } else if (m.type === 'body') {
                      bodyCount++;
                      mapping.push(`- ${m.type} #${bodyCount} → block_id: body-${bodyCount}`);
                    } else if (m.type === 'conclusion') {
                      conclusionCount++;
                      mapping.push(`- ${m.type} #${conclusionCount} → block_id: conclusion-${conclusionCount}`);
                    }
                  });
                }
                return mapping.length > 0 ? mapping.join('\n') : 'No structure provided.';
              })()}`
              : `Essay Question (editable by student):
${essay_question || "(not provided)"}

Structure (JSON-like, modules in order): 
${JSON.stringify(structure || [], null, 2)}

Block ID Mapping (for your reference when adding [block_id: ...] markers):
${(() => {
                let introCount = 0, bodyCount = 0, conclusionCount = 0;
                const mapping = [];
                if (Array.isArray(structure)) {
                  structure.forEach((m) => {
                    if (m.type === 'intro') {
                      introCount++;
                      mapping.push(`- ${m.type} #${introCount} → block_id: intro-${introCount}`);
                    } else if (m.type === 'body') {
                      bodyCount++;
                      mapping.push(`- ${m.type} #${bodyCount} → block_id: body-${bodyCount}`);
                    } else if (m.type === 'conclusion') {
                      conclusionCount++;
                      mapping.push(`- ${m.type} #${conclusionCount} → block_id: conclusion-${conclusionCount}`);
                    }
                  });
                }
                return mapping.length > 0 ? mapping.join('\n') : 'No structure provided.';
              })()}

Full essay text:
${essay_full || `
Point: ${point || "(legacy)"} 
Evidence 1: ${evidence1 || "(legacy)"} 
Evidence 2: ${evidence2 || "(legacy)"} 
Link: ${link || "(legacy)"}
`}
`
          }
        ]
      })
    });

    const data = await response.json();

    // 安全检查，防止接口返回异常
    if (data.choices && data.choices[0]) {
      const aiMessage = data.choices[0].message.content;
      
      // [Agent-04 骨架] 尝试解析 JSON 格式的响应
      let parsedResult = null;
      try {
        // 提取纯净 JSON（去除所有 Markdown 代码块和解释性文字）
        let jsonStr = aiMessage.trim();
        
        // 移除 Markdown 代码块标记（```json 或 ```）
        if (jsonStr.startsWith('```')) {
          const lines = jsonStr.split('\n');
          lines.shift(); // 移除第一行 ```json 或 ```
          // 找到最后一个 ``` 并移除
          const lastIndex = lines.findIndex(line => line.trim() === '```');
          if (lastIndex !== -1) {
            lines.splice(lastIndex);
          } else {
            lines.pop(); // 如果没有找到，移除最后一行
          }
          jsonStr = lines.join('\n');
        }
        
        // 移除 JSON 前后的解释性文字（如 "这是评审结果："、"JSON 如下："等）
        // 查找第一个 { 和最后一个 }
        const firstBrace = jsonStr.indexOf('{');
        const lastBrace = jsonStr.lastIndexOf('}');
        if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
          jsonStr = jsonStr.substring(firstBrace, lastBrace + 1);
        }
        
        jsonStr = jsonStr.trim();
        parsedResult = JSON.parse(jsonStr);
        
        // [Agent-04 骨架] 验证 A-Level 新 JSON Schema
        if (examType === 'AL_ECON') {
          // 验证新结构
          if (!parsedResult.overall || !parsedResult.criteria || !parsedResult.paragraphs || !parsedResult.actions || !parsedResult.model_essay) {
            throw new Error("A-Level JSON 结构不完整：缺少 overall, criteria, paragraphs, actions 或 model_essay");
          }
          
          // 验证 overall 结构
          if (!parsedResult.overall.score || !parsedResult.overall.grade || !parsedResult.overall.summary) {
            throw new Error("overall 结构不完整：缺少 score, grade 或 summary");
          }
          
          // 验证 criteria 必须映射为 AO1_Knowledge, AO2_Application, AO3_Analysis, AO4_Evaluation
          const requiredCriteria = ['AO1_Knowledge', 'AO2_Application', 'AO3_Analysis', 'AO4_Evaluation'];
          const actualCriteria = Object.keys(parsedResult.criteria);
          const missingCriteria = requiredCriteria.filter(c => !actualCriteria.includes(c));
          if (missingCriteria.length > 0) {
            console.warn(`缺少必需的 criteria 维度: ${missingCriteria.join(', ')}`);
            // 补充缺失的维度
            missingCriteria.forEach(c => {
              parsedResult.criteria[c] = 0;
            });
          }
          
          // 验证 paragraphs 数组结构
          if (!Array.isArray(parsedResult.paragraphs)) {
            parsedResult.paragraphs = [];
          } else {
            parsedResult.paragraphs = parsedResult.paragraphs.map((para, index) => {
              if (!para.type || !para.peel_check || !para.issues || !para.example_revision) {
                console.warn(`paragraphs[${index}] 结构不完整，已补充默认值`);
                return {
                  type: para.type || 'body',
                  peel_check: para.peel_check || { point: false, evidence: false, explain: false, link: false },
                  issues: Array.isArray(para.issues) ? para.issues : [],
                  example_revision: para.example_revision || ""
                };
              }
              return para;
            });
          }
          
          // 验证 actions 数组
          if (!Array.isArray(parsedResult.actions)) {
            parsedResult.actions = [];
          }
          
          // 验证 model_essay
          if (typeof parsedResult.model_essay !== 'string') {
            parsedResult.model_essay = "";
          }
        } else {
          // IELTS 或其他格式的验证（保持原有逻辑）
          if (!parsedResult.overall || !parsedResult.dimension_scores || !parsedResult.justification) {
            throw new Error("JSON 结构不完整");
          }
          
          // 验证 feedback_loops 数组
          if (!parsedResult.feedback_loops || !Array.isArray(parsedResult.feedback_loops)) {
            console.warn("缺少 feedback_loops 数组，将创建空数组");
            parsedResult.feedback_loops = [];
          } else {
            // 验证 feedback_loops 中每个对象的结构
            parsedResult.feedback_loops = parsedResult.feedback_loops.map((loop, index) => {
              if (!loop.original_segment || !loop.diagnosis || !loop.improved_segment) {
                console.warn(`feedback_loops[${index}] 缺少必需字段，已补充默认值`);
                return {
                  original_segment: loop.original_segment || "未提供原文",
                  diagnosis: loop.diagnosis || "未提供诊断",
                  improved_segment: loop.improved_segment || "未提供改进版本",
                  block_id: loop.block_id || null
                };
              }
              return loop;
            });
          }
        }
        
        // [Agent-04] 验证维度名称是否匹配，并检查考纲隔离
        const expectedDimensions = dimensionNames;
        const actualDimensions = Object.keys(parsedResult.dimension_scores);
        const dimensionsMatch = expectedDimensions.every(dim => actualDimensions.includes(dim));
        
        // 考纲隔离检查：确保 A-Level 模式下不会出现雅思维度
        const forbiddenIELTSDims = ["Task Response", "Coherence & Cohesion", "Lexical Resource", "Grammatical Range & Accuracy"];
        const forbiddenALDims = ["AO1 Knowledge", "AO2 Application", "AO3 Analysis", "AO4 Evaluation"];
        
        if (examType === 'AL_ECON') {
          const hasIELTSDims = actualDimensions.some(dim => forbiddenIELTSDims.includes(dim));
          if (hasIELTSDims) {
            console.error("⚠️ 考纲隔离违规：A-Level 模式下检测到雅思评分维度！");
            // 强制修正：移除雅思维度，只保留 A-Level 维度
            const correctedScores = {};
            expectedDimensions.forEach(dim => {
              correctedScores[dim] = parsedResult.dimension_scores[dim] || (scaleType === 'numeric' ? 5 : 'C');
            });
            parsedResult.dimension_scores = correctedScores;
          }
        } else if (examType === 'IELTS') {
          const hasALDim = actualDimensions.some(dim => forbiddenALDims.includes(dim));
          if (hasALDim) {
            console.error("⚠️ 考纲隔离违规：IELTS 模式下检测到 A-Level 评分维度！");
            // 强制修正：移除 A-Level 维度，只保留雅思维度
            const correctedScores = {};
            expectedDimensions.forEach(dim => {
              correctedScores[dim] = parsedResult.dimension_scores[dim] || 5;
            });
            parsedResult.dimension_scores = correctedScores;
          }
        }
        
        if (!dimensionsMatch) {
          console.warn(`维度名称不匹配。期望: ${expectedDimensions.join(', ')}, 实际: ${actualDimensions.join(', ')}`);
        }
        
        // 在控制台打印结果（用于验证）
        console.log('=== 评分结果 JSON ===');
        console.log('考试类型:', examType);
        console.log('维度名称:', dimensionNames);
        console.log('返回的 JSON:', JSON.stringify(parsedResult, null, 2));
        console.log('==================');
        
        // 返回标准化的 JSON 响应
        res.status(200).json({ 
          review: aiMessage, // 保留原始文本用于向后兼容
          structured: parsedResult, // 新增结构化数据
          examType: examType,
          dimensions: dimensionNames
        });
      } catch (parseError) {
        // 如果解析失败，记录错误但仍然返回原始文本（向后兼容）
        console.error('JSON 解析失败:', parseError);
        console.log('原始 AI 响应:', aiMessage);
        console.log('考试类型:', examType);
        console.log('期望的维度:', dimensionNames);
        
        // 返回原始文本，但添加警告
        res.status(200).json({ 
          review: aiMessage,
          warning: "AI 返回的格式不是标准 JSON，已返回原始文本",
          examType: examType,
          dimensions: dimensionNames
        });
      }
    } else {
      throw new Error("AI 响应异常");
    }

  } catch (error) {
    console.error("API Error:", error);
    res.status(500).json({ review: "糟糕，老师的连接断开了。请检查 Vercel 环境变量或网络状态。" });
  }
}