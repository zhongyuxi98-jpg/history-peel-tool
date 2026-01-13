export default async function handler(req, res) {
  // 仅允许 POST 请求
  if (req.method !== 'POST') return res.status(405).json({ review: "Method Not Allowed" });

  // 1. [关键修改] 从 req.body 中新增解构出 language 参数
  const { point, evidence1, evidence2, link, language } = req.body;
  const apiKey = process.env.DASHSCOPE_API_KEY;

  // 2. [新增] 动态生成语言风格指令
  let languageDirective = "";
  if (language === 'zh') {
    languageDirective = "请完全使用【中文】进行批改。你现在是一位严厉但负责的『中教老师』，重点检查史实细节。";
  } else if (language === 'en') {
    languageDirective = "Please respond strictly in 【English】. Act as a 'Native British/American Examiner'. Focus on academic phrasing, tone, and logical flow.";
  } else {
    // 默认双语模式
    languageDirective = "请使用【双语】批改：核心评价（如 Band 分级）用英文，具体的改进指导和史实分析用中文，确保学生能精准理解如何改进。";
  }

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
            content: `你是一位专业的 A-Level 历史老师。${languageDirective} 学生正在练习 1950s 美国民权运动的 PEEL 段落写作。
            
            批改准则：
            1. 态度检测：如果输入是 '123' 或乱码，请毒舌且严厉地训诫学生，要求其端正学术态度。
            2. 结构评分：检查 Point, Evidence, Link 是否逻辑闭环。
            3. 史实核查：必须提及核心史实（如 Brown v. Board, Montgomery Bus Boycott, Little Rock 9 等）。
            4. 改进建议：给出具体的修改建议，甚至可以给出一句示范。`
          },
          {
            role: "user",
            content: `学生提交内容：
            Point: ${point}
            Evidence 1: ${evidence1}
            Evidence 2: ${evidence2}
            Link: ${link}
            
            请根据上述内容给出你的 Review。`
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