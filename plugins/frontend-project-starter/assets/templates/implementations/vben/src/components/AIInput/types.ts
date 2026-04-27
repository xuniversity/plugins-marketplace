/**
 * AIInput 组件的类型定义
 */

/**
 * AIInput 组件的属性接口
 */
export interface AIInputProps {
  /** 输入框的值 */
  modelValue: string | undefined;
  /** 输入框标签 */
  label?: string;
  /** 占位符文本 */
  placeholder?: string;
  /** 文本域行数（仅在 textarea 模式下生效） */
  rows?: number;
  /** 输入框模式 */
  mode?: 'input' | 'textarea';
  /** 是否启用AI样式 */
  enableAiStyling?: boolean;
  /** 边框颜色（用于渐变），格式：'#color1,#color2' */
  borderColor?: string;
  /** 样式模式 */
  styleMode?: 'background' | 'border';
  /** 预设数据，组件初始化时自动填入 */
  presetData?: string;
  /** 是否自动润色（需要配合 presetData 使用） */
  autoPolish?: boolean;
  /** 边框圆角 */
  borderRadius?: string;
  /** 是否显示思考过程 */
  showThinkingProcess?: boolean;
  /** 思考预算（tokens） */
  thinkingBudget?: number;
  /** 使用的AI模型 */
  model?: string;
  /** 自定义系统提示词，如果设置则会覆盖默认的润色提示词 */
  systemPrompt?: string;
  /** 自定义用户提示词模板，可以使用 {content} 占位符 */
  userPromptTemplate?: string;
  /** 无法生成时的提示信息 */
  emptyGenerateMessage?: string;
  /** 是否显示 AI 生成水印（仅 textarea 模式生效） */
  showWatermark?: boolean;
  /** 外部控制的加载状态 */
  loading?: boolean;
  /** 加载状态时显示的文本 */
  loadingText?: string;
  /** 风格选择弹窗位置，默认向上弹出 */
  popoverPosition?: 'bottom' | 'top';
  /** 控制按钮显示模式：'full' 全部显示（默认）, 'copy-only' 只显示复制按钮, 'none' 不显示 */
  controlsMode?: 'copy-only' | 'full' | 'none';
}

/**
 * AIInput 组件的事件接口
 */
export interface AIInputEmits {
  /** 更新输入框的值 */
  'update:modelValue': [value: string];
  /** AI润色完成 */
  polish: [text: string];
  /** 用户反馈 */
  feedback: [type: 'negative' | 'positive'];
}

/**
 * 样式选项接口
 */
export interface StyleOption {
  /** 样式值 */
  value: 'concise' | 'professional';
  /** 样式标签 */
  label: string;
  /** 样式描述 */
  tooltip: string;
  /** 样式图标 */
  icon: string;
}

/**
 * 用户反馈类型
 */
export type FeedbackType = 'negative' | 'positive';

/**
 * 输入框模式类型
 */
export type InputMode = 'input' | 'textarea';

/**
 * 样式模式类型
 */
export type StyleMode = 'background' | 'border';

/**
 * AI润色样式类型
 */
export type PolishStyle = 'concise' | 'professional';

/**
 * AI处理模式
 */
export type AIProcessMode = 'custom' | 'polish';

/**
 * 自定义提示词配置
 */
export interface CustomPromptConfig {
  /** 系统提示词 */
  systemPrompt: string;
  /** 用户提示词模板，使用 {content} 作为内容占位符 */
  userPromptTemplate: string;
}
