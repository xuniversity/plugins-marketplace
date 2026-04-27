export { default as AttachmentPreview } from './index.vue';

export interface AttachmentItem {
  filename: string;
  path: string;
  url: string;
  type: string;
  size: number | string;
}

export interface AttachmentPreviewProps {
  attachments: AttachmentItem[];
  maxDisplay?: number;
}
