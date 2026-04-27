import { message } from 'ant-design-vue';

/**
 * 复制文本到剪贴板
 *
 * @param text 要复制的文本
 * @param showMessage 是否显示提示消息，默认 true
 * @returns 是否复制成功
 *
 * @example
 * await copyToClipboard('Hello World');
 * await copyToClipboard('code_123', false); // 不显示提示
 */
export async function copyToClipboard(
  text: string,
  showMessage = true,
): Promise<boolean> {
  try {
    // 优先使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      if (showMessage) {
        message.success('已复制到剪贴板');
      }
      return true;
    }

    // 降级方案：使用 execCommand
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '-9999px';
    document.body.append(textArea);
    textArea.focus();
    textArea.select();

    const successful = document.execCommand('copy');
    textArea.remove();

    if (successful) {
      if (showMessage) {
        message.success('已复制到剪贴板');
      }
      return true;
    }

    throw new Error('execCommand failed');
  } catch {
    if (showMessage) {
      message.error('复制失败');
    }
    return false;
  }
}
