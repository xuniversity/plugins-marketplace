export { default as AttachmentUpload } from './index.vue';

export interface AttachmentUploadProps {
  modelValue?: string[]; // v-model 绑定的文件URL数组
  maxCount?: number; // 最大文件数量
  maxSize?: number; // 单个文件最大大小（字节）
  accept?: string; // 接受的文件类型
  disabled?: boolean; // 是否禁用
  draggable?: boolean; // 是否启用拖拽上传
  tip?: string; // 自定义提示文案
  preserveAspectRatio?: boolean; // 是否保持图片宽高比自适应
  previewWidth?: number; // 预览容器宽度
  previewHeight?: number; // 预览容器高度
}
