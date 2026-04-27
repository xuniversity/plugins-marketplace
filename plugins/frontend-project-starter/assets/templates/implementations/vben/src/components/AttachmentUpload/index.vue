<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import { message } from 'ant-design-vue';

import { getFileInfoApi, uploadFile } from '#/api/core/file';
import MediaPreview from '#/components/MediaPreview/index.vue';
import {
  MdiDelete,
  MdiEye,
  MdiFileDocumentOutline,
  MdiFilePdfBox,
  MdiFileVideoOutline,
  VscodeIconsFileTypeExcel,
  VscodeIconsFileTypePowerpoint,
  VscodeIconsFileTypeWord,
} from '#/icons';

interface Props {
  modelValue?: string[]; // v-model 绑定的文件URL数组
  maxCount?: number; // 最大文件数量
  maxSize?: number; // 单个文件最大大小（字节）
  accept?: string; // 接受的文件类型
  disabled?: boolean; // 是否禁用
  draggable?: boolean; // 是否启用拖拽上传
  tip?: string; // 自定义提示文案
  preserveAspectRatio?: boolean; // 是否保持图片宽高比自适应
  maxPreviewSize?: number; // 预览最大尺寸（像素）
  previewWidth?: number; // 预览容器宽度（像素）
  previewHeight?: number; // 预览容器高度（像素）
}

interface Emits {
  (e: 'update:modelValue', urls: string[]): void;
  (e: 'change', urls: string[]): void;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  maxCount: 9,
  maxSize: 20 * 1024 * 1024, // 20MB
  accept:
    'image/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip,.rar,.7z',
  disabled: false,
  draggable: false,
  tip: '',
  preserveAspectRatio: false,
  maxPreviewSize: 200,
  previewWidth: 200,
  previewHeight: 60,
});

const emit = defineEmits<Emits>();

// 内部文件列表（包含URL和文件信息）
interface FileItem {
  url: string;
  name: string;
  type: string;
  size?: number;
  uploading?: boolean; // 上传中状态
  tempId?: string; // 临时ID，用于上传中的占位项
}

const fileList = ref<FileItem[]>([]);
const uploadLoading = computed(() => fileList.value.some((f) => !!f.uploading));
let existingFileResolveSerial = 0;

// 预览相关状态（使用 MediaPreview 组件）
const previewVisible = ref(false);
const previewItems = ref<
  Array<{ name: string; type: 'audio' | 'image' | 'video'; url: string }>
>([]);
const previewIndex = ref(0);

// 拖拽相关状态
const isDragging = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const isHovering = ref(false);

// 根据文件扩展名获取文件类型
const getFileTypeFromExt = (ext: string): string => {
  const normalizedExt = ext.toLowerCase();
  // 图片类型
  if (
    ['bmp', 'gif', 'jpeg', 'jpg', 'png', 'svg', 'webp'].includes(normalizedExt)
  ) {
    return 'image';
  }

  // PDF
  if (normalizedExt === 'pdf') {
    return 'application/pdf';
  }

  // Word
  if (['doc', 'docx'].includes(normalizedExt)) {
    return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
  }

  // Excel
  if (['csv', 'xls', 'xlsx'].includes(normalizedExt)) {
    return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  }

  // PowerPoint
  if (['ppt', 'pptx'].includes(normalizedExt)) {
    return 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
  }

  // 视频
  if (normalizedExt === 'mp4') {
    return 'video/mp4';
  }
  if (normalizedExt === 'mov') {
    return 'video/quicktime';
  }
  if (normalizedExt === 'avi') {
    return 'video/x-msvideo';
  }
  if (normalizedExt === 'mkv') {
    return 'video/x-matroska';
  }

  // 压缩文件
  if (['7z', 'gz', 'rar', 'tar', 'zip'].includes(normalizedExt)) {
    return 'application/zip';
  }

  return 'document';
};

