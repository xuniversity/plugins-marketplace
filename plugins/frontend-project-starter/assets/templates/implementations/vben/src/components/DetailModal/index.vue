<script setup lang="ts">
/**
 * DetailModal 组件
 *
 * 通用的详情展示弹窗组件，采用现代化的表单式布局设计
 */
import type { PropType } from 'vue';

import { computed, defineComponent, h, isVNode, ref } from 'vue';

import { Modal, Spin } from 'ant-design-vue';

export interface DetailTab {
  content?: any;
  key: string;
  label: string;
}

export interface DetailHeader {
  createdAt?: Date | string;
  extra?: any;
  sentAt?: Date | string;
  subtitle?: string;
  title: string;
  titleExtra?: any;
  updatedAt?: Date | string;
}

interface Props {
  activeTab?: string;
  autoHeight?: boolean;
  bodyStyle?: Record<string, any>;
  header?: DetailHeader;
  height?: string;
  layout?: 'flat' | 'tabs';
  loading?: boolean;
  maskClosable?: boolean;
  tabs?: DetailTab[];
  visible?: boolean;
  width?: number | string;
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  loading: false,
  autoHeight: false,
  header: undefined,
  tabs: undefined,
  activeTab: undefined,
  width: '900px',
  height: 'auto',
  layout: 'flat',
  bodyStyle: () => ({}),
  maskClosable: false,
});

const emit = defineEmits<{
  afterVisibleChange: [open: boolean];
  close: [];
  tabChange: [key: string];
  'update:activeTab': [value: string];
  'update:visible': [value: boolean];
}>();

const VNodeRenderer = defineComponent({
  name: 'DetailModalVNodeRenderer',
  props: {
    vnode: {
      type: [Object, Function, String] as PropType<any>,
      default: undefined,
    },
  },
  render() {
    const { vnode } = this;
    if (!vnode) return null;
    if (typeof vnode === 'string' || typeof vnode === 'number') {
      return vnode as any;
    }
    if (isVNode(vnode)) {
      return vnode;
    }
    return h(vnode);
  },
});

const currentTab = ref(props.activeTab || props.tabs?.[0]?.key || '');

const handleClose = () => {
  emit('update:visible', false);
  emit('close');
};

const handleAfterOpenChange = (open: boolean) => {
  emit('afterVisibleChange', open);
};

const handleTabChange = (key: string) => {
  currentTab.value = key;
  emit('update:activeTab', key);
  emit('tabChange', key);
};

const modalBodyStyle = computed(() => {
  const baseStyle = {
    padding: 0,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column' as const,
  };

  if (props.autoHeight) {
    return {
      ...baseStyle,
      height: 'auto',
      maxHeight: '80vh',
      ...props.bodyStyle,
    };
  }

  return {
    ...baseStyle,
    height: '80vh',
    maxHeight: '80vh',
    ...props.bodyStyle,
  };
});

const contentClass = computed(() => ({
  'detail-flat-content': true,
  'detail-flat-content-no-scroll': props.autoHeight,
}));
</script>

<template>
  <Modal
    :body-style="modalBodyStyle"
    :closable="false"
    :footer="null"
    :loading="loading"
    :mask-closable="maskClosable"
    :open="visible"
    :width="width"
    wrap-class-name="detail-modal"
    @after-open-change="handleAfterOpenChange"
    @cancel="handleClose"
  >
    <!-- 自定义头部 -->
    <div class="detail-header">
      <div class="detail-header-left">
        <div class="detail-title-section">
          <div
            class="detail-title-row"
            :class="{ 'detail-title-row-with-extra': !!header?.titleExtra }"
          >
            <h3 class="detail-title">{{ header?.title || '详情' }}</h3>
            <div v-if="header?.titleExtra" class="detail-title-extra">
              <VNodeRenderer :vnode="header.titleExtra" />
            </div>
          </div>
          <p v-if="header?.subtitle" class="detail-subtitle">
            {{ header.subtitle }}
          </p>
        </div>
        <div v-if="$slots['header-content']" class="detail-header-content">
          <slot name="header-content"></slot>
        </div>
        <div
          v-if="header?.createdAt || header?.updatedAt || header?.sentAt"
          class="detail-time-section"
        >
          <div v-if="header.createdAt" class="detail-time-item">
            <span class="detail-time-label">创建时间</span>
            <span class="detail-time-value">
              {{
                typeof header.createdAt === 'string'
                  ? header.createdAt
                  : new Date(header.createdAt).toLocaleString()
              }}
            </span>
          </div>
          <div v-if="header.sentAt" class="detail-time-item">
            <span class="detail-time-label">发送时间</span>
            <span class="detail-time-value">
              {{
                typeof header.sentAt === 'string'
                  ? header.sentAt
                  : new Date(header.sentAt).toLocaleString()
              }}
            </span>
          </div>
          <div v-if="header.updatedAt" class="detail-time-item">
            <span class="detail-time-label">更新时间</span>
            <span class="detail-time-value">
              {{
                typeof header.updatedAt === 'string'
                  ? header.updatedAt
                  : new Date(header.updatedAt).toLocaleString()
              }}
            </span>
          </div>
        </div>
      </div>
      <div class="detail-header-right">
        <div v-if="header?.extra" class="detail-header-extra">
          <VNodeRenderer :vnode="header.extra" />
        </div>
        <button
          aria-label="关闭"
          class="detail-close-btn"
          type="button"
          @click="handleClose"
        >
          <svg
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path
              d="M6 18L18 6M6 6l12 12"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="detail-content">
      <!-- 平铺布局 -->
      <div v-if="layout === 'flat'" :class="contentClass">
        <slot name="content"></slot>
      </div>

      <!-- Tab布局 -->
      <div
        v-else-if="layout === 'tabs' && tabs?.length"
        class="detail-tabs-content"
      >
        <!-- Tab导航 -->
        <div class="detail-tabs-nav">
          <div
            v-for="tab in tabs"
            :key="tab.key"
            :class="[{ 'detail-tab-active': currentTab === tab.key }]"
            class="detail-tab-item"
            @click="handleTabChange(tab.key)"
          >
            {{ tab.label }}
          </div>
        </div>

        <!-- Tab内容 -->
        <div class="detail-tabs-body">
          <template v-for="tab in tabs" :key="tab.key">
            <div v-show="currentTab === tab.key" class="detail-tab-pane">
              <slot :name="`tab-${tab.key}`" :tab="tab">
                <component :is="tab.content" v-if="tab.content" />
              </slot>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 自定义 Footer -->
    <div v-if="$slots.footer" class="detail-footer">
      <slot name="footer"></slot>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="detail-loading">
      <Spin size="large" />
      <p class="detail-loading-text">加载中...</p>
    </div>
  </Modal>
