export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ message: "Method Not Allowed" });

  const { topic } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  try {
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
            content: "你是一位资深的 A-Level 历史专家。请针对学生提供的历史术语进行深度解析。要求：1. 简洁解释该术语背景；2. 说明它在 1950s 美国民权运动中的关键作用；3. 给出一个高质量的 PEEL 写作示范句（中英双语）。回复字数控制在 200 字以内，排版清晰。"
          },
          {
            role: "user",
            content: `讲解知识点：${topic}`
          }
        ]
      })
    });

    const data = await response.json();
    res.status(200).json({ explanation: data.choices[0].message.content });
  } catch (error) {
    res.status(500).json({ explanation: "历史老师去图书馆了，请稍后再试。" });
  }
}
