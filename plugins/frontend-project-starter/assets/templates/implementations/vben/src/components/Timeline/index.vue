<script setup lang="ts">
import type { Component } from 'vue';
import type { AttachmentItem } from '#/components/AttachmentPreview';

import { computed } from 'vue';

import { AttachmentPreview } from '#/components/AttachmentPreview';
import { EmptyState } from '#/components/EmptyState';

export interface TimelineItem {
  id: number | string;
  content: string;
  time: string;
  fileInfos?: AttachmentItem[];
  recorder?: string;
  status?: string;
  title?: string;
  type?: 'default' | 'dynamic' | 'talk';
  [key: string]: unknown;
}

export interface TimelineAction {
  action: (item: TimelineItem) => void;
  color?: string;
  icon?: Component;
  label: string;
}

const props = withDefaults(
  defineProps<{
    actions?: TimelineAction[];
    emptyText?: string;
    items: TimelineItem[];
  }>(),
  {
    actions: () => [],
    emptyText: '暂无记录',
  },
);

const emit = defineEmits<{
  itemClick: [item: TimelineItem];
}>();

const parseTimelineDate = (value: string) => {
  if (value.includes('年') && value.includes('月')) {
    const yearMatch = value.match(/(\d{4})年/);
    const monthMatch = value.match(/(\d{1,2})月/);
    const dayMatch = value.match(/(\d{1,2})日/);

    if (yearMatch?.[1] && monthMatch?.[1]) {
      const year = Number.parseInt(yearMatch[1], 10);
      const month = Number.parseInt(monthMatch[1], 10);
      const day = dayMatch?.[1] ? Number.parseInt(dayMatch[1], 10) : 1;
      return new Date(year, month - 1, day);
    }
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? new Date(0) : parsed;
};

const groupedItems = computed(() => {
  const yearGroups = new Map<
    string,
    {
      monthGroups: Map<
        string,
        {
          dayGroups: Map<
            string,
            {
              date: string;
              dayMonth: string;
              items: TimelineItem[];
            }
          >;
          monthYear: string;
          simpleMonth: string;
        }
      >;
      year: string;
    }
  >();

  const sortedItems = [...props.items].sort((a, b) => {
    return parseTimelineDate(b.time).getTime() - parseTimelineDate(a.time).getTime();
  });

  sortedItems.forEach((item) => {
    const date = parseTimelineDate(item.time);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const yearString = `${year}年`;
    const monthYear = `${year}年${month}月`;
    const simpleMonth = `${month}月`;
    const dayMonth = `${day}日`;

    if (!yearGroups.has(yearString)) {
      yearGroups.set(yearString, {
        year: yearString,
        monthGroups: new Map(),
      });
    }

    const yearGroup = yearGroups.get(yearString)!;

    if (!yearGroup.monthGroups.has(monthYear)) {
      yearGroup.monthGroups.set(monthYear, {
        monthYear,
        simpleMonth,
        dayGroups: new Map(),
      });
    }

    const monthGroup = yearGroup.monthGroups.get(monthYear)!;

    if (!monthGroup.dayGroups.has(dayMonth)) {
      monthGroup.dayGroups.set(dayMonth, {
        date: `${year}-${month.toString().padStart(2, '0')}-${day
          .toString()
          .padStart(2, '0')}`,
        dayMonth,
        items: [],
      });
    }

    monthGroup.dayGroups.get(dayMonth)!.items.push(item);
  });

  return [...yearGroups.values()].map((yearGroup) => ({
    ...yearGroup,
    monthGroups: [...yearGroup.monthGroups.values()].map((monthGroup) => ({
      ...monthGroup,
      dayGroups: [...monthGroup.dayGroups.values()].sort((a, b) => {
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      }),
    })),
  }));
});

const getTimelineColor = (item: TimelineItem) => {
  if (item.type === 'dynamic') {
    return 'hsl(var(--primary))';
  }
  if (item.type === 'talk') {
    return 'hsl(var(--success))';
  }
  return 'hsl(var(--muted-foreground) / 48%)';
};

const getStatusClass = (status?: string) => {
  if (status === '已取消') {
    return 'is-muted';
  }
  if (status === '已完成') {
    return 'is-complete';
  }
  if (status === '进行中') {
    return 'is-active';
  }
  return 'is-default';
};

const handleItemClick = (item: TimelineItem) => {
  emit('itemClick', item);
};

const handleActionClick = (
  action: TimelineAction,
  item: TimelineItem,
  event: MouseEvent,
) => {
  event.stopPropagation();
  action.action(item);
};
</script>

<template>
  <div class="timeline-container">
    <EmptyState
      v-if="items.length === 0"
      :description="emptyText"
      icon-type="document"
      title="暂无记录"
    />

    <div v-else class="timeline-wrapper">
      <div class="timeline-main-line"></div>

      <div
        v-for="yearGroup in groupedItems"
        :key="yearGroup.year"
        class="year-group"
      >
        <div
          v-for="(monthGroup, monthIndex) in yearGroup.monthGroups"
          :key="monthGroup.monthYear"
          class="month-group"
        >
          <div
            v-for="(dayGroup, dayIndex) in monthGroup.dayGroups"
            :key="dayGroup.dayMonth"
            class="day-group"
          >
            <div
              v-for="(item, itemIndex) in dayGroup.items"
              :key="item.id"
              class="timeline-item-wrapper"
            >
              <div class="timeline-left">
                <div v-if="itemIndex === 0" class="date-info">
                  <div
                    v-if="monthIndex === 0 && dayIndex === 0"
                    class="year-label"
                  >
                    {{ yearGroup.year }}
                  </div>
                  <div v-if="dayIndex === 0" class="month-label">
                    {{ monthGroup.simpleMonth }}
                  </div>
                  <div class="day-label">{{ dayGroup.dayMonth }}</div>
                </div>
              </div>

              <div class="timeline-node">
                <div
                  :style="{ backgroundColor: getTimelineColor(item) }"
                  class="timeline-dot"
                ></div>
              </div>

              <div class="timeline-content">
                <div class="timeline-item" @click="handleItemClick(item)">
                  <div class="item-content-wrapper">
                    <div class="item-main">
                      <template v-if="item.title">
                        <h3 class="item-title">{{ item.title }}</h3>
                        <p
                          v-if="item.content !== item.title"
                          class="item-description"
                        >
                          {{ item.content }}
                        </p>
                      </template>
                      <p v-else class="item-description">
                        {{ item.content }}
                      </p>

                      <p v-if="item.recorder" class="item-recorder">
                        {{ item.recorder }}
                      </p>

                      <AttachmentPreview
                        v-if="item.fileInfos?.length"
                        :attachments="item.fileInfos"
                        :max-display="3"
                      />
                    </div>

                    <div class="item-meta">
                      <span class="item-time">{{ item.time }}</span>
                      <span
                        v-if="item.status"
                        :class="getStatusClass(item.status)"
                        class="item-status"
                      >
                        {{ item.status }}
                      </span>
                    </div>
                  </div>

                  <div v-if="actions.length > 0" class="item-actions">
                    <button
                      v-for="action in actions"
                      :key="action.label"
                      :style="{ color: action.color || 'hsl(var(--primary))' }"
                      :title="action.label"
                      class="action-btn"
                      type="button"
                      @click="(event) => handleActionClick(action, item, event)"
                    >
                      <component :is="action.icon" v-if="action.icon" />
                      <span v-else class="action-text">{{ action.label }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-container {
  position: relative;
}

.timeline-wrapper {
  position: relative;
}

.timeline-main-line {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 59px;
  z-index: 1;
  width: 2px;
  background-color: hsl(var(--border));
}

.timeline-item-wrapper {
  position: relative;
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
}

.timeline-left {
  display: flex;
  flex-shrink: 0;
  justify-content: flex-end;
  width: 50px;
  padding-right: 4px;
}

.date-info {
  text-align: right;
}

.year-label {
  margin-bottom: 1px;
  font-size: 12px;
  font-weight: 400;
  color: hsl(var(--muted-foreground) / 55%);
}

.month-label {
  margin-bottom: 2px;
  font-size: 14px;
  font-weight: 600;
  color: hsl(var(--foreground));
}

.day-label {
  font-size: 12px;
  color: hsl(var(--muted-foreground));
}

.timeline-node {
  position: relative;
  z-index: 2;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-top: 8px;
}

.timeline-dot {
  position: relative;
  z-index: 3;
  width: 12px;
  height: 12px;
  border: 3px solid hsl(var(--card));
  border-radius: 50%;
  box-shadow: 0 0 0 1px hsl(var(--border));
}

.timeline-content {
  position: relative;
  flex: 1;
  padding-left: 16px;
  margin-top: 8px;
}

.timeline-item {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  min-height: 40px;
  padding: 12px 16px;
  cursor: pointer;
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius-md);
  box-shadow: 0 1px 2px hsl(var(--foreground) / 4%);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.timeline-item:hover {
  border-color: hsl(var(--primary) / 35%);
  box-shadow: 0 4px 12px hsl(var(--foreground) / 8%);
}

.item-content-wrapper {
  flex: 1;
  min-width: 0;
}

.item-main {
  margin-bottom: 8px;
}

.item-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: hsl(var(--foreground));
}

.item-description {
  margin: 4px 0;
  font-size: 14px;
  line-height: 1.5;
  color: hsl(var(--foreground));
}

.item-recorder {
  margin: 4px 0 0;
  font-size: 12px;
  color: hsl(var(--muted-foreground));
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.item-time {
  font-size: 12px;
  color: hsl(var(--muted-foreground));
}

.item-status {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-sm);
}

.item-status.is-muted,
.item-status.is-default {
  color: hsl(var(--muted-foreground));
  background: hsl(var(--muted));
}

.item-status.is-complete {
  color: hsl(var(--primary));
  background: hsl(var(--primary) / 10%);
}

.item-status.is-active {
  color: hsl(var(--success));
  background: hsl(var(--success) / 12%);
}

.item-actions {
  display: flex;
  gap: 4px;
  align-items: flex-start;
  margin-left: 8px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  font-size: 18px;
  cursor: pointer;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.action-btn:hover {
  background: hsl(var(--muted));
  transform: scale(1.04);
}

.action-btn:active {
  transform: scale(0.96);
}

.action-text {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.month-group {
  margin-bottom: 32px;
}

.month-group:last-child,
.day-group:last-child,
.year-group:last-child {
  margin-bottom: 0;
}

.day-group {
  margin-bottom: 8px;
}

.year-group {
  margin-bottom: 40px;
}

@media (max-width: 640px) {
  .timeline-main-line {
    left: 59px;
  }

  .timeline-left {
    width: 50px;
    padding-right: 10px;
  }

  .timeline-content {
    padding-left: 10px;
  }

  .timeline-item {
    padding: 10px 12px;
  }

  .item-actions {
    margin-left: 8px;
  }

  .year-label,
  .day-label,
  .item-time {
    font-size: 11px;
  }

  .month-label,
  .item-description {
    font-size: 13px;
  }

  .item-title {
    font-size: 15px;
  }
}
</style>
