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

/**
 * Command Words 识别配置
 * A-Level 历史/经济学考试中的关键指令词及其含义
 */
export const COMMAND_WORDS = {
  // 评估类（需要判断和结论）
  "evaluate": {
    meaning: "评估不同观点、论据的有效性，做出判断和结论",
    focus: "需要权衡利弊，给出明确的判断",
    requires: ["AO4 Evaluation", "对比分析", "结论性判断"]
  },
  "assess": {
    meaning: "评估某事物的价值、重要性或影响程度",
    focus: "需要量化或定性评估，判断重要性",
    requires: ["AO4 Evaluation", "重要性判断", "影响分析"]
  },
  "judge": {
    meaning: "基于证据做出明确的判断或决定",
    focus: "需要明确的立场和判断依据",
    requires: ["AO4 Evaluation", "明确立场", "证据支撑"]
  },
  
  // 分析类（需要深入剖析）
  "analyse": {
    meaning: "深入分析问题的组成部分、因果关系和逻辑结构",
    focus: "需要拆解问题，识别因果关系",
    requires: ["AO3 Analysis", "因果关系", "逻辑论证"]
  },
  "examine": {
    meaning: "仔细检查和分析某事物的各个方面",
    focus: "需要全面审视各个维度",
    requires: ["AO3 Analysis", "多角度审视", "细节分析"]
  },
  "explain": {
    meaning: "解释某事物的原因、过程或机制",
    focus: "需要清晰的因果链条和机制说明",
    requires: ["AO2 Application", "AO3 Analysis", "机制解释"]
  },
  
  // 描述类（需要事实和细节）
  "describe": {
    meaning: "描述某事物的特征、过程或事实",
    focus: "需要准确的事实和细节",
    requires: ["AO1 Knowledge", "事实准确性", "细节描述"]
  },
  "outline": {
    meaning: "概述主要观点或要点",
    focus: "需要简洁但全面的要点总结",
    requires: ["AO1 Knowledge", "要点总结", "结构清晰"]
  },
  
  // 比较类（需要对比分析）
  "compare": {
    meaning: "比较两个或多个事物的相似性和差异性",
    focus: "需要明确的对比框架和差异分析",
    requires: ["AO3 Analysis", "对比框架", "差异识别"]
  },
  "contrast": {
    meaning: "强调两个或多个事物的差异",
    focus: "需要突出差异点",
    requires: ["AO3 Analysis", "差异分析", "对比论证"]
  }
};

/**
 * 识别题目中的 Command Words
 * @param {string} question - 题目文本
 * @returns {Object} 识别结果，包含 commandWord, meaning, focus, requires
 */
export function identifyCommandWord(question) {
  if (!question || typeof question !== 'string') {
    return {
      commandWord: null,
      meaning: "未识别到明确的指令词",
      focus: "请根据题目要求作答",
      requires: []
    };
  }

  const questionLower = question.toLowerCase();
  
  // 按优先级匹配（评估类 > 分析类 > 描述类）
  const priorityOrder = [
    "evaluate", "assess", "judge",
    "analyse", "analyze", "examine", "explain",
    "compare", "contrast",
    "describe", "outline"
  ];

  for (const word of priorityOrder) {
    // 使用单词边界匹配，避免误匹配（如 "evaluated" 中的 "evaluate"）
    const regex = new RegExp(`\\b${word}\\b`, 'i');
    if (regex.test(questionLower)) {
      const config = COMMAND_WORDS[word] || COMMAND_WORDS[word.replace(/e$/, '')]; // 处理 analyze vs analyse
      if (config) {
        return {
          commandWord: word,
          ...config
        };
      }
    }
  }

  // 如果没有匹配到，返回默认值
  return {
    commandWord: null,
    meaning: "未识别到明确的指令词，请根据题目要求作答",
    focus: "请仔细阅读题目要求",
    requires: []
  };
}

/**
 * 生成 Command Word 识别提示文本（用于 system_prompt）
 * @param {string} question - 题目文本
 * @returns {string} 格式化的提示文本
 */
export function getCommandWordPrompt(question) {
  const identification = identifyCommandWord(question);
  
  if (!identification.commandWord) {
    return `题目分析：未识别到明确的 Command Word。请仔细分析题目要求。`;
  }

  return `题目分析 - Command Word 识别：
【指令词】${identification.commandWord.toUpperCase()}
【含义】${identification.meaning}
【重点要求】${identification.focus}
【需要的技能】${identification.requires.join('、')}

批改时必须确保学生的回答符合 "${identification.commandWord}" 的要求：
- 如果题目要求 ${identification.commandWord}，学生必须${identification.focus}
- 评分时重点关注：${identification.requires.join('、')}`;
}

