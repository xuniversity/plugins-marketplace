<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  shallowRef,
  watch,
} from 'vue';

import { message } from 'ant-design-vue';
import Quill from 'quill';

import { uploadFile as uploadFileApi } from '#/api/core/file';

import 'quill/dist/quill.snow.css';

export interface RichEditorProps {
  modelValue?: string;
  placeholder?: string;
  height?: number | string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<RichEditorProps>(), {
  modelValue: '',
  placeholder: '请输入内容...',
  height: 300,
  disabled: false,
});

const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void;
}>();

const editorRef = ref<HTMLDivElement | null>(null);
const quillInstance = shallowRef<null | Quill>(null);
const isInternalChange = ref(false);
const rawImageSizeLimit = 15 * 1024 * 1024;
const normalizedUploadSizeLimit = 5 * 1024 * 1024;
const maxImageDimension = 1920;
const optimizableImageTypes = new Set([
  'image/bmp',
  'image/jpeg',
  'image/png',
  'image/webp',
]);

const editorHeight = computed(() => {
  const h = props.height;
  return typeof h === 'number' ? `${h}px` : h;
});

const shouldOptimizeImage = (file: File) => {
  return optimizableImageTypes.has(file.type);
};

const buildOptimizedFilename = (originalName: string, mimeType: string) => {
  const baseName = originalName.replace(/\.[^./\\]+$/, '') || 'image';
  const extensionMap: Record<string, string> = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
  };
  const extension = extensionMap[mimeType] || 'jpg';
  return `${baseName}.${extension}`;
};

const canvasToBlob = (
  canvas: HTMLCanvasElement,
  mimeType: string,
  quality: number,
) => {
  return new Promise<Blob | null>((resolve) => {
    canvas.toBlob(resolve, mimeType, quality);
  });
};

const loadImageForOptimization = (file: File) => {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const imageUrl = URL.createObjectURL(file);
    const image = new Image();
    image.decoding = 'async';

    const handleLoad = () => {
      URL.revokeObjectURL(imageUrl);
      resolve(image);
    };

    const handleError = () => {
      URL.revokeObjectURL(imageUrl);
      reject(new Error('图片解码失败'));
    };

    image.addEventListener('load', handleLoad, { once: true });
    image.addEventListener('error', handleError, { once: true });
    image.src = imageUrl;
  });
};

const optimizeImageForUpload = async (file: File) => {
  if (!shouldOptimizeImage(file)) {
    return file;
  }

  const image = await loadImageForOptimization(file);
  const longestSide = Math.max(image.naturalWidth, image.naturalHeight);
  const scale =
    longestSide > maxImageDimension ? maxImageDimension / longestSide : 1;
  const targetWidth = Math.max(1, Math.round(image.naturalWidth * scale));
  const targetHeight = Math.max(1, Math.round(image.naturalHeight * scale));
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  if (!context) {
    return file;
  }

  canvas.width = targetWidth;
  canvas.height = targetHeight;
  context.imageSmoothingEnabled = true;
  context.imageSmoothingQuality = 'high';
  context.drawImage(image, 0, 0, targetWidth, targetHeight);

  const preferredMimeType = 'image/webp';
  let quality = file.type === 'image/png' ? 0.92 : 0.84;
  let optimizedBlob = await canvasToBlob(canvas, preferredMimeType, quality);

  while (
    optimizedBlob &&
    optimizedBlob.size > normalizedUploadSizeLimit &&
    quality > 0.6
  ) {
    quality = Number((quality - 0.08).toFixed(2));
    optimizedBlob = await canvasToBlob(canvas, preferredMimeType, quality);
  }

  if (!optimizedBlob) {
    return file;
  }

  const optimizedMimeType = optimizedBlob.type || preferredMimeType;
  const optimizedFile = new File(
    [optimizedBlob],
    buildOptimizedFilename(file.name, optimizedMimeType),
    {
      lastModified: file.lastModified,
      type: optimizedMimeType,
    },
  );

  return scale < 1 || optimizedFile.size < file.size ? optimizedFile : file;
};

