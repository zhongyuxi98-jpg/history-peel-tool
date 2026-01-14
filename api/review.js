export default async function handler(req, res) {
  // 仅允许 POST 请求
  if (req.method !== 'POST') return res.status(405).json({ review: "Method Not Allowed" });

  // 接收：写作内容 + 动态题目 + 段落类型 + 语言约束
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
    structure
  } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

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

  const outputFormat = `Return STRICTLY structured text with the following headers:
[Score: A-E]
[Diagnostic]
[Model Version]
In [Diagnostic], give bullet points and at least ONE improved model sentence.`;

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
            content: `You are an A-Level History examiner and academic writing coach. ${languageDirective}
${strictConstraint}

Task:
- Grade and diagnose the student's writing for 1950s US Civil Rights (A-Level standard).
- Align feedback with the selected section type and rubric.
            
            批改准则：
            1. 态度检测：如果输入是 '123' 或乱码，请毒舌且严厉地训诫学生，要求其端正学术态度。
            2. A-Level alignment: focus on argument, evidence precision, and evaluation.
            3. Structure alignment: ${sectionRubric}
            4. Fact-check: correct or flag weak/incorrect claims; encourage specific events (e.g. Brown v. Board, Montgomery Bus Boycott, Little Rock Nine) when relevant.

${outputFormat}`
          },
          {
            role: "user",
            content: `Essay Question (editable by student):
${essay_question || "(not provided)"}

Structure (JSON-like, modules in order): 
${JSON.stringify(structure || [], null, 2)}

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
      res.status(200).json({ review: aiMessage });
    } else {
      throw new Error("AI 响应异常");
    }

  } catch (error) {
    console.error("API Error:", error);
    res.status(500).json({ review: "糟糕，老师的连接断开了。请检查 Vercel 环境变量或网络状态。" });
  }
}