/**
 * 考纲评分配置 (Scoring Rubrics Configuration)
 * 根据不同的考试类型定义评分维度和标准
 */

export const RUBRICS = {
  /**
   * IELTS 学术写作评分标准 (0-9分制)
   * Task 2 评分维度
   */
  IELTS: {
    name: "IELTS Academic Writing",
    dimensions: [
      {
        name: "Task Response",
        description: "是否完整回答了题目要求，观点是否清晰，论证是否充分"
      },
      {
        name: "Coherence & Cohesion",
        description: "文章结构是否清晰，段落之间逻辑是否连贯，连接词使用是否恰当"
      },
      {
        name: "Lexical Resource",
        description: "词汇使用是否准确、多样，是否使用了学术词汇"
      },
      {
        name: "Grammatical Range & Accuracy",
        description: "语法结构是否多样，语法错误是否影响理解"
      }
    ],
    scoringRange: "0-9",
    scaleType: "numeric"
  },

  /**
   * A-Level Economics 评分标准 (A*-E等级制)
   * AO (Assessment Objectives) 评分维度
   */
  AL_ECON: {
    name: "A-Level Economics",
    dimensions: [
      {
        name: "AO1 Knowledge",
        description: "对经济学概念、理论和事实的准确理解与掌握"
      },
      {
        name: "AO2 Application",
        description: "将经济学知识应用到具体情境和案例中的能力"
      },
      {
        name: "AO3 Analysis",
        description: "分析经济问题，识别因果关系，构建逻辑论证的能力"
      },
      {
        name: "AO4 Evaluation",
        description: "评估不同观点、论据和结论，做出判断和结论的能力"
      }
    ],
    scoringRange: "A*-E",
    scaleType: "grade"
  }
};

/**
 * 获取指定考试类型的评分维度描述
 * @param {string} examType - 考试类型 ('IELTS' 或 'AL_ECON')
 * @returns {string} 格式化的维度描述文本
 */
export function getRubricDescription(examType) {
  const rubric = RUBRICS[examType];
  if (!rubric) {
    throw new Error(`Unknown exam type: ${examType}`);
  }

  const dimensionList = rubric.dimensions
    .map((dim, index) => `${index + 1}. ${dim.name}: ${dim.description}`)
    .join("\n");

  return `评分标准 (${rubric.name}, ${rubric.scoringRange}):
${dimensionList}

你必须严格按照以上四个维度进行评分，不要混淆不同考纲的标准。`;
}

/**
 * 获取维度名称列表
 * @param {string} examType - 考试类型
 * @returns {Array<string>} 维度名称数组
 */
export function getDimensionNames(examType) {
  const rubric = RUBRICS[examType];
  if (!rubric) {
    throw new Error(`Unknown exam type: ${examType}`);
  }
  return rubric.dimensions.map(dim => dim.name);
}

