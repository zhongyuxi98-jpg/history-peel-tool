// 导入 Command Words 识别
import { getCommandWordPrompt } from '../src/configs.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ explanation: "Method Not Allowed" });
  }

  const { topic, language, essay_question, section_type, constraint } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  try {
    const strictConstraint = constraint
      ? `\n\n${constraint}`
      : "\n\nConstraint: Follow the selected language mode strictly.";

    // [Agent-04] Command Words 识别
    const commandWordPrompt = essay_question ? getCommandWordPrompt(essay_question) : "";

    const response = await fetch(
      'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: "qwen-plus", // 质量优先，上课用这个最稳
          messages: [
            {
              role: "system",
              content: `你是 [Agent-04 考纲逻辑专家]。你的任务是完善后端 system_prompt 和数据协议。

${commandWordPrompt ? `\n${commandWordPrompt}\n` : ""}

你是一位专业的 A-Level 历史老师。请针对 1950s 美国民权运动背景进行深度讲解。${strictConstraint}
要求：
1. 语言：${language === 'en' ? 'Strict Academic English' : (language === 'zh' ? '严谨学术中文' : '中英双语对照')}。
2. 包含：该知识点的定义、其在民权运动中的具体重要性、以及 A-Level 考试建议。
3. 质量：内容要详实，不要过于简略。
4. 如果提供了 essay_question（学生可编辑），请将该知识点如何用于回答该题目说清楚。
5. ${commandWordPrompt ? '在讲解时，特别说明该知识点如何帮助学生满足题目中识别到的 Command Word 要求。' : '仔细分析题目要求，确保讲解内容与题目要求对齐。'}`
            },
            {
              role: "user",
              content: `Essay question: ${essay_question || "(none)"}\nSection type: ${section_type || "(none)"}\n\n请详细解析：${topic}`
            }
          ]
        })
      }
    );

    const data = await response.json();
    const content = data.choices[0].message.content;

    res.status(200).json({ explanation: content });

  } catch (error) {
    console.error(error);
    res.status(500).json({ explanation: "AI 接口连接异常，请稍后重试。" });
  }
}
