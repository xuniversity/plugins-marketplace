<script lang="ts" setup>
import { Pagination } from 'ant-design-vue';

export interface TablePaginationProps {
  current: number;
  pageSize: number;
  pageSizeOptions?: string[];
  showQuickJumper?: boolean;
  showSizeChanger?: boolean;
  showTotal?: boolean;
  size?: 'default' | 'small';
  total: number;
}

interface TablePaginationEmits {
  (e: 'change', page: number, pageSize: number): void;
  (e: 'update:current', page: number): void;
  (e: 'update:pageSize', pageSize: number): void;
}

withDefaults(defineProps<TablePaginationProps>(), {
  showQuickJumper: true,
  showSizeChanger: true,
  showTotal: true,
  pageSizeOptions: () => ['10', '20', '50', '100'],
  size: 'default',
});

const emit = defineEmits<TablePaginationEmits>();

// 处理分页变化
const handlePageChange = (page: number, pageSize: number) => {
  emit('change', page, pageSize);
  emit('update:current', page);
  emit('update:pageSize', pageSize);
};

// 总计显示函数
const showTotalText = (total: number, range: [number, number]) => {
  return `第 ${range[0]}-${range[1]} 条，共 ${total} 条`;
};
</script>

<template>
  <div class="flex justify-center p-4">
    <Pagination
      :current="current"
      :page-size="pageSize"
      :page-size-options="pageSizeOptions"
      :show-quick-jumper="showQuickJumper"
      :show-size-changer="showSizeChanger"
      :show-total="showTotal ? showTotalText : undefined"
      :size="size"
      :total="total"
      @change="handlePageChange"
    />
  </div>
</template>

<style scoped>
/* 分页样式优化 */
:deep(.ant-pagination) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

:deep(.ant-pagination-total-text) {
  order: -1;
  margin-right: auto;
  margin-left: 0;
  font-size: 14px;
  color: hsl(var(--muted-foreground));
}

:deep(.ant-pagination .ant-pagination-options) {
  margin-left: 16px;
}

:deep(.ant-pagination-item) {
  border-radius: var(--radius-lg);
}

:deep(.ant-pagination-item-active) {
  background-color: hsl(var(--primary));
  border-color: hsl(var(--primary));
}

:deep(.ant-pagination-item-active a) {
  color: hsl(var(--primary-foreground));
}

:deep(.ant-pagination-prev),
:deep(.ant-pagination-next) {
  border-radius: var(--radius-lg);
}
</style>
