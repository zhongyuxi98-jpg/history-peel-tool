import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 支持的考试类型
const EXAM_TYPES = {
  alevel: 'alevel_prompt.txt',
  ielts: 'ielts_prompt.txt',
  toefl: 'toefl_prompt.txt',
  ib: 'ib_prompt.txt'
};

// 根据考试类型读取对应的 system prompt
function getSystemPrompt(examType = 'alevel') {
  const promptFile = EXAM_TYPES[examType] || EXAM_TYPES.alevel;

  try {
    const promptPath = join(__dirname, 'prompts', promptFile);
    return readFileSync(promptPath, 'utf-8');
  } catch (error) {
    console.error(`Failed to read prompt for ${examType}:`, error);
    // 回退到默认提示
    return 'You are an academic essay examiner. Return only valid JSON following the schema.';
  }
}

// 读取 fallback schema
function getFallbackSchema(examType = 'alevel') {
  // 根据考试类型返回不同的默认结构
  const baseSchema = {
    overall_analysis: {
      score: 0,
      grade: examType === 'ielts' ? 'Band 0' : examType === 'toefl' ? '0/5' : examType === 'ib' ? '1' : 'U',
      criteria_scores: {},
      summary: ['Error: Unable to process essay']
    },
    paragraph_reviews: [],
    action_items: [],
    model_essay: {
      intro: '',
      body: [],
      conclusion: ''
    }
  };

  // 设置不同考试类型的评分维度
  if (examType === 'ielts') {
    baseSchema.overall_analysis.criteria_scores = {
      Task_Response: 0,
      Coherence_Cohesion: 0,
      Lexical_Resource: 0,
      Grammatical_Range_Accuracy: 0
    };
  } else if (examType === 'toefl') {
    baseSchema.overall_analysis.criteria_scores = {
      Development: 0,
      Organization: 0,
      Language_Use: 0,
      Mechanics: 0
    };
  } else if (examType === 'ib') {
    baseSchema.overall_analysis.criteria_scores = {
      Knowledge_Understanding: 0,
      Application_Analysis: 0,
      Synthesis_Evaluation: 0,
      Use_of_Terminology: 0
    };
  } else {
    // A-Level 默认
    baseSchema.overall_analysis.criteria_scores = {
      AO1_Knowledge: 0,
      AO2_Application: 0,
      AO3_Analysis: 0,
      AO4_Evaluation: 0
    };
  }

  return baseSchema;
}

// 验证 JSON 结构是否符合 schema
function validateSchema(data) {
  const requiredFields = ['overall_analysis', 'paragraph_reviews', 'action_items', 'model_essay'];

  for (const field of requiredFields) {
    if (!data || typeof data !== 'object' || !(field in data)) {
      console.warn(`Missing required field: ${field}`);
      return false;
    }
  }

  // 验证 overall_analysis 结构
  if (!data.overall_analysis || typeof data.overall_analysis !== 'object') {
    return false;
  }

  const requiredOverallFields = ['score', 'grade'];
  for (const field of requiredOverallFields) {
    if (!(field in data.overall_analysis)) {
      return false;
    }
  }

  // 确保数组字段存在
  if (!Array.isArray(data.paragraph_reviews)) {
    data.paragraph_reviews = [];
  }
  if (!Array.isArray(data.action_items)) {
    data.action_items = [];
  }

  return true;
}

// Vercel serverless 函数
export default async function handler(req, res) {
  // 只允许 POST 请求
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method Not Allowed',
      message: 'Only POST requests are allowed'
    });
  }

  // 检查 Content-Type（必须在解构 body 之前）
  const contentType = req.headers['content-type'];
  if (!contentType || !contentType.includes('application/json')) {
    return res.status(415).json({
      error: 'Content-Type must be application/json'
    });
  }

  // 解构请求参数，支持 examType
  const { essay, examType = 'alevel' } = req.body;

  // 验证 examType
  if (!EXAM_TYPES[examType]) {
    return res.status(400).json({
      error: 'Invalid exam type',
      message: `Supported types: ${Object.keys(EXAM_TYPES).join(', ')}`
    });
  }

  if (essay && essay.length > 15000) {
    return res.status(400).json({
      error: 'Essay too long'
    });
  }

  if (!essay || typeof essay !== 'string' || essay.trim().length === 0) {
    return res.status(400).json({
      error: 'Invalid essay content',
      message: 'Essay is required and must be a non-empty string'
    });
  }

  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) {
    console.error('DASHSCOPE_API_KEY is not set');
    const fallbackSchema = getFallbackSchema(examType);
    return res.status(500).json({
      ...fallbackSchema,
      error: 'API key not configured'
    });
  }

  const systemPrompt = getSystemPrompt(examType);
  const fallbackSchema = getFallbackSchema(examType);

  try {
    // 调用大模型
    const response = await fetch(
      'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'qwen-plus',
          messages: [
            {
              role: 'system',
              content: systemPrompt
            },
            {
              role: 'user',
              content: `Please review this essay according to the schema:\n\n${essay}`
            }
          ],
          temperature: 0.3,
          response_format: { type: 'json_object' }
        })
      }
    );

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const apiData = await response.json();
    const modelResponse = apiData.choices?.[0]?.message?.content;

    if (!modelResponse) {
      throw new Error('No content in API response');
    }

    // 尝试解析 JSON
    let parsedData;
    try {
      // 移除可能的 markdown 代码块标记
      const cleanedResponse = modelResponse
        .replace(/^```json\s*/i, '')
        .replace(/^```\s*/i, '')
        .replace(/\s*```$/i, '')
        .trim();

      parsedData = JSON.parse(cleanedResponse);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      console.error('Raw response:', modelResponse);
      return res.json(fallbackSchema);
    }

    // 验证结构
    if (!validateSchema(parsedData)) {
      console.warn('Schema validation failed, merging with fallback');
      const mergedData = {
        ...fallbackSchema,
        ...parsedData,
        overall_analysis: {
          ...fallbackSchema.overall_analysis,
          ...(parsedData.overall_analysis || {})
        },
        paragraph_reviews: Array.isArray(parsedData.paragraph_reviews)
          ? parsedData.paragraph_reviews
          : fallbackSchema.paragraph_reviews,
        action_items: Array.isArray(parsedData.action_items)
          ? parsedData.action_items
          : fallbackSchema.action_items,
        model_essay: {
          ...fallbackSchema.model_essay,
          ...(parsedData.model_essay || {})
        }
      };
      return res.json(mergedData);
    }

    // 添加 examType 到响应中，方便前端使用
    parsedData.examType = examType;

    return res.json(parsedData);

  } catch (error) {
    console.error('Error in review API:', error);
    return res.status(500).json({
      ...fallbackSchema,
      error: 'AI service error',
      message: error.message
    });
  }
}
