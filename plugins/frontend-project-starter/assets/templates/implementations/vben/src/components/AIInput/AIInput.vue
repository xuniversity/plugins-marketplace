<!-- eslint-disable no-console -->
<script setup lang="ts">
import type { AIInputEmits, AIInputProps } from './types';

import type { AiApi } from '#/api/core/ai';

import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

import { useClipboard } from '@vueuse/core';

import { aiService } from '#/api/core/ai';
import AiWatermark from '#/components/AiWatermark/index.vue';
import {
  MdiAiLine,
  MdiBrain,
  MdiCheck,
  MdiCopy,
  MdiLightning,
  MdiRefresh,
  MdiSchool,
  MdiThumbDown,
  MdiThumbUp,
} from '#/icons';
import { createStreamHandler } from '#/utils/stream-utils';

import ThinkingProcess from './ThinkingProcess.vue';

const props = withDefaults(defineProps<AIInputProps>(), {
  label: '',
  placeholder: '请输入内容...',
  rows: 8,
  mode: 'textarea',
  enableAiStyling: true,
  borderColor: 'hsl(var(--primary)),hsl(var(--primary) / 0.72)',
  styleMode: 'background',
  presetData: '',
  autoPolish: false,
  borderRadius: 'var(--radius)',
  showThinkingProcess: false,
  thinkingBudget: 1000,
  model: 'qwen-plus',
  systemPrompt: '',
  userPromptTemplate: '',
  emptyGenerateMessage: '',
  showWatermark: true,
  loading: false,
  loadingText: '✨ AI正在生成中...',
  popoverPosition: 'top',
  controlsMode: 'full',
});

const emit = defineEmits<AIInputEmits>();

// Clipboard functionality
const { copy } = useClipboard({ legacy: true });

// State
const inputText = computed({
  get: () => (props.loading ? props.loadingText : props.modelValue),
  set: (value) => emit('update:modelValue', value ?? ''),
});

const isPolishing = ref(false);
const showPostControls = ref(false);
const selectedStyle = ref<'concise' | 'professional'>('concise');
const originalText = ref('');
const isFocused = ref(false);
const feedbackGiven = ref<'negative' | 'positive' | null>(null);
const showStylePopover = ref(false);
const styleButtonRef = ref<HTMLElement | null>(null);
const isThinking = ref(false);
const thinkingContent = ref('');
const thinkingSteps = ref<string[]>([]);
const copySuccess = ref(false);
const thinkingProcessRef = ref<InstanceType<typeof ThinkingProcess>>();
const polishButtonRef = ref<HTMLElement>();
const thinkingButtonPre = ref<HTMLElement>();
const thinkingButtonPost = ref<HTMLElement>();
const currentTriggerElement = ref<HTMLElement | null>(null);
const thinkingAnimationTimer = ref<null | number>(null);
const thinkingAnimationStep = ref(0);
const isRepolishing = ref(false);
const isAiGenerated = ref(false);
const emptyGenerateError = ref('');

// Generate unique ID for accessibility
const inputId = `ai-input-${Math.random().toString(36).slice(2, 11)}`;

// 过滤AI返回结果，移除冗余信息
const filterAIResponse = (text: string): string => {
  if (!text) return text;

  let filtered = text.trim();

  // 移除常见的前缀标记
  const prefixes = [
    /^优化后的文本[：:]\s*/,
    /^润色结果[：:]\s*/,
    /^\[优化后的文本\][：:]\s*/,
    /^润色后[：:]\s*/,
    /^结果[：:]\s*/,
    /^答案[：:]\s*/,
    /^修改后[：:]\s*/,
  ];

  for (const prefix of prefixes) {
    filtered = filtered.replace(prefix, '');
  }

  // 移除说明性文本段落
  const lines = filtered.split('\n');
  const cleanedLines = [];
  let skipExplanation = false;

  for (const line of lines) {
    const trimmedLine = line.trim();

    // 跳过说明性段落
    if (
      trimmedLine.includes('说明：') ||
      trimmedLine.includes('注：') ||
      trimmedLine.includes('解释：') ||
      /^\d+\./.test(trimmedLine)
    ) {
      skipExplanation = true;
      continue;
    }

    // 如果是空行且之前在跳过说明，继续跳过
    if (skipExplanation && trimmedLine === '') {
      continue;
    }

    // 重置跳过状态
    if (
      skipExplanation &&
      trimmedLine !== '' &&
      !trimmedLine.includes('说明：') &&
      !trimmedLine.includes('注：')
    ) {
      skipExplanation = false;
    }

    if (!skipExplanation) {
      cleanedLines.push(line);
    }
  }

  return cleanedLines.join('\n').trim();
};

// Computed styles
const borderColors = computed(() => {
  const colors = props.borderColor.split(',');
  return {
    from: colors[0] || 'hsl(var(--primary))',
    to: colors[1] || colors[0] || 'hsl(var(--primary) / 0.72)',
  };
});

const inputBackgroundClass = computed(() => {
  if (!props.enableAiStyling) {
    return 'ai-input-surface';
  }

  return props.styleMode === 'border'
    ? 'ai-input-surface'
    : 'ai-input-gradient-surface';
});

const borderGradientStyle = computed(() => {
  return props.enableAiStyling && props.styleMode === 'background'
    ? `background: linear-gradient(135deg, ${borderColors.value.from} 0%, ${borderColors.value.to} 50%, ${borderColors.value.from} 100%);`
    : 'display: none;';
});