const resolveFileType = (file: File): string => {
  if (file.type?.startsWith('image/')) {
    return 'image';
  }
  if (file.type) {
    return file.type;
  }
  const ext = file.name.split('.').pop() || '';
  return getFileTypeFromExt(ext);
};

// 根据URL获取文件类型
const getFileTypeFromUrl = (url: string): string => {
  const ext = url.toLowerCase().split('.').pop() || '';
  return getFileTypeFromExt(ext);
};

// 从URL初始化文件列表
const buildFallbackFileItem = (url: string): FileItem => {
  const fileName = url.split('/').pop() || url;
  return {
    url,
    name: fileName,
    type: getFileTypeFromUrl(url),
  };
};

watch(
  () => props.modelValue,
  async (newUrls) => {
    const urls = newUrls || [];
    const resolveId = ++existingFileResolveSerial;

    if (urls.length === 0) {
      fileList.value = [];
      return;
    }

    const resolvedItems = await Promise.all(
      urls.map(async (url) => {
        try {
          const fileInfo = await getFileInfoApi(url);
          return {
            url,
            name: fileInfo.filename || url.split('/').pop() || url,
            type: fileInfo.contentType || getFileTypeFromUrl(url),
            size: fileInfo.size,
          } satisfies FileItem;
        } catch (error) {
          console.warn('获取附件信息失败，回退到URL文件名:', error);
          return buildFallbackFileItem(url);
        }
      }),
    );

    if (resolveId !== existingFileResolveSerial) {
      return;
    }
    fileList.value = resolvedItems;
  },
  { immediate: true },
);

// 判断是否为图片
const isImage = (type: string) => {
  return type === 'image' || type.startsWith('image/');
};

const isVideo = (type: string) => {
  return type.startsWith('video/');
};

const isPreviewableMedia = (type: string) => {
  return isImage(type) || isVideo(type);
};

// 获取文件图标组件
const getFileIconComponent = (type: string) => {
  if (type === 'application/pdf') {
    return MdiFilePdfBox;
  }
  if (isVideo(type)) {
    return MdiFileVideoOutline;
  }
  if (type.includes('word') || type.includes('document')) {
    return VscodeIconsFileTypeWord;
  }
  if (type.includes('excel') || type.includes('spreadsheet')) {
    return VscodeIconsFileTypeExcel;
  }
  if (type.includes('powerpoint') || type.includes('presentation')) {
    return VscodeIconsFileTypePowerpoint;
  }
  return MdiFileDocumentOutline;
};

// 格式化文件大小
const formatFileSize = (size?: number): string => {
  if (!size) return '';
  if (size < 1024) return `${size}B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)}KB`;
  return `${(size / (1024 * 1024)).toFixed(1)}MB`;
};

// 可上传数量
const canUploadCount = computed(() => {
  return Math.max(0, props.maxCount - fileList.value.length);
});

// 获取容器尺寸
const getContainerSize = (
  file: FileItem,
): { height: string; width: string } => {
  if (props.preserveAspectRatio && isImage(file.type)) {
    return {
      width: `${props.previewWidth}px`,
      height: `${props.previewHeight}px`,
    };
  }
  return { width: '96px', height: '96px' };
};

