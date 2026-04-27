<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

import { MdiBrain, MdiChevronUp } from '#/icons';

interface Props {
  mode?: 'input' | 'textarea';
  thinkingSteps?: string[];
  isThinking?: boolean;
  currentThinkingText?: string;
  triggerElement?: HTMLElement | null;
  showButton?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'textarea',
  thinkingSteps: () => [],
  isThinking: false,
  currentThinkingText: '',
  triggerElement: null,
  showButton: true,
});

// State
const isExpanded = ref(false);
const bubbleContainer = ref<HTMLElement>();
const bubbleStyle = ref<Record<string, string>>({});
const scrollContainer = ref<HTMLElement>();
const thinkingButton = ref<HTMLElement>();

// Computed
const showViewButton = computed(() => {
  // 只有在需要显示按钮且有思考过程或正在思考时才显示按钮
  return (
    props.showButton &&
    (props.isThinking ||
      props.thinkingSteps.length > 0 ||
      (props.currentThinkingText &&
        props.currentThinkingText.trim().length > 0))
  );
});

const bubbleClass = computed(() => {
  return isExpanded.value ? 'thinking-bubble-show' : 'thinking-bubble-hide';
});

// Methods
const calculateBubblePosition = () => {
  if (!bubbleContainer.value) return;

  // 优先使用外部传入的触发元素，否则使用内部按钮
  const trigger = props.triggerElement || thinkingButton.value;

  // 计算弹窗宽度：响应式设计
  const isMobile = window.innerWidth <= 768;
  // 使用三元表达式简化if-else语句
  const bubbleWidth = isMobile
    ? Math.max(window.innerWidth * 0.85, 320) // 移动端：使用85%视口宽度，最小320px
    : Math.min(Math.max(window.innerWidth * 0.5, 480), 700); // 桌面端：使用50%屏幕宽度，最小480px，最大700px

  // 如果没有触发元素，使用默认位置（右下角）
  if (!trigger) {
    bubbleStyle.value = {
      right: '20px',
      bottom: '80px',
      width: `${bubbleWidth}px`,
      transformOrigin: 'bottom right',
    };
    return;
  }

  const bubble = bubbleContainer.value;
  const triggerRect = trigger.getBoundingClientRect();
  const bubbleRect = bubble.getBoundingClientRect();

  // 优先尝试让弹窗右边框与思考按钮右边框对齐
  let left = triggerRect.right - bubbleWidth; // 弹窗右边框对齐按钮右边框
  // 默认在上方显示（避免被 Modal 底部按钮遮挡）
  let top = triggerRect.top - bubbleRect.height - 8;
  let transformOrigin = 'bottom right';

  // 如果弹窗宽度超出左边界，向右调整
  if (left < 8) {
    left = 8;
    transformOrigin = 'bottom left';
  }

  // 如果弹窗宽度超出右边界，向左调整
  if (left + bubbleWidth > window.innerWidth - 8) {
    left = window.innerWidth - bubbleWidth - 8;
    transformOrigin = 'bottom right';
  }

  // 如果上方空间不够，改为下方
  if (top < 8) {
    top = triggerRect.bottom + 8;
    // 保持水平对齐不变，只改变垂直方向
    if (transformOrigin === 'bottom right') transformOrigin = 'top right';
    else if (transformOrigin === 'bottom left') transformOrigin = 'top left';
  }

  bubbleStyle.value = {
    left: `${left}px`,
    top: `${top}px`,
    width: `${bubbleWidth}px`,
    transformOrigin,
  };
};

const expandBubble = async () => {
  // 先设置展开状态，但暂时隐藏
  isExpanded.value = true;
  await nextTick();

  // 立即计算位置
  calculateBubblePosition();

  // 确保位置计算完成后再显示
  await nextTick();
};

const collapseBubble = () => {
  isExpanded.value = false;
};

const toggleBubble = () => {
  if (isExpanded.value) {
    collapseBubble();
  } else {
    expandBubble();
  }
};

// 监听窗口大小变化
const handleResize = () => {
  if (isExpanded.value) {
    calculateBubblePosition();
  }
};

// 点击外部关闭
const handleClickOutside = (event: MouseEvent) => {
  if (!isExpanded.value) return;

  const target = event.target as HTMLElement;
  const bubble = bubbleContainer.value;
  const trigger = props.triggerElement || thinkingButton.value;

  if (
    bubble &&
    !bubble.contains(target) &&
    trigger &&
    !trigger.contains(target)
  ) {
    collapseBubble();
  }
};

// 监听触发元素变化，重新计算位置
watch(
  () => [thinkingButton.value, props.triggerElement],
  () => {
    if (isExpanded.value) {
      nextTick(() => {
        calculateBubblePosition();
      });
    }
  },
);

// 监听思考状态，自动展开/收起气泡
watch(
  () => props.isThinking,
  (newValue, oldValue) => {
    if (newValue) {
      // 开始思考时延迟展开气泡，确保思考按钮已经渲染
      setTimeout(async () => {
        if (props.isThinking) {
          // 等待一个额外的 nextTick，确保触发元素已更新
          await nextTick();
          expandBubble();
        }
      }, 300); // 300ms延迟确保DOM更新和按钮渲染完成
    } else if (oldValue && !newValue) {
      // 思考结束后延迟2秒自动关闭弹窗
      setTimeout(() => {
        if (!props.isThinking) {
          collapseBubble();
        }
      }, 2000);
    }
  },
);

