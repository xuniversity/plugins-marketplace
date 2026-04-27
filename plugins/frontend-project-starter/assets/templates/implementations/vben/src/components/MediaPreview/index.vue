<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import { useAntdDesignTokens } from '@vben/hooks';

import { MdiClose, MdiDownload, MdiMagnify, MdiMinus, MdiPlus } from '#/icons';

interface MediaItem {
  url: string;
  name: string;
  type: 'audio' | 'image' | 'video';
}

interface MediaPreviewProps {
  visible?: boolean;
  items?: MediaItem[];
  current?: number;
  zIndex?: number;
}

const props = withDefaults(defineProps<MediaPreviewProps>(), {
  visible: false,
  items: () => [],
  current: 0,
  zIndex: undefined,
});

const emit = defineEmits<{
  close: [];
  'update:visible': [value: boolean];
}>();

// 获取 Ant Design 的设计 token
const { tokens } = useAntdDesignTokens();

// 计算 zIndex：使用传入的 zIndex 或默认值（zIndexPopupBase + 10000）
const previewZIndex = computed(() => {
  return props.zIndex ?? tokens.zIndexPopupBase + 10_000;
});

const currentIndex = ref(props.current);
const scale = ref(1);
const minScale = 0.5;
const maxScale = 3;

// 监听 props.current 变化，同步更新 currentIndex
watch(
  () => props.current,
  (newVal) => {
    currentIndex.value = newVal ?? 0;
  },
  { immediate: true },
);

// 当 visible 变为 true 时，重置 currentIndex 到 props.current
watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      currentIndex.value = props.current ?? 0;
      scale.value = 1;
    }
  },
);

// 当前媒体项
const currentItem = computed(() => {
  return props.items[currentIndex.value] || null;
});

const isImageItem = computed(() => {
  return currentItem.value?.type === 'image';
});

// 是否有多个媒体项
const hasMultiple = computed(() => {
  return props.items.length > 1;
});

const showCounter = computed(() => hasMultiple.value);

const showNavigation = computed(() => hasMultiple.value);

const showZoomControls = computed(() => isImageItem.value);

const showDownloadButton = computed(() => !!currentItem.value);

const isCompactToolbar = computed(() => {
  return (
    !!currentItem.value &&
    !showCounter.value &&
    !showNavigation.value &&
    !showZoomControls.value &&
    showDownloadButton.value
  );
});

const showHeaderDownloadButton = computed(() => isCompactToolbar.value);

const showToolbar = computed(() => {
  return !!currentItem.value && (isImageItem.value || hasMultiple.value);
});

// 是否可以上一个
const canPrevious = computed(() => {
  return hasMultiple.value && currentIndex.value > 0;
});

// 是否可以下一个
const canNext = computed(() => {
  return hasMultiple.value && currentIndex.value < props.items.length - 1;
});

// 是否可以放大
const canZoomIn = computed(() => {
  return scale.value < maxScale;
});

// 是否可以缩小
const canZoomOut = computed(() => {
  return scale.value > minScale;
});

// 关闭预览
const handleClose = () => {
  scale.value = 1; // 重置缩放
  emit('update:visible', false);
  emit('close');
};

// 上一个
const handlePrevious = () => {
  if (canPrevious.value) {
    currentIndex.value--;
    scale.value = 1; // 切换时重置缩放
  }
};

// 下一个
const handleNext = () => {
  if (canNext.value) {
    currentIndex.value++;
    scale.value = 1; // 切换时重置缩放
  }
};

// 下载当前媒体
const handleDownload = () => {
  if (!currentItem.value) return;

  const link = document.createElement('a');
  link.href = currentItem.value.url;
  link.download = currentItem.value.name;
  link.target = '_blank';
  document.body.append(link);
  link.click();
  link.remove();
};

// 放大图片
const zoomIn = () => {
  if (scale.value < maxScale) {
    scale.value = Math.min(scale.value + 0.25, maxScale);
  }
};

// 缩小图片
const zoomOut = () => {
  if (scale.value > minScale) {
    scale.value = Math.max(scale.value - 0.25, minScale);
  }
};

// 重置缩放
const resetZoom = () => {
  scale.value = 1;
};

// 计算图片样式
const imageStyle = computed(() => {
  if (isImageItem.value) {
    return {
      transform: `scale(${scale.value})`,
      transition: 'transform 0.2s ease',
    };
  }
  return {};
});

// 键盘事件处理
const handleKeydown = (e: KeyboardEvent) => {
  if (!props.visible) return;

  switch (e.key) {
    case '0': {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        resetZoom();
      }
      break;
    }
    case '+':
    // eslint-disable-next-line no-fallthrough
    case '=': {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        zoomIn();
      }
      break;
    }
    case '-': {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        zoomOut();
      }
      break;
    }
    case 'ArrowLeft': {
      handlePrevious();
      break;
    }
    case 'ArrowRight': {
      handleNext();
      break;
    }
    case 'Escape': {
      handleClose();
      break;
    }
  }
};

