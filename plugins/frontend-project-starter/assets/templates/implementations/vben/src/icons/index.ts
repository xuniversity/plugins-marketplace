/**
 * 应用图标管理
 *
 * 使用 createIconifyIcon 创建图标组件
 * 图标来源：https://icon-sets.iconify.design/
 *
 * 命名规范：
 * - PascalCase 命名
 * - 格式：{IconSet}{IconName}
 * - 示例：MdiMagnify, LucideSearch
 *
 * 优先使用 outline 风格图标
 */

import { createIconifyIcon } from '@vben-core/icons';

// ==================== 通用图标 ====================

/** 搜索 */
export const MdiMagnify = createIconifyIcon('mdi:magnify');

/** 通知铃铛 */
export const MdiBellOutline = createIconifyIcon('mdi:bell-outline');

/** 刷新 */
export const MdiRefresh = createIconifyIcon('mdi:refresh');

/** 关闭 */
export const MdiClose = createIconifyIcon('mdi:close');

/** 筛选 */
export const MdiFilter = createIconifyIcon('mdi:filter-outline');

/** 下拉展开 */
export const MdiChevronDown = createIconifyIcon('mdi:chevron-down');

/** 上拉收起 */
export const MdiChevronUp = createIconifyIcon('mdi:chevron-up');

/** 左箭头 */
export const MdiChevronLeft = createIconifyIcon('mdi:chevron-left');

/** 右箭头 */
export const MdiChevronRight = createIconifyIcon('mdi:chevron-right');

/** 回车键 */
export const MdiKeyboardReturn = createIconifyIcon('mdi:keyboard-return');

/** 全屏 */
export const MdiFullscreen = createIconifyIcon('mdi:fullscreen');

/** 退出全屏 */
export const MdiFullscreenExit = createIconifyIcon('mdi:fullscreen-exit');

// ==================== 操作图标 ====================

/** 新增/添加 */
export const MdiPlus = createIconifyIcon('mdi:plus');

/** 编辑 */
export const MdiPencil = createIconifyIcon('mdi:pencil-outline');

/** 删除 */
export const MdiDelete = createIconifyIcon('mdi:delete-outline');

/** 查看/眼睛 */
export const MdiEye = createIconifyIcon('mdi:eye-outline');

/** 置顶/图钉 */
export const MdiPin = createIconifyIcon('mdi:pin-outline');

/** 屏蔽/盾牌 */
export const MdiShield = createIconifyIcon('mdi:shield-outline');

/** 导出 */
export const MdiExport = createIconifyIcon('mdi:export');

/** 导入 */
export const MdiImport = createIconifyIcon('mdi:import');

// ==================== 状态图标 ====================

/** 成功/对号 */
export const MdiCheck = createIconifyIcon('mdi:check');

/** 全部已读 */
export const MdiCheckAll = createIconifyIcon('mdi:check-all');

/** 警告 */
export const MdiAlert = createIconifyIcon('mdi:alert-outline');

/** 信息 */
export const MdiInformation = createIconifyIcon('mdi:information-outline');

/** 错误 */
export const MdiCloseCircle = createIconifyIcon('mdi:close-circle-outline');

// ==================== 其他常用图标 ====================

/** 设置 */
export const MdiCog = createIconifyIcon('mdi:cog-outline');

/** 用户 */
export const MdiAccount = createIconifyIcon('mdi:account-outline');

/** 日历 */
export const MdiCalendar = createIconifyIcon('mdi:calendar-outline');

/** 时钟 */
export const MdiClock = createIconifyIcon('mdi:clock-outline');

/** 时钟（轮廓） */
export const MdiClockOutline = createIconifyIcon('mdi:clock-outline');

/** 消息气泡 */
export const MdiMessageOutline = createIconifyIcon('mdi:message-outline');

/** 账户切换/转交 */
export const MdiAccountSwitch = createIconifyIcon('mdi:account-switch-outline');

/** 警告圆形 */
export const MdiAlertCircleOutline = createIconifyIcon(
  'mdi:alert-circle-outline',
);

/** 帮助/问号圆形 */
export const MdiHelpCircleOutline = createIconifyIcon(
  'mdi:help-circle-outline',
);

/** 标签 */
export const MdiTag = createIconifyIcon('mdi:tag-outline');