// 监听思考内容变化，自动滚动到底部
watch(
  () => [props.currentThinkingText, props.thinkingSteps],
  () => {
    if (isExpanded.value && scrollContainer.value) {
      nextTick(() => {
        const container = scrollContainer.value;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  },
  { deep: true },
);

onMounted(() => {
  window.addEventListener('resize', handleResize);
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  document.removeEventListener('click', handleClickOutside);
});

// 暴露方法
defineExpose({
  expandBubble,
  collapseBubble,
  isExpanded,
});
</script>

<template>
  <div class="thinking-process-container">
    <!-- Thinking Process Button -->
    <button
      v-if="showViewButton"
      ref="thinkingButton"
      :class="[mode === 'input' ? 'p-1' : 'p-2']"
      :title="isExpanded ? '收起思考过程' : '查看思考过程'"
      class="thinking-view-btn flex items-center gap-2 transition-all duration-200"
      @click="toggleBubble"
    >
      <MdiBrain
        :class="mode === 'input' ? 'h-4 w-4' : 'h-5 w-5'"
        class="text-muted-foreground"
      />
    </button>

    <!-- Thinking Process Bubble -->
    <Teleport to="body">
      <div
        v-if="isExpanded"
        ref="bubbleContainer"
        :class="[bubbleClass]"
        :style="bubbleStyle"
        class="thinking-bubble thinking-bubble-surface border-border fixed z-[1050] border backdrop-blur-sm"
      >
        <div
          class="border-border flex items-center justify-between border-b p-3"
        >
          <div class="flex items-center gap-2">
            <MdiBrain class="text-muted-foreground h-4 w-4" />
            <span class="text-foreground text-sm font-semibold">
              AI 思考过程
            </span>
          </div>
          <button
            class="hover:bg-accent rounded-full p-1 transition-colors duration-200"
            title="收起"
            @click="collapseBubble"
          >
            <MdiChevronUp class="text-muted-foreground h-4 w-4" />
          </button>
        </div>

        <div ref="scrollContainer" class="max-h-80 overflow-y-auto p-3">
          <!-- Show thinking content if available -->
          <div
            v-if="currentThinkingText && currentThinkingText.trim()"
            class="text-foreground/80 whitespace-pre-wrap text-sm leading-relaxed"
          >
            {{ currentThinkingText.trim() }}
          </div>

          <!-- Show thinking steps if no content but has steps -->
          <div v-else-if="thinkingSteps.length > 0" class="space-y-1">
            <div
              v-for="(step, index) in thinkingSteps"
              :key="index"
              class="text-foreground/80 text-sm leading-relaxed"
            >
              {{ step }}
            </div>
          </div>

          <!-- Thinking in Progress -->
          <div
            v-else-if="isThinking"
            class="text-foreground/80 flex items-center gap-2 text-sm"
          >
            <div
              class="h-4 w-4 animate-spin rounded-full border-2 border-[hsl(var(--primary))] border-t-transparent"
            ></div>
            <span>AI 正在思考...</span>
          </div>

          <!-- No thinking data -->
          <div v-else class="text-muted-foreground py-4 text-center text-sm">
            暂无思考过程
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.thinking-process-container {
  --thinking-process-shell-radius: calc(var(--radius) + 6px);
  --thinking-process-shell-shadow:
    0 14px 32px hsl(var(--overlay)), 0 4px 12px hsl(var(--foreground) / 0.08);
  --thinking-process-scrollbar-radius: 999px;
}

@keyframes thinking-bubble-in {
  0% {
    filter: blur(4px);
    opacity: 0;
    transform: scale(0.8);
  }

  50% {
    filter: blur(1px);
    opacity: 0.8;
    transform: scale(1.02);
  }

  100% {
    filter: blur(0);
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes thinking-bubble-out {
  0% {
    filter: blur(0);
    opacity: 1;
    transform: scale(1);
  }

  50% {
    filter: blur(1px);
    opacity: 0.6;
    transform: scale(0.95);
  }

  100% {
    filter: blur(4px);
    opacity: 0;
    transform: scale(0.8);
  }
}

/* 响应式设计 - 小屏幕适配 */
@media (max-width: 768px) {
  .thinking-bubble {
    min-width: 320px;
    max-width: 85vw;
  }
}

.thinking-view-btn {
  border-radius: calc(var(--radius) + 2px);
  color: hsl(var(--muted-foreground));
  transition: all 0.2s;
}

.thinking-view-btn:hover {
  background-color: hsl(var(--accent));
  color: hsl(var(--foreground));
}

.thinking-view-btn:active {
  transform: scale(0.95);
}

.thinking-bubble {
  min-width: 480px;
  max-width: 700px;

  /* 动画的变换原点会在 JS 中动态设置 */
}

.thinking-bubble-surface {
  background: hsl(var(--popover) / 0.96);
  border-radius: var(--thinking-process-shell-radius);
  box-shadow: var(--thinking-process-shell-shadow);
  color: hsl(var(--popover-foreground));
}

.thinking-bubble-show {
  animation: thinking-bubble-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
}

.thinking-bubble-hide {
  animation: thinking-bubble-out 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)
    forwards;
}

/* 滚动条样式 */
.thinking-bubble :deep(.max-h-80) {
  scrollbar-color: hsl(var(--muted-foreground) / 0.32) transparent;
  scrollbar-width: thin;
}

.thinking-bubble :deep(.max-h-80)::-webkit-scrollbar {
  width: 4px;
}

.thinking-bubble :deep(.max-h-80)::-webkit-scrollbar-track {
  background: transparent;
}

.thinking-bubble :deep(.max-h-80)::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.32);
  border-radius: var(--thinking-process-scrollbar-radius);
}

.thinking-bubble :deep(.max-h-80)::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.5);
}
</style>
