<script setup lang="ts">
/**
 * DetailDrawer 组件
 *
 * 通用的详情展示抽屉组件，采用现代化的表单式布局设计
 *
 * 主要特性：
 * - ✨ 表单式布局，高信息密度
 * - 📑 支持 flat 和 tabs 两种布局模式
 * - 🎨 优雅的视觉设计
 * - 📱 响应式设计
 * - 🎯 自定义 Footer 和水印支持
 */
import type { CSSProperties, PropType } from 'vue';

import { computed, defineComponent, h, isVNode, ref, watch } from 'vue';

import { MdiClose } from '#/icons';

import { Drawer, Spin } from 'ant-design-vue';

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  destroyOnClose: false,
  loading: false,
  header: undefined,
  tabs: undefined,
  activeTab: undefined,
  width: '70vw',
  height: 'auto',
  layout: 'flat',
  bodyStyle: () => ({}),
});

const emit = defineEmits<{
  afterVisibleChange: [open: boolean];
  close: [];
  tabChange: [key: string];
  'update:activeTab': [value: string];
  'update:visible': [value: boolean];
}>();

/**
 * VNode 渲染器组件
 * 用于正确渲染动态 VNode，避免闭包捕获导致的生命周期问题
 * 通过将 VNode 作为 prop 传入，确保每次渲染都使用最新的 VNode
 */
const VNodeRenderer = defineComponent({
  name: 'VNodeRenderer',
  props: {
    vnode: {
      type: [Object, Function, String] as PropType<any>,
      default: undefined,
    },
  },
  render() {
    const { vnode } = this;
    if (!vnode) return null;
    // Render plain text directly (common for simple status / ids).
    if (typeof vnode === 'string' || typeof vnode === 'number') {
      return vnode as any;
    }
    // 如果是 VNode，直接返回渲染
    if (isVNode(vnode)) {
      return vnode;
    }
    // 如果是组件，使用 h 函数渲染
    return h(vnode);
  },
});

export interface DetailTab {
  key: string;
  label: string;
  content?: any;
}

export interface DetailHeader {
  title: string;
  subtitle?: string;
  createdAt?: Date | string;
  createdAtLabel?: string;
  updatedAt?: Date | string;
  updatedAtLabel?: string;
  sentAt?: Date | string;
  sentAtLabel?: string;
  extra?: any;
  titleExtra?: any;
}

interface Props {
  visible?: boolean;
  destroyOnClose?: boolean;
  loading?: boolean;
  header?: DetailHeader;
  tabs?: DetailTab[];
  activeTab?: string;
  width?: number | string;
  height?: string;
  layout?: 'flat' | 'tabs';
  bodyStyle?: Record<string, any>;
}

const resolveCurrentTab = (activeTab = props.activeTab, tabs = props.tabs) => {
  if (activeTab && tabs?.some((tab) => tab.key === activeTab)) {
    return activeTab;
  }

  return tabs?.[0]?.key || activeTab || '';
};

const currentTab = ref(resolveCurrentTab());

watch(
  [() => props.activeTab, () => props.tabs],
  ([activeTab, tabs]) => {
    const nextTab = resolveCurrentTab(activeTab, tabs);
    if (nextTab !== currentTab.value) {
      currentTab.value = nextTab;
    }
  },
  { deep: true },
);

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

const drawerBodyStyle = computed<CSSProperties>(() => ({
  padding: 0,
  height: '100%',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  ...props.bodyStyle,
}));
</script>