// 监听鼠标滚轮缩放
const handleWheel = (e: WheelEvent) => {
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault();
    if (e.deltaY < 0) {
      zoomIn();
    } else {
      zoomOut();
    }
  }
};

// 点击遮罩关闭（阻止内容区域的点击冒泡）
const handleMaskClick = (e: MouseEvent) => {
  if (e.target === e.currentTarget) {
    handleClose();
  }
};

// 在组件挂载时添加键盘监听
onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

// 在组件卸载时移除键盘监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <Teleport to="body">
    <Transition name="media-preview-fade">
      <div
        v-if="visible"
        class="media-preview-overlay"
        :style="{ zIndex: previewZIndex }"
        @click="handleMaskClick"
      >
        <!-- 预览内容区域 -->
        <div class="media-preview-wrapper" @wheel="handleWheel">
          <!-- 头部 -->
          <div class="media-preview-header">
            <div class="media-preview-title">
              {{ currentItem?.name || '媒体预览' }}
            </div>
            <div class="media-preview-header-actions">
              <button
                v-if="showHeaderDownloadButton"
                class="media-preview-header-btn"
                title="下载"
                @click="handleDownload"
              >
                <MdiDownload class="text-xl" />
              </button>
              <button class="media-preview-close" @click="handleClose">
                <MdiClose class="text-xl" />
              </button>
            </div>
          </div>

          <!-- 媒体内容 -->
          <div v-if="currentItem" class="media-preview-content">
            <!-- 图片 -->
            <img
              v-if="currentItem.type === 'image'"
              :alt="currentItem.name"
              :src="currentItem.url"
              :style="imageStyle"
              class="media-image"
            />

            <!-- 视频 -->
            <video
              v-else-if="currentItem.type === 'video'"
              :src="currentItem.url"
              class="media-video"
              controls
              preload="metadata"
            ></video>

            <!-- 音频 -->
            <audio
              v-else-if="currentItem.type === 'audio'"
              :src="currentItem.url"
              class="media-audio"
              controls
              preload="metadata"
            ></audio>
          </div>

          <!-- 底部工具栏 -->
          <div v-if="showToolbar" class="media-preview-toolbar">
            <div v-if="showCounter" class="toolbar-left">
              <span class="media-counter">
                {{ currentIndex + 1 }} / {{ props.items.length }}
              </span>
            </div>

            <div v-if="showNavigation" class="toolbar-center">
              <!-- 导航按钮 -->
              <a-button
                :disabled="!canPrevious || undefined"
                class="preview-nav-btn"
                size="small"
                @click="handlePrevious"
              >
                ‹ 上一个
              </a-button>
              <a-button
                :disabled="!canNext || undefined"
                class="preview-nav-btn"
                size="small"
                @click="handleNext"
              >
                下一个 ›
              </a-button>
            </div>

            <div
              v-if="showZoomControls || showDownloadButton"
              class="toolbar-right"
            >
              <!-- 缩放控制（仅图片显示） -->
              <template v-if="showZoomControls">
                <a-button
                  :disabled="!canZoomOut || undefined"
                  class="preview-icon-btn"
                  size="small"
                  @click="zoomOut"
                >
                  <MdiMinus class="preview-icon" />
                </a-button>

                <a-button
                  class="preview-icon-btn"
                  size="small"
                  @click="resetZoom"
                >
                  <MdiMagnify class="preview-icon" />
                </a-button>

                <a-button
                  :disabled="!canZoomIn || undefined"
                  class="preview-icon-btn"
                  size="small"
                  @click="zoomIn"
                >
                  <MdiPlus class="preview-icon" />
                </a-button>
              </template>

              <a-button
                v-if="showDownloadButton"
                class="preview-icon-btn"
                size="small"
                @click="handleDownload"
              >
                <MdiDownload class="preview-icon" />
              </a-button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* 遮罩层 */
.media-preview-overlay {
  --media-preview-surface: hsl(var(--card) / 0.72);
  --media-preview-surface-hover: hsl(var(--card) / 0.9);
  --media-preview-surface-subtle: hsl(var(--card) / 0.42);
  --media-preview-border: hsl(var(--border) / 0.72);
  --media-preview-border-strong: hsl(var(--border) / 0.9);
  --media-preview-text: hsl(var(--foreground));
  --media-preview-text-muted: hsl(var(--muted-foreground));
  --media-preview-shadow: 0 4px 12px hsl(var(--foreground) / 0.2);
  --media-preview-surface-radius: calc(var(--radius) + 2px);

  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: hsl(var(--overlay));
}

/* 预览内容包装器 - 去除白底卡片 */
.media-preview-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
  box-shadow: none;
}

/* 头部 - 悬浮透明 */
.media-preview-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: flex-end; /* 只保留右侧关闭按钮 */
  padding: 16px 24px;
  border-bottom: none;
  background: linear-gradient(to bottom, hsl(var(--overlay)), transparent);
}

.media-preview-title {
  display: none; /* 隐藏标题，增强沉浸感 */
}

.media-preview-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.media-preview-header-btn,
.media-preview-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  color: var(--media-preview-text);
  cursor: pointer;
  background: var(--media-preview-surface-subtle);
  border: 1px solid var(--media-preview-border);
  border-radius: 50%;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.media-preview-header-btn svg,