const getBorderClass = () => {
  if (!props.enableAiStyling) {
    return 'border-input';
  }

  return props.styleMode === 'border'
    ? 'border-transparent ai-border-mode'
    : 'border-transparent';
};

const getScrollbarClass = () => {
  return !props.enableAiStyling || props.styleMode === 'border'
    ? 'basic-scrollbar'
    : 'ai-scrollbar';
};

// Style options
const styles = [
  {
    value: 'professional' as const,
    label: '专业风格',
    tooltip: '语言更专业、书面化',
    component: MdiSchool,
  },
  {
    value: 'concise' as const,
    label: '简洁风格',
    tooltip: '语言更简洁、精炼',
    component: MdiLightning,
  },
];

// Computed properties
const currentStyleComponent = computed(() => {
  const style = styles.find((s) => s.value === selectedStyle.value);
  return style ? style.component : MdiAiLine;
});

const currentStyleTooltip = computed(() => {
  const style = styles.find((s) => s.value === selectedStyle.value);
  return style ? `${style.label} - ${style.tooltip}` : '';
});

// 根据rows自动确定组件模式
const computedMode = computed(() => {
  if (props.mode !== 'textarea') {
    return props.mode;
  }
  // 如果rows <= 1，使用input模式
  return props.rows <= 1 ? 'input' : 'textarea';
});

// 是否显示思考按钮（在post-controls中）
const showThinkingButton = computed(() => {
  return (
    props.showThinkingProcess &&
    (isThinking.value ||
      thinkingSteps.value.length > 0 ||
      (thinkingContent.value && thinkingContent.value.trim().length > 0))
  );
});

// 思考动画相关方法
const stopThinkingAnimation = () => {
  if (thinkingAnimationTimer.value) {
    clearTimeout(thinkingAnimationTimer.value);
    thinkingAnimationTimer.value = null;
  }
};

const startThinkingAnimation = () => {
  stopThinkingAnimation(); // 先清除可能存在的定时器

  const thinkingTexts = [
    '🤔 AI正在思考中',
    '🤔 AI正在思考中.',
    '🤔 AI正在思考中..',
    '🤔 AI正在思考中...',
    '🧠 AI正在分析中...',
    '✨ AI正在优化中...',
    '💭 AI正在创作中...',
  ];

  thinkingAnimationStep.value = 0;

  const animate = () => {
    if (isThinking.value) {
      // 前4个是基础的点点动画，后面3个是不同的emoji和文本
      if (thinkingAnimationStep.value < 4) {
        inputText.value = thinkingTexts[thinkingAnimationStep.value] || '';
      } else {
        // 随机选择一个有趣的变体
        const randomIndex = 4 + Math.floor(Math.random() * 3);
        inputText.value = thinkingTexts[randomIndex] || '';
      }

      thinkingAnimationStep.value = (thinkingAnimationStep.value + 1) % 8;
      thinkingAnimationTimer.value = Number(
        setTimeout(animate, thinkingAnimationStep.value < 4 ? 500 : 800),
      );
    }
  };

  animate();
};

// Methods
const toggleStylePopover = () => {
  showStylePopover.value = !showStylePopover.value;
};

const selectStyle = (style: 'concise' | 'professional') => {
  selectedStyle.value = style;
  showStylePopover.value = false;
};

const toggleThinking = () => {
  // 如果不显示思考过程，直接返回
  if (!props.showThinkingProcess) return;

  // 设置当前触发元素
  currentTriggerElement.value = showPostControls.value
    ? thinkingButtonPost.value || null
    : thinkingButtonPre.value || null;

  // 触发共享的ThinkingProcess组件
  if (thinkingProcessRef.value) {
    if (thinkingProcessRef.value.isExpanded) {
      thinkingProcessRef.value.collapseBubble();
    } else {
      thinkingProcessRef.value.expandBubble();
    }
  }
};

const handleInput = () => {
  showPostControls.value = false;
  feedbackGiven.value = null;
  isRepolishing.value = false; // 重置重新优化状态
  isAiGenerated.value = false; // 用户手动输入，移除AI生成标记
  emptyGenerateError.value = '';

  // 切换回 pre-controls 后，更新触发元素
  nextTick(() => {
    currentTriggerElement.value = props.showThinkingProcess
      ? thinkingButtonPre.value || null
      : null;
  });
};

const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = () => {
  isFocused.value = false;
};

