<script lang="ts" setup>
import type { FlowApi } from '#/api/core/flow';

import { computed } from 'vue';

import { Popover, Tag, Timeline } from 'ant-design-vue';

interface FlowStatusTagProps {
  /** 流程实例数据 */
  flowInstance?: FlowApi.FlowInstanceResponse | null;
  /** 列表页轻量流程摘要 */
  flowSummary?: FlowApi.FlowSummaryResponse | null;
  /** 加载中状态 */
  loading?: boolean;
  /** 错误信息 */
  error?: null | string;
  /** 无流程数据时的兜底文案（用于统一列表状态展示，避免再退回普通 Tag） */
  fallbackText?: null | string;
  /** 无流程数据时的提示内容 */
  fallbackDetail?: null | string;
  /**
   * 兜底状态的色调（不影响有 flowInstance 时的展示）
   * - default: 灰
   * - processing: 主色
   * - success: 绿
   * - warning: 橙
   * - error: 红
   */
  fallbackTone?: 'default' | 'error' | 'processing' | 'success' | 'warning';
}

const props = withDefaults(defineProps<FlowStatusTagProps>(), {
  flowInstance: null,
  flowSummary: null,
  loading: false,
  error: null,
  fallbackText: null,
  fallbackDetail: null,
  fallbackTone: 'default',
});

interface FlowTimelineNodeViewModel {
  id: string;
  nodeName: string;
  opinion?: string;
  startAt?: string;
  endAt?: string;
  status: FlowApi.NodeStatus;
}

/** 流程状态映射 */
const getFlowStatusText = (status?: FlowApi.FlowStatus | null) => {
  if (!status) return '';
  const statusMap = {
    INITIALIZED: '待审核',
    RUNNING: '审核中',
    COMPLETED: '审核通过',
    FAILED: '审核不通过',
  };
  return statusMap[status] || status;
};

/** 获取主 Tag 的样式类（更大、更亮） */
const getTagClass = (status?: FlowApi.FlowStatus | null) => {
  if (!status) return 'flow-status-tag flow-status-error';

  const classMap = {
    INITIALIZED: 'flow-status-default',
    RUNNING: 'flow-status-processing',
    COMPLETED: 'flow-status-success',
    FAILED: 'flow-status-error',
  };
  return `flow-status-tag ${classMap[status] || 'flow-status-default'}`;
};

/** 兜底状态样式（用于非流程状态或流程数据缺失时的统一展示） */
const getFallbackClass = (
  tone: FlowStatusTagProps['fallbackTone'] = 'default',
) => {
  const classMap = {
    default: 'flow-status-default',
    processing: 'flow-status-processing',
    success: 'flow-status-success',
    warning: 'flow-status-warning',
    error: 'flow-status-error',
  } as const;
  return `flow-status-tag ${classMap[tone] || 'flow-status-default'}`;
};

/** 节点状态颜色映射（用于 Timeline） */
const getNodeStatusColor = (status?: FlowApi.NodeStatus | null) => {
  if (!status) return 'gray';
  const colorMap = {
    COMPLETED: 'green',
    RUNNING: 'blue',
    WAITING: 'gray',
    FAILED: 'red',
    REJECTED: 'orange',
  };
  return colorMap[status] || 'gray';
};

/** 节点状态文案 */
const getNodeStatusText = (status?: FlowApi.NodeStatus | null) => {
  if (!status) return '';
  const statusMap = {
    COMPLETED: '已完成',
    RUNNING: '进行中',
    WAITING: '待处理',
    FAILED: '失败',
    REJECTED: '已驳回',
  };
  return statusMap[status] || status;
};

/** 格式化日期时间 */
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};

/** 组装流程节点信息（nodeInstance + nodeDef） */
const normalizedFlow = computed(() => {
  if (props.flowInstance) {
    const nodeInstances = props.flowInstance.nodeInstances || [];
    const nodeDefinitions =
      props.flowInstance.flowDefinition?.nodeDefinitions || [];
    const timeline: FlowTimelineNodeViewModel[] = nodeInstances.map(
      (nodeInstance) => {
        const nodeDef = nodeDefinitions.find(
          (definition) => definition.id === nodeInstance.nodeDefinitionId,
        );

        return {
          id: nodeInstance.id,
          nodeName: nodeDef?.name || '未知节点',
          opinion: nodeInstance.context?.opinion,
          startAt: nodeInstance.startAt,
          endAt: nodeInstance.endAt,
          status: nodeInstance.status,
        };
      },
    );
    const runningNode = timeline.find((node) => node.status === 'RUNNING');
    let currentNodeName = '';
    if (runningNode) {
      currentNodeName = runningNode.nodeName;
    } else if (props.flowInstance.status === 'COMPLETED') {
      currentNodeName = '已结束';
    } else if (props.flowInstance.status === 'FAILED') {
      currentNodeName = '已终止';
    }

    return {
      currentNodeName,
      displayText: getFlowStatusText(props.flowInstance.status),
      flowName:
        props.flowInstance.flowDefinition?.name || props.flowInstance.name,
      timeline,
      status: props.flowInstance.status,
    };
  }

  if (props.flowSummary) {
    return {
      currentNodeName: props.flowSummary.currentNodeName || '',
      displayText:
        props.flowSummary.displayText ||
        getFlowStatusText(props.flowSummary.status),
      flowName: props.flowSummary.flowName || '',
      timeline:
        props.flowSummary.timeline?.map((node) => ({
          id: node.id,
          nodeName: node.nodeName || '未知节点',
          opinion: node.opinion,
          startAt: node.startAt,
          endAt: node.endAt,
          status: node.status,
        })) || [],
      status: props.flowSummary.status,
    };
  }

  return null;
});

