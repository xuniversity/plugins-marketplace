<script lang="ts" setup>
import type { CSSProperties } from 'vue';

/**
 * AuditLayout - 通用审核布局组件
 *
 * 功能：
 * - 左侧内容区域（插槽）
 * - 右侧 AI 审核助手面板（可折叠）
 * - 固定底部操作条：通过/驳回/待定/转交老师
 */
import type {
  AuditLayoutEmits,
  AuditLayoutProps,
  RejectActionType,
} from './types';

import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue';

import { Button, Card, Input, Modal, Popover, Select } from 'ant-design-vue';

import {
  LetsIconsCheckFill,
  LetsIconsCloseRoundFill,
  MdiAlertCircleOutline,
  MdiArrowLeft,
  MdiCheck,
  MdiChevronRight,
  MdiClockOutline,
  MdiClose,
  MdiCopy,
  MdiHelpCircleOutline,
  MdiRefresh,
  MingcuteBulb2AiLine,
  MingcuteTransfer3Fill,
} from '#/icons';

// ==================== Props & Emits ====================

const props = withDefaults(defineProps<AuditLayoutProps>(), {
  pageTitle: '',
  showBackButton: false,
  backButtonTitle: '返回',
  auditResult: null,
  contentLoading: false,
  readonly: false,
  loading: false,
  error: null,
  nodeInstanceId: undefined,
  rejectableTargets: () => [],
  actionLoading: false,
  title: '审核助手',
  loadingHintTitle: 'AI 分析中',
  loadingMessages: () => [
    '正在分析当前材料',
    '正在整理关键信息',
    '正在生成辅助建议',
  ],
});

const emit = defineEmits<AuditLayoutEmits>();

// ==================== 状态 ====================

/** 复制成功状态 */
const copySuccess = ref(false);

/** 侧边栏折叠状态 */
const isCollapsed = ref(true);
const leftPaneRef = ref<HTMLElement | null>(null);
const assistantRef = ref<HTMLElement | null>(null);
const footerBarRef = ref<HTMLElement | null>(null);
const assistantStickyTop = ref(16);
const assistantMaxHeight = ref(520);
const assistantDockLeft = ref(0);
const assistantCollapsedShellWidth = ref(64);
const viewportWidth = ref(
  typeof window === 'undefined'
    ? 0
    : document.documentElement.clientWidth || window.innerWidth,
);
const isDesktopAssistant = ref(
  typeof window === 'undefined' ? false : window.innerWidth > 1280,
);
const assistantFloatReady = ref(false);
let layoutResizeObserver: null | ResizeObserver = null;
const DESKTOP_ASSISTANT_FLOAT_GAP = 8;
const DESKTOP_ASSISTANT_FLOAT_HORIZONTAL_PADDING = 8;
const DESKTOP_ASSISTANT_COLLAPSED_PANEL_WIDTH = 56;
const DESKTOP_ASSISTANT_MIN_TOP = 120;
const assistantHintVisible = ref(false);
const assistantHintTitle = ref('');
const assistantHintText = ref('');
const assistantHintTone = ref<'complete' | 'error'>('complete');
const assistantHintDismissed = ref(false);
let assistantRevealFrame: null | number = null;

/** 加载中状态文案 */
const resolvedLoadingHintTitle = computed(() => {
  const title = props.loadingHintTitle?.trim();
  return title || 'AI 分析中';
});
const resolvedLoadingMessages = computed(() => {
  const messages = props.loadingMessages
    .map((message) => message.trim())
    .filter(Boolean);
  return messages.length > 0
    ? messages
    : ['正在分析当前材料', '正在整理关键信息', '正在生成辅助建议'];
});
const loadingMessageIndex = ref(0);
const loadingMessage = computed(
  () =>
    resolvedLoadingMessages.value[loadingMessageIndex.value] ??
    resolvedLoadingMessages.value[0]!,
);
const assistantHintCard = computed(() => {
  if (
    props.loading &&
    isCollapsed.value &&
    isDesktopAssistant.value &&
    assistantFloatReady.value &&
    !assistantHintDismissed.value
  ) {
    return {
      tone: 'loading' as const,
      title: resolvedLoadingHintTitle.value,
      text: loadingMessage.value,
    };
  }

  if (!assistantHintVisible.value) {
    return null;
  }

  return {
    tone: assistantHintTone.value,
    title: assistantHintTitle.value,
    text: assistantHintText.value,
  };
});
const showPageHeader = computed(
  () => props.showBackButton || Boolean(props.pageTitle),
);
const analyzeActionText = computed(() =>
  props.loading ? '分析中' : '重新分析',
);
const analyzeDisabled = computed(() => props.loading || props.readonly);
const actionDisabled = computed(() => props.readonly || !props.nodeInstanceId);
const assistantShellStyle = computed(() =>
  isDesktopAssistant.value
    ? {
        height: `${assistantMaxHeight.value}px`,
        width: isCollapsed.value
          ? `${assistantCollapsedShellWidth.value}px`
          : undefined,
      }
    : undefined,
);
const assistantPanelStyle = computed((): CSSProperties => {
  const baseStyle: CSSProperties = {
    '--audit-layout-assistant-max-height': `${assistantMaxHeight.value}px`,
  };

  if (!isDesktopAssistant.value) {
    return baseStyle;
  }

  if (isCollapsed.value) {
    return {
      ...baseStyle,
      height: `${assistantMaxHeight.value}px`,
      left: 'auto',
      maxHeight: `${assistantMaxHeight.value}px`,
      opacity: assistantFloatReady.value ? 1 : 0,
      pointerEvents: assistantFloatReady.value ? 'auto' : 'none',
      position: 'fixed',
      right: `${DESKTOP_ASSISTANT_FLOAT_GAP}px`,
      top: `${assistantStickyTop.value}px`,
      transition: assistantFloatReady.value ? 'opacity 120ms ease-out' : 'none',
      visibility: assistantFloatReady.value ? 'visible' : 'hidden',
      width: `${DESKTOP_ASSISTANT_COLLAPSED_PANEL_WIDTH}px`,
      zIndex: 20,
    };
  }

  const panelLeft =
    assistantDockLeft.value + DESKTOP_ASSISTANT_FLOAT_HORIZONTAL_PADDING;
  const panelWidth = Math.max(
    320,
    viewportWidth.value - panelLeft - DESKTOP_ASSISTANT_FLOAT_GAP,
  );

  return {
    ...baseStyle,
    height: `${assistantMaxHeight.value}px`,
    left: `${panelLeft}px`,
    maxHeight: `${assistantMaxHeight.value}px`,
    opacity: assistantFloatReady.value ? 1 : 0,
    pointerEvents: assistantFloatReady.value ? 'auto' : 'none',
    position: 'fixed',
    right: 'auto',
    top: `${assistantStickyTop.value}px`,
    transition: assistantFloatReady.value ? 'opacity 120ms ease-out' : 'none',
    visibility: assistantFloatReady.value ? 'visible' : 'hidden',
    width: `${panelWidth}px`,
    zIndex: 20,
  };
});
const approveButtonClass = computed(() =>
  actionDisabled.value
    ? 'min-w-[120px] audit-layout__action-button--disabled'
    : 'min-w-[120px] audit-layout__action-button--approve',
);
const rejectButtonClass = computed(() =>
  actionDisabled.value
    ? 'min-w-[120px] audit-layout__action-button--disabled'
    : 'min-w-[120px]',
);
const pendingButtonClass = computed(() =>
  actionDisabled.value
    ? 'min-w-[120px] audit-layout__action-button--disabled'
    : 'min-w-[120px] audit-layout__action-button--pending',
);
const escalateButtonClass = computed(() =>
  actionDisabled.value
    ? 'min-w-[120px] audit-layout__action-button--disabled'
    : 'min-w-[120px] audit-layout__action-button--escalate',
);

