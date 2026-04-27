<script lang="ts" setup>
/**
 * CustomTag 组件
 *
 * 自定义标签组件，支持图标、颜色自定义和删除功能
 *
 * 主要特性：
 * - 🎨 支持自定义颜色
 * - 🖼️ 支持自定义图标
 * - ✖️ 可选的删除功能
 * - 🏷️ 系统标签/自定义标签区分
 * - ⚡ 流畅的动画效果
 */
import { computed } from 'vue';

import { MdiClose } from '#/icons';

export interface CustomTagProps {
  closable?: boolean;
  color?: string;
  disabled?: boolean;
  icon?: string;
  iconComponent?: any;
  id?: number | string;
  isBadgeShow?: boolean;
  name: string;
  type?: 'CUSTOM' | 'custom' | 'SYS' | 'system';
}

interface CustomTagEmits {
  click: [id?: number | string];
  close: [id?: number | string];
}

const props = withDefaults(defineProps<CustomTagProps>(), {
  id: undefined,
  type: 'custom',
  color: 'hsl(var(--primary))',
  icon: undefined,
  iconComponent: undefined,
  closable: false,
  disabled: false,
  isBadgeShow: false,
});

const emit = defineEmits<CustomTagEmits>();

// 计算标签类型
const isSystemTag = computed(() => {
  return props.type === 'SYS' || props.type === 'system';
});

// 计算是否可删除
const isDeletable = computed(() => {
  return props.closable && !isSystemTag.value && !props.disabled;
});

// 处理关闭事件
const handleClose = (e: Event) => {
  e.stopPropagation();
  if (isDeletable.value) {
    emit('close', props.id);
  }
};

// 处理点击事件
const handleClick = () => {
  if (!props.disabled) {
    emit('click', props.id);
  }
};
</script>

<template>
  <div
    :class="{
      'system-tag': isSystemTag,
      'closable-tag': isDeletable,
      'disabled-tag': disabled,
    }"
    :style="{ '--tag-accent': color }"
    class="custom-tag"
    @click="handleClick"
  >
    <!-- 图标 -->
    <component :is="iconComponent" v-if="iconComponent" class="tag-icon" />

    <!-- 标签文本 -->
    <span class="tag-text">{{ name }}</span>

    <!-- 删除按钮 -->
    <MdiClose v-if="isDeletable" class="delete-icon" @click="handleClose" />
  </div>
</template>

<style scoped>
/* 自定义标签样式 */
.custom-tag {
  --tag-surface: color-mix(
    in srgb,
    var(--tag-accent) 10%,
    hsl(var(--card)) 90%
  );
  --tag-border: color-mix(
    in srgb,
    var(--tag-accent) 18%,
    hsl(var(--border)) 82%
  );
  --tag-shadow: 0 1px 2px hsl(var(--foreground) / 0.08);
  position: relative;
  box-sizing: border-box;
  display: inline-flex;
  gap: 4px;
  align-items: center;
  height: 24px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--tag-accent);
  cursor: default;
  user-select: none;
  background-color: var(--tag-surface);
  border: 1px solid var(--tag-border);
  border-radius: calc(var(--radius) - 2px);
  box-shadow: var(--tag-shadow);
  transition: all 0.2s ease;
}

/* 可删除标签需要为删除按钮预留空间 */
.closable-tag {
  padding-right: 28px;
}

.custom-tag.disabled-tag {
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
}

/* 图标样式 */
.tag-icon {
  flex-shrink: 0;
  width: 14px;
  height: 14px;
}

/* 标签文本样式 */
.tag-text {
  line-height: 1;
  white-space: nowrap;
}

/* 删除按钮样式 */
.delete-icon {
  position: absolute;
  top: 50%;
  right: 8px;
  width: 14px;
  height: 14px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
  transform: translateY(-50%);
}

.custom-tag:hover .delete-icon {
  opacity: 0.8;
}

.delete-icon:hover {
  opacity: 1 !important;
}

/* 系统标签样式 */
.system-tag {
  position: relative;
}
</style>
