import 'dotenv/config'; // 加载环境变量
import express from 'express';
import cors from 'cors';
import reviewHandler from './api/review.js';
import explainHandler from './api/explain.js';

const app = express();

app.use(cors());
app.use(express.json());

// 本地开发时，将 serverless 函数包装为 Express 路由
app.post('/api/review', async (req, res) => {
  await reviewHandler(req, res);
});

app.post('/api/explain', async (req, res) => {
  await explainHandler(req, res);
});

// 本地开发服务器
if (process.env.NODE_ENV !== 'production' || !process.env.VERCEL) {
  const PORT = process.env.PORT || 5501;
  app.listen(PORT, () => {
    console.log(`API server running at http://localhost:${PORT}`);
  });
}

// Vercel 需要导出 app（虽然不会用到，但保持兼容）
export default app;