/** 驳回/待定/转交弹窗 */
const rejectModalState = reactive({
  visible: false,
  type: 'reject' as RejectActionType,
  reason: '',
  targetNodeDefId: undefined as string | undefined,
});
const rejectReasonError = ref('');
let loadingMessageTimer: null | number = null;

// ==================== 方法定义 ====================

/** 触发 AI 分析 */
const handleAnalyze = () => {
  if (props.readonly || props.loading) return;
  emit('analyze');
};

/** 页面返回 */
const handleBack = () => {
  emit('back');
};

/** 是否偏好减少动态效果 */
const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/** 停止加载文案轮换 */
const stopLoadingMessageCycle = () => {
  if (!loadingMessageTimer) return;
  window.clearInterval(loadingMessageTimer);
  loadingMessageTimer = null;
};

/** 清理审核助手提示计时器 */
const clearAssistantHintTimers = () => {};

/** 清理审核助手显隐校准帧 */
const cancelAssistantRevealFrame = () => {
  if (!assistantRevealFrame) return;
  window.cancelAnimationFrame(assistantRevealFrame);
  assistantRevealFrame = null;
};

/** 隐藏审核助手提示 */
const hideAssistantHint = () => {
  assistantHintVisible.value = false;
};

/** 关闭审核助手提示 */
const dismissAssistantHint = () => {
  assistantHintDismissed.value = true;
  assistantHintVisible.value = false;
};

/** 获取收起态完成提示 */
const getAssistantCompletionHint = (): string => {
  const highlightedCount =
    props.auditResult?.checklist.filter(
      (item) => item.status === 'fail' || item.status === 'warning',
    ).length ?? 0;

  if (highlightedCount > 0) {
    return `发现 ${highlightedCount} 条重点，点击查看建议`;
  }

  return 'AI 建议已生成，点击展开查看';
};

/** 展示审核助手提示 */
const showAssistantHint = (
  tone: 'complete' | 'error',
  title: string,
  text: string,
) => {
  if (typeof window === 'undefined') return;

  clearAssistantHintTimers();
  assistantHintDismissed.value = false;
  assistantHintTone.value = tone;
  assistantHintTitle.value = title;
  assistantHintText.value = text;
  assistantHintVisible.value = true;
};

/** 更新审核助手吸附位置与可用高度 */
const updateAssistantLayoutMetrics = (
  captureTop = false,
  revealWhenReady = true,
) => {
  if (typeof window === 'undefined') return;

  const assistantElement = assistantRef.value;
  const leftPaneElement = leftPaneRef.value;
  if (!assistantElement) return;

  isDesktopAssistant.value = window.innerWidth > 1280;
  if (!isDesktopAssistant.value) {
    assistantFloatReady.value = true;
    return;
  }

  viewportWidth.value =
    document.documentElement.clientWidth || window.innerWidth;

  const rect = assistantElement.getBoundingClientRect();
  const leftPaneRect = leftPaneElement?.getBoundingClientRect();
  const nextTop = Math.max(DESKTOP_ASSISTANT_MIN_TOP, Math.round(rect.top));
  const footerHeight = footerBarRef.value?.offsetHeight || 0;
  const bottomReserve = footerHeight + DESKTOP_ASSISTANT_FLOAT_GAP;

  if (captureTop) {
    assistantStickyTop.value = nextTop;
  }
  const shellRightInset = Math.max(
    0,
    Math.round(viewportWidth.value - rect.right),
  );
  assistantDockLeft.value = Math.round(leftPaneRect?.right || rect.left);
  assistantCollapsedShellWidth.value = Math.max(
    DESKTOP_ASSISTANT_COLLAPSED_PANEL_WIDTH,
    DESKTOP_ASSISTANT_COLLAPSED_PANEL_WIDTH +
      DESKTOP_ASSISTANT_FLOAT_GAP * 2 -
      shellRightInset,
  );
  assistantMaxHeight.value = Math.max(
    320,
    Math.floor(window.innerHeight - assistantStickyTop.value - bottomReserve),
  );
  if (revealWhenReady) {
    assistantFloatReady.value = true;
  }

  return [
    assistantDockLeft.value,
    assistantCollapsedShellWidth.value,
    assistantMaxHeight.value,
    assistantStickyTop.value,
    viewportWidth.value,
    isCollapsed.value ? 'collapsed' : 'expanded',
  ].join(':');
};

const scheduleAssistantLayoutMetrics = (
  captureTop = false,
  hideUntilReady = false,
) => {
  if (typeof window === 'undefined') return;

  cancelAssistantRevealFrame();

  if (!hideUntilReady) {
    assistantRevealFrame = window.requestAnimationFrame(() => {
      assistantRevealFrame = null;
      updateAssistantLayoutMetrics(captureTop);
    });
    return;
  }

  if (hideUntilReady) {
    assistantFloatReady.value = false;
  }

  let stableFrameCount = 0;
  let previousSignature = '';
  let shouldCaptureTop = captureTop;

  const waitForStableLayout = () => {
    assistantRevealFrame = window.requestAnimationFrame(() => {
      const signature = updateAssistantLayoutMetrics(shouldCaptureTop, false);
      shouldCaptureTop = false;

      if (!isDesktopAssistant.value) {
        assistantFloatReady.value = true;
        assistantRevealFrame = null;
        return;
      }

      if (signature && signature === previousSignature) {
        stableFrameCount += 1;
      } else {
        previousSignature = signature ?? '';
        stableFrameCount = 0;
      }

      if (stableFrameCount >= 2) {
        assistantFloatReady.value = true;
        assistantRevealFrame = null;
        return;
      }

      waitForStableLayout();
    });
  };

  waitForStableLayout();
};

const handleWindowResize = () => {
  updateAssistantLayoutMetrics(false);
};

/** 开始加载文案轮换 */
const startLoadingMessageCycle = () => {
  loadingMessageIndex.value = 0;

  if (
    typeof window === 'undefined' ||
    prefersReducedMotion() ||
    resolvedLoadingMessages.value.length <= 1
  ) {
    stopLoadingMessageCycle();
    return;
  }

  stopLoadingMessageCycle();
  loadingMessageTimer = window.setInterval(() => {
    loadingMessageIndex.value =
      (loadingMessageIndex.value + 1) % resolvedLoadingMessages.value.length;
  }, 1800);
};

/** 审核通过 */
const handleApprove = () => {
  if (actionDisabled.value) return;
  emit('approve');
};