/** 是否显示 Tag */
const shouldShowTag = computed(() => {
  return (
    normalizedFlow.value || props.error || props.loading || !!props.fallbackText
  );
});

const resolvedFallbackDetail = computed(() => {
  if (props.fallbackDetail) return props.fallbackDetail;
  if (props.fallbackText === '待审核') return '暂无流程实例';
  return null;
});

const isStaticFallbackStatus = computed(() => {
  if (normalizedFlow.value || props.error) {
    return false;
  }

  return props.fallbackText === '草稿' || props.fallbackText === '已取消';
});

const hasPopoverContent = computed(() => {
  if (isStaticFallbackStatus.value) {
    return false;
  }

  return (
    !!normalizedFlow.value || !!props.error || !!resolvedFallbackDetail.value
  );
});

const statusBehaviorClass = computed(() =>
  hasPopoverContent.value
    ? 'flow-status-tag-interactive flow-status-tag-hoverable'
    : 'flow-status-tag-static',
);
</script>

<template>
  <Popover
    v-if="hasPopoverContent"
    placement="bottomLeft"
    trigger="hover"
    overlay-class-name="flow-status-popover"
  >
    <template #content>
      <div class="min-w-[280px] max-w-[360px]">
        <template v-if="normalizedFlow">
          <div class="flow-status-popover-content">
            <!-- 流程基本信息 -->
            <div class="mb-3 border-b pb-2">
              <div class="flex items-center justify-between">
                <div class="flow-status-title font-medium">
                  {{ normalizedFlow?.flowName || '-' }}
                </div>
              </div>
              <div
                v-if="normalizedFlow?.currentNodeName"
                class="flow-status-meta mt-1 text-xs"
              >
                当前节点：
                <span class="text-primary">{{
                  normalizedFlow?.currentNodeName
                }}</span>
              </div>
            </div>

            <!-- 流程节点时间线 -->
            <Timeline class="!mb-0 ml-1 mt-6">
              <Timeline.Item
                v-for="(node, index) in normalizedFlow?.timeline || []"
                :key="node.id"
                :color="getNodeStatusColor(node.status)"
                :class="{
                  'flow-node-current': node.status === 'RUNNING',
                  '!pb-6':
                    index !== (normalizedFlow?.timeline?.length || 0) - 1,
                  '!pb-0':
                    index === (normalizedFlow?.timeline?.length || 0) - 1,
                }"
              >
                <div class="flow-node-content -mt-1.5">
                  <!-- 节点标题与状态 -->
                  <div class="flex items-center justify-between">
                    <span
                      class="text-sm font-medium"
                      :class="{
                        'text-primary': node.status === 'RUNNING',
                        'flow-node-title': node.status !== 'RUNNING',
                      }"
                    >
                      {{ node.nodeName }}
                    </span>
                    <!-- 仅在非等待状态显示小 Tag -->
                    <Tag
                      v-if="node.status !== 'WAITING'"
                      :color="getNodeStatusColor(node.status)"
                      class="!mr-0 ml-2 scale-90"
                      size="small"
                    >
                      {{ getNodeStatusText(node.status) }}
                    </Tag>
                  </div>

                  <!-- 时间信息（紧凑展示） -->
                  <div
                    v-if="node.startAt || node.endAt"
                    class="flow-status-meta mt-1 text-xs"
                  >
                    <span v-if="node.endAt">
                      {{ formatDateTime(node.endAt) }} 完成
                    </span>
                    <span v-else-if="node.startAt">
                      {{ formatDateTime(node.startAt) }} 开始
                    </span>
                  </div>

                  <!-- 审核意见（紧凑展示） -->
                  <div
                    v-if="node.opinion"
                    class="flow-node-opinion mt-2 px-2 py-1.5 text-xs"
                  >
                    <div class="flex items-start gap-1.5">
                      <span class="flow-status-meta shrink-0">意见:</span>
                      <span class="flow-node-opinion-text">{{
                        node.opinion
                      }}</span>
                    </div>
                  </div>
                </div>
              </Timeline.Item>
            </Timeline>
          </div>
        </template>

        <!-- 错误状态 -->
        <template v-else-if="props.error">
          <div class="flow-status-error-message text-sm">
            {{ props.error }}
          </div>
        </template>

        <template v-else-if="resolvedFallbackDetail">
          <div class="flow-status-meta max-w-[320px] text-sm leading-6">
            {{ resolvedFallbackDetail }}
          </div>
        </template>
      </div>
    </template>

    <!-- 加载中状态 -->
    <span
      v-if="props.loading && !normalizedFlow"
      class="flow-status-tag flow-status-loading"
      :class="statusBehaviorClass"
    >
      加载中...
    </span>
    <!-- 主 Tag 触发器（大号、亮色） -->
    <span
      v-else-if="normalizedFlow"
      :class="[statusBehaviorClass, getTagClass(normalizedFlow.status)]"
    >
      {{ normalizedFlow.displayText }}
    </span>
    <span v-else-if="props.error" :class="[statusBehaviorClass, getTagClass()]">
      状态异常
    </span>
    <span
      v-else-if="props.fallbackText"
      :class="[statusBehaviorClass, getFallbackClass(props.fallbackTone)]"
    >
      {{ props.fallbackText }}
    </span>
  </Popover>

  <span
    v-else-if="shouldShowTag && props.loading"
    class="flow-status-tag flow-status-loading"
    :class="statusBehaviorClass"
  >
    加载中...
  </span>
  <span
    v-else-if="shouldShowTag && props.fallbackText"
    :class="[statusBehaviorClass, getFallbackClass(props.fallbackTone)]"
  >
    {{ props.fallbackText }}
  </span>
