export { default as MediaPreview } from './index.vue';

export interface MediaItem {
  url: string;
  name: string;
  type: 'audio' | 'image' | 'video';
}

export interface MediaPreviewProps {
  visible: boolean;
  items: MediaItem[];
  current?: number;
}