/** 打开驳回/待定/转交弹窗 */
const openRejectModal = (type: RejectActionType) => {
  if (actionDisabled.value) return;

  rejectModalState.type = type;
  rejectModalState.visible = true;
  rejectModalState.reason = '';
  rejectReasonError.value = '';

  // 预填充 AI 建议的原因
  if (props.auditResult) {
    if (type === 'reject' && props.auditResult.rejectReason) {
      rejectModalState.reason = props.auditResult.rejectReason;
    } else if (type === 'pending' && props.auditResult.pendingReason) {
      rejectModalState.reason = props.auditResult.pendingReason;
    } else if (type === 'escalate' && props.auditResult.escalateReason) {
      rejectModalState.reason = props.auditResult.escalateReason;
    }
  }

  // 默认选择第一个可驳回目标
  if (props.rejectableTargets && props.rejectableTargets.length > 0) {
    // 根据类型选择默认目标节点
    const defaultTarget = props.rejectableTargets.find((t) => {
      if (type === 'pending') return t.name.includes('待定');
      if (type === 'escalate')
        return t.name.includes('老师') || t.name.includes('转交');
      return true;
    });
    rejectModalState.targetNodeDefId =
      defaultTarget?.id || props.rejectableTargets[0]?.id;
  }
};

/** 确认驳回/待定/转交 */
const handleConfirmReject = () => {
  if (!rejectModalState.reason.trim()) {
    rejectReasonError.value = `请输入${getReasonLabel(rejectModalState.type)}`;
    return;
  }

  emit('reject', {
    type: rejectModalState.type,
    reason: rejectModalState.reason,
    targetNodeDefId: rejectModalState.targetNodeDefId,
  });

  rejectModalState.visible = false;
};

const handleRejectReasonInput = () => {
  if (rejectReasonError.value && rejectModalState.reason.trim()) {
    rejectReasonError.value = '';
  }
};

watch(
  () => rejectModalState.visible,
  (visible) => {
    if (!visible) {
      rejectReasonError.value = '';
    }
  },
);

watch(
  () => props.loading,
  (loading, previousLoading) => {
    if (loading) {
      assistantHintDismissed.value = false;
      hideAssistantHint();
      startLoadingMessageCycle();
      return;
    }

    stopLoadingMessageCycle();
    loadingMessageIndex.value = 0;

    if (
      !previousLoading ||
      !isCollapsed.value ||
      !isDesktopAssistant.value ||
      props.contentLoading
    ) {
      return;
    }

    if (props.error) {
      showAssistantHint('error', 'AI 审核未完成', '点击展开查看原因或重新分析');
      return;
    }

    if (props.auditResult) {
      showAssistantHint(
        'complete',
        'AI 审核已完成',
        getAssistantCompletionHint(),
      );
    }
  },
  { immediate: true },
);

watch(isCollapsed, async () => {
  if (!isCollapsed.value) {
    hideAssistantHint();
  }
  await nextTick();
  updateAssistantLayoutMetrics(false);
});

onMounted(async () => {
  await nextTick();
  scheduleAssistantLayoutMetrics(true, true);
  window.addEventListener('resize', handleWindowResize);
  if (typeof ResizeObserver !== 'undefined') {
    layoutResizeObserver = new ResizeObserver(() => {
      updateAssistantLayoutMetrics(false);
    });
    if (leftPaneRef.value) {
      layoutResizeObserver.observe(leftPaneRef.value);
    }
    if (assistantRef.value) {
      layoutResizeObserver.observe(assistantRef.value);
    }
    if (footerBarRef.value) {
      layoutResizeObserver.observe(footerBarRef.value);
    }
  }
});

onBeforeUnmount(() => {
  stopLoadingMessageCycle();
  hideAssistantHint();
  cancelAssistantRevealFrame();
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleWindowResize);
  }
  layoutResizeObserver?.disconnect();
  layoutResizeObserver = null;
});

/** 复制摘要内容 */
const handleCopySummary = async () => {
  if (!props.auditResult?.summary) return;

  try {
    await navigator.clipboard.writeText(props.auditResult.summary);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  } catch (error) {
    console.error('复制失败:', error);
  }
};

/** 切换侧边栏折叠状态 */
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

/** 获取推荐文本 */
const getRecommendationText = (recommendation: string): string => {
  const textMap: Record<string, string> = {
    PASS: '建议通过',
    REJECT: '建议驳回',
    PENDING: '建议待定',
    ESCALATE: '转交老师',
  };
  return textMap[recommendation] ?? recommendation;
};

const getRecommendationTitleClass = (recommendation: string) => {
  const classMap: Record<string, string> = {
    PASS: 'audit-layout__recommendation-title--pass',
    REJECT: 'audit-layout__recommendation-title--reject',
    PENDING: 'audit-layout__recommendation-title--pending',
    ESCALATE: 'audit-layout__recommendation-title--escalate',
  };
  return classMap[recommendation] ?? 'text-foreground';
};

const getRecommendationBadgeClass = (recommendation: string) => {
  const classMap: Record<string, string> = {
    PASS: 'audit-layout__recommendation-badge--pass',
    REJECT: 'audit-layout__recommendation-badge--reject',
    PENDING: 'audit-layout__recommendation-badge--pending',
    ESCALATE: 'audit-layout__recommendation-badge--escalate',
  };
  return classMap[recommendation] ?? 'audit-layout__recommendation-badge';
};

const getRecommendationPanelClass = (recommendation: string) => {
  const classMap: Record<string, string> = {
    PASS: 'audit-layout__recommendation-panel--pass',
    REJECT: 'audit-layout__recommendation-panel--reject',
    PENDING: 'audit-layout__recommendation-panel--pending',
    ESCALATE: 'audit-layout__recommendation-panel--escalate',
  };
  return classMap[recommendation] ?? 'audit-layout__recommendation-panel';
};

/** 获取检查状态图标 */
const getCheckStatusIcon = (status: string): { color: string; icon: any } => {
  const iconMap: Record<string, { color: string; icon: any }> = {
    pass: {
      icon: LetsIconsCheckFill,
      color: 'audit-layout__status-icon--pass',
    },
    fail: {
      icon: LetsIconsCloseRoundFill,
      color: 'audit-layout__status-icon--fail',
    },
    warning: {
      icon: MdiAlertCircleOutline,
      color: 'audit-layout__status-icon--warning',
    },
    unknown: {
      icon: MdiHelpCircleOutline,
      color: 'audit-layout__status-icon--unknown',
    },
  };
  return iconMap[status] ?? iconMap.unknown!;
};

/** 获取弹窗标题 */
const getModalTitle = (type: RejectActionType): string => {
  const titleMap: Record<RejectActionType, string> = {
    reject: '驳回修改',
    pending: '加入待定名单',
    escalate: '转交老师处理',
  };
  return titleMap[type];
};

/** 获取原因标签 */
const getReasonLabel = (type: RejectActionType): string => {
  const labelMap: Record<RejectActionType, string> = {
    reject: '驳回原因',
    pending: '待定原因',
    escalate: '转交原因',
  };
  return labelMap[type];
};

// ==================== 暴露方法 ====================

defineExpose({
  /** 关闭驳回弹窗 */
  closeRejectModal: () => {
    rejectModalState.visible = false;
    rejectReasonError.value = '';
  },
});
</script>