const handlePolish = async () => {
  const previousText = inputText.value ?? '';

  // 检查是否是思考状态的占位文本
  const isThinkingText =
    inputText.value?.includes('🤔') ||
    inputText.value?.includes('🧠') ||
    inputText.value?.includes('✨') ||
    inputText.value?.includes('💭');

  // 如果当前显示的是思考占位文本，使用原始文本
  const userInput = isThinkingText
    ? originalText.value?.trim()
    : inputText.value?.trim();
  const presetInput = props.presetData?.trim();
  const useCustomPrompt = Boolean(
    props.systemPrompt && props.userPromptTemplate,
  );
  const contentToUse = useCustomPrompt ? presetInput || userInput : userInput;

  console.log(
    '🔍 handlePolish 开始 - userInput:',
    userInput,
    'inputText.value:',
    inputText.value,
    'isThinkingText:',
    isThinkingText,
  );
  if (!contentToUse) {
    if (props.emptyGenerateMessage) {
      emptyGenerateError.value = props.emptyGenerateMessage;
    }
    console.log('❌ handlePolish 提前返回 - 输入为空');
    return;
  }

  emptyGenerateError.value = '';

  // 检测是否为重新优化场景（当前在post-controls界面）
  const isRepolishingMode = showPostControls.value;
  console.log(
    '🔄 handlePolish - 是否为重新优化:',
    isRepolishingMode,
    'showPostControls:',
    showPostControls.value,
  );

  // 根据场景设置不同的loading状态
  if (isRepolishingMode) {
    isRepolishing.value = true;
    console.log('🔄 设置 isRepolishing = true (重新优化模式)');
  } else {
    isPolishing.value = true;
    console.log('🔄 设置 isPolishing = true (初次优化模式)');
  }

  feedbackGiven.value = null;
  copySuccess.value = false; // 重置复制状态
  thinkingContent.value = ''; // 重置思考内容
  thinkingSteps.value = []; // 重置思考步骤

  // 如果不是重新优化，则切换到pre-controls
  if (!isRepolishingMode) {
    showPostControls.value = false;
  }

  // 等待DOM更新后再设置触发元素和思考状态
  await nextTick();

  // 设置思考状态和触发元素
  if (props.showThinkingProcess) {
    // 现在设置思考状态，让思考按钮先渲染
    isThinking.value = true;

    // 再等待一次DOM更新，确保思考按钮已经渲染
    await nextTick();

    // 根据当前模式设置触发元素
    if (isRepolishingMode) {
      // 重新优化模式：使用post-controls中的思考按钮
      currentTriggerElement.value = thinkingButtonPost.value || null;
      console.log('设置重新优化思考触发元素:', currentTriggerElement.value);
    } else {
      // 初次优化模式：使用pre-controls中的思考按钮
      currentTriggerElement.value =
        thinkingButtonPre.value || polishButtonRef.value || null;
      console.log('设置思考触发元素:', currentTriggerElement.value);

      // 额外延迟确保触发元素完全渲染
      setTimeout(() => {
        currentTriggerElement.value =
          thinkingButtonPre.value || polishButtonRef.value || null;
        console.log('延迟后重新设置思考触发元素:', currentTriggerElement.value);
      }, 100);
    }
  } else {
    // 非思考模式下，也设置thinking状态以显示loading，但不设置触发元素
    isThinking.value = true;
    currentTriggerElement.value = null;
  }

  const stylePrompt =
    selectedStyle.value === 'professional'
      ? '语言更专业、书面化'
      : '语言更简洁、精炼';

  // 检测是否为重新生成场景
  const isRegeneration = showPostControls.value;
  const currentText = inputText.value?.trim();

  let prompt: string;

  if (useCustomPrompt) {
    // 使用自定义提示词模式
    let systemPromptText = props.systemPrompt;
    const userContent = props.userPromptTemplate.replace(
      '{content}',
      contentToUse,
    );

    // 如果是重新生成，在系统提示词中添加差异化要求
    if (isRegeneration) {
      systemPromptText = `${props.systemPrompt}\n\n重要提示：这是重新生成请求，请采用不同的表述方式、角度或风格来生成内容，避免与之前的版本过于相似。`;
      console.log('🔄 自定义提示词模式 - 重新生成');
    } else {
      console.log('✨ 自定义提示词模式 - 首次生成');
    }

    // 将 systemPrompt 和 userContent 合并为单个 prompt
    prompt = `${systemPromptText}\n\n${userContent}`;

    console.log(
      '🤖 使用自定义提示词模式，内容源:',
      `${contentToUse.slice(0, 100)}...`,
    );
  } else {
    // 使用默认的润色模式
    if (
      isRegeneration &&
      originalText.value &&
      currentText !== originalText.value
    ) {
      // 重新生成场景：提供原文和当前润色结果，要求生成不同版本
      prompt = `请基于以下内容重新生成一个优化版本。

**原始文本：**
${originalText.value}

**当前版本：**
${currentText}

**要求：**
- 风格：${stylePrompt}
- 使用不同的表述方式
- 保持原意，不编造信息
- 直接输出结果，无需解释

请生成一个新的优化版本：`;

      console.log(
        '🔄 重新生成模式，原文长度:',
        originalText.value?.length,
        '当前文本长度:',
        currentText?.length,
      );
    } else {
      // 初次生成场景：优化提示词
      prompt = `请对以下文本进行润色优化。

**润色要求：**
- 风格：${stylePrompt}
- 保持原意，不编造信息
- 直接输出结果，无需解释

**原始文本：**
${userInput}`;

      console.log('✨ 初次生成模式，文本长度:', userInput?.length);
    }
  }

  console.log('📝 使用的提示词模式:', isRegeneration ? '重新生成' : '初次生成');

  try {
    console.log('🚀 进入try块开始处理请求');
    // 只有在初次生成时才更新原始文本，重新生成时保持原文不变
    if (!isRegeneration) {
      originalText.value = contentToUse;
    }
    let polishedText = '';

    // 构建符合 OpenAI 标准格式的请求参数
    const requestParams: AiApi.ChatRequest = {
      model: props.model,
      messages: [{ role: 'user', content: prompt }],
      enable_thinking: props.showThinkingProcess,
    };

    console.log(
      '📡 准备调用 streamChatCompletion，参数:',
      JSON.stringify(requestParams, null, 2),
    );
    const response = await aiService.streamChatCompletion(requestParams);

    const handler = createStreamHandler((data) => {
      if (data.reasoning_content) {
        // 思考阶段
        console.log('🧠 AI思考阶段，内容：', data.reasoning_content);
        // 确保思考状态为true（无论是否为重新优化模式）
        isThinking.value = true;

        // 解析思考步骤（假设每行是一个思考步骤）
        const lines = data.reasoning_content
          .split('\n')
          .filter((line) => line.trim());
        for (const line of lines) {
          if (line.trim() && !thinkingSteps.value.includes(line.trim())) {
            thinkingSteps.value.push(line.trim());
          }
        }

        thinkingContent.value = data.reasoning_content;
        // 🔥 重要：思考阶段绝对不能修改 textarea 内容！
        // textarea 应该保持原始文本或显示简单的思考提示
        // 只在非重新优化场景下启动思考动画
        if (
          !isRepolishingMode &&
          inputText.value &&
          !inputText.value.includes('🤔') &&
          !inputText.value.includes('🧠') &&
          !inputText.value.includes('✨') &&
          !inputText.value.includes('💭')
        ) {
          startThinkingAnimation();
        }
      }

      if (data.content) {
        // 结果阶段，累积内容并过滤
        console.log('💬 AI输出阶段，内容：', data.content);
        // 只在思考模式下才重置 thinking状态（从思考阶段切换到结果阶段）
        // 在非思考模式下，保持thinking状态以显示loading直到完成
        if (props.showThinkingProcess && isThinking.value) {
          isThinking.value = false;
        }
        // 确保停止思考动画（无论是否设置了isThinking状态）
        stopThinkingAnimation();
        polishedText = data.content;
        const filteredText = filterAIResponse(polishedText);
        inputText.value = filteredText;
      }

      if (data.done) {
        console.log('✅ 流式请求完成');
        // 确保重置 thinking状态
        isThinking.value = false;
        stopThinkingAnimation();

        // 最终过滤处理
        const finalText = filterAIResponse(polishedText);
        inputText.value = finalText;
        isAiGenerated.value = true;

        // 根据场景决定是否切换界面
        if (!isRepolishingMode) {
          showPostControls.value = true;
          // 切换到 post-controls 后，更新触发元素
          nextTick(() => {
            currentTriggerElement.value = props.showThinkingProcess
              ? thinkingButtonPost.value || null
              : null;
          });
        }
        // 如果是重新优化，保持当前界面状态

        emit('polish', finalText);
      }
    });

    try {
      await handler(response);
    } catch (handlerError) {
      console.error('❌ 流式请求错误:', handlerError);
      // 确保重置 thinking状态
      isThinking.value = false;
      stopThinkingAnimation();
      copySuccess.value = false; // 重置复制状态
      // 注意：错误时保留思考内容，让用户可以查看之前的思考过程
      // thinkingContent.value = '' // 不清空思考内容
      // thinkingSteps.value = [] // 不清空思考步骤
      inputText.value = isRegeneration
        ? currentText || previousText || originalText.value
        : originalText.value || previousText;

      // 根据是否为重新优化来决定界面状态
      if (!isRepolishingMode) {
        // 如果是首次优化出错，回到pre-controls
        showPostControls.value = false;
      }
      // 如果是重新优化出错，保持在post-controls界面
      throw handlerError;
    }
  } catch (error) {
    console.error('💥 catch块 - AI润色失败:', error);
    isThinking.value = false;
    stopThinkingAnimation();
    copySuccess.value = false; // 重置复制状态
    // 注意：错误时保留思考内容，让用户可以查看之前的思考过程
    // thinkingContent.value = '' // 不清空思考内容
    // thinkingSteps.value = [] // 不清空思考步骤
    inputText.value = isRegeneration
      ? currentText || previousText || originalText.value
      : originalText.value || previousText;

    // 根据是否为重新优化来决定界面状态
    if (!isRepolishingMode) {
      // 如果是首次优化出错，回到pre-controls
      showPostControls.value = false;
    }
    // 如果是重新优化出错，保持在post-controls界面
  } finally {
    console.log('🔄 finally块 - 重置loading状态');
    // 只重置 loading 状态，不重置 thinking 状态
    // thinking 状态由流完成时统一处理
    isPolishing.value = false;
    isRepolishing.value = false;
  }
};