// 上传图片并插入到编辑器的通用函数
const uploadAndInsertImage = async (file: File, insertIndex: number) => {
  if (file.size > rawImageSizeLimit) {
    message.error('图片大小不能超过 15MB');
    return;
  }

  let hideLoading: (() => void) | undefined;
  try {
    hideLoading = message.loading('图片处理中...', 0);
    const uploadFile = await optimizeImageForUpload(file);

    if (uploadFile.size > normalizedUploadSizeLimit) {
      message.error('图片压缩后仍超过 5MB，请先缩小尺寸后再上传');
      return;
    }

    const formData = new FormData();
    formData.append('file', uploadFile);
    const result = await uploadFileApi(formData);

    if (quillInstance.value) {
      try {
        quillInstance.value.insertEmbed(
          insertIndex,
          'image',
          (result as any).url,
        );
        quillInstance.value.setSelection(insertIndex + 1, 0);
        message.success('图片上传成功');
      } catch (error) {
        console.error('Failed to insert image:', error);
        message.error('图片插入失败，请重试');
      }
    } else {
      message.error('编辑器未就绪，无法插入图片');
    }
  } catch (error) {
    message.error('图片上传失败，请重试');
    console.error('图片上传失败:', error);
  } finally {
    hideLoading?.();
  }
};

// 获取当前插入位置
const getInsertIndex = (): number => {
  if (!quillInstance.value) return 0;

  try {
    const length = quillInstance.value.getLength();
    if (length > 1) {
      try {
        const selection = quillInstance.value.getSelection(true);
        return selection && typeof selection.index === 'number'
          ? Math.max(0, Math.min(selection.index, length - 1))
          : length - 1;
      } catch {
        return length - 1;
      }
    }
    return 0;
  } catch {
    return 0;
  }
};

// 自定义图片处理器（工具栏点击上传）
const imageHandler = async () => {
  if (!quillInstance.value) return;

  // 在打开文件选择对话框之前保存选择范围
  const insertIndex = getInsertIndex();

  const input = document.createElement('input');
  input.setAttribute('type', 'file');
  input.setAttribute('accept', 'image/*');
  input.click();

  input.addEventListener('change', async () => {
    const file = input.files?.[0];
    if (!file) return;
    await uploadAndInsertImage(file, insertIndex);
  });
};

// 处理粘贴事件（在捕获阶段拦截，阻止 Quill 默认的 Base64 处理）
const handlePaste = (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items || !quillInstance.value) return;

  // 检查是否有图片文件
  let imageFile: File | null = null;
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      imageFile = item.getAsFile();
      break;
    }
  }

  if (imageFile) {
    // 完全阻止事件传播，防止 Quill 处理
    e.preventDefault();
    e.stopImmediatePropagation();

    // 获取插入位置并上传图片
    const insertIndex = getInsertIndex();
    uploadAndInsertImage(imageFile, insertIndex);
  }
};

// 处理拖拽事件（拦截拖拽的图片文件）
const handleDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files;
  if (!files || files.length === 0 || !quillInstance.value) return;

  // 检查是否有图片文件
  const imageFile = [...files].find((file) => file.type.startsWith('image/'));

  if (imageFile) {
    // 阻止默认行为，防止 Quill 处理
    e.preventDefault();
    e.stopImmediatePropagation();

    // 获取插入位置并上传图片
    const insertIndex = getInsertIndex();
    uploadAndInsertImage(imageFile, insertIndex);
  }
};

// 阻止 dragover 默认行为（允许 drop）
const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
};

