export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ explanation: "Method Not Allowed" });
  }

  const { topic, language } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  try {
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
              content: `你是一位专业的 A-Level 历史老师。请针对 1950s 美国民权运动背景进行深度讲解。
要求：
1. 语言：${language === 'en' ? 'Strict Academic English' : (language === 'zh' ? '严谨学术中文' : '中英双语对照')}。
2. 包含：该知识点的定义、其在民权运动中的具体重要性、以及 A-Level 考试建议。
3. 质量：内容要详实，不要过于简略。`
            },
            {
              role: "user",
              content: `请详细解析：${topic}`
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