// 根据 accept 生成格式提示文本
const formatHintText = computed(() => {
  const acceptTypes = props.accept.split(',').map((type) => type.trim());
  const formatNames: string[] = [];

  for (const type of acceptTypes) {
    if (type === 'image/*') {
      formatNames.push('图片');
    } else if (type === 'video/*') {
      continue;
    } else if (type === '.pdf' || type.includes('pdf')) {
      formatNames.push('PDF');
    } else if (type === '.doc' || type === '.docx' || type.includes('word')) {
      formatNames.push('Word');
    } else if (
      type === '.xls' ||
      type === '.xlsx' ||
      type.includes('excel') ||
      type.includes('spreadsheet')
    ) {
      formatNames.push('Excel');
    } else if (
      type === '.ppt' ||
      type === '.pptx' ||
      type.includes('powerpoint') ||
      type.includes('presentation')
    ) {
      formatNames.push('PPT');
    } else if (type === '.txt') {
      formatNames.push('TXT');
    } else if (type === '.csv') {
      formatNames.push('CSV');
    } else if (
      type === '.zip' ||
      type === '.rar' ||
      type === '.7z' ||
      type.includes('zip')
    ) {
      formatNames.push('压缩文件');
    } else if (['.avi', '.mkv', '.mov', '.mp4'].includes(type)) {
      formatNames.push(type.replace('.', '').toUpperCase());
    }
  }

  // 去重
  const uniqueFormats = [...new Set(formatNames)];

  if (uniqueFormats.length === 0) {
    return '支持多种格式';
  } else if (uniqueFormats.length === 1) {
    return `支持${uniqueFormats[0]}格式`;
  } else {
    return `支持${uniqueFormats.join('、')}等格式`;
  }
});

// 更新 v-model（过滤掉正在上传的文件）
const updateModelValue = () => {
  const urls = fileList.value
    .filter((file) => !file.uploading && file.url)
    .map((file) => file.url);
  emit('update:modelValue', urls);
  emit('change', urls);
};

const isValidFileType = (file: File) => {
  const acceptTypes = props.accept.split(',').map((type) => type.trim());
  const fileName = file.name.toLowerCase();
  const fileExtension = `.${fileName.split('.').pop() || ''}`;

  for (const type of acceptTypes) {
    if (type.startsWith('.')) {
      if (fileExtension === type.toLowerCase()) return true;
      continue;
    }
    if (type.includes('*')) {
      const mimePrefix = type.split('/')[0] || '';
      if (mimePrefix && file.type.startsWith(mimePrefix)) return true;
      continue;
    }
    if (file.type === type) return true;
  }

  return false;
};

// 文件上传前验证（a-upload 回调）
const beforeUpload = (file: File, fileListArray: File[]) => {
  if (!isValidFileType(file)) {
    message.error('不支持该文件类型！');
    return false;
  }

  if (file.size > props.maxSize) {
    message.error(
      `文件大小不能超过 ${Math.round(props.maxSize / 1024 / 1024)}MB！`,
    );
    return false;
  }

  const totalCount = fileList.value.length + fileListArray.length;
  if (totalCount > props.maxCount) {
    message.error(
      `最多上传${props.maxCount}个文件，当前已有${fileList.value.length}个，本次选择${fileListArray.length}个，超出限制！`,
    );
    return false;
  }

  handleUpload(file);
  return false; // 阻止自动上传
};