<template>
  <div class="audit-layout flex h-full flex-col">
    <div v-if="showPageHeader" class="audit-layout__page-header">
      <Button
        v-if="showBackButton"
        type="text"
        class="audit-layout__page-back !px-2"
        :title="backButtonTitle"
        @click="handleBack"
      >
        <MdiArrowLeft class="h-5 w-5" />
      </Button>
      <div class="audit-layout__page-header-content">
        <h1 v-if="pageTitle" class="audit-layout__page-title">
          {{ pageTitle }}
        </h1>
      </div>
    </div>
    <slot name="page-header-extra"></slot>
    <div class="audit-layout__main">
      <div
        ref="leftPaneRef"
        class="audit-layout__left flex flex-col gap-2 overflow-y-auto transition-all duration-300"
        :class="{ 'audit-layout__left--collapsed': isCollapsed }"
      >
        <slot v-if="contentLoading" name="content-loading">
          <div class="audit-layout__content-loading">
            <div class="audit-layout__content-skeleton-card">
              <span class="audit-layout__content-skeleton-title"></span>
              <div class="audit-layout__content-skeleton-grid">
                <span class="audit-layout__content-skeleton-line"></span>
                <span class="audit-layout__content-skeleton-line"></span>
                <span
                  class="audit-layout__content-skeleton-line audit-layout__content-skeleton-line--wide"
                ></span>
                <span class="audit-layout__content-skeleton-line"></span>
              </div>
            </div>
            <div class="audit-layout__content-skeleton-card">
              <span class="audit-layout__content-skeleton-title"></span>
              <div class="space-y-3">
                <span
                  class="audit-layout__content-skeleton-line audit-layout__content-skeleton-line--wide"
                ></span>
                <span
                  class="audit-layout__content-skeleton-line audit-layout__content-skeleton-line--wide"
                ></span>
                <span class="audit-layout__content-skeleton-line"></span>
              </div>
            </div>
          </div>
        </slot>
        <slot v-else></slot>
      </div>
      <div
        ref="assistantRef"
        class="audit-layout__assistant"
        :class="{ 'audit-layout__assistant--collapsed': isCollapsed }"
        :style="assistantShellStyle"
      >
        <div
          class="audit-layout__assistant-panel"
          :class="{ 'audit-layout__assistant-panel--collapsed': isCollapsed }"
          :style="assistantPanelStyle"
        >
          <div v-if="isCollapsed" class="audit-layout__assistant-collapsed">
            <Transition name="audit-layout-assistant-tip">
              <template v-if="assistantHintCard">
                <slot
                  v-if="assistantHintCard.tone === 'loading'"
                  name="assistant-loading-hint"
                  :message="assistantHintCard.text"
                  :title="assistantHintCard.title"
                >
                  <div
                    class="audit-layout__assistant-tip"
                    :class="`audit-layout__assistant-tip--${assistantHintCard.tone}`"
                    role="status"
                    aria-live="polite"
                  >
                    <div class="audit-layout__assistant-tip-header">
                      <span class="audit-layout__assistant-tip-title">
                        {{ assistantHintCard.title }}
                      </span>
                      <button
                        class="audit-layout__assistant-tip-close"
                        title="关闭提示"
                        @click.stop="dismissAssistantHint"
                      >
                        <MdiClose class="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <span class="audit-layout__assistant-tip-text">
                      {{ assistantHintCard.text }}
                    </span>
                  </div>
                </slot>
                <div
                  v-else
                  class="audit-layout__assistant-tip"
                  :class="`audit-layout__assistant-tip--${assistantHintCard.tone}`"
                  role="status"
                  aria-live="polite"
                >
                  <div class="audit-layout__assistant-tip-header">
                    <span class="audit-layout__assistant-tip-title">
                      {{ assistantHintCard.title }}
                    </span>
                    <button
                      class="audit-layout__assistant-tip-close"
                      title="关闭提示"
                      @click.stop="dismissAssistantHint"
                    >
                      <MdiClose class="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <span class="audit-layout__assistant-tip-text">
                    {{ assistantHintCard.text }}
                  </span>
                </div>
              </template>
            </Transition>
            <button
              class="audit-layout__assistant-trigger bg-muted/70 text-muted-foreground hover:bg-muted rounded-full p-2 transition-colors"
              :class="{
                'audit-layout__assistant-trigger--busy': loading,
                'audit-layout__assistant-trigger--ready':
                  !loading && !!auditResult,
              }"
              title="展开审核助手"
              @click="toggleCollapse"
            >
              <MingcuteBulb2AiLine
                class="h-5 w-5"
                :class="loading ? 'audit-layout__assistant-icon--loading' : ''"
              />
            </button>

            <Popover
              v-if="auditResult"
              placement="left"
              trigger="hover"
              :overlay-style="{ maxWidth: '320px' }"
            >
              <template #content>
                <div class="relative">
                  <div class="mb-2 flex items-center gap-2">
                    <span
                      :class="
                        getRecommendationTitleClass(auditResult.recommendation)
                      "
                      class="text-base font-bold"
                    >
                      {{ getRecommendationText(auditResult.recommendation) }}
                    </span>
                    <span class="text-muted-foreground text-xs">
                      {{ auditResult.confidence }}%
                    </span>
                  </div>
                  <p class="text-foreground/80 pr-6 text-sm leading-relaxed">
                    {{ auditResult.summary }}
                  </p>
                  <button
                    class="absolute right-0 top-0 rounded-full p-1 transition-all duration-200"
                    :class="
                      copySuccess
                        ? 'audit-layout__copy-button--success'
                        : 'text-muted-foreground hover:text-foreground'
                    "
                    title="复制摘要"
                    @click.stop="handleCopySummary"
                  >
                    <MdiCheck v-if="copySuccess" class="h-4 w-4" />
                    <MdiCopy v-else class="h-4 w-4" />
                  </button>
                </div>
              </template>
              <div
                class="hover:bg-muted cursor-pointer rounded-full p-2 transition-colors"
              >
                <LetsIconsCheckFill
                  v-if="auditResult.recommendation === 'PASS'"
                  class="audit-layout__recommendation-icon--pass h-5 w-5"
                />
                <LetsIconsCloseRoundFill
                  v-else-if="auditResult.recommendation === 'REJECT'"
                  class="audit-layout__recommendation-icon--reject h-5 w-5"
                />
                <MdiClockOutline
                  v-else-if="auditResult.recommendation === 'PENDING'"
                  class="audit-layout__recommendation-icon--pending h-5 w-5"
                />
                <MingcuteTransfer3Fill
                  v-else-if="auditResult.recommendation === 'ESCALATE'"
                  class="audit-layout__recommendation-icon--escalate h-5 w-5"
                />
              </div>
            </Popover>

            <button
              class="audit-layout__assistant-trigger bg-muted/70 text-muted-foreground hover:bg-muted mt-auto rounded-full p-2 transition-colors"
              :class="{ 'pointer-events-none opacity-50': analyzeDisabled }"
              title="重新分析"
              :disabled="analyzeDisabled"
              @click="handleAnalyze"
            >
              <MdiRefresh
                class="h-4 w-4"
                :class="{ 'audit-layout__refresh-icon--loading': loading }"
              />
            </button>
          </div>

          <Card v-else :bordered="false" class="audit-layout__card shadow-sm">
            <div class="audit-layout__content">
              <div class="audit-layout__header">
                <div class="mb-4 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <div class="bg-muted rounded-full p-1.5">
                      <MingcuteBulb2AiLine
                        class="text-muted-foreground h-4 w-4"
                      />
                    </div>
                    <span class="text-foreground font-medium">{{ title }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <Button
                      type="link"
                      size="small"
                      :disabled="analyzeDisabled"
                      class="!flex items-center gap-1 !px-0"
                      @click="handleAnalyze"
                    >
                      <MdiRefresh
                        class="h-4 w-4"
                        :class="{
                          'audit-layout__refresh-icon--loading': loading,
                        }"
                      />
                      <span>{{ analyzeActionText }}</span>
                    </Button>
                    <button
                      class="bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground ml-2 rounded-full p-1 transition-colors"
                      title="收起"
                      @click="toggleCollapse"
                    >
                      <MdiChevronRight class="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <template v-if="auditResult && !loading">
                  <div class="mb-4 flex items-center gap-3 px-1">
                    <span
                      :class="
                        getRecommendationTitleClass(auditResult.recommendation)
                      "
                      class="text-2xl font-bold"
                    >
                      {{ getRecommendationText(auditResult.recommendation) }}
                    </span>
                    <span
                      :class="
                        getRecommendationBadgeClass(auditResult.recommendation)
                      "
                      class="rounded-[calc(var(--radius)+4px)] px-3 py-0.5 text-sm font-bold"
                    >
                      {{ auditResult.confidence }}% 置信度
                    </span>
                  </div>

                  <div
                    :class="
                      getRecommendationPanelClass(auditResult.recommendation)
                    "
                    class="relative mb-4 rounded-[calc(var(--radius)+8px)] border p-4"
                  >
                    <p class="text-foreground/80 pr-6 text-sm leading-relaxed">
                      {{ auditResult.summary }}
                    </p>
                    <button
                      class="absolute bottom-3 right-3 rounded-full p-1 transition-all duration-200"
                      :class="
                        copySuccess
                          ? 'audit-layout__copy-button--success'
                          : 'text-muted-foreground hover:text-foreground'
                      "
                      title="复制摘要"
                      @click="handleCopySummary"
                    >
                      <MdiCheck v-if="copySuccess" class="h-4 w-4" />
                      <MdiCopy v-else class="h-4 w-4" />
                    </button>
                  </div>
                </template>
              </div>

              <div
                v-if="auditResult && !loading"
                class="audit-layout__checklist"
              >
                <h4
                  class="bg-card text-muted-foreground sticky top-0 z-10 mb-2 px-1 pb-2 text-xs font-bold uppercase tracking-widest"
                >
                  审核清单详情
                </h4>
                <div class="space-y-0">
                  <div
                    v-for="(item, index) in auditResult.checklist"
                    :key="index"
                    class="border-border/50 flex items-start gap-3 border-b py-4 last:border-b-0"
                  >
                    <div class="mt-0.5 flex-shrink-0">
                      <component
                        :is="getCheckStatusIcon(item.status).icon"
                        class="h-5 w-5"
                        :class="getCheckStatusIcon(item.status).color"
                      />
                    </div>
                    <div class="flex-1">
                      <h5 class="text-foreground mb-1 text-sm font-semibold">
                        {{ item.item }}
                      </h5>
                      <p
                        class="text-[13px] leading-normal"
                        :class="{
                          'audit-layout__check-description--fail':
                            item.status === 'fail',
                          'text-muted-foreground': item.status !== 'fail',
                        }"
                      >
                        {{ item.description }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <slot
                v-if="loading"
                name="assistant-loading"
                :message="loadingMessage"
              >
                <div
                  class="audit-layout__loading-state"
                  role="status"
                  aria-live="polite"
                >
                  <div class="audit-layout__loading-emblem" aria-hidden="true">
                    <span class="audit-layout__loading-halo"></span>
                    <span
                      class="audit-layout__loading-ring audit-layout__loading-ring--outer"
                    ></span>
                    <span
                      class="audit-layout__loading-ring audit-layout__loading-ring--inner"
                    ></span>
                    <MingcuteBulb2AiLine class="audit-layout__loading-icon" />
                  </div>
                  <div class="audit-layout__loading-copy">
                    <p class="audit-layout__loading-title">
                      {{ loadingMessage }}
                    </p>
                    <div class="audit-layout__loading-dots" aria-hidden="true">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </slot>

              <div
                v-else-if="error"
                class="rounded-[calc(var(--radius)+6px)] bg-[hsl(var(--destructive)/0.12)] p-4 text-center text-[hsl(var(--destructive))]"
              >
                {{ error }}
                <Button
                  type="link"
                  size="small"
                  :disabled="readonly"
                  @click="handleAnalyze"
                >
                  重试
                </Button>
              </div>

              <div
                v-else-if="!auditResult"
                class="text-muted-foreground flex-1 py-8 text-center"
              >
                <MingcuteBulb2AiLine
                  class="mx-auto mb-2 h-12 w-12 opacity-50"
                />
                <p>
                  {{
                    readonly
                      ? '当前记录为只读状态'
                      : '点击“重新分析”生成审核建议'
                  }}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>

    <!-- 固定底部操作条 -->
    <div
      class="border-border fixed bottom-0 left-0 right-0 z-50 border-t bg-[hsl(var(--card)/0.96)] px-8 py-4 shadow-[0_-8px_24px_hsl(var(--foreground)/0.08)] backdrop-blur"
      ref="footerBarRef"
    >
      <div
        class="mx-auto flex max-w-screen-xl items-center justify-center gap-4"
      >
        <Button
          type="primary"
          size="large"
          :class="approveButtonClass"
          :loading="actionLoading"
          :disabled="actionDisabled"
          @click="handleApprove"
        >
          <MdiCheck class="mr-1 h-4 w-4" />
          审核通过
        </Button>

        <Button
          type="primary"
          danger
          size="large"
          :class="rejectButtonClass"
          :loading="actionLoading"
          :disabled="actionDisabled"
          @click="openRejectModal('reject')"
        >
          <MdiClose class="mr-1 h-4 w-4" />
          驳回修改
        </Button>

        <Button
          size="large"
          :class="pendingButtonClass"
          :loading="actionLoading"
          :disabled="actionDisabled"
          @click="openRejectModal('pending')"
        >
          <MdiClockOutline class="mr-1 h-4 w-4" />
          加入待定
        </Button>

        <Button
          size="large"
          :class="escalateButtonClass"
          :loading="actionLoading"
          :disabled="actionDisabled"
          @click="openRejectModal('escalate')"
        >
          <MingcuteTransfer3Fill class="mr-1 h-4 w-4" />
          转交老师
        </Button>
      </div>
    </div>

    <!-- 驳回/待定/转交弹窗 -->
    <Modal
      v-model:open="rejectModalState.visible"
      :title="getModalTitle(rejectModalState.type)"
      :confirm-loading="actionLoading"
      @ok="handleConfirmReject"
    >
      <div class="space-y-4 py-4">
        <!-- 目标节点选择 -->
        <div v-if="rejectableTargets && rejectableTargets.length > 0">
          <label class="text-foreground/80 mb-2 block text-sm font-medium">
            流转到节点
          </label>
          <Select
            v-model:value="rejectModalState.targetNodeDefId"
            class="w-full"
            placeholder="选择目标节点"
          >
            <Select.Option
              v-for="target in rejectableTargets"
              :key="target.id"
              :value="target.id"
            >
              {{ target.name }}
              <span v-if="target.description" class="text-muted-foreground">
                - {{ target.description }}
              </span>
            </Select.Option>
          </Select>
        </div>

        <!-- 原因输入 -->
        <div>
          <label class="text-foreground/80 mb-2 block text-sm font-medium">
            {{ getReasonLabel(rejectModalState.type) }}
          </label>
          <Input.TextArea
            v-model:value="rejectModalState.reason"
            :rows="4"
            :status="rejectReasonError ? 'error' : undefined"
            placeholder="请输入原因..."
            @input="handleRejectReasonInput"
          />
          <div
            v-if="rejectReasonError"
            class="mt-1 text-sm text-[hsl(var(--destructive))]"
          >
            {{ rejectReasonError }}
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.audit-layout {
  --audit-layout-success-border: hsl(var(--success) / 0.2);
  --audit-layout-success-surface: hsl(var(--success) / 0.12);
  --audit-layout-success-surface-weak: hsl(var(--success) / 0.08);
  --audit-layout-success-shadow:
    0 18px 32px hsl(var(--success) / 0.08),
    0 4px 12px hsl(var(--success) / 0.12);
  --audit-layout-warning-border: hsl(var(--warning) / 0.2);
  --audit-layout-warning-surface: hsl(var(--warning) / 0.12);
  --audit-layout-warning-surface-weak: hsl(var(--warning) / 0.08);
  --audit-layout-warning-text: hsl(var(--warning));
  --audit-layout-primary-border: hsl(var(--primary) / 0.2);
  --audit-layout-primary-surface: hsl(var(--primary) / 0.12);
  --audit-layout-primary-surface-weak: hsl(var(--primary) / 0.08);
  --audit-layout-primary-shadow:
    0 18px 32px hsl(var(--primary) / 0.08),
    0 4px 12px hsl(var(--primary) / 0.12);
  --audit-layout-destructive-border: hsl(var(--destructive) / 0.2);
  --audit-layout-destructive-surface: hsl(var(--destructive) / 0.12);
  --audit-layout-destructive-surface-weak: hsl(var(--destructive) / 0.08);
  --audit-layout-destructive-shadow:
    0 18px 32px hsl(var(--destructive) / 0.08),
    0 4px 12px hsl(var(--destructive) / 0.12);
  min-height: 0;
  padding-bottom: 80px;
}

.audit-layout__page-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 10px 16px;
  border: 1px solid hsl(var(--primary) / 0.08);
  border-radius: calc(var(--radius) + 2px);
  background: linear-gradient(
    90deg,
    hsl(var(--primary) / 0.09) 0%,
    hsl(var(--primary) / 0.06) 28%,
    hsl(var(--primary) / 0.03) 56%,
    hsl(var(--card) / 0.98) 100%
  );
  box-shadow: 0 8px 18px hsl(var(--primary) / 0.03);
}