</template>

<style>
/* 全局样式：针对使用 wrap-class-name 的 Modal */
.detail-modal .ant-modal-content {
  padding: 0 !important;
  overflow: hidden;
  background: hsl(var(--popover));
  color: hsl(var(--foreground));
  border: 1px solid hsl(var(--border));
  border-radius: calc(var(--radius) + 6px);
  box-shadow:
    0 16px 38px hsl(var(--overlay)),
    0 6px 16px hsl(var(--foreground) / 0.12);
}

.detail-modal .ant-modal-content .ant-modal-body {
  padding: 0 !important;
}

.detail-modal .ant-modal-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>

<style scoped>
/* 头部样式 */
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 20px;
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 8%) 0%,
    hsl(var(--primary) / 4%) 100%
  );
  border-bottom: 1px solid hsl(var(--border));
}

.detail-header-left {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 16px;
}

.detail-title-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.detail-title-row {
  display: flex;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 8px;
  align-items: flex-start;
  min-width: 0;
  max-width: 100%;
}

.detail-title-row-with-extra .detail-title {
  max-width: min(100%, 72%);
}

.detail-title {
  flex: 0 1 auto;
  min-width: 0;
  max-width: 100%;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
  color: hsl(var(--foreground));
  overflow-wrap: anywhere;
  white-space: normal;
}

.detail-title-extra {
  display: inline-flex;
  flex: 0 0 auto;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  min-width: 0;
  max-width: 100%;
  padding-top: 2px;
}

@media (max-width: 768px) {
  .detail-title-row-with-extra .detail-title {
    max-width: 100%;
  }
}

.detail-subtitle {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  color: hsl(var(--muted-foreground));
}

.detail-header-content {
  margin-top: 8px;
}

.detail-time-section {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.detail-time-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-time-label {
  font-size: 12px;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
}

.detail-time-value {
  font-size: 13px;
  font-weight: 500;
  color: hsl(var(--foreground));
}

.detail-header-right {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.detail-header-extra {
  display: flex;
  align-items: center;
}

.detail-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  font-size: 16px;
  color: hsl(var(--destructive));
  cursor: pointer;
  background: hsl(var(--destructive) / 10%);
  border: 1px solid hsl(var(--destructive) / 20%);
  border-radius: calc(var(--radius) + 2px);
  box-shadow: 0 2px 8px hsl(var(--destructive) / 10%);
  transition:
    color 0.2s ease,
    background-color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.detail-close-btn:hover {
  color: hsl(var(--destructive-foreground));
  background: hsl(var(--destructive));
  border-color: hsl(var(--destructive));
  box-shadow: 0 4px 12px hsl(var(--destructive) / 20%);
  transform: translateY(-1px);
}

.detail-close-btn:active {
  transform: translateY(0);
}

.detail-close-btn:focus-visible {
  outline: 2px solid hsl(var(--destructive) / 36%);
  outline-offset: 2px;
}

/* 内容区域 */
.detail-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

/* Footer 区域 */
.detail-footer {
  padding: 16px 24px;
  background: hsl(var(--popover));
  border-top: 1px solid hsl(var(--border));
}

.detail-flat-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0;
  overflow: hidden auto;
  scrollbar-color: hsl(var(--muted-foreground) / 30%) transparent;
  scrollbar-width: thin;
  background: hsl(var(--popover));
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.detail-flat-content::-webkit-scrollbar {
  width: 6px;
}

.detail-flat-content::-webkit-scrollbar-track {
  background: transparent;
}

.detail-flat-content::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 30%);
  border-radius: 999px;
}

.detail-flat-content-no-scroll {
  overflow: visible !important;
}

.detail-tabs-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

.detail-tabs-nav {
  display: flex;
  padding: 0;
  background: hsl(var(--muted) / 30%);
  border-bottom: 1px solid hsl(var(--border));
}

.detail-tab-item {
  position: relative;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.detail-tab-item:hover {
  color: hsl(var(--primary));
  background: hsl(var(--primary) / 5%);
}

.detail-tab-active {
  color: hsl(var(--primary)) !important;
  background: hsl(var(--primary) / 8%);
  border-bottom-color: hsl(var(--primary));
}

.detail-tabs-body {
  flex: 1;
  overflow: hidden auto;
  scrollbar-color: hsl(var(--muted-foreground) / 30%) transparent;
  scrollbar-width: thin;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.detail-tab-pane {
  min-height: 100%;
  padding: 0;
  background: hsl(var(--popover));
}

/* 加载状态 */
.detail-loading {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: hsl(var(--overlay));
  backdrop-filter: blur(4px);
}

.detail-loading-text {
  margin-top: 16px;
  font-size: 14px;
  color: hsl(var(--muted-foreground));
}
</style>