const handleFeedback = (type: 'negative' | 'positive') => {
  feedbackGiven.value = type;
  emit('feedback', type);
};

const handleCopy = async () => {
  try {
    // 获取要复制的内容，排除思考状态提示
    const isThinkingText =
      inputText.value?.includes('🤔') ||
      inputText.value?.includes('🧠') ||
      inputText.value?.includes('✨') ||
      inputText.value?.includes('💭');
    const contentToCopy = isThinkingText ? originalText.value : inputText.value;

    if (!contentToCopy || !contentToCopy.trim()) {
      console.warn('没有可复制的内容');
      return;
    }

    await copy(contentToCopy.trim());

    // 显示复制成功状态
    copySuccess.value = true;
    console.log('复制成功:', `${contentToCopy.slice(0, 50)}...`);

    // 2秒后重置复制状态
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  } catch (error) {
    console.error('复制失败:', error);
    // 可以在这里添加错误提示
  }
};

// Click outside to close popover
const handleClickOutside = (event: Event) => {
  if (
    styleButtonRef.value &&
    !styleButtonRef.value.contains(event.target as Node)
  ) {
    showStylePopover.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  stopThinkingAnimation(); // 清理定时器
});

// 处理预设数据和自动润色
watch(
  () => props.presetData,
  (newPresetData) => {
    if (newPresetData && newPresetData.trim()) {
      const currentValue = inputText.value?.trim();
      const presetValue = newPresetData.trim();

      // 如果当前值为空，或者当前值就是预设数据，则设置预设数据
      if (!currentValue || currentValue === presetValue) {
        // 重置状态：隐藏后处理控制按钮和水印
        showPostControls.value = false;

        // 设置预设数据
        inputText.value = presetValue;

        // 如果启用自动润色，延迟执行润色
        if (props.autoPolish) {
          nextTick(() => {
            setTimeout(() => {
              handlePolish();
            }, 500); // 延迟500ms让用户看到预设数据
          });
        }
      }
    }
  },
  { immediate: true },
);
</script>

