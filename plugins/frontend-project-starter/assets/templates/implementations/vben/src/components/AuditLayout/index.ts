/**
 * AuditLayout - 通用审核布局组件
 *
 * 提供左侧内容区域插槽 + 右侧 AI 审核助手面板 + 底部操作按钮的通用布局
 */
export { default as AuditLayout } from './AuditLayout.vue';
export type {
  AuditChecklistItem,
  AuditLayoutEmits,
  AuditLayoutProps,
  AuditRecommendation,
  AuditResult,
  ChecklistStatus,
  RejectActionData,
  RejectActionType,
  RejectTarget,
} from './types';
