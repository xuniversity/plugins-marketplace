<script lang="ts" setup>
import type { NoticeConfig } from './types';

import { computed, nextTick, ref, watch } from 'vue';

import { Button, Empty, Modal } from 'ant-design-vue';

const props = withDefaults(
  defineProps<{
    confirmLoading?: boolean;
    notice: NoticeConfig;
    open: boolean;
  }>(),
  {
    confirmLoading: false,
  },
);

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'confirm'): void;
  (e: 'update:open', value: boolean): void;
}>();

const modalOpen = computed({
  get: () => props.open,
  set: (value: boolean) => emit('update:open', value),
});

const SCROLL_BOTTOM_THRESHOLD = 8;

const noticeContentRef = ref<HTMLElement>();
const hasReadAll = ref(false);

const updateReadState = () => {
  const contentElement = noticeContentRef.value;

  if (!contentElement) {
    hasReadAll.value = false;
    return;
  }

  const { clientHeight, scrollHeight, scrollTop } = contentElement;

  hasReadAll.value =
    scrollHeight <= clientHeight ||
    scrollTop + clientHeight >= scrollHeight - SCROLL_BOTTOM_THRESHOLD;
};

const resetReadState = async () => {
  hasReadAll.value = false;
  await nextTick();

  const contentElement = noticeContentRef.value;

  if (!contentElement) {
    return;
  }

  contentElement.scrollTop = 0;
  updateReadState();
};

const handleContentScroll = () => {
  updateReadState();
};

const handleCancel = () => {
  emit('cancel');
  modalOpen.value = false;
};

const handleConfirm = () => {
  if (!hasReadAll.value) {
    return;
  }

  emit('confirm');
};

watch(
  () => props.open,
  (open) => {
    if (open) {
      void resetReadState();
      return;
    }

    hasReadAll.value = false;
  },
);
</script>

<template>
  <Modal
    v-model:open="modalOpen"
    :footer="null"
    :mask-closable="false"
    centered
    width="840px"
    @cancel="handleCancel"
  >
    <div class="notice-modal">
      <div class="notice-header">
        <h3 class="notice-title">{{ notice.title }}</h3>
        <p v-if="notice.description" class="notice-description">
          {{ notice.description }}
        </p>
      </div>

      <div
        ref="noticeContentRef"
        class="notice-content"
        @scroll="handleContentScroll"
      >
        <ol class="notice-list">
          <li v-for="item in notice.items" :key="item" class="notice-list-item">
            {{ item }}
          </li>
        </ol>

        <div v-if="notice.contactLines?.length" class="notice-section">
          <div class="notice-section-title">补充说明</div>
          <p
            v-for="line in notice.contactLines"
            :key="line"
            class="notice-contact-line"
          >
            {{ line }}
          </p>
        </div>

        <div
          v-if="notice.qrCodeUrl || notice.qrCodeTitle || notice.qrCodeCaption"
          class="notice-qrcode"
        >
          <img
            v-if="notice.qrCodeUrl"
            :alt="notice.qrCodeTitle || 'notice qr code'"
            :src="notice.qrCodeUrl"
            class="notice-qrcode-image"
            @error="updateReadState"
            @load="updateReadState"
          />
          <div v-else class="notice-qrcode-placeholder">服务群二维码</div>
          <div class="notice-qrcode-meta">
            <div class="notice-qrcode-title">
              {{ notice.qrCodeTitle || '服务群' }}
            </div>
            <div v-if="notice.qrCodeCaption" class="notice-qrcode-caption">
              {{ notice.qrCodeCaption }}
            </div>
          </div>
        </div>

        <Empty
          v-else-if="notice.items.length === 0 && !notice.description"
          description="暂无注意事项"
        />
      </div>

      <div class="notice-actions">
        <div class="notice-read-tip" :class="{ 'is-ready': hasReadAll }">
          {{
            hasReadAll
              ? '已完成阅读，可进入下一步'
              : '请先完整阅读并滚动至底部后再确认'
          }}
        </div>
        <Button size="large" @click="handleCancel">
          {{ notice.cancelText || '取消' }}
        </Button>
        <Button
          :disabled="!hasReadAll"
          :loading="confirmLoading"
          size="large"
          type="primary"
          @click="handleConfirm"
        >
          {{ notice.confirmText || '我已确认' }}
        </Button>
      </div>
    </div>
  </Modal>