<template>
  <div class="ai-input-container relative">
    <label
      v-if="label"
      :for="inputId"
      class="text-foreground/80 mb-1 block text-sm font-medium"
    >
      {{ label }}
    </label>

    <div class="relative">
      <div class="ai-input-wrapper relative">
        <!-- Textarea 容器 -->
        <div v-if="computedMode === 'textarea'" class="relative">
          <textarea
            :id="inputId"
            v-model="inputText"
            :class="[
              inputBackgroundClass,
              getBorderClass(),
              getScrollbarClass(),
              isFocused && props.enableAiStyling ? 'ai-input-focused' : '',
              props.loading ? 'ai-input-loading' : '',
            ]"
            :placeholder="placeholder"
            :readonly="props.loading"
            :rows="rows"
            :style="{ 'z-index': 1, 'border-radius': props.borderRadius }"
            class="ai-input-field font-inter relative w-full resize-none border-2 px-4 py-3 pb-12 transition-all duration-300 focus:outline-none"
            @blur="handleBlur"
            @focus="handleFocus"
            @input="handleInput"
          ></textarea>

          <!-- AI 生成水印 (仅 textarea 模式，加载时不显示) -->
          <AiWatermark
            v-if="props.showWatermark && !props.loading && isAiGenerated"
            :opacity="0.7"
            :visible="true"
            class="ai-watermark pointer-events-none"
            font-size="xs"
            position="bottom-left"
            text="本内容由AI生成"
          />
        </div>

        <input
          v-else-if="computedMode === 'input'"
          :id="inputId"
          v-model="inputText"
          :class="[
            inputBackgroundClass,
            getBorderClass(),
            isFocused && props.enableAiStyling ? 'ai-input-focused' : '',
            computedMode === 'input' ? 'px-4 py-3 pr-24' : 'px-4 py-3',
          ]"
          :placeholder="placeholder"
          :style="{ 'z-index': 1, 'border-radius': props.borderRadius }"
          class="ai-input-field font-inter relative w-full border-2 transition-all duration-300 focus:outline-none"
          type="text"
          @blur="handleBlur"
          @focus="handleFocus"
          @input="handleInput"
        />
        <div
          v-if="props.enableAiStyling"
          :class="[isFocused ? 'opacity-20' : 'opacity-0']"
          :style="`z-index: -1; border-radius: ${props.borderRadius}; ${borderGradientStyle}`"
          class="ai-border-gradient absolute inset-0 transition-opacity duration-300"
        ></div>
      </div>

      <div v-if="emptyGenerateError" class="ai-input-error mt-2 text-sm">
        {{ emptyGenerateError }}
      </div>

      <!-- Unified controls container -->
      <div
        v-if="props.controlsMode !== 'none'"
        :class="[
          computedMode === 'input' ? 'top-1/2 -translate-y-1/2' : 'bottom-4',
        ]"
        class="absolute right-4 z-20 flex items-center gap-2"
      >
        <!-- Thinking Process Component (shared instance, no button) -->
        <ThinkingProcess
          v-if="showThinkingProcess"
          ref="thinkingProcessRef"
          :current-thinking-text="thinkingContent"
          :is-thinking="isThinking"
          :mode="computedMode"
          :show-button="false"
          :thinking-steps="thinkingSteps"
          :trigger-element="currentTriggerElement"
        />

        <!-- Pre-polish controls (visible by default, hidden when loading) - only in full mode -->
        <div
          v-if="props.controlsMode === 'full'"
          v-show="!showPostControls && !props.loading"
          :class="[
            computedMode === 'input'
              ? 'ai-floating-controls--input gap-0.5 px-1'
              : 'ai-floating-controls--textarea gap-0.5 px-1 py-0.5',
          ]"
          class="ai-floating-controls relative flex items-center backdrop-blur-sm"
        >
          <!-- Thinking Process Button (pre-polish) -->
          <button
            v-if="showThinkingButton"
            ref="thinkingButtonPre"
            :class="[computedMode === 'input' ? 'p-0.5' : 'p-1.5']"
            class="ai-icon-action-btn flex items-center gap-2 transition-all duration-200"
            title="查看思考过程"
            @click="toggleThinking"
          >
            <MdiBrain
              :class="[computedMode === 'input' ? 'h-4 w-4' : 'h-5 w-5']"
              class="text-muted-foreground"
            />
          </button>

          <div class="relative">
            <button
              ref="styleButtonRef"
              :class="[computedMode === 'input' ? 'p-0.5' : 'p-1.5']"
              :title="currentStyleTooltip"
              class="ai-icon-action-btn flex items-center gap-2 transition-all duration-200"
              @click="toggleStylePopover"
            >
              <component
                :is="currentStyleComponent"
                :class="[computedMode === 'input' ? 'h-4 w-4' : 'h-5 w-5']"
                class="text-foreground/80"
              />
            </button>

            <!-- Style popover -->
            <div
              v-if="showStylePopover"
              :class="[
                props.popoverPosition === 'top'
                  ? 'bottom-full mb-1'
                  : 'top-full mt-1',
              ]"
              class="ai-style-popover absolute left-0 z-30 min-w-[180px]"
            >
              <button
                v-for="(style, index) in styles"
                :key="style.value"
                :class="[
                  style.value === selectedStyle
                    ? 'bg-[hsl(var(--primary)/0.12)] text-[hsl(var(--primary))]'
                    : 'hover:bg-accent',
                  index !== styles.length - 1 ? 'border-border border-b' : '',
                ]"
                class="flex w-full items-center gap-3 p-3 text-left transition-all duration-200"
                @click="selectStyle(style.value)"
              >
                <component
                  :is="style.component"
                  class="h-4 w-4 flex-shrink-0"
                />
                <div class="flex flex-col">
                  <span class="text-sm font-medium">{{ style.label }}</span>
                  <span class="text-muted-foreground text-xs">
                    {{ style.tooltip }}
                  </span>
                </div>
              </button>

              <!-- Divider -->
              <div class="border-border border-t"></div>

              <!-- Model info -->
              <div class="p-3">
                <div class="flex items-center gap-2">
                  <span class="text-muted-foreground text-xs">
                    使用模型: {{ props.model }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <button
            ref="polishButtonRef"
            :class="[
              computedMode === 'input'
                ? 'h-7 min-w-[65px] gap-1 px-1.5 py-0.5 text-xs'
                : 'h-9 min-w-[100px] gap-1.5 px-3 py-1.5 text-sm',
            ]"
            :disabled="isPolishing || isThinking || isRepolishing"
            class="ai-input-submit-btn flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary)/0.25)] focus:ring-offset-2 focus:ring-offset-[hsl(var(--background))] disabled:cursor-not-allowed disabled:opacity-50"
            @click="handlePolish"
          >
            <svg
              v-if="isPolishing || isThinking || isRepolishing"
              class="h-4 w-4 animate-spin text-current"
              fill="none"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                fill="currentColor"
              />
            </svg>
            <MdiAiLine
              v-else
              :class="computedMode === 'input' ? 'h-3 w-3' : 'h-4 w-4'"
            />
            {{
              isPolishing || isThinking || isRepolishing
                ? '处理中...'
                : computedMode === 'input'
                  ? '生成'
                  : 'AI 生成'
            }}
          </button>
        </div>

        <!-- Post-polish controls (hidden by default and when loading) - only in full mode -->
        <div
          v-if="props.controlsMode === 'full'"
          v-show="showPostControls && !props.loading"
          :class="[
            computedMode === 'input'
              ? 'ai-floating-controls--input p-0.5'
              : 'ai-floating-controls--textarea p-0.5',
          ]"
          class="ai-floating-controls action-controls flex items-center justify-between backdrop-blur-sm"
        >
          <div class="flex items-center gap-0.5">
            <!-- Thinking Process Button (triggers shared instance) -->
            <button
              v-if="showThinkingButton"
              ref="thinkingButtonPost"
              :class="[computedMode === 'input' ? 'p-0.5' : 'p-1.5']"
              class="ai-icon-action-btn flex items-center gap-2 transition-all duration-200"
              title="查看思考过程"
              @click="toggleThinking"
            >
              <MdiBrain
                :class="[computedMode === 'input' ? 'h-4 w-4' : 'h-5 w-5']"
                class="text-muted-foreground"
              />
            </button>
            <button
              :class="[
                feedbackGiven === 'positive'
                  ? 'ai-feedback-positive'
                  : 'ai-icon-action-btn',
                computedMode === 'input' ? 'p-1' : 'p-1.5',
              ]"
              class="action-btn ai-icon-chip-btn rounded-full transition-all duration-200"
              title="满意"
              @click="handleFeedback('positive')"
            >
              <MdiThumbUp
                :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
              />
            </button>
            <button
              :class="[
                feedbackGiven === 'negative'
                  ? 'ai-feedback-negative'
                  : 'ai-icon-action-btn',
                computedMode === 'input' ? 'p-1' : 'p-1.5',
              ]"
              class="action-btn ai-icon-chip-btn rounded-full transition-all duration-200"
              title="不满意"
              @click="handleFeedback('negative')"
            >
              <MdiThumbDown
                :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
              />
            </button>
            <button
              :class="[
                copySuccess ? 'ai-copy-success' : 'ai-icon-action-btn',
                computedMode === 'input' ? 'p-1' : 'p-1.5',
              ]"
              class="action-btn ai-icon-chip-btn rounded-full transition-all duration-200"
              title="复制结果"
              @click="handleCopy"
            >
              <MdiCheck
                v-if="copySuccess"
                :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
              />
              <MdiCopy
                v-else
                :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
              />
            </button>
          </div>
          <button
            :class="[
              isPolishing || isThinking || isRepolishing
                ? 'bg-muted text-muted-foreground'
                : 'ai-action-btn-primary',
              computedMode === 'input'
                ? 'gap-0.5 px-2 py-0.5 text-xs'
                : 'gap-0.5 px-2.5 py-0.5 text-sm',
            ]"
            :disabled="isPolishing || isThinking || isRepolishing"
            class="action-btn flex items-center font-medium transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
            @click="handlePolish"
          >
            <svg
              v-if="isPolishing || isThinking || isRepolishing"
              class="h-4 w-4 animate-spin text-current"
              fill="none"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                fill="currentColor"
              />
            </svg>
            <MdiRefresh
              v-else
              :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
            />
            {{
              isPolishing || isThinking || isRepolishing
                ? '处理中...'
                : '重新生成'
            }}
          </button>
        </div>

        <!-- Copy-only control (only in copy-only mode) -->
        <div
          v-if="props.controlsMode === 'copy-only'"
          v-show="!props.loading"
          class="ai-floating-controls ai-floating-controls--copy flex items-center p-0.5 backdrop-blur-sm"
        >
          <button
            :class="[
              copySuccess ? 'ai-copy-success' : 'ai-icon-action-btn',
              computedMode === 'input' ? 'p-1' : 'p-1.5',
            ]"
            class="action-btn ai-icon-chip-btn rounded-full transition-all duration-200"
            title="复制内容"
            @click="handleCopy"
          >
            <MdiCheck
              v-if="copySuccess"
              :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
            />
            <MdiCopy
              v-else
              :class="computedMode === 'input' ? 'h-3.5 w-3.5' : 'h-4 w-4'"
            />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes border-glow {
  0%,
  100% {
    filter: brightness(1);
    background-position: 0% 50%;
  }

  50% {
    filter: brightness(1.05);
    background-position: 100% 50%;
  }
}

