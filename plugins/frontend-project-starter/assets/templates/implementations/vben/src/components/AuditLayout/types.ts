/**
 * AuditLayout 组件类型定义
 *
 * 通用的 AI 辅助审核布局组件类型
 */

/** 审核建议类型 */
export type AuditRecommendation = 'ESCALATE' | 'PASS' | 'PENDING' | 'REJECT';

/** 检查项状态 */
export type ChecklistStatus = 'fail' | 'pass' | 'unknown' | 'warning';

/** 检查清单项 */
export interface AuditChecklistItem {
  /** 检查项名称 */
  item: string;
  /** 检查状态 */
  status: ChecklistStatus;
  /** 检查结果说明 */
  description: string;
}

/** AI 审核结果 */
export interface AuditResult {
  /** 审核建议：通过/驳回/待定/转交老师 */
  recommendation: AuditRecommendation;
  /** 置信度 0-100 */
  confidence: number;
  /** 总体建议说明 */
  summary: string;
  /** 检查清单 */
  checklist: AuditChecklistItem[];
  /** 驳回原因模板 */
  rejectReason?: string;
  /** 待定原因说明 */
  pendingReason?: string;
  /** 转交老师原因说明 */
  escalateReason?: string;
}

/** 可驳回的目标节点 */
export interface RejectTarget {
  /** 节点定义 ID */
  id: string;
  /** 节点名称 */
  name: string;
  /** 节点描述 */
  description?: string;
}

/** 驳回/待定/转交操作类型 */
export type RejectActionType = 'escalate' | 'pending' | 'reject';

/** 驳回/待定/转交操作数据 */
export interface RejectActionData {
  /** 操作类型 */
  type: RejectActionType;
  /** 原因说明 */
  reason: string;
  /** 目标节点定义 ID */
  targetNodeDefId?: string;
}

/** AuditLayout 组件 Props */
export interface AuditLayoutProps {
  /** 页面标题 */
  pageTitle?: string;
  /** 是否显示页面返回按钮 */
  showBackButton?: boolean;
  /** 返回按钮提示文案 */
  backButtonTitle?: string;
  /** AI 审核结果 */
  auditResult?: AuditResult | null;
  /** 左侧业务内容加载状态 */
  contentLoading?: boolean;
  /** 是否只读（只查看，不可分析和审核） */
  readonly?: boolean;
  /** AI 分析加载状态 */
  loading?: boolean;
  /** AI 分析错误信息 */
  error?: null | string;
  /** 当前可操作节点实例 ID（控制按钮是否可用） */
  nodeInstanceId?: string;
  /** 可驳回的目标节点列表 */
  rejectableTargets?: RejectTarget[];
  /** 操作按钮加载状态 */
  actionLoading?: boolean;
  /** 面板标题（默认"审核助手"） */
  title?: string;
  /** 收起态加载提示标题 */
  loadingHintTitle?: string;
  /** 加载态轮播文案 */
  loadingMessages?: string[];
}

/** AuditLayout 组件 Emits */
export interface AuditLayoutEmits {
  /** 触发 AI 分析 或 审核通过 */
  (e: 'analyze' | 'approve' | 'back'): void;
  /** 驳回/待定/转交操作 */
  (e: 'reject', data: RejectActionData): void;
}
