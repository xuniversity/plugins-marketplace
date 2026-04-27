<script setup lang="ts">
/**
 * AI 水印组件
 * 用于标识 AI 生成的内容
 */

// 定义组件属性
interface Props {
  /** 水印文案 */
  text?: string;
  /** 是否显示 */
  visible?: boolean;
  /** 自定义类名 */
  class?: string;
  /** 水印位置 */
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
  /** 透明度 (0-1) */
  opacity?: number;
  /** 字体大小 */
  fontSize?: 'base' | 'lg' | 'sm' | 'xs';
}

const props = withDefaults(defineProps<Props>(), {
  text: '本内容由AI生成',
  visible: true,
  class: '',
  position: 'bottom-left',
  opacity: 1,
  fontSize: 'sm',
});

// 计算位置类名
const positionClass = {
  'bottom-left': 'bottom-0 left-0',
  'bottom-right': 'bottom-0 right-0',
  'top-left': 'top-0 left-0',
  'top-right': 'top-0 right-0',
}[props.position];

// 计算字体大小类名
const fontSizeClass = {
  xs: 'text-xs',
  sm: 'text-sm',
  base: 'text-base',
  lg: 'text-lg',
}[props.fontSize];
</script>

<template>
  <div
    v-if="visible"
    :class="[positionClass, props.class]"
    :style="{ opacity }"
    class="ai-watermark"
  >
    <div :class="[fontSizeClass]" class="ai-watermark-content">
      <span class="font-medium">{{ text }}</span>
    </div>
  </div>
</template>

<style scoped>
/* AI生成水印样式 */
.ai-watermark {
  position: absolute;
  z-index: 10;
  pointer-events: none;
}

.ai-watermark-content {
  --ai-watermark-radius: calc(var(--radius) - 2px);
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  color: hsl(var(--primary) / 75%);
  white-space: nowrap;
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 12%) 0%,
    hsl(var(--primary) / 12%) 100%
  );
  backdrop-filter: blur(4px);
  border-radius: var(--ai-watermark-radius);
  box-shadow: 0 2px 6px hsl(var(--primary) / 8%);
  transition: all 0.3s ease;
}

.ai-watermark-content:hover {
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 16%) 0%,
    hsl(var(--primary) / 16%) 100%
  );
  box-shadow: 0 3px 8px hsl(var(--primary) / 12%);
}
</style>