<template>
  <Drawer
    :body-style="drawerBodyStyle"
    :closable="false"
    :destroy-on-close="destroyOnClose"
    :footer="null"
    :loading="loading"
    :mask-closable="true"
    :open="visible"
    :width="width"
    placement="right"
    wrap-class-name="detail-drawer"
    @after-open-change="handleAfterOpenChange"
    @close="handleClose"
  >
    <!-- 自定义头部 -->
    <div class="detail-header">
      <div class="detail-header-left">
        <div class="detail-title-section">
          <div
            class="detail-title-row"
            :class="{ 'detail-title-row-with-extra': !!header?.titleExtra }"
          >
            <h3 class="detail-title" :title="header?.title || '详情'">
              {{ header?.title || '详情' }}
            </h3>
            <div v-if="header?.titleExtra" class="detail-title-extra">
              <VNodeRenderer :vnode="header.titleExtra" />
            </div>
          </div>
          <p v-if="header?.subtitle" class="detail-subtitle">
            {{ header.subtitle }}
          </p>
        </div>
        <div
          v-if="header?.createdAt || header?.updatedAt || header?.sentAt"
          class="detail-time-section"
        >
          <div v-if="header.createdAt" class="detail-time-item">
            <span class="detail-time-label">{{
              header.createdAtLabel || '创建时间'
            }}</span>
            <span class="detail-time-value">
              {{
                typeof header.createdAt === 'string'
                  ? header.createdAt
                  : new Date(header.createdAt).toLocaleString()
              }}
            </span>
          </div>
          <div v-if="header.sentAt" class="detail-time-item">
            <span class="detail-time-label">{{
              header.sentAtLabel || '发送时间'
            }}</span>
            <span class="detail-time-value">
              {{
                typeof header.sentAt === 'string'
                  ? header.sentAt
                  : new Date(header.sentAt).toLocaleString()
              }}
            </span>
          </div>
          <div v-if="header.updatedAt" class="detail-time-item">
            <span class="detail-time-label">{{
              header.updatedAtLabel || '更新时间'
            }}</span>
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
          <MdiClose />
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="detail-content">
      <!-- 平铺布局 -->
      <div v-if="layout === 'flat'" class="detail-flat-content">
        <slot name="content"></slot>
      </div>

      <!-- 水印插槽 - 固定在内容区域底部，不随内容滚动 -->
      <div
        v-if="$slots.watermark && layout === 'flat'"
        class="detail-watermark"
      >
        <slot name="watermark"></slot>
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
  </Drawer>
</template>

<style>
/* 全局样式：针对使用 wrap-class-name 的 Drawer */
.detail-drawer .ant-drawer-content-wrapper {
  box-shadow:
    0 16px 38px hsl(var(--overlay)),
    0 6px 16px hsl(var(--foreground) / 0.12);
}

.detail-drawer .ant-drawer-content {
  background: hsl(var(--popover));
  color: hsl(var(--foreground));
  border-left: 1px solid hsl(var(--border));
}

.detail-drawer .ant-drawer-body {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 !important;
  overflow: hidden;
}
</style>

<style scoped>
/* 响应式设计 */
@media (max-width: 768px) {
  /* 移动设备上的滚动条优化 */
  .detail-flat-content::-webkit-scrollbar,
  .detail-tabs-body::-webkit-scrollbar {
    width: 3px;
  }

  .detail-flat-content::-webkit-scrollbar-thumb,
  .detail-tabs-body::-webkit-scrollbar-thumb {
    background: hsl(var(--muted-foreground) / 20%);
  }

  .detail-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .detail-header-right {
    align-self: flex-end;
  }

  .detail-time-section {
    gap: 16px;
  }

  .detail-tabs-nav {
    padding: 0;
    overflow-x: auto;
  }

  .detail-flat-content,
  .detail-tab-pane {
    padding: 0;
  }
}

/* 头部样式 */
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 24px 16px;
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

.detail-time-section {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
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

.detail-close-btn:focus-visible {
  outline: 2px solid hsl(var(--destructive) / 36%);
  outline-offset: 2px;
}

.detail-close-btn:active {
  transform: translateY(0);
}

/* 内容区域 */
.detail-content {
  position: relative;
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

/* 水印区域 - 固定在内容区域底部 */
.detail-watermark {
  position: absolute;
  bottom: 16px;
  left: 24px;
  z-index: 10;
  pointer-events: none;
}

.detail-flat-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0;
  overflow: hidden auto;
  scrollbar-color: hsl(var(--muted-foreground) / 30%) transparent;

  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  background: hsl(var(--popover));

  /* 平滑滚动 */
  scroll-behavior: smooth;

  /* iOS弹性滚动 */
  -webkit-overflow-scrolling: touch;
}

/* WebKit浏览器滚动条样式 */
.detail-flat-content::-webkit-scrollbar {
  width: 6px;
}

.detail-flat-content::-webkit-scrollbar-track {
  background: transparent;
}

.detail-flat-content::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 30%);
  border-radius: 999px;
  transition: background 0.2s ease;
}

.detail-flat-content::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 50%);
}

.detail-tabs-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

/* Tab导航 */
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

/* Tab内容 */
.detail-tabs-body {
  flex: 1;
  overflow: hidden auto;
  scrollbar-color: hsl(var(--muted-foreground) / 30%) transparent;

  /* 自定义滚动条样式 */
  scrollbar-width: thin;

  /* 平滑滚动 */
  scroll-behavior: smooth;

  /* iOS弹性滚动 */
  -webkit-overflow-scrolling: touch;
}

/* WebKit浏览器滚动条样式 - Tab内容 */
.detail-tabs-body::-webkit-scrollbar {
  width: 6px;
}

.detail-tabs-body::-webkit-scrollbar-track {
  background: transparent;
}

.detail-tabs-body::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 30%);
  border-radius: 999px;
  transition: background 0.2s ease;
}

.detail-tabs-body::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 50%);
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