</template>

<style scoped>
.flow-status-tag {
  @apply inline-flex h-7 items-center justify-center px-3 text-sm font-medium transition-colors;
  border-radius: calc(var(--radius) + 2px);
}

.flow-status-tag-interactive {
  @apply cursor-pointer;
}

.flow-status-tag-static {
  @apply cursor-not-allowed;
}

/* 自定义 Tag 样式：更亮、更像按钮 */
.flow-status-default {
  background: hsl(var(--muted) / 0.72);
  color: hsl(var(--muted-foreground));
}

.flow-status-processing {
  background: hsl(var(--primary) / 0.12);
  color: hsl(var(--primary));
}

.flow-status-success {
  background: hsl(var(--success) / 0.14);
  color: hsl(var(--success));
}

.flow-status-warning {
  background: hsl(var(--warning) / 0.14);
  color: hsl(var(--warning));
}

.flow-status-error {
  background: hsl(var(--destructive) / 0.14);
  color: hsl(var(--destructive));
}

.flow-status-loading {
  background: hsl(var(--muted) / 0.72);
  color: hsl(var(--muted-foreground) / 0.92);
}

.flow-status-tag-hoverable.flow-status-default {
  background: hsl(var(--muted) / 0.72);
}

.flow-status-tag-hoverable.flow-status-default:hover {
  background: hsl(var(--muted) / 0.92);
}

.flow-status-tag-hoverable.flow-status-processing {
  background: hsl(var(--primary) / 0.12);
}

.flow-status-tag-hoverable.flow-status-processing:hover {
  background: hsl(var(--primary) / 0.2);
}

.flow-status-tag-hoverable.flow-status-success {
  background: hsl(var(--success) / 0.14);
}

.flow-status-tag-hoverable.flow-status-success:hover {
  background: hsl(var(--success) / 0.24);
}

.flow-status-tag-hoverable.flow-status-warning {
  background: hsl(var(--warning) / 0.14);
}

.flow-status-tag-hoverable.flow-status-warning:hover {
  background: hsl(var(--warning) / 0.24);
}

.flow-status-tag-hoverable.flow-status-error {
  background: hsl(var(--destructive) / 0.14);
}

.flow-status-tag-hoverable.flow-status-error:hover {
  background: hsl(var(--destructive) / 0.24);
}

.flow-status-popover-content {
  max-height: min(70vh, 720px);
  overflow-y: auto;
  padding-right: 4px;
  color: hsl(var(--foreground));
}

.flow-status-title {
  color: hsl(var(--foreground));
}

.flow-status-meta {
  color: hsl(var(--muted-foreground));
}

.flow-node-title {
  color: hsl(var(--foreground) / 0.9);
}

.flow-node-opinion {
  border: 1px solid hsl(var(--border) / 0.68);
  border-radius: calc(var(--radius) + 2px);
  background: hsl(var(--muted) / 0.5);
}

.flow-node-opinion-text {
  color: hsl(var(--foreground) / 0.92);
}

.flow-status-error-message {
  color: hsl(var(--destructive));
}

/* 时间线节点动画 */
.flow-node-current :deep(.ant-timeline-item-head) {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  @apply border-primary bg-primary text-primary;
}

@keyframes pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 hsl(var(--primary) / 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px hsl(var(--primary) / 0);
  }
}
</style>
