export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { point, evidence1, evidence2, link } = req.body;

  const aiFeedback = `
【PEEL 结构分析报告】
🎯 观点 (Point): ${point ? "已识别" : "未填写"}
📚 证据 (Evidence): 检测到 ${(evidence1 || "").length + (evidence2 || "").length} 个字符的内容。
🔗 逻辑 (Link): ${link ? "已检测到收尾" : "建议加强总结"}

💡 老师建议：
这是来自后端的模拟回复。请确保你已经完成了 Vercel 的部署，以便后续连接真正的 Gemini 智能批改模型。
  `;

  return res.status(200).json({ review: aiFeedback });
}