.media-preview-header-btn path,
.media-preview-close svg,
.media-preview-close path {
  fill: currentColor !important;
  color: inherit !important;
}

.media-preview-header-btn:hover,
.media-preview-close:hover {
  color: var(--media-preview-text);
  background: var(--media-preview-surface);
  transform: scale(1.05);
}

/* 媒体内容区域 - 最大化 */
.media-preview-content {
  flex: 1;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  overflow: hidden;
}

.media-image {
  display: block;
  max-width: 90vw;
  max-height: 85vh;
  cursor: grab;
  object-fit: contain;
  border-radius: var(--media-preview-surface-radius);
  transition: transform 0.2s ease;
}

.media-image:active {
  cursor: grabbing;
}

.media-video {
  max-width: 90vw;
  max-height: 85vh;
  border-radius: var(--media-preview-surface-radius);
  box-shadow: var(--media-preview-shadow);
}

.media-audio {
  width: 100%;
  max-width: 500px;
  border: 1px solid var(--media-preview-border-strong);
  border-radius: calc(var(--radius) + 6px);
  background: hsl(var(--card) / 0.96);
}

/* 底部工具栏 - 底部悬浮 */
.media-preview-toolbar {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  gap: 32px;
  align-items: center;
  justify-content: center;
  padding: 16px 32px;
  background: hsl(var(--overlay));
  background: color-mix(in srgb, hsl(var(--overlay)) 82%, hsl(var(--card)) 18%);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(16px);
  border: 1px solid var(--media-preview-border);
  box-shadow: 0 4px 24px hsl(var(--foreground) / 0.3);
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.media-counter {
  font-size: 15px;
  font-weight: 500;
  color: var(--media-preview-text);
  font-feature-settings: 'tnum';
  padding: 4px 12px;
  background: var(--media-preview-surface-subtle);
  border-radius: calc(var(--radius) + 8px);
}

/* 过渡动画 */
.media-preview-fade-enter-active,
.media-preview-fade-leave-active {
  transition: opacity 0.3s ease;
}

.media-preview-fade-enter-from,
.media-preview-fade-leave-to {
  opacity: 0;
}
</style>

<style>
/* 全局样式 - 工具栏按钮（使用自定义 class 确保样式生效） */

/* 通用按钮样式 */
.preview-nav-btn,
.preview-icon-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: var(--media-preview-surface, hsl(var(--card) / 0.72)) !important;
  border: 1px solid var(--media-preview-border, hsl(var(--border) / 0.72)) !important;
  color: var(--media-preview-text, hsl(var(--foreground))) !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  box-shadow: none !important;
}

.preview-nav-btn:hover,
.preview-icon-btn:hover {
  color: var(--media-preview-text, hsl(var(--foreground))) !important;
  background: var(
    --media-preview-surface-hover,
    hsl(var(--card) / 0.9)
  ) !important;
  border-color: var(
    --media-preview-border-strong,
    hsl(var(--border))
  ) !important;
  transform: translateY(-2px);
  box-shadow: var(
    --media-preview-shadow,
    0 4px 12px hsl(var(--foreground) / 0.2)
  ) !important;
}

.preview-nav-btn[disabled],
.preview-icon-btn[disabled] {
  color: var(
    --media-preview-text-muted,
    hsl(var(--muted-foreground))
  ) !important;
  background: hsl(var(--card) / 0.4) !important;
  border-color: transparent !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
  pointer-events: none !important; /* 禁止点击 */
}

/* 确保 disabled 按钮 hover 时不变化 */
.preview-nav-btn[disabled]:hover,
.preview-icon-btn[disabled]:hover {
  color: var(
    --media-preview-text-muted,
    hsl(var(--muted-foreground))
  ) !important;
  background: hsl(var(--card) / 0.4) !important;
  border-color: transparent !important;
  transform: none !important;
  box-shadow: none !important;
}

/* 文字按钮样式（上一个、下一个） */
.preview-nav-btn {
  width: auto !important;
  height: 36px !important;
  padding: 0 16px !important;
  border-radius: calc(var(--radius) + 14px) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}

/* 图标按钮样式（缩放、下载等） */
.preview-icon-btn {
  width: 40px !important;
  height: 40px !important;
  padding: 0 !important;
  border-radius: 50% !important;
}

/* 图标样式 */
.preview-icon {
  font-size: 22px !important;
  color: var(--media-preview-text, hsl(var(--foreground))) !important;
}

.preview-icon svg,
.preview-icon path {
  fill: currentColor !important;
  color: inherit !important;
}

.preview-icon-btn[disabled] .preview-icon {
  color: var(
    --media-preview-text-muted,
    hsl(var(--muted-foreground))
  ) !important;
}

.preview-icon-btn[disabled] .preview-icon svg,
.preview-icon-btn[disabled] .preview-icon path {
  fill: var(
    --media-preview-text-muted,
    hsl(var(--muted-foreground))
  ) !important;
}
</style>