/** 文件夹 */
export const MdiFolder = createIconifyIcon('mdi:folder-outline');

/** 文件 */
export const MdiFile = createIconifyIcon('mdi:file-outline');

/** 配置/设置 */
export const HugeiconsConfiguration = createIconifyIcon(
  'hugeicons:configuration-01',
);

/** 业务搜索 */
export const HugeiconsJobSearch = createIconifyIcon('hugeicons:job-search');

/** 下载 */
export const MdiDownload = createIconifyIcon('mdi:download');

/** 上传 */
export const MdiUpload = createIconifyIcon('mdi:upload');

/** 网格/应用网格 */
export const MdiViewGrid = createIconifyIcon('flowbite:grid-outline');

// ==================== 导航图标 ====================

/** 首页 */
export const MdiHome = createIconifyIcon('mdi:home-outline');

/** 菜单 */
export const MdiMenu = createIconifyIcon('mdi:menu');

/** 返回 */
export const MdiArrowLeft = createIconifyIcon('mdi:arrow-left');

/** 前进 */
export const MdiArrowRight = createIconifyIcon('mdi:arrow-right');

/** 灯泡/提示 */
export const MdiLightbulb = createIconifyIcon('mdi:lightbulb-on-outline');

// ==================== AI相关图标 ====================

/** AI */
export const MdiAiLine = createIconifyIcon('mdi:robot-outline');

/** AI Logo */
export const HumbleiconsAi = createIconifyIcon('humbleicons:ai');

/** AI 灯泡 */
export const MingcuteBulb2AiLine = createIconifyIcon('mingcute:bulb-2-ai-line');

/** 转交 */
export const MingcuteTransfer3Fill = createIconifyIcon(
  'mingcute:transfer-3-fill',
);

/** 大脑/思考 */
export const MdiBrain = createIconifyIcon('mdi:brain');

/** 点赞 */
export const MdiThumbUp = createIconifyIcon('mdi:thumb-up-outline');

/** 点踩 */
export const MdiThumbDown = createIconifyIcon('mdi:thumb-down-outline');

/** 闪电/快速 */
export const MdiLightning = createIconifyIcon('mdi:lightning-bolt-outline');

/** 学校/专业 */
export const MdiSchool = createIconifyIcon('mdi:school-outline');

/** 复制 */
export const MdiCopy = createIconifyIcon('mdi:content-copy');

/** 圆形填充对号 (Lets Icons) */
export const LetsIconsCheckFill = createIconifyIcon('lets-icons:check-fill');

/** 圆形填充关闭 (Lets Icons) */
export const LetsIconsCloseRoundFill = createIconifyIcon(
  'lets-icons:close-round-fill',
);

/** 减号 */
export const MdiMinus = createIconifyIcon('mdi:minus');

// ==================== 文件类型图标 ====================

/** PDF文件 */
export const MdiFilePdfBox = createIconifyIcon('mdi:file-pdf-box');

/** 通用文档 */
export const MdiFileDocumentOutline = createIconifyIcon(
  'mdi:file-document-outline',
);

/** 视频文件 */
export const MdiFileVideoOutline = createIconifyIcon('mdi:file-video-outline');

/** Word文档 */
export const VscodeIconsFileTypeWord = createIconifyIcon(
  'vscode-icons:file-type-word',
);

/** Excel表格 */
export const VscodeIconsFileTypeExcel = createIconifyIcon(
  'vscode-icons:file-type-excel',
);

/** PowerPoint演示 */
export const VscodeIconsFileTypePowerpoint = createIconifyIcon(
  'vscode-icons:file-type-powerpoint',
);

/**
 * 如何添加新图标：
 *
 * 1. 访问 https://icon-sets.iconify.design/
 * 2. 搜索需要的图标（推荐使用 Material Design Icons - mdi）
 * 3. 复制图标名称（如 account-outline）
 * 4. 使用 createIconifyIcon 创建：
 *    export const MdiAccountOutline = createIconifyIcon('mdi:account-outline');
 * 5. 添加 JSDoc 注释说明图标用途
 *
 * 推荐图标集：
 * - mdi: Material Design Icons (最全面)
 * - lucide: Lucide Icons (简洁美观)
 * - carbon: Carbon Icons (IBM设计)
 * - heroicons: Heroicons (Tailwind官方)
 */