@keyframes border-glow-smooth {
  0%,
  100% {
    filter: brightness(1);
    background-position: 0% 50%;
  }

  50% {
    filter: brightness(1.02);
    background-position: 100% 50%;
  }
}

@keyframes gradient-shift {
  0% {
    filter: brightness(1);
    background-position: 0% 50%;
  }

  50% {
    filter: brightness(1.03);
    background-position: 100% 50%;
  }

  100% {
    filter: brightness(1);
    background-position: 0% 50%;
  }
}

@keyframes loading-pulse {
  0%,
  100% {
    opacity: 0.6;
  }

  50% {
    opacity: 1;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in-down {
  from {
    opacity: 0;
    transform: translateY(-16px);
  }

  to {
    opacity: 1;
    transform: translateY(-8px);
  }
}

@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-input-container {
  width: 100%;
  --ai-input-shell-radius: calc(var(--radius) + 6px);
  --ai-input-action-radius: calc(var(--radius) + 2px);
  --ai-input-floating-border: hsl(var(--border) / 0.72);
  --ai-input-floating-shadow:
    0 12px 28px hsl(var(--overlay)), 0 4px 10px hsl(var(--foreground) / 0.08);
  --ai-input-success-surface: hsl(var(--success) / 0.12);
  --ai-input-destructive-surface: hsl(var(--destructive) / 0.12);
  --ai-input-scrollbar-radius: 999px;
}

.ai-input-wrapper {
  position: relative;
}

.ai-input-error {
  color: hsl(var(--destructive));
}

.ai-input-field {
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
  background-clip: padding-box;
  border: 2px solid transparent;
}

.ai-input-field[type='text'] {
  height: 48px;
  max-height: 48px;
}

.ai-input-field:not([type='text']) {
  min-height: auto;
}

.ai-input-field.ai-input-gradient-surface {
  background: linear-gradient(
    135deg,
    hsl(var(--background)) 0%,
    hsl(var(--primary) / 0.06) 52%,
    hsl(var(--primary) / 0.12) 100%
  );
}

.ai-input-field.ai-input-surface {
  background: hsl(var(--background));
  border-color: hsl(var(--border));
}

.ai-input-field.ai-input-gradient-surface:focus {
  background: linear-gradient(
    135deg,
    hsl(var(--background)) 0%,
    hsl(var(--primary) / 0.1) 52%,
    hsl(var(--primary) / 0.16) 100%
  );
  box-shadow: 0 0 20px hsl(var(--primary) / 0.1);
}

.ai-input-field.ai-input-surface:focus {
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 2px hsl(var(--primary) / 0.12);
}

/* 加载状态样式 */
.ai-input-field.ai-input-loading {
  font-weight: 500;
  color: hsl(var(--muted-foreground));
  pointer-events: none;
  cursor: default;
  animation: loading-pulse 1.5s ease-in-out infinite;
}

/* 边框模式AI风格 */
.ai-input-field.ai-border-mode {
  position: relative !important;
  background:
    linear-gradient(hsl(var(--background)), hsl(var(--background))) padding-box,
    linear-gradient(
        135deg,
        hsl(var(--primary) / 0.12),
        hsl(var(--primary) / 0.16),
        hsl(var(--primary) / 0.12),
        hsl(var(--primary) / 0.12)
      )
      border-box !important;
  background-size: 200% 200% !important;
  border: 2px solid transparent !important;
  animation: border-glow-smooth 4s ease-in-out infinite !important;
}

.ai-input-field.ai-border-mode:hover:not(:focus) {
  background:
    linear-gradient(hsl(var(--background)), hsl(var(--background))) padding-box,
    linear-gradient(
        135deg,
        hsl(var(--primary) / 0.2),
        hsl(var(--primary) / 0.26),
        hsl(var(--primary) / 0.2),
        hsl(var(--primary) / 0.2)
      )
      border-box !important;
  background-size: 200% 200% !important;
  animation: border-glow-smooth 3s ease-in-out infinite !important;
}

.ai-watermark {
  bottom: 16px;
  left: 8px;
}

.ai-floating-controls {
  background: hsl(var(--popover) / 0.94);
  border: 1px solid var(--ai-input-floating-border);
  border-radius: var(--ai-input-shell-radius);
  box-shadow: var(--ai-input-floating-shadow);
  color: hsl(var(--popover-foreground));
}

.ai-floating-controls--input {
  background: hsl(var(--popover) / 0.9);
}

.ai-floating-controls--textarea,
.ai-floating-controls--copy {
  background: hsl(var(--popover) / 0.96);
}

.ai-style-popover {
  background: hsl(var(--popover) / 0.98);
  border: 1px solid hsl(var(--border));
  border-radius: var(--ai-input-shell-radius);
  box-shadow: var(--ai-input-floating-shadow);
  color: hsl(var(--popover-foreground));
}

.ai-input-field.ai-border-mode:focus {
  background:
    linear-gradient(hsl(var(--background)), hsl(var(--background))) padding-box,
    linear-gradient(
        135deg,
        hsl(var(--primary) / 0.5),
        hsl(var(--primary) / 0.62),
        hsl(var(--primary) / 0.5),
        hsl(var(--primary) / 0.5)
      )
      border-box !important;
  background-size: 200% 200% !important;
  box-shadow:
    0 0 0 3px hsl(var(--primary) / 0.08),
    0 0 16px hsl(var(--primary) / 0.08) !important;
  animation: border-glow 3s ease-in-out infinite !important;
}

.ai-border-gradient {
  padding: 2px;
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}

/* AI风格滚动条 */
.ai-scrollbar {
  scrollbar-color: hsl(var(--primary) / 0.3) transparent;
  scrollbar-width: thin;
}

.ai-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.ai-scrollbar::-webkit-scrollbar-track {
  background: transparent;
  border-radius: var(--ai-input-scrollbar-radius);
}

.ai-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 0.3),
    hsl(var(--primary) / 0.3)
  );
  border: 1px solid hsl(var(--background) / 0.2);
  border-radius: var(--ai-input-scrollbar-radius);
  transition: all 0.3s ease;
}

