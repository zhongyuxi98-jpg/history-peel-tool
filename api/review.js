import express from 'express';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const router = express.Router();

// 读取 system prompt
function getSystemPrompt() {
  try {
    const promptPath = join(__dirname, 'prompts', 'review_system_prompt.txt');
    return readFileSync(promptPath, 'utf-8');
  } catch (error) {
    console.error('Failed to read system prompt:', error);
    return 'You are an A-Level History examiner. Return only valid JSON following the schema.';
  }
}

// 读取 fallback schema
function getFallbackSchema() {
  try {
    const schemaPath = join(__dirname, '..', 'data', 'review_schema.json');
    const schemaContent = readFileSync(schemaPath, 'utf-8');
    return JSON.parse(schemaContent);
  } catch (error) {
    console.error('Failed to read fallback schema:', error);
    return {
      overall_analysis: {
        score: 0,
        grade: "U",
        ao_scores: {
          AO1_Knowledge: 0,
          AO2_Application: 0,
          AO3_Analysis: 0,
          AO4_Evaluation: 0
        },
        summary: ["Error: Unable to load schema"]
      },
      paragraph_reviews: [],
      action_items: [],
      model_essay: {
        intro: "",
        body: [],
        conclusion: ""
      }
    };
  }
}

// 验证 JSON 结构是否符合 schema
function validateSchema(data, fallbackSchema) {
  const requiredFields = ['overall_analysis', 'paragraph_reviews', 'action_items', 'model_essay'];
  
  for (const field of requiredFields) {
    if (!data || typeof data !== 'object' || !(field in data)) {
      console.warn(`Missing required field: ${field}, using fallback`);
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

router.post('/review', async (req, res) => {
  const { essay } = req.body;
  
  if (!req.is('application/json')) {
    return res.status(415).json({
      error: 'Content-Type must be application/json'
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
    const fallbackSchema = getFallbackSchema();
    return res.status(500).json({
      ...fallbackSchema,
      error: 'API key not configured'
    });
  }

  const systemPrompt = getSystemPrompt();
  const fallbackSchema = getFallbackSchema();

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
      // 使用 fallback schema
      return res.json(fallbackSchema);
    }

    // 验证结构
    if (!validateSchema(parsedData, fallbackSchema)) {
      console.warn('Schema validation failed, using fallback');
      // 合并 fallback 以确保所有必需字段存在
      const mergedData = {
        ...fallbackSchema,
        ...parsedData,
        overall_analysis: {
          ...fallbackSchema.overall_analysis,
          ...parsedData.overall_analysis
        },
        paragraph_reviews: Array.isArray(parsedData.paragraph_reviews) 
          ? parsedData.paragraph_reviews 
          : fallbackSchema.paragraph_reviews,
        action_items: Array.isArray(parsedData.action_items)
          ? parsedData.action_items
          : fallbackSchema.action_items,
        model_essay: {
          ...fallbackSchema.model_essay,
          ...parsedData.model_essay
        }
      };
      return res.json(mergedData);
    }

    // 返回解析后的 JSON 对象
    return res.json(parsedData);

  } catch (error) {
    console.error('Error in review API:', error);
    // 返回 fallback schema
    return res.status(500).json({
      ...fallbackSchema,
      error: 'AI service error',
      message: error.message
    });
  }
});

export default router;