// 处理文件上传
const handleUpload = async (file: File) => {
  // 生成临时ID
  const tempId = `temp_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
  const fileType = resolveFileType(file);

  // 先添加占位项（带上传中状态）
  const placeholderFile: FileItem = {
    url: '', // 上传中时没有URL
    name: file.name,
    type: fileType,
    size: file.size,
    uploading: true,
    tempId,
  };
  fileList.value.push(placeholderFile);

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await uploadFile(formData);

    // 上传成功，更新占位项
    const index = fileList.value.findIndex((f) => f.tempId === tempId);
    if (index !== -1) {
      fileList.value[index] = {
        url: response.url,
        name: file.name,
        type: fileType,
        size: file.size,
        uploading: false,
      };
    }

    // 更新 v-model
    updateModelValue();

    message.success('上传成功');
  } catch (error) {
    console.error('上传失败', error);
    message.error('上传失败');
    // 上传失败，移除占位项
    const index = fileList.value.findIndex((f) => f.tempId === tempId);
    if (index !== -1) {
      fileList.value.splice(index, 1);
    }
  }
};

// 删除附件
const handleRemoveAttachment = (index: number) => {
  fileList.value.splice(index, 1);
  updateModelValue();
};

// 处理附件点击（预览）
const handleAttachmentClick = (file: FileItem) => {
  if (!file.url || file.uploading) return;

  if (isPreviewableMedia(file.type)) {
    const mediaFiles = fileList.value
      .filter(
        (item) =>
          !!item.url && !item.uploading && isPreviewableMedia(item.type),
      )
      .map((item) => ({
        name: item.name,
        type: isVideo(item.type) ? ('video' as const) : ('image' as const),
        url: item.url,
      }));

    previewItems.value = mediaFiles;
    const index = mediaFiles.findIndex((item) => item.url === file.url);
    previewIndex.value = Math.max(index, 0);
    previewVisible.value = true;
  } else {
    // 非图片类型 - 直接在新窗口打开
    window.open(file.url, '_blank');
  }
};

// 处理拖拽进入
const handleDragEnter = (e: DragEvent) => {
  if (props.disabled || !props.draggable) return;
  e.preventDefault();
  e.stopPropagation();
  isDragging.value = true;
};

// 处理拖拽经过
const handleDragOver = (e: DragEvent) => {
  if (props.disabled || !props.draggable) return;
  e.preventDefault();
  e.stopPropagation();
};

// 处理拖拽离开
const handleDragLeave = (e: DragEvent) => {
  if (props.disabled || !props.draggable) return;
  e.preventDefault();
  e.stopPropagation();
  // 只有当离开整个拖拽区域时才设置为 false
  if (e.currentTarget === e.target) {
    isDragging.value = false;
  }
};

// 处理多个文件的上传
const handleMultipleFiles = async (files: File[]) => {
  // 验证文件数量
  const totalCount = fileList.value.length + files.length;
  if (totalCount > props.maxCount) {
    message.error(
      `最多上传${props.maxCount}个文件，当前已有${fileList.value.length}个，本次选择${files.length}个，超出限制！`,
    );
    return;
  }

  // 逐个验证并上传文件
  for (const file of files) {
    if (!isValidFileType(file)) {
      message.error(`文件 ${file.name} 类型不支持！`);
      continue;
    }

    // 验证文件大小
    if (file.size > props.maxSize) {
      message.error(
        `文件 ${file.name} 大小超过 ${Math.round(props.maxSize / 1024 / 1024)}MB 限制！`,
      );
      continue;
    }

    // 上传文件
    await handleUpload(file);
  }
};

// 处理文件放置
const handleDrop = async (e: DragEvent) => {
  if (props.disabled || !props.draggable) return;
  e.preventDefault();
  e.stopPropagation();
  isDragging.value = false;

  const files = [...(e.dataTransfer?.files || [])];
  if (files.length === 0) return;

  await handleMultipleFiles(files);
};

// 点击拖拽区域触发文件选择
const handleDragAreaClick = () => {
  if (props.disabled) return;
  fileInputRef.value?.click();
};

// 处理文件选择
const handleFileInputChange = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  const files = [...(target.files || [])];
  if (files.length === 0) return;

  await handleMultipleFiles(files);

  // 清空 input，以便可以重复选择相同文件
  target.value = '';
};

// 处理粘贴上传
const handlePaste = async (e: ClipboardEvent) => {
  if (props.disabled) return;

  const items = [...(e.clipboardData?.items || [])];
  if (items.length === 0) return;

  const files = items
    .map((item) => item.getAsFile())
    .filter((file): file is File => !!file)
    .map((file) => {
      // Some browsers may expose pasted blobs with a generic name like "blob".
      const name =
        file.name && file.name !== 'blob'
          ? file.name
          : `pasted-${Date.now()}.${file.type.includes('image') ? 'png' : 'bin'}`;
      return file.name === name
        ? file
        : new File([file], name, { type: file.type });
    });

  if (files.length === 0) return;

  e.preventDefault();
  e.stopPropagation();
  await handleMultipleFiles(files);
};

// Allow paste upload without explicitly focusing this component:
// if the user is hovering the upload area, handle the paste from document.
const handleDocumentPaste = (e: ClipboardEvent) => {
  if (!isHovering.value) return;
  void handlePaste(e);
};

onMounted(() => {
  document.addEventListener('paste', handleDocumentPaste);
});

onUnmounted(() => {
  document.removeEventListener('paste', handleDocumentPaste);
});
</script>

<template>
  <a-spin :spinning="uploadLoading" tip="正在上传文件...">
    <div
      class="attachment-upload"
      tabindex="0"
      @mouseenter="isHovering = true"
      @mouseleave="isHovering = false"
      @paste="handlePaste"
    >
      <!-- 拖拽提示区域 -->
      <div
        v-if="draggable"
        :class="{
          'drag-drop-area-active': isDragging,
          'drag-drop-area-disabled': disabled || uploadLoading,
        }"
        class="drag-drop-area"
        tabindex="0"
        @click="handleDragAreaClick"
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
        @dragover="handleDragOver"
        @drop="handleDrop"
        @keydown.enter.prevent="handleDragAreaClick"
        @keydown.space.prevent="handleDragAreaClick"
      >
        <input
          ref="fileInputRef"
          :accept="accept"
          :disabled="disabled || uploadLoading"
          multiple
          style="display: none"
          type="file"
          @change="handleFileInputChange"
        />
        <div class="drag-drop-content">
          <div class="drag-drop-icon">
            <svg
              fill="none"
              height="28"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              viewBox="0 0 24 24"
              width="28"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" x2="12" y1="3" y2="15" />
            </svg>
          </div>
          <div class="drag-drop-text">
            {{ isDragging ? '松开鼠标上传文件' : '拖拽文件到此处上传' }}
          </div>
          <div class="drag-drop-hint">或点击此处选择文件</div>
        </div>
      </div>

      <div class="flex flex-wrap gap-3">
        <!-- 已上传的文件 -->
        <div
          v-for="(file, index) in fileList"
          :key="file.tempId || file.url"
          :style="getContainerSize(file)"
          class="attachment-item"
        >
          <!-- 图片预览 -->
          <div
            v-if="isImage(file.type)"
            :class="{ 'preserve-ratio': preserveAspectRatio }"
            class="attachment-preview"
          >
            <img
              v-if="file.url"
              :src="file.url"
              alt="附件"
              class="attachment-image"
            />
            <!-- 上传中遮罩 -->
            <div v-if="file.uploading" class="uploading-overlay">
              <a-spin size="small" />
              <span class="uploading-text">上传中...</span>
            </div>
            <!-- 操作遮罩（非上传中时显示） -->
            <div v-else class="attachment-overlay">
              <div class="attachment-actions">
                <div
                  class="action-btn"
                  title="预览"
                  @click.stop="handleAttachmentClick(file)"
                >
                  <MdiEye class="text-xl" />
                </div>
                <div
                  class="action-btn action-btn-delete"
                  title="删除"
                  @click.stop="handleRemoveAttachment(index)"
                >
                  <MdiDelete class="text-xl" />
                </div>
              </div>
            </div>
          </div>

          <!-- 文件预览 -->
          <div v-else class="attachment-file">
            <div
              class="attachment-file-preview"
              @click="handleAttachmentClick(file)"
            >
              <div class="attachment-file-icon">
                <component :is="getFileIconComponent(file.type)" class="icon" />
              </div>
              <div class="attachment-file-info">
                <div :title="file.name" class="attachment-file-name">
                  {{ file.name }}
                </div>
                <div v-if="(file.size ?? 0) > 0" class="attachment-file-size">
                  {{ formatFileSize(file.size) }}
                </div>
              </div>
              <!-- 上传中遮罩 -->
              <div v-if="file.uploading" class="uploading-overlay">
                <a-spin size="small" />
                <span class="uploading-text">上传中...</span>
              </div>
            </div>
            <div
              v-if="!file.uploading"
              class="attachment-delete-btn"
              @click.stop="handleRemoveAttachment(index)"
            >
              <MdiDelete class="text-base" />
            </div>
          </div>
        </div>

        <!-- 上传区域（非拖拽模式沿用 a-upload，参考 PowerEI 实现） -->
        <a-upload
          v-if="canUploadCount > 0 && !disabled && !draggable"
          :accept="accept"
          :before-upload="beforeUpload"
          :disabled="uploadLoading"
          :show-upload-list="false"
          list-type="picture-card"
          multiple
        >
          <div class="upload-area">
            <a-spin :spinning="uploadLoading">
              <div class="upload-content">
                <div class="upload-icon">
                  <svg
                    fill="none"
                    height="32"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    viewBox="0 0 24 24"
                    width="32"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" x2="12" y1="3" y2="15" />
                  </svg>
                </div>
                <div class="upload-text">上传附件</div>
              </div>
            </a-spin>
          </div>
        </a-upload>
      </div>

      <!-- 提示信息 -->
      <div class="attachment-hint">
        <div v-if="tip">{{ tip }}</div>
        <div>
          已上传 {{ fileList.length }}/{{ maxCount }} 个文件，{{
            formatHintText
          }}，支持点击、拖拽{{ !disabled ? '、粘贴' : '' }}上传，单个文件最大{{
            Math.round(maxSize / 1024 / 1024)
          }}MB
        </div>
      </div>
    </div>
  </a-spin>

  <!-- 图片预览弹窗 -->
  <MediaPreview
    v-model:visible="previewVisible"
    :current="previewIndex"
    :items="previewItems"
  />
</template>

<style scoped>
.attachment-upload {
  --attachment-surface: hsl(var(--card));
  --attachment-surface-muted: hsl(var(--muted) / 0.7);
  --attachment-surface-soft: hsl(var(--accent) / 0.7);
  --attachment-border: hsl(var(--border));
  --attachment-border-strong: hsl(var(--primary) / 0.34);
  --attachment-text: hsl(var(--foreground));
  --attachment-text-soft: hsl(var(--muted-foreground));
  --attachment-overlay: hsl(var(--overlay));
  --attachment-shadow: 0 4px 12px hsl(var(--foreground) / 0.12);
  --attachment-shadow-soft: 0 4px 12px hsl(var(--foreground) / 0.1);
  --attachment-inverse: hsl(var(--primary-foreground));
  width: 100%;
}

.attachment-upload:focus-visible {
  outline: 2px solid hsl(var(--primary) / 40%);
  outline-offset: 3px;
  border-radius: var(--radius);
}

/* 拖拽区域样式 */
.drag-drop-area {
  width: 100%;
  min-height: 56px;
  padding: 12px 14px;
  margin-bottom: 12px;
  cursor: pointer;
  background: var(--attachment-surface-muted);
  border: 2px dashed var(--attachment-border);
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

.drag-drop-area:hover {
  background: var(--attachment-surface-soft);
  border-color: hsl(var(--primary));
}

.drag-drop-area-active {
  background: hsl(var(--primary) / 0.1);
  border-color: hsl(var(--primary));
  border-style: solid;
  box-shadow: 0 0 0 4px hsl(var(--primary) / 10%);
}

.drag-drop-area-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.drag-drop-area-disabled:hover {
  background: var(--attachment-surface-muted);
  border-color: var(--attachment-border);
}

.drag-drop-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10px;
}

.drag-drop-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
  color: var(--attachment-text-soft);
  transition: all 0.3s ease;
}

.drag-drop-area:hover .drag-drop-icon,
.drag-drop-area-active .drag-drop-icon {
  color: hsl(var(--primary));
  transform: translateY(-4px);
}

.drag-drop-text {
  margin-bottom: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--attachment-text);
}

.drag-drop-hint {
  font-size: 14px;
  color: var(--attachment-text-soft);
}

/* 附件项容器 */
.attachment-item {
  position: relative;
  flex-shrink: 0;
}

/* 图片预览样式 */
.attachment-preview {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--attachment-border);
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

.attachment-preview:hover {
  box-shadow: var(--attachment-shadow);
  transform: translateY(-2px);
}

/* 图片样式 */
.attachment-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attachment-preview.preserve-ratio .attachment-image {
  object-fit: contain;
}

/* 遮罩层 */
.attachment-overlay {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  background: var(--attachment-overlay);
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.attachment-preview:hover .attachment-overlay {
  pointer-events: auto;
  opacity: 1;
}

/* 操作按钮容器 */
.attachment-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: center;
}

/* 操作按钮 */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: var(--attachment-inverse);
  cursor: pointer;
  background: hsl(var(--primary-foreground) / 0.18);
  border: 1px solid hsl(var(--primary-foreground) / 0.24);
  border-radius: 50%;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: hsl(var(--primary-foreground) / 0.28);
  transform: scale(1.1);
}

.action-btn-delete:hover {
  background: hsl(var(--destructive) / 0.86);
  border-color: hsl(var(--destructive) / 0.92);
}

/* 上传中遮罩 */
.uploading-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
  background: hsl(var(--background) / 0.88);
  border-radius: inherit;
}

.uploading-text {
  font-size: 12px;
  color: var(--attachment-text-soft);
}

/* 文件预览样式 */
.attachment-file {
  position: relative;
  width: 100%;
  height: 100%;
}

.attachment-file-preview {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 8px;
  overflow: hidden;
  cursor: pointer;
  background: var(--attachment-surface-muted);
  border: 1px solid var(--attachment-border);
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

.attachment-file-preview:hover {
  background: var(--attachment-surface-soft);
  border-color: hsl(var(--primary));
  box-shadow: var(--attachment-shadow-soft);
  transform: translateY(-2px);
}

.attachment-file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 50px;
}

.icon {
  width: 48px !important;
  height: 48px !important;
  font-size: 48px !important;
}

.attachment-file-info {
  width: 100%;
  text-align: center;
}

.attachment-file-name {
  overflow: hidden;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.2;
  color: var(--attachment-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-file-size {
  margin-top: 2px;
  font-size: 10px;
  color: var(--attachment-text-soft);
}

/* 删除按钮 */
.attachment-delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--attachment-inverse);
  cursor: pointer;
  background: hsl(var(--destructive) / 0.92);
  border-radius: 50%;
  box-shadow: 0 4px 12px hsl(var(--destructive) / 0.28);
  opacity: 0;
  transition: all 0.3s ease;
}

.attachment-file:hover .attachment-delete-btn {
  opacity: 1;
}

.attachment-delete-btn:hover {
  background: hsl(var(--destructive));
  transform: scale(1.1);
}

/* 上传区域样式 */
.upload-area {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  cursor: pointer;
  background: var(--attachment-surface-muted);
  border: 1.5px dashed var(--attachment-border);
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

.upload-area:hover {
  background: var(--attachment-surface-soft);
  border-color: hsl(var(--primary));
}

.upload-area:hover .upload-icon {
  color: hsl(var(--primary));
  transform: translateY(-2px);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  color: var(--attachment-text-soft);
  transition: all 0.3s ease;
}

.upload-text {
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
  color: var(--attachment-text-soft);
}

.attachment-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  line-height: 1.6;
  color: var(--attachment-text-soft);
}

/* 移除 Ant Design Upload 组件的默认边框和样式 */
:deep(.ant-upload-wrapper.ant-upload-picture-card-wrapper) {
  display: inline-block;
  width: 96px;
  height: 96px;
}

:deep(
  .ant-upload-wrapper.ant-upload-picture-card-wrapper
    .ant-upload.ant-upload-select
) {
  width: 96px;
  height: 96px;
  padding: 0;
  margin: 0;
  background: transparent;
  border: none;
}

:deep(.ant-upload.ant-upload-select-picture-card) {
  width: 96px;
  height: 96px;
  padding: 0;
  margin: 0;
  background: transparent;
  border: none;
}
</style>