.ai-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 0.5),
    hsl(var(--primary) / 0.5)
  );
  box-shadow: 0 2px 4px hsl(var(--foreground) / 0.1);
}

.ai-scrollbar::-webkit-scrollbar-thumb:active {
  background: linear-gradient(
    135deg,
    hsl(var(--primary) / 0.7),
    hsl(var(--primary) / 0.7)
  );
}

.ai-scrollbar::-webkit-scrollbar-corner {
  background: transparent;
}

/* 基础滚动条样式 */
.basic-scrollbar {
  scrollbar-color: hsl(var(--muted-foreground) / 0.32) transparent;
  scrollbar-width: thin;
}

.basic-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.basic-scrollbar::-webkit-scrollbar-track {
  background: transparent;
  border-radius: var(--ai-input-scrollbar-radius);
}

.basic-scrollbar::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.32);
  border-radius: var(--ai-input-scrollbar-radius);
  transition: all 0.3s ease;
}

.basic-scrollbar::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.52);
}

.basic-scrollbar::-webkit-scrollbar-corner {
  background: transparent;
}

.font-inter {
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
}

.action-controls {
  animation: fade-in 0.3s ease-out;
}

.ai-icon-action-btn {
  border-radius: var(--ai-input-action-radius);
  color: hsl(var(--muted-foreground));
}

