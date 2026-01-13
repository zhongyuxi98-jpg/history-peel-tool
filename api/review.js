export default async function handler(req, res) {
  // 仅允许 POST 请求
  if (req.method !== 'POST') return res.status(405).json({ review: "Method Not Allowed" });

  const { point, evidence1, evidence2, link } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  try {
    // 调用阿里云百炼的 OpenAI 兼容接口
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
            content: "你是一位专业且严厉的历史老师。学生正在练习 PEEL 写作（关于1950s美国民权运动）。如果学生输入 '123' 等无意义内容，请毒舌地指出其缺乏学术态度。如果学生写了内容，请检查是否提到了 Brown v. Board 或 Montgomery Bus Boycott 等核心史实，并给出中文改进建议。"
          },
          {
            role: "user",
            content: `学生提交内容：\nPoint: ${point}\nEvidence: ${evidence1}, ${evidence2}\nLink: ${link}`
          }
        ]
      })
    });

    const data = await response.json();
    const aiMessage = data.choices[0].message.content;
    res.status(200).json({ review: aiMessage });
  } catch (error) {
    res.status(500).json({ review: "糟糕，老师的连接断开了。请检查 Vercel 变量是否生效。" });
  }
}