</template>

<style scoped>
.notice-modal {
  --notice-surface: hsl(var(--card) / 0.98);
  --notice-surface-muted: hsl(var(--muted) / 0.74);
  --notice-border: hsl(var(--border) / 0.9);
  --notice-divider: hsl(var(--border) / 0.72);
  --notice-text: hsl(var(--foreground));
  --notice-text-soft: hsl(var(--muted-foreground));
  --notice-text-faint: hsl(var(--muted-foreground) / 0.92);
  --notice-shadow: 0 8px 24px hsl(var(--foreground) / 0.06);
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 12px;
}

.notice-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notice-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--notice-text);
}

.notice-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: var(--notice-text-soft);
}

.notice-content {
  max-height: 56vh;
  overflow-y: auto;
  padding: 20px 24px;
  border-radius: calc(var(--radius) + 8px);
  background: linear-gradient(
    180deg,
    hsl(var(--card) / 0.98) 0%,
    var(--notice-surface-muted) 100%
  );
  border: 1px solid var(--notice-border);
}

.notice-list {
  margin: 0;
  padding-left: 28px;
  list-style-type: decimal !important;
}

.notice-list-item {
  display: list-item;
  list-style-type: decimal !important;
  margin-bottom: 10px;
  padding-left: 6px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--notice-text);
  white-space: pre-line;
}

.notice-list-item::marker {
  font-weight: 600;
  color: var(--notice-text-soft);
}

.notice-list-item:last-child {
  margin-bottom: 0;
}

.notice-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed var(--notice-divider);
}

.notice-section-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: hsl(var(--primary));
}

.notice-contact-line {
  margin: 0 0 6px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--notice-text-soft);
}

.notice-contact-line:last-child {
  margin-bottom: 0;
}

.notice-qrcode {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 18px;
  margin-top: 20px;
  padding-top: 24px;
  border-top: 1px dashed var(--notice-divider);
}

.notice-qrcode-image {
  width: min(100%, 360px);
  max-width: 360px;
  height: auto;
  border-radius: calc(var(--radius) + 8px);
  object-fit: contain;
  border: 1px solid var(--notice-divider);
  background: hsl(var(--background));
  box-shadow: var(--notice-shadow);
}

.notice-qrcode-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: min(100%, 240px);
  min-height: 240px;
  padding: 12px;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.6;
  text-align: center;
  color: var(--notice-text-faint);
  border: 1px dashed hsl(var(--border));
  border-radius: calc(var(--radius) + 4px);
  background: hsl(var(--muted) / 0.45);
}

.notice-qrcode-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  text-align: center;
}

.notice-qrcode-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--notice-text);
}

.notice-qrcode-caption {
  font-size: 13px;
  line-height: 1.6;
  color: var(--notice-text-soft);
}

.notice-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.notice-read-tip {
  flex: 1;
  font-size: 13px;
  line-height: 1.6;
  color: var(--notice-text-faint);
}

.notice-read-tip.is-ready {
  color: hsl(var(--primary));
}

@media (max-width: 768px) {
  .notice-content {
    max-height: 50vh;
    padding: 16px;
  }

  .notice-qrcode {
    gap: 14px;
  }

  .notice-qrcode-image {
    width: min(100%, 280px);
  }

  .notice-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .notice-actions :deep(.ant-btn) {
    width: 100%;
  }

  .notice-read-tip {
    text-align: center;
  }
}
</style>
