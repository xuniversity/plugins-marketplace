export namespace AiApi {
  export type MessageRole = 'assistant' | 'system' | 'user';

  export interface ContentPart {
    image_url?: { url: string };
    text?: string;
    type: 'image_url' | 'text';
  }

  export interface Message {
    content: ContentPart[] | string;
    role: MessageRole;
  }

  export interface ChatRequest {
    enable_thinking?: boolean;
    messages: Message[];
    model?: string;
  }
}

const AI_REQUEST_TIMEOUT = 180_000;

export const aiService = {
  async chatCompletion(params: AiApi.ChatRequest) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), AI_REQUEST_TIMEOUT);

    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      signal: controller.signal,
    }).finally(() => window.clearTimeout(timer));

    if (!response.ok) {
      throw new Error(`AI request failed: ${response.status}`);
    }

    return response.text();
  },

  streamChatCompletion(params: AiApi.ChatRequest) {
    return fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
  },
};