.audit-layout__page-back {
  flex: none;
  min-width: 32px;
  height: 32px;
  border-radius: calc(var(--radius) + 4px);
  color: hsl(var(--foreground) / 0.72);
}

.audit-layout__page-back:hover,
.audit-layout__page-back:focus-visible {
  color: hsl(var(--primary));
  background: hsl(var(--primary) / 0.08) !important;
}

.audit-layout__page-header-content {
  min-width: 0;
  flex: 1;
}

.audit-layout__page-title {
  margin: 0;
  font-size: clamp(16px, 1.2vw, 18px);
  font-weight: 600;
  line-height: 1.25;
  color: hsl(var(--foreground));
  word-break: break-word;
}

.audit-layout__action-button--disabled {
  border-color: hsl(var(--border)) !important;
  background: hsl(var(--muted) / 0.8) !important;
  color: hsl(var(--muted-foreground)) !important;
  box-shadow: none !important;
  cursor: not-allowed;
}

.audit-layout__action-button--approve {
  border-color: hsl(var(--success)) !important;
  background: hsl(var(--success)) !important;
  color: hsl(var(--success-foreground)) !important;
}

.audit-layout__action-button--approve:hover {
  border-color: hsl(var(--success) / 0.92) !important;
  background: hsl(var(--success) / 0.92) !important;
}

