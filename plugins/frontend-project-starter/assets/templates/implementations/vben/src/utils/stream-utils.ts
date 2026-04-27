/**
 * 流式响应处理工具
 */

/**
 * 流式响应数据块接口
 */
export interface StreamChunk {
  /** 内容数据 */
  content?: null | string;
  /** 推理/思考内容 */
  reasoning_content?: null | string;
  /** 数据类型 */
  type?: 'error' | 'markdown' | 'tool_call' | 'tool_response';
}

/**
 * 聊天完成响应接口
 */
export interface ChatCompletionResponse {
  /** 推理/思考内容 */
  reasoning_content: string;
  /** 响应内容 */
  content: string;
}

/**
 * 处理AI流式响应的回调函数类型
 */
export interface StreamCallback {
  (data: { content: string; done?: boolean; reasoning_content?: string }): void;
}

/**
 * 处理AI流式响应数据
 * @param response Fetch API的Response对象
 * @param callback 处理每个数据块的回调函数
 */
export async function handleStreamResponse(
  response: Response,
  callback: StreamCallback,
): Promise<void> {
  if (!response.ok || !response.body) {
    throw new Error('流式请求失败');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  // 累积内容的变量
  let accumulatedContent = '';
  let accumulatedReasoning = '';
  let pendingChunk = '';

  const emitCurrentState = () => {
    callback({
      content: accumulatedContent,
      reasoning_content: accumulatedReasoning,
    });
  };

  const processPayload = (payload: string) => {
    const normalizedPayload = payload.trim();

    if (!normalizedPayload || normalizedPayload === '[DONE]') {
      return;
    }

    try {
      const data: StreamChunk = JSON.parse(normalizedPayload);

      if (data.content) {
        accumulatedContent += data.content;
      }

      if (data.reasoning_content) {
        accumulatedReasoning += data.reasoning_content;
      }

      emitCurrentState();
    } catch {
      // 兼容后端直接返回纯文本分片的 SSE。
      accumulatedContent += payload;
      emitCurrentState();
    }
  };

  const processSseBuffer = (buffer: string, flush = false): string => {
    const normalizedBuffer = buffer.replaceAll('\r\n', '\n');
    const eventChunks = normalizedBuffer.split('\n\n');
    const remaining = flush ? '' : (eventChunks.pop() ?? '');

    for (const eventChunk of eventChunks) {
      const payload = eventChunk
        .split('\n')
        .filter((line) => line.startsWith('data:'))
        .map((line) => line.replace(/^data:\s?/, ''))
        .join('\n');

      if (payload) {
        processPayload(payload);
      }
    }

    return remaining;
  };

  try {
    // 读取流
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        pendingChunk += decoder.decode();
        if (pendingChunk.trim()) {
          pendingChunk = processSseBuffer(pendingChunk, true);
        }
        // 流结束，传递最终结果和完成标志
        callback({
          content: accumulatedContent,
          done: true,
          reasoning_content: accumulatedReasoning,
        });
        break;
      }

      // 解码二进制数据
      pendingChunk += decoder.decode(value, { stream: true });
      pendingChunk = processSseBuffer(pendingChunk);
    }
  } catch (error) {
    throw new Error(`处理流数据时出错: ${error}`);
  } finally {
    reader.releaseLock();
  }
}

/**
 * 创建一个处理流式响应的函数
 * @param callback 处理数据的回调函数
 * @returns 一个Promise，解析为最终的完整响应
 */
export function createStreamHandler(
  callback?: StreamCallback,
): (response: Response) => Promise<ChatCompletionResponse> {
  return async (response: Response) => {
    // 如果没有提供回调函数，直接解析JSON响应
    if (!callback) {
      return await response.json();
    }

    // 使用共享的处理逻辑处理流式响应
    let finalContent = '';
    let finalReasoningContent = '';

    await handleStreamResponse(response, (data) => {
      // 更新最终内容
      if (data.content) finalContent = data.content;
      if (data.reasoning_content)
        finalReasoningContent = data.reasoning_content;

      // 调用外部回调
      callback(data);
    });

    // 返回最终结果
    return {
      content: finalContent,
      reasoning_content: finalReasoningContent,
    };
  };
}
