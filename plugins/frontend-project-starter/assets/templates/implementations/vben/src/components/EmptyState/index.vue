<script setup lang="ts">
import type { Component } from 'vue';

/**
 * EmptyState 空状态组件
 *
 * 美观的空状态展示组件，参考现代设计风格
 */

export interface EmptyStateProps {
  /** 标题 */
  title?: string;
  /** 描述信息 */
  description?: string;
  /** 图标类型（预设图标） */
  iconType?:
    | 'document'
    | 'folder'
    | 'message'
    | 'notification'
    | 'search'
    | 'wallet';
  /** 自定义图标组件（优先级高于 iconType） */
  icon?: Component;
}

withDefaults(defineProps<EmptyStateProps>(), {
  title: '暂无数据',
  description: '当前没有任何内容',
  iconType: 'folder',
  icon: undefined,
});
</script>

<template>
  <div class="empty-state-container">
    <div class="empty-state-card">
      <!-- 图标区域 -->
      <div class="empty-state-icon-wrapper">
        <!-- 自定义图标（优先显示） -->
        <div v-if="icon" class="empty-state-custom-icon">
          <component :is="icon" class="h-12 w-12 text-primary" />
        </div>

        <!-- 文件夹图标 -->
        <svg
          v-else-if="iconType === 'folder'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <!-- 背景装饰 -->
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <!-- 文件夹主体 -->
          <path
            d="M20 28C20 25.7909 21.7909 24 24 24H32L36 28H56C58.2091 28 60 29.7909 60 32V52C60 54.2091 58.2091 56 56 56H24C21.7909 56 20 54.2091 20 52V28Z"
            fill="hsl(var(--primary) / 20%)"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <!-- 文件夹内部线条 -->
          <path
            d="M28 40H52"
            stroke="hsl(var(--primary) / 50%)"
            stroke-linecap="round"
            stroke-width="2"
          />
          <path
            d="M28 46H44"
            stroke="hsl(var(--primary) / 30%)"
            stroke-linecap="round"
            stroke-width="2"
          />
        </svg>

        <!-- 文档图标 -->
        <svg
          v-else-if="iconType === 'document'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <path
            d="M26 20H46L54 28V60C54 61.1046 53.1046 62 52 62H26C24.8954 62 24 61.1046 24 60V22C24 20.8954 24.8954 20 26 20Z"
            fill="hsl(var(--primary) / 20%)"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M46 20V28H54"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M30 38H48"
            stroke="hsl(var(--primary) / 50%)"
            stroke-linecap="round"
            stroke-width="2"
          />
          <path
            d="M30 46H48"
            stroke="hsl(var(--primary) / 40%)"
            stroke-linecap="round"
            stroke-width="2"
          />
          <path
            d="M30 54H40"
            stroke="hsl(var(--primary) / 30%)"
            stroke-linecap="round"
            stroke-width="2"
          />
        </svg>

        <!-- 消息图标 -->
        <svg
          v-else-if="iconType === 'message'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <path
            d="M20 26C20 24.8954 20.8954 24 22 24H58C59.1046 24 60 24.8954 60 26V46C60 47.1046 59.1046 48 58 48H44L36 56V48H22C20.8954 48 20 47.1046 20 46V26Z"
            fill="hsl(var(--primary) / 20%)"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <circle cx="32" cy="36" fill="hsl(var(--primary))" r="2" />
          <circle cx="40" cy="36" fill="hsl(var(--primary))" r="2" />
          <circle cx="48" cy="36" fill="hsl(var(--primary))" r="2" />
        </svg>

        <!-- 通知图标 -->
        <svg
          v-else-if="iconType === 'notification'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <path
            d="M40 18C32.268 18 26 24.268 26 32V42L22 50H58L54 42V32C54 24.268 47.732 18 40 18Z"
            fill="hsl(var(--primary) / 20%)"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
          <path
            d="M34 50V52C34 55.3137 36.6863 58 40 58C43.3137 58 46 55.3137 46 52V50"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
        </svg>

        <!-- 搜索图标 -->
        <svg
          v-else-if="iconType === 'search'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <circle
            cx="36"
            cy="36"
            fill="hsl(var(--primary) / 20%)"
            r="14"
            stroke="hsl(var(--primary))"
            stroke-width="2"
          />
          <path
            d="M46 46L56 56"
            stroke="hsl(var(--primary))"
            stroke-linecap="round"
            stroke-width="3"
          />
        </svg>

        <!-- 钱包图标 -->
        <svg
          v-else-if="iconType === 'wallet'"
          class="empty-state-icon"
          fill="none"
          viewBox="0 0 80 80"
        >
          <circle cx="40" cy="40" fill="hsl(var(--primary) / 8%)" r="36" />
          <path
            d="M20 30C20 27.7909 21.7909 26 24 26H56C58.2091 26 60 27.7909 60 30V54C60 56.2091 58.2091 58 56 58H24C21.7909 58 20 56.2091 20 54V30Z"
            fill="hsl(var(--primary) / 20%)"
            stroke="hsl(var(--primary))"
            stroke-width="2"
          />
          <path
            d="M20 34H60"
            stroke="hsl(var(--primary))"
            stroke-width="2"
          />
          <rect
            fill="hsl(var(--primary))"
            height="10"
            rx="2"
            width="16"
            x="44"
            y="40"
          />
          <circle cx="52" cy="45" fill="hsl(var(--primary-foreground))" r="2" />
        </svg>
      </div>

      <!-- 文字内容 -->
      <div class="empty-state-content">
        <h3 class="empty-state-title">{{ title }}</h3>
        <p v-if="description" class="empty-state-description">{{ description }}</p>
      </div>

      <!-- 操作区域插槽 -->
      <div v-if="$slots.action" class="empty-state-action">
        <slot name="action"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.empty-state-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 48px 24px;
}

.empty-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 480px;
  padding: 48px 32px;
  text-align: center;
}

.empty-state-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
}

.empty-state-icon {
  width: 80px;
  height: 80px;
}

.empty-state-custom-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: hsl(var(--primary) / 8%);
  border-radius: 50%;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: hsl(var(--foreground));
}

.empty-state-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: hsl(var(--muted-foreground));
}

.empty-state-action {
  margin-top: 20px;
}
</style>
