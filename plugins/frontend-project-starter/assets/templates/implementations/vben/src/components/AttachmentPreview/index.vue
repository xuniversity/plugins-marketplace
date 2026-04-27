<script setup lang="ts">
import { computed, ref } from 'vue';

import MediaPreview from '#/components/MediaPreview/index.vue';
import {
  MdiFileDocumentOutline,
  MdiFilePdfBox,
  MdiFileVideoOutline,
  VscodeIconsFileTypeExcel,
  VscodeIconsFileTypePowerpoint,
  VscodeIconsFileTypeWord,
} from '#/icons';

interface AttachmentItem {
  filename: string;
  path: string;
  url: string;
  type: string;
  size: number | string;
}

interface Props {
  attachments: AttachmentItem[];
  maxDisplay?: number;
}

const props = withDefaults(defineProps<Props>(), {
  maxDisplay: 4,
});

// 判断文件类型
const isImage = (fileType: string) => {
  return fileType.startsWith('image/');
};

const isVideo = (fileType: string) => {
  return fileType.startsWith('video/');
};

const isPreviewableMedia = (fileType: string) => {
  return isImage(fileType) || isVideo(fileType);
};

const isPdf = (fileType: string) => {
  return fileType === 'application/pdf';
};

// 获取文件图标组件
const getFileIconComponent = (fileType: string) => {
  if (isPdf(fileType)) {
    return MdiFilePdfBox;
  }
  if (isVideo(fileType)) {
    return MdiFileVideoOutline;
  }
  if (fileType.includes('word') || fileType.includes('document')) {
    return VscodeIconsFileTypeWord;
  }
  if (fileType.includes('excel') || fileType.includes('spreadsheet')) {
    return VscodeIconsFileTypeExcel;
  }
  if (fileType.includes('powerpoint') || fileType.includes('presentation')) {
    return VscodeIconsFileTypePowerpoint;
  }
  return MdiFileDocumentOutline;
};

// 格式化文件大小
const formatFileSize = (size: number | string) => {
  const sizeNum = typeof size === 'string' ? Number.parseInt(size, 10) : size;
  if (sizeNum < 1024) {
    return `${sizeNum}B`;
  }
  if (sizeNum < 1024 * 1024) {
    return `${(sizeNum / 1024).toFixed(1)}KB`;
  }
  if (sizeNum < 1024 * 1024 * 1024) {
    return `${(sizeNum / (1024 * 1024)).toFixed(1)}MB`;
  }
  return `${(sizeNum / (1024 * 1024 * 1024)).toFixed(1)}GB`;
};

// 显示的附件列表
const displayAttachments = computed(() => {
  return props.attachments.slice(0, props.maxDisplay);
});

// 是否有更多附件
const hasMore = computed(() => {
  return props.attachments.length > props.maxDisplay;
});

// 剩余附件数量
const remainingCount = computed(() => {
  return props.attachments.length - props.maxDisplay;
});

// MediaPreview 相关状态
const mediaPreviewVisible = ref(false);
const mediaItems = ref<
  Array<{
    name: string;
    type: 'audio' | 'image' | 'video';
    url: string;
  }>
>([]);
const currentMediaIndex = ref(0);

// 处理附件点击
const handleAttachmentClick = (attachment: AttachmentItem) => {
  if (!attachment.url) return;

  if (isPreviewableMedia(attachment.type)) {
    const previewableItems = props.attachments
      .filter((item) => isPreviewableMedia(item.type))
      .map((item) => ({
        name: item.filename,
        type: isVideo(item.type) ? ('video' as const) : ('image' as const),
        url: item.url,
      }));

    mediaItems.value = previewableItems;
    const mediaIndex = previewableItems.findIndex(
      (item) => item.url === attachment.url,
    );
    currentMediaIndex.value = Math.max(mediaIndex, 0);
    mediaPreviewVisible.value = true;
  } else {
    // 非图片类型 - 直接在新窗口打开
    window.open(attachment.url, '_blank');
  }
};
</script>