.audit-layout__action-button--pending {
  border-color: hsl(var(--warning)) !important;
  background: hsl(var(--warning)) !important;
  color: hsl(var(--warning-foreground)) !important;
}

.audit-layout__action-button--pending:hover {
  border-color: hsl(var(--warning) / 0.92) !important;
  background: hsl(var(--warning) / 0.92) !important;
}

.audit-layout__action-button--escalate {
  border-color: hsl(var(--primary)) !important;
  background: hsl(var(--primary)) !important;
  color: hsl(var(--primary-foreground)) !important;
}

.audit-layout__action-button--escalate:hover {
  border-color: hsl(var(--primary) / 0.92) !important;
  background: hsl(var(--primary) / 0.92) !important;
}

.audit-layout__assistant-trigger:hover:not(:disabled) {
  color: hsl(var(--primary));
}

.audit-layout__main {
  display: flex;
  flex: 1;
  min-height: 0;
  align-items: flex-start;
}

.audit-layout__left {
  flex: 1;
  min-width: 0;
  align-self: stretch;
}

.audit-layout__content-loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.audit-layout__content-skeleton-card {
  border: 1px solid hsl(var(--border) / 0.5);
  border-radius: calc(var(--radius) + 4px);
  background: linear-gradient(
    180deg,
    hsl(var(--card) / 0.98),
    hsl(var(--background) / 0.96)
  );
  padding: 24px;
  box-shadow: 0 1px 2px hsl(var(--foreground) / 0.04);
}

.audit-layout__content-skeleton-title,
.audit-layout__content-skeleton-line {
  display: block;
  border-radius: 9999px;
  background: linear-gradient(
    90deg,
    hsl(var(--muted) / 0.72) 25%,
    hsl(var(--accent) / 0.96) 37%,
    hsl(var(--muted) / 0.72) 63%
  );
  background-size: 400% 100%;
  animation: audit-layout-content-skeleton 1.6s ease-in-out infinite;
}

.audit-layout__content-skeleton-title {
  width: 140px;
  height: 18px;
  margin-bottom: 24px;
}

.audit-layout__content-skeleton-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px 24px;
}

.audit-layout__content-skeleton-line {
  width: 100%;
  height: 14px;
}

.audit-layout__content-skeleton-line--wide {
  width: 72%;
}

.audit-layout__left--collapsed {
  padding-right: 0;
}

.audit-layout__assistant {
  width: 400px;
  max-width: 100%;
  flex-shrink: 0;
  position: relative;
}

.audit-layout__assistant--collapsed {
  width: 72px;
}

