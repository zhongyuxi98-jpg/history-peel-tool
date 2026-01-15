// 导入考纲配置
import { RUBRICS, getRubricDescription, getDimensionNames } from '../src/configs.js';

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

  // 根据考试类型确定输出格式
  const scoringRange = RUBRICS[examType].scoringRange;
  const scaleType = RUBRICS[examType].scaleType;
  
  const outputFormat = `You MUST return a valid JSON object with the following structure:
{
  "overall": "总体评分或等级（${scoringRange}）",
  "dimension_scores": {
    "${dimensionNames[0]}": ${scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[1]}": ${scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[2]}": ${scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'},
    "${dimensionNames[3]}": ${scaleType === 'numeric' ? '0-9之间的数字' : 'A*-E之间的等级'}
  },
  "justification": "详细的评分理由和改进建议（可以包含 [block_id: type-number] 标记来定位具体段落）"
}

CRITICAL REQUIREMENTS:
1. 你必须严格按照 ${examType} 考纲的四个维度打分：${dimensionNames.join(', ')}
2. 不要混淆不同考纲的标准
3. 返回的必须是有效的 JSON，不要包含任何额外的文本或格式
4. 在 justification 中，如果针对特定段落，使用 [block_id: type-number] 格式（例如：[block_id: intro-1], [block_id: body-2], [block_id: conclusion-1]）`;

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
            content: `You are a professional ${examType === 'IELTS' ? 'IELTS Academic Writing' : 'A-Level'} examiner and academic writing coach. ${languageDirective}
${strictConstraint}

Task:
- Grade and diagnose the student's writing according to ${examType} standards.
- Align feedback with the selected section type and rubric.
            
批改准则：
1. 态度检测：如果输入是 '123' 或乱码，请毒舌且严厉地训诫学生，要求其端正学术态度。
2. 考纲对齐：${rubricDescription}
3. Structure alignment: ${sectionRubric}
4. Fact-check: correct or flag weak/incorrect claims; encourage specific events (e.g. Brown v. Board, Montgomery Bus Boycott, Little Rock Nine) when relevant.

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
      
      // 尝试解析 JSON 格式的响应
      let parsedResult = null;
      try {
        // 尝试提取 JSON（可能被包裹在 markdown 代码块中）
        let jsonStr = aiMessage.trim();
        // 移除可能的 markdown 代码块标记
        if (jsonStr.startsWith('```')) {
          const lines = jsonStr.split('\n');
          lines.shift(); // 移除第一行 ```json 或 ```
          lines.pop(); // 移除最后一行 ```
          jsonStr = lines.join('\n');
        }
        parsedResult = JSON.parse(jsonStr);
        
        // 验证 JSON 结构
        if (!parsedResult.overall || !parsedResult.dimension_scores || !parsedResult.justification) {
          throw new Error("JSON 结构不完整");
        }
        
        // 验证维度名称是否匹配
        const expectedDimensions = dimensionNames;
        const actualDimensions = Object.keys(parsedResult.dimension_scores);
        const dimensionsMatch = expectedDimensions.every(dim => actualDimensions.includes(dim));
        
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