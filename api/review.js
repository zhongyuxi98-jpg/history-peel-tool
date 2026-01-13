export default function handler(req, res) {
  // 模拟 AI 思考延迟
  setTimeout(() => {
    const { point, evidence, explanation, link } = req.body;
    
    // 基础的字数检测模拟逻辑
    const feedback = {
      score: "4/5",
      analysis: {
        P: "Point Clear.",
        E: evidence.length > 30 ? "Good Evidence." : "Evidence too short.",
        Ex: "Logic follows.",
        L: "Link is present."
      },
      suggestion: "This is a simulated AI response. Once Vercel is connected, this will be replaced by real LLM feedback."
    };

    res.status(200).json(feedback);
  }, 1000);
}