.audit-layout__assistant-panel {
  height: var(--audit-layout-assistant-max-height, calc(100dvh - 216px));
  max-height: var(--audit-layout-assistant-max-height, calc(100dvh - 216px));
  overflow: hidden;
  border: 1px solid hsl(var(--border) / 0.65);
  border-radius: calc(var(--radius) + 2px);
  background: linear-gradient(
    180deg,
    hsl(var(--card) / 0.98),
    hsl(var(--background) / 0.96)
  );
  box-shadow:
    0 22px 54px hsl(var(--foreground) / 0.08),
    0 8px 24px hsl(var(--foreground) / 0.05);
}

.audit-layout__assistant-panel--collapsed {
  overflow: visible;
}

.audit-layout__assistant-collapsed {
  position: relative;
  display: flex;
  height: 100%;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  border-radius: inherit;
  background: hsl(var(--card) / 0.94);
  padding: 12px 0;
}

.audit-layout__assistant-tip {
  --audit-layout-assistant-tip-border-color: hsl(var(--primary) / 0.16);
  --audit-layout-assistant-tip-shadow:
    0 18px 32px hsl(var(--primary) / 0.08),
    0 4px 12px hsl(var(--primary) / 0.12);
  --audit-layout-assistant-tip-title-color: hsl(var(--primary));
  --audit-layout-assistant-tip-arrow-offset: 32px;
  position: absolute;
  top: 6px;
  right: calc(100% + 12px);
  display: flex;
  width: 248px;
  flex-direction: column;
  gap: 8px;
  padding: 13px 14px;
  border: 1px solid var(--audit-layout-assistant-tip-border-color);
  border-radius: calc(var(--radius) + 10px);
  background: hsl(var(--popover) / 0.98);
  box-shadow:
    0 18px 32px hsl(var(--foreground) / 0.08),
    var(--audit-layout-assistant-tip-shadow);
  pointer-events: auto;
  z-index: 1;
}

.audit-layout__assistant-tip::before,
.audit-layout__assistant-tip::after {
  content: '';
  position: absolute;
  top: var(--audit-layout-assistant-tip-arrow-offset);
  transform: translateY(-50%) rotate(45deg);
}

.audit-layout__assistant-tip::before {
  right: -9px;
  width: 18px;
  height: 18px;
  border-top: 1px solid var(--audit-layout-assistant-tip-border-color);
  border-right: 1px solid var(--audit-layout-assistant-tip-border-color);
  background: hsl(var(--popover) / 0.98);
}

.audit-layout__assistant-tip::after {
  right: -6px;
  width: 12px;
  height: 12px;
  background: hsl(var(--popover) / 0.98);
}

.audit-layout__assistant-tip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.audit-layout__assistant-tip-title {
  color: var(--audit-layout-assistant-tip-title-color);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
  line-height: 1.2;
}

.audit-layout__assistant-tip-text {
  color: hsl(var(--foreground) / 0.82);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.4;
  padding-right: 4px;
}

.audit-layout__assistant-tip-close {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 9999px;
  background: transparent;
  color: hsl(var(--muted-foreground));
  transition:
    background-color 160ms ease-out,
    color 160ms ease-out;
}

.audit-layout__assistant-tip-close:hover {
  background: hsl(var(--muted) / 0.75);
  color: hsl(var(--foreground));
}

.audit-layout__assistant-tip--loading {
  --audit-layout-assistant-tip-border-color: hsl(var(--primary) / 18%);
  --audit-layout-assistant-tip-shadow:
    0 18px 32px hsl(var(--primary) / 10%), 0 4px 12px hsl(var(--primary) / 12%);
  --audit-layout-assistant-tip-title-color: hsl(var(--primary));
}

.audit-layout__assistant-tip--complete {
  --audit-layout-assistant-tip-border-color: var(--audit-layout-success-border);
  --audit-layout-assistant-tip-shadow: var(--audit-layout-success-shadow);
  --audit-layout-assistant-tip-title-color: hsl(var(--success));
}

.audit-layout__assistant-tip--error {
  --audit-layout-assistant-tip-border-color: var(
    --audit-layout-destructive-border
  );
  --audit-layout-assistant-tip-shadow: var(--audit-layout-destructive-shadow);
  --audit-layout-assistant-tip-title-color: hsl(var(--destructive));
}

.audit-layout-assistant-tip-enter-active,
.audit-layout-assistant-tip-leave-active {
  transition:
    opacity 180ms ease-out,
    transform 180ms ease-out;
}

.audit-layout-assistant-tip-enter-from,
.audit-layout-assistant-tip-leave-to {
  opacity: 0;
  transform: translate3d(6px, 0, 0) scale(0.96);
}

.audit-layout__assistant-trigger--busy {
  background: hsl(var(--primary) / 10%) !important;
  color: hsl(var(--primary)) !important;
  box-shadow: 0 0 0 1px hsl(var(--primary) / 12%);
}

.audit-layout__assistant-trigger--ready {
  background: var(--audit-layout-success-surface) !important;
  color: hsl(var(--success)) !important;
  box-shadow: 0 0 0 1px var(--audit-layout-success-border);
}

.audit-layout__copy-button--success,
.audit-layout__recommendation-title--pass,
.audit-layout__recommendation-icon--pass,
.audit-layout__status-icon--pass {
  color: hsl(var(--success));
}

.audit-layout__recommendation-title--reject,
.audit-layout__recommendation-icon--reject,
.audit-layout__status-icon--fail,
.audit-layout__check-description--fail {
  color: hsl(var(--destructive));
}

.audit-layout__recommendation-title--pending,
.audit-layout__recommendation-icon--pending,
.audit-layout__status-icon--warning {
  color: var(--audit-layout-warning-text);
}

.audit-layout__status-icon--unknown {
  color: hsl(var(--primary) / 0.82);
}

.audit-layout__recommendation-title--escalate,
.audit-layout__recommendation-icon--escalate {
  color: hsl(var(--primary));
}

.audit-layout__recommendation-badge {
  border: 1px solid hsl(var(--border));
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
}

.audit-layout__recommendation-badge--pass {
  border: 1px solid var(--audit-layout-success-border);
  background: var(--audit-layout-success-surface);
  color: hsl(var(--success));
}

.audit-layout__recommendation-badge--reject {
  border: 1px solid var(--audit-layout-destructive-border);
  background: var(--audit-layout-destructive-surface);
  color: hsl(var(--destructive));
}

.audit-layout__recommendation-badge--pending {
  border: 1px solid var(--audit-layout-warning-border);
  background: var(--audit-layout-warning-surface);
  color: var(--audit-layout-warning-text);
}

.audit-layout__recommendation-badge--escalate {
  border: 1px solid var(--audit-layout-primary-border);
  background: var(--audit-layout-primary-surface);
  color: hsl(var(--primary));
}

.audit-layout__recommendation-panel {
  border-color: hsl(var(--border) / 0.6);
  background: hsl(var(--muted) / 0.4);
}

.audit-layout__recommendation-panel--pass {
  border-color: var(--audit-layout-success-border);
  background: var(--audit-layout-success-surface-weak);
}

.audit-layout__recommendation-panel--reject {
  border-color: var(--audit-layout-destructive-border);
  background: var(--audit-layout-destructive-surface-weak);
}