onMounted(() => {
  if (!editorRef.value) return;

  const options: any = {
    theme: 'snow',
    placeholder: props.placeholder,
    readOnly: props.disabled,
    modules: {
      toolbar: {
        container: [
          [{ header: [1, 2, 3, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ color: [] }, { background: [] }],
          [{ list: 'ordered' }, { list: 'bullet' }],
          [{ align: [] }],
          ['blockquote', 'code-block'],
          ['link', 'image'],
          ['clean'],
        ],
        handlers: {
          image: imageHandler,
        },
      },
    },
  };

  quillInstance.value = new Quill(editorRef.value, options);

  // 初始化内容
  if (props.modelValue) {
    quillInstance.value.clipboard.dangerouslyPasteHTML(props.modelValue);
  }

  // 监听内容变化
  quillInstance.value.on('text-change', () => {
    if (!editorRef.value) return;
    const html = editorRef.value.querySelector('.ql-editor')?.innerHTML || '';
    // 如果内容只有空段落，则返回空字符串
    const cleanHtml = html === '<p><br></p>' ? '' : html;
    isInternalChange.value = true;
    emit('update:modelValue', cleanHtml);
    isInternalChange.value = false;
  });

  // 在捕获阶段监听粘贴事件，在 Quill 处理之前拦截图片
  editorRef.value.addEventListener('paste', handlePaste, true);

  // 在捕获阶段监听拖拽事件
  editorRef.value.addEventListener('drop', handleDrop, true);
  editorRef.value.addEventListener('dragover', handleDragOver, true);
});

onBeforeUnmount(() => {
  // 移除事件监听器
  if (editorRef.value) {
    editorRef.value.removeEventListener('paste', handlePaste, true);
    editorRef.value.removeEventListener('drop', handleDrop, true);
    editorRef.value.removeEventListener('dragover', handleDragOver, true);
  }
  if (quillInstance.value) {
    quillInstance.value = null;
  }
});

// 外部变更时同步内容
watch(
  () => props.modelValue,
  (newVal) => {
    if (isInternalChange.value) return;
    if (!quillInstance.value || !editorRef.value) return;

    const currentHtml =
      editorRef.value.querySelector('.ql-editor')?.innerHTML || '';
    const cleanCurrentHtml = currentHtml === '<p><br></p>' ? '' : currentHtml;

    if (newVal !== cleanCurrentHtml) {
      quillInstance.value.clipboard.dangerouslyPasteHTML(newVal || '');
    }
  },
);

// 监听禁用状态变化
watch(
  () => props.disabled,
  (newVal) => {
    if (quillInstance.value) {
      quillInstance.value.enable(!newVal);
    }
  },
);
</script>

<template>
  <div :class="{ 'rich-editor--disabled': disabled }" class="rich-editor">
    <div
      ref="editorRef"
      :style="{ height: editorHeight }"
      class="editor-container"
    ></div>
  </div>
</template>

<style scoped>
.rich-editor {
  --rich-editor-shell-radius: var(--radius);
  --rich-editor-callout-radius: calc(var(--radius) + 6px);
  --rich-editor-media-radius: calc(var(--radius) + 8px);
  --rich-editor-media-shadow:
    0 10px 24px hsl(var(--overlay)), 0 2px 6px hsl(var(--foreground) / 0.08);
  overflow: hidden;
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  border-radius: var(--rich-editor-shell-radius);
  transition: border-color 0.3s;
}

.rich-editor:hover:not(.rich-editor--disabled) {
  border-color: hsl(var(--primary));
}

.rich-editor:focus-within:not(.rich-editor--disabled) {
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 2px hsl(var(--primary) / 10%);
}

.rich-editor--disabled {
  cursor: not-allowed;
  background-color: hsl(var(--muted) / 50%);
}

.editor-container {
  min-height: 200px;
}

/* Quill 样式覆盖 */
.rich-editor :deep(.ql-toolbar.ql-snow) {
  background-color: hsl(var(--muted) / 30%);
  border: none;
  border-bottom: 1px solid hsl(var(--border));
}

.rich-editor :deep(.ql-container.ql-snow) {
  font-size: 14px;
  border: none;
}

.rich-editor :deep(.ql-editor) {
  min-height: 180px;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.85;
  color: hsl(var(--foreground));
  font-kerning: normal;
}

.rich-editor :deep(.ql-editor p) {
  margin-bottom: 0.95em;
}

.rich-editor :deep(.ql-editor h1),
.rich-editor :deep(.ql-editor h2),
.rich-editor :deep(.ql-editor h3) {
  margin: 1.4em 0 0.7em;
  font-family: 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', serif;
  font-weight: 600;
  line-height: 1.4;
}

.rich-editor :deep(.ql-editor h1) {
  font-size: 1.7rem;
}

.rich-editor :deep(.ql-editor h2) {
  font-size: 1.4rem;
}

.rich-editor :deep(.ql-editor h3) {
  font-size: 1.15rem;
}

.rich-editor :deep(.ql-editor blockquote) {
  padding: 12px 16px;
  color: hsl(var(--muted-foreground));
  background: hsl(var(--muted) / 35%);
  border-left: 3px solid hsl(var(--primary) / 35%);
  border-radius: var(--rich-editor-callout-radius);
}

.rich-editor :deep(.ql-editor img) {
  max-width: min(100%, 720px);
  height: auto;
  background: hsl(var(--popover));
  border: 1px solid hsl(var(--border) / 70%);
  border-radius: var(--rich-editor-media-radius);
  box-shadow: var(--rich-editor-media-shadow);
  vertical-align: top;
}

.rich-editor :deep(.ql-editor.ql-blank::before) {
  left: 16px;
  font-style: normal;
  color: hsl(var(--muted-foreground));
}

/* 禁用状态样式 */
.rich-editor--disabled :deep(.ql-toolbar) {
  pointer-events: none;
  opacity: 0.6;
}

.rich-editor--disabled :deep(.ql-editor) {
  cursor: not-allowed;
  background-color: hsl(var(--muted) / 50%);
}
</style>