.ai-icon-action-btn:hover {
  background: hsl(var(--accent));
  color: hsl(var(--foreground));
}

.ai-icon-chip-btn.ai-feedback-positive,
.ai-icon-chip-btn.ai-copy-success {
  background: var(--ai-input-success-surface);
  color: hsl(var(--success));
}

.ai-icon-chip-btn.ai-feedback-negative {
  background: var(--ai-input-destructive-surface);
  color: hsl(var(--destructive));
}

.ai-action-btn-primary {
  border-radius: var(--ai-input-action-radius);
  color: hsl(var(--primary));
}

.ai-action-btn-primary:hover {
  background: hsl(var(--primary) / 0.08);
}

.action-btn:hover {
  transform: scale(1.05);
}

/* 思考气泡样式 */
.thinking-bubble {
  transform: translateY(-8px);
  animation: slide-in-down 0.3s ease-out;
}

.thinking-toggle {
  min-width: 140px;
  cursor: pointer;
  user-select: none;
  border: none;
}

.thinking-toggle:hover {
  box-shadow: 0 4px 12px hsl(var(--primary) / 0.3);
  transform: translateY(-1px);
}

.thinking-content {
  background: hsl(var(--popover) / 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid hsl(var(--border));
  animation: slide-in-up 0.2s ease-out;
}

.thinking-content::-webkit-scrollbar {
  width: 4px;
}

.thinking-content::-webkit-scrollbar-track {
  background: hsl(var(--muted) / 0.4);
  border-radius: var(--ai-input-scrollbar-radius);
}

.thinking-content::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: var(--ai-input-scrollbar-radius);
}

.thinking-content::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground) / 0.5);
}

.ai-input-submit-btn {
  border-radius: var(--ai-input-shell-radius);
  color: hsl(var(--primary-foreground));
  background: linear-gradient(
    135deg,
    color-mix(in srgb, hsl(var(--primary)) 88%, hsl(var(--card)) 12%) 0%,
    color-mix(in srgb, hsl(var(--primary)) 80%, hsl(var(--foreground)) 20%) 100%
  );
  box-shadow:
    0 10px 24px hsl(var(--primary) / 0.18),
    0 4px 12px hsl(var(--overlay));
}

.ai-input-submit-btn:hover:not(:disabled) {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, hsl(var(--primary)) 82%, hsl(var(--foreground)) 18%) 0%,
    color-mix(in srgb, hsl(var(--primary)) 74%, hsl(var(--foreground)) 26%) 100%
  );
  box-shadow:
    0 14px 30px hsl(var(--primary) / 0.24),
    0 6px 14px hsl(var(--overlay));
  transform: translateY(-1px);
}
</style>