.audit-layout__recommendation-panel--pending {
  border-color: var(--audit-layout-warning-border);
  background: var(--audit-layout-warning-surface-weak);
}

.audit-layout__recommendation-panel--escalate {
  border-color: var(--audit-layout-primary-border);
  background: var(--audit-layout-primary-surface-weak);
}

.audit-layout__card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  max-height: 100%;
}

.audit-layout__card :deep(.ant-card-body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 14px;
}

.audit-layout__card :deep(.ant-card) {
  height: 100%;
  border-radius: calc(var(--radius) + 12px);
  background: transparent;
  box-shadow: none !important;
}

.audit-layout__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.audit-layout__header {
  flex-shrink: 0;
}

.audit-layout__checklist {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.audit-layout__checklist::-webkit-scrollbar {
  width: 3px;
}

.audit-layout__checklist::-webkit-scrollbar-track {
  background: transparent;
}

.audit-layout__checklist::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 20%);
  border-radius: 999px;
}

.audit-layout__checklist::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 40%);
}

.audit-layout__loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 32px 16px;
  text-align: center;
}

.audit-layout__loading-emblem {
  position: relative;
  display: grid;
  width: 96px;
  height: 96px;
  place-items: center;
  overflow: hidden;
  border-radius: 9999px;
  background: radial-gradient(
    circle at 35% 30%,
    hsl(var(--card) / 0.98) 0%,
    hsl(var(--primary) / 6%) 34%,
    hsl(var(--primary) / 10%) 68%,
    hsl(var(--primary) / 14%) 100%
  );
  box-shadow:
    0 16px 32px hsl(var(--primary) / 12%),
    inset 0 1px 0 hsl(var(--background) / 0.72);
}

.audit-layout__loading-halo {
  position: absolute;
  inset: 18px;
  border-radius: inherit;
  background: radial-gradient(
    circle,
    hsl(var(--primary) / 28%) 0%,
    hsl(var(--primary) / 10%) 56%,
    transparent 74%
  );
  filter: blur(6px);
  animation: audit-layout-loading-halo 2.8s cubic-bezier(0.22, 1, 0.36, 1)
    infinite;
}

.audit-layout__loading-ring {
  position: absolute;
  border-radius: 9999px;
  border: 1px solid hsl(var(--primary) / 20%);
}

.audit-layout__loading-ring--outer {
  inset: 8px;
  animation: audit-layout-loading-ring 2.6s cubic-bezier(0.25, 1, 0.5, 1)
    infinite;
}

.audit-layout__loading-ring--inner {
  inset: 20px;
  border-color: hsl(var(--primary) / 30%);
  animation: audit-layout-loading-ring 2.6s cubic-bezier(0.25, 1, 0.5, 1)
    infinite 0.45s;
}

.audit-layout__loading-icon {
  position: relative;
  z-index: 1;
  width: 42px;
  height: 42px;
  color: hsl(var(--primary));
  filter: drop-shadow(0 8px 18px hsl(var(--primary) / 22%));
  animation: audit-layout-loading-icon 2.6s cubic-bezier(0.22, 1, 0.36, 1)
    infinite;
}

.audit-layout__loading-copy {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 26px;
  gap: 8px;
}

.audit-layout__loading-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: hsl(var(--primary) / 45%);
  animation: audit-layout-loading-text 2.6s cubic-bezier(0.22, 1, 0.36, 1)
    infinite;
}

.audit-layout__loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transform: translateY(2px);
}

.audit-layout__loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: hsl(var(--primary));
  opacity: 0.24;
  transform: scale(0.84);
  animation: audit-layout-loading-dot 1.2s ease-in-out infinite;
}

.audit-layout__loading-dots span:nth-child(2) {
  animation-delay: 0.18s;
}

.audit-layout__loading-dots span:nth-child(3) {
  animation-delay: 0.36s;
}

.audit-layout__assistant-icon--loading,
.audit-layout__refresh-icon--loading {
  color: hsl(var(--primary));
  animation: audit-layout-action-icon 1.8s cubic-bezier(0.22, 1, 0.36, 1)
    infinite;
}

@keyframes audit-layout-loading-halo {
  0%,
  100% {
    opacity: 0.42;
    transform: scale(0.9);
  }

  50% {
    opacity: 0.9;
    transform: scale(1.06);
  }
}

@keyframes audit-layout-content-skeleton {
  0% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0 50%;
  }
}

@keyframes audit-layout-loading-ring {
  0%,
  100% {
    opacity: 0.38;
    transform: scale(0.94);
  }

  50% {
    opacity: 0.82;
    transform: scale(1);
  }
}

@keyframes audit-layout-loading-icon {
  0%,
  100% {
    opacity: 0.78;
    color: hsl(var(--primary) / 68%);
    transform: translateY(0) scale(0.94);
  }

  50% {
    opacity: 1;
    color: hsl(var(--primary));
    transform: translateY(-1px) scale(1.04);
  }
}

@keyframes audit-layout-loading-text {
  0%,
  100% {
    opacity: 0.72;
    color: hsl(var(--primary) / 42%);
  }

  50% {
    opacity: 1;
    color: hsl(var(--primary) / 90%);
  }
}

@keyframes audit-layout-loading-dot {
  0%,
  100% {
    opacity: 0.24;
    transform: translateY(0) scale(0.84);
  }

  45% {
    opacity: 1;
    transform: translateY(-4px) scale(1);
  }
}

@keyframes audit-layout-action-icon {
  0%,
  100% {
    opacity: 0.64;
    color: hsl(var(--primary) / 52%);
    transform: scale(0.92);
  }

  50% {
    opacity: 1;
    color: hsl(var(--primary));
    transform: scale(1);
  }
}

@keyframes audit-layout-status-dot {
  0%,
  100% {
    box-shadow: 0 0 0 0 hsl(var(--primary) / 0.14);
    transform: scale(0.94);
  }

  50% {
    box-shadow: 0 0 0 6px hsl(var(--primary) / 0);
    transform: scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .audit-layout__content-skeleton-title,
  .audit-layout__content-skeleton-line,
  .audit-layout__loading-halo,
  .audit-layout__loading-ring,
  .audit-layout__loading-icon,
  .audit-layout__loading-title,
  .audit-layout__loading-dots span,
  .audit-layout__assistant-icon--loading,
  .audit-layout__refresh-icon--loading {
    animation: none !important;
  }
}

@media (max-width: 1280px) {
  .audit-layout__page-header {
    gap: 6px;
    padding: 9px 12px;
  }

  .audit-layout__page-title {
    font-size: 16px;
  }

  .audit-layout__main {
    flex-direction: column;
  }

  .audit-layout__left {
    padding-right: 0;
  }

  .audit-layout__assistant,
  .audit-layout__assistant--collapsed {
    width: 100%;
    height: auto;
    max-height: none;
  }

  .audit-layout__assistant-panel {
    position: static !important;
    top: auto !important;
    left: auto !important;
    width: auto !important;
    height: auto !important;
    max-height: none !important;
    overflow: visible;
  }

  .audit-layout__card {
    min-height: 420px;
    max-height: 60vh;
  }

  .audit-layout__assistant-tip {
    width: min(272px, calc(100vw - 120px));
  }
}
</style>
