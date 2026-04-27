<script lang="ts" setup>
import type { TableColumnsType } from 'ant-design-vue';

import { Table } from 'ant-design-vue';

export interface TableContentProps {
  columns: TableColumnsType;
  dataSource: any[];
  loading?: boolean;
  rowClassName?: (record: any, index: number) => string;
  rowKey?: string;
  rowSelection?: any;
  scroll?: { x?: number | string; y?: number | string };
  showPagination?: boolean;
  size?: 'large' | 'middle' | 'small';
}

interface TableContentEmits {
  (e: 'rowClick', record: any, index: number): void;
  (e: 'selectionChange', selectedRowKeys: any[], selectedRows: any[]): void;
}

withDefaults(defineProps<TableContentProps>(), {
  loading: false,
  rowKey: 'id',
  size: 'small',
  showPagination: false,
  scroll: () => ({}),
  rowSelection: undefined,
  rowClassName: undefined,
});

const emit = defineEmits<TableContentEmits>();

// 处理行点击
const handleRowClick = (record: any, index: number) => {
  emit('rowClick', record, index);
};
</script>

<template>
  <div class="px-4">
    <Table
      :columns="columns"
      :custom-row="
        (record: any, index?: number) => ({
          onClick: () => handleRowClick(record, index ?? 0),
        })
      "
      :data-source="dataSource"
      :loading="loading"
      :pagination="showPagination ? undefined : false"
      :row-class-name="rowClassName"
      :row-key="rowKey"
      :row-selection="rowSelection"
      :scroll="scroll"
      :size="size"
      class="min-h-table w-full"
    >
      <!-- 通过插槽透传所有自定义内容 -->
      <template v-for="(_, name) in $slots" :key="name" #[name]="slotData">
        <slot :name="name" v-bind="slotData"></slot>
      </template>
    </Table>
  </div>
</template>

<style scoped>
/* 表格最小高度 - 设置为屏幕高度的50% */
.min-h-table {
  --table-fixed-surface: hsl(var(--card));
  --table-header-surface: color-mix(
    in srgb,
    hsl(var(--muted)) 50%,
    hsl(var(--card))
  );
  --table-hover-surface: color-mix(
    in srgb,
    hsl(var(--muted)) 30%,
    hsl(var(--card))
  );

  min-height: 160px;
}

/* 表格样式优化 */
:deep(.ant-table-thead > tr > th) {
  padding: 0.75rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: hsl(var(--foreground));
  text-transform: uppercase;
  vertical-align: middle;
  letter-spacing: 0.05em;
  background-color: var(--table-header-surface);
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: var(--table-hover-surface);
}

:deep(.ant-table-tbody > tr > td) {
  padding: 0.75rem 0.5rem;
  vertical-align: top;
  border-bottom: 1px solid hsl(var(--border));
}

:deep(.ant-table) {
  background: hsl(var(--card));
  border-radius: var(--radius-lg);
}

:deep(.ant-table-container) {
  border-radius: var(--radius-lg);
}

/* 修复表格固定列背景色 - 确保固定列能遮挡滚动内容 */
:deep(.ant-table-cell-fix-left),
:deep(.ant-table-cell-fix-right) {
  background: var(--table-fixed-surface) !important;
}

/* 表头固定列使用 muted 背景色 */
:deep(.ant-table-thead .ant-table-cell-fix-left),
:deep(.ant-table-thead .ant-table-cell-fix-right) {
  background: var(--table-header-surface) !important;
}

/* 固定列边界伪元素宽度（AntD 默认 30px，收窄避免遮挡感） */
:deep(.ant-table-cell-fix-left-last::after),
:deep(.ant-table-cell-fix-right-first::after) {
  width: 0;
  box-shadow: none;
}

/* 仅在对应方向存在可滚动内容时显示阴影，避免常驻阴影干扰 */
:deep(.ant-table-ping-right .ant-table-cell-fix-left-last::after) {
  box-shadow: inset -10px 0 8px -8px hsl(var(--foreground) / 8%);
}

:deep(.ant-table-ping-left .ant-table-cell-fix-right-first::after) {
  box-shadow: inset 10px 0 8px -8px hsl(var(--foreground) / 8%);
}

/* hover 时固定列背景色 - 使用不透明颜色确保遮挡下层内容 */
:deep(.ant-table-tbody > tr:hover > .ant-table-cell-fix-left),
:deep(.ant-table-tbody > tr:hover > .ant-table-cell-fix-right) {
  background: var(--table-hover-surface) !important;
}
</style>
