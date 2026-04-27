<script lang="ts" setup>
import type { CSSProperties } from 'vue';

import { computed } from 'vue';

import { Button } from 'ant-design-vue';

import { MdiRefresh } from '#/icons';

const props = withDefaults(
  defineProps<{
    ariaLabel?: string;
    buttonSize?: number;
    disabled?: boolean;
    loading?: boolean;
    size?: 'large' | 'middle' | 'small';
  }>(),
  {
    ariaLabel: '刷新',
    buttonSize: 32,
    disabled: false,
    loading: false,
    size: 'small',
  },
);

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void;
}>();

const buttonStyle = computed<CSSProperties>(() => {
  const size = `${Math.max(24, props.buttonSize)}px`;
  return {
    width: size,
    minWidth: size,
    height: size,
  };
});

const handleClick = (event: MouseEvent) => {
  if (props.loading || props.disabled) {
    return;
  }
  emit('click', event);
};
</script>

<template>
  <Button
    :aria-label="ariaLabel"
    :disabled="disabled || loading"
    :size="size"
    :style="buttonStyle"
    class="refresh-icon-button"
    shape="circle"
    type="default"
    @click="handleClick"
  >
    <MdiRefresh
      class="refresh-icon"
      :class="{ 'refresh-icon-spinning': loading }"
    />
  </Button>
</template>

<style scoped>
.refresh-icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.refresh-icon {
  font-size: 14px;
  line-height: 1;
}

.refresh-icon-spinning {
  animation: refresh-icon-spin 0.8s linear infinite;
}

@keyframes refresh-icon-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
