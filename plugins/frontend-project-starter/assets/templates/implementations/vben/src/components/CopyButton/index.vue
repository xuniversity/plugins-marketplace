<script lang="ts" setup>
import { computed, onBeforeUnmount, ref } from 'vue';

import { MdiCheck, MdiCopy } from '#/icons';
import { copyToClipboard } from '#/utils/clipboard';

const props = withDefaults(
  defineProps<{
    ariaLabel?: string;
    copiedAriaLabel?: string;
    copiedTitle?: string;
    disabled?: boolean;
    iconClass?: string;
    showMessage?: boolean;
    stopPropagation?: boolean;
    successDuration?: number;
    text: string;
    title?: string;
  }>(),
  {
    ariaLabel: '复制',
    copiedAriaLabel: '已复制',
    copiedTitle: '已复制',
    disabled: false,
    iconClass: 'h-4 w-4',
    showMessage: true,
    stopPropagation: false,
    successDuration: 1500,
    title: '复制',
  },
);

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void;
  (e: 'copied', text: string): void;
}>();

const copied = ref(false);
let successTimer: number | undefined;

const currentAriaLabel = computed(() =>
  copied.value ? props.copiedAriaLabel : props.ariaLabel,
);

const currentTitle = computed(() =>
  copied.value ? props.copiedTitle : props.title,
);

const clearSuccessTimer = () => {
  if (successTimer) {
    window.clearTimeout(successTimer);
    successTimer = undefined;
  }
};

const showCopiedState = () => {
  copied.value = true;
  clearSuccessTimer();
  successTimer = window.setTimeout(() => {
    copied.value = false;
    successTimer = undefined;
  }, props.successDuration);
};

const handleClick = async (event: MouseEvent) => {
  if (props.stopPropagation) {
    event.stopPropagation();
  }

  emit('click', event);

  if (props.disabled || !props.text) {
    return;
  }

  const copiedSuccess = await copyToClipboard(props.text, props.showMessage);
  if (!copiedSuccess) {
    return;
  }

  showCopiedState();
  emit('copied', props.text);
};

onBeforeUnmount(() => {
  clearSuccessTimer();
});
</script>

<template>
  <button
    :aria-label="currentAriaLabel"
    :disabled="disabled || !text"
    :title="currentTitle"
    class="copy-button text-muted-foreground hover:bg-accent hover:text-foreground disabled:text-muted-foreground/60 inline-flex items-center justify-center rounded p-1 transition-colors disabled:cursor-not-allowed disabled:hover:bg-transparent"
    type="button"
    @click="handleClick"
  >
    <MdiCheck v-if="copied" :class="iconClass" />
    <MdiCopy v-else :class="iconClass" />
  </button>
</template>

<style scoped>
.copy-button {
  line-height: 1;
}
</style>