<template>
  <div v-if="attachments.length > 0" class="attachment-preview">
    <div class="attachment-list">
      <div
        v-for="attachment in displayAttachments"
        :key="attachment.path"
        class="attachment-item"
        @click="handleAttachmentClick(attachment)"
      >
        <!-- 图片预览 -->
        <div v-if="isImage(attachment.type)" class="attachment-image">
          <img
            :alt="attachment.filename"
            :src="attachment.url"
            class="attachment-img"
            loading="lazy"
          />
          <div class="attachment-overlay">
            <div class="attachment-name">{{ attachment.filename }}</div>
            <div class="attachment-size">
              {{ formatFileSize(attachment.size) }}
            </div>
          </div>
        </div>

        <!-- 文件图标预览 -->
        <div v-else class="attachment-file">
          <div class="attachment-file-icon">
            <component
              :is="getFileIconComponent(attachment.type)"
              class="file-icon"
            />
          </div>
          <div class="attachment-file-info">
            <div :title="attachment.filename" class="attachment-file-name">
              {{ attachment.filename }}
            </div>
            <div class="attachment-file-size">
              {{ formatFileSize(attachment.size) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 更多附件提示 -->
      <div v-if="hasMore" class="attachment-more">
        <div class="more-indicator">
          <a-avatar :size="32" class="more-avatar">
            <template #icon>
              <span class="text-sm">+{{ remainingCount }}</span>
            </template>
          </a-avatar>
          <div class="more-text">更多附件</div>
        </div>
      </div>
    </div>

    <!-- 媒体预览组件 -->
    <MediaPreview
      v-model:visible="mediaPreviewVisible"
      :current="currentMediaIndex"
      :items="mediaItems"
    />
  </div>
</template>

<style scoped>
/* 响应式设计 */
@media (max-width: 768px) {
  .attachment-image {
    width: 100px;
    height: 100px;
  }

  .attachment-file {
    width: 100px;
    height: 100px;
  }

  .attachment-file-icon {
    height: 70px;
  }

  .file-icon {
    font-size: 65px !important;
  }
}

.attachment-preview {
  --attachment-surface: hsl(var(--card));
  --attachment-surface-muted: hsl(var(--muted) / 0.72);
  --attachment-surface-strong: hsl(var(--card) / 0.96);
  --attachment-border: hsl(var(--border));
  --attachment-text: hsl(var(--foreground));
  --attachment-text-soft: hsl(var(--muted-foreground));
  --attachment-shadow: 0 4px 12px hsl(var(--foreground) / 0.1);
  margin-top: 8px;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attachment-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.attachment-item:hover {
  box-shadow: var(--attachment-shadow);
  transform: translateY(-2px);
}

/* 图片预览样式 */
.attachment-image {
  position: relative;
  width: 120px;
  height: 120px;
  overflow: hidden;
  border: 1px solid var(--attachment-border);
  border-radius: var(--radius);
}

.attachment-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attachment-overlay {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 6px 8px;
  font-size: 11px;
  line-height: 1.3;
  color: hsl(var(--primary-foreground));
  background: linear-gradient(transparent, hsl(var(--overlay)));
}

.attachment-name {
  overflow: hidden;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  opacity: 0.8;
}

/* 文件预览样式 */
.attachment-file {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  padding: 0;
  overflow: hidden;
  text-align: center;
  background: var(--attachment-surface-muted);
  border: 1px solid var(--attachment-border);
  border-radius: var(--radius);
}

.attachment-file-icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 80px;
}

.file-icon {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  height: 100% !important;
  font-size: 80px !important;
  color: hsl(var(--primary)) !important;
}

.attachment-file-info {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 8px 6px 6px;
  background: linear-gradient(transparent, var(--attachment-surface-strong));
}

.attachment-file-name {
  margin-bottom: 2px;
  overflow: hidden;
  font-size: 10px;
  font-weight: 500;
  line-height: 1.2;
  color: var(--attachment-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-file-size {
  font-size: 9px;
  color: var(--attachment-text-soft);
}

/* 更多附件样式 */
.attachment-more {
  display: flex;
  align-items: center;
  justify-content: center;
}

.more-indicator {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.more-avatar {
  width: 40px !important;
  height: 40px !important;
  color: var(--attachment-text-soft) !important;
  background-color: hsl(var(--muted)) !important;
}

.more-text {
  font-size: 11px;
  color: var(--attachment-text-soft);
}
</style>
