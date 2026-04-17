# Mandatory Component Mapping

This reference mirrors `.cursor/rules/templates-rules-vben.mdc` and the shared component exports under `apps/web-antd/src/components`. Keep them in sync when project rules or shared components change.

## Required Components

| Scenario | Must use | Do not use |
| --- | --- | --- |
| CRUD list pages | `TableLayout` | `<a-table>` |
| Detail display | `DetailModal` or `DetailDrawer` | `<a-modal>` for read-only detail display |
| File upload | `AttachmentUpload` | `<a-upload>` or `<input type="file">` |
| Attachment display | `AttachmentPreview` | Custom attachment lists |
| Media preview | `MediaPreview` | Custom preview dialogs |
| Workflow status display backed by flow data | `FlowStatusTag` | Plain `<a-tag>`, `CustomTag`, or ad-hoc status text |
| AI audit or approval workbench | `AuditLayout` | Custom split layouts or hand-built fixed action bars |
| Read-before-confirm notices or undertakings | `NoticeConfirmModal` | Custom modal plus manual scroll/checkbox gating logic |
| AI input or generation | `AIInput` | Custom AI input areas |
| AI-generated content labeling | `AiWatermark` | Custom AI watermark or label UI |

## Exceptions

- Use `<a-modal>` for create or edit forms when the modal is the form container rather than a read-only detail view.
- When status comes from `flowInstance` or `flowSummary`, use `FlowStatusTag` even for fallback copy instead of reverting to a plain tag.
- Use `CustomTag` for business labels or categories, not workflow instance states.
- Use `AuditLayout` for pages that combine AI review recommendations with approve/reject/pending/escalate actions.
- Use `NoticeConfirmModal` when confirmation must be gated on the user finishing the notice content.
- Any input involving AI generation or polishing must use `AIInput`.
- Any AI-generated content shown to users must be wrapped with `AiWatermark`.

## Template-Only Scaffolds

These components exist in `.specify/templates/project-vben/components/` but are not currently exported from `apps/web-antd/src/components`.

| Scenario | Start from | Notes |
| --- | --- | --- |
| Standalone filters | `.specify/templates/project-vben/components/FilterForm` | Port the template into `apps/web-antd/src/components/FilterForm` before importing `#/components/FilterForm`. |
| Timeline history | `.specify/templates/project-vben/components/Timeline` | Port the template into `apps/web-antd/src/components/Timeline` before importing `#/components/Timeline`. |

## Component Entry Points

| Component | Import path | Typical use |
| --- | --- | --- |
| `TableLayout` | `#/components/TableLayout` | Search, filter, table, and pagination pages |
| `DetailModal` | `#/components/DetailModal` | Simple modal detail layouts |
| `DetailDrawer` | `#/components/DetailDrawer` | Complex or multi-tab detail layouts |
| `FilterForm` | `#/components/FilterForm` | Independent filter panels |
| `AttachmentUpload` | `#/components/AttachmentUpload` | Upload flows |
| `AttachmentPreview` | `#/components/AttachmentPreview` | Attachment display |
| `MediaPreview` | `#/components/MediaPreview` | Image, video, and audio preview |
| `FlowStatusTag` | `#/components/Flow` | Workflow status tags with drill-down popover details |
| `AuditLayout` | `#/components/AuditLayout` | Audit workbenches with AI assistant and action bar |
| `NoticeConfirmModal` | `#/components/NoticeConfirmModal` | Notices or undertakings that must be read before confirming |
| `CustomTag` | `#/components/CustomTag` | Custom status or category tags |
| `RichEditor` | `#/components/RichEditor` | Rich text editing |
| `EmptyState` | `#/components/EmptyState` | Empty states |
| `AIInput` | `#/components/AIInput` | AI-assisted input |
| `AiWatermark` | `#/components/AiWatermark` | AI-content watermarking |
