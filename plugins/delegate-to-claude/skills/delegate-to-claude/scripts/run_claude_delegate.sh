#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_claude_delegate.sh --prompt-file FILE --delegate-dir DIR [options]

Options:
  --prompt-file FILE            Required. UTF-8 text file containing the full prompt.
  --delegate-dir DIR            Required. Unified delegate working directory.
  --repo-dir DIR                Repository directory to expose to Claude. Default: current directory.
  --output-format FMT           Claude output format. Default: stream-json.
  --model MODEL                 Optional Claude model alias or full model name.
  --max-turns N                 Optional max turns for non-interactive mode.
  --permission-mode MODE        Claude permission mode. Default: bypassPermissions.
  --timeout-seconds N           Optional timeout for the Claude process. 0 means no timeout. Default: 0.
  --poll-interval N             Poll interval in seconds for result file checks. Default: 2.
  --no-partial-messages         Disable partial message events in stream output.
  --no-hook-events              Disable hook events in stream output.
  --allow-session-persistence   Do not append --no-session-persistence.
  --no-skip-permissions         Do not append --dangerously-skip-permissions.
  --help                        Show this message.

Environment:
  CLAUDE_BIN                    Claude executable name or path. Default: claude
EOF
}

prompt_file=""
delegate_dir=""
repo_dir="$(pwd)"
output_format="stream-json"
model=""
max_turns=""
permission_mode="bypassPermissions"
timeout_seconds="0"
poll_interval="2"
skip_permissions=1
include_partial_messages=1
include_hook_events=1
disable_session_persistence=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt-file)
      prompt_file="${2:-}"
      shift 2
      ;;
    --delegate-dir)
      delegate_dir="${2:-}"
      shift 2
      ;;
    --repo-dir)
      repo_dir="${2:-}"
      shift 2
      ;;
    --output-format)
      output_format="${2:-}"
      shift 2
      ;;
    --model)
      model="${2:-}"
      shift 2
      ;;
    --max-turns)
      max_turns="${2:-}"
      shift 2
      ;;
    --permission-mode)
      permission_mode="${2:-}"
      shift 2
      ;;
    --timeout-seconds)
      timeout_seconds="${2:-}"
      shift 2
      ;;
    --poll-interval)
      poll_interval="${2:-}"
      shift 2
      ;;
    --no-partial-messages)
      include_partial_messages=0
      shift
      ;;
    --no-hook-events)
      include_hook_events=0
      shift
      ;;
    --allow-session-persistence)
      disable_session_persistence=0
      shift
      ;;
    --no-skip-permissions)
      skip_permissions=0
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$prompt_file" ]]; then
  echo "--prompt-file is required" >&2
  usage >&2
  exit 2
fi

if [[ -z "$delegate_dir" ]]; then
  echo "--delegate-dir is required" >&2
  usage >&2
  exit 2
fi

if [[ ! -f "$prompt_file" ]]; then
  echo "Prompt file not found: $prompt_file" >&2
  exit 2
fi

if [[ ! -d "$repo_dir" ]]; then
  echo "Repository directory not found: $repo_dir" >&2
  exit 2
fi

mkdir -p "$delegate_dir"

claude_bin="${CLAUDE_BIN:-claude}"
raw_output_file="${delegate_dir}/raw-output.jsonl"
launcher_log_file="${delegate_dir}/launcher.log"
command_file="${delegate_dir}/command.txt"
status_file="${delegate_dir}/status.json"
result_file="${delegate_dir}/result.json"
meta_file="${delegate_dir}/launcher-meta.json"
launcher_result_file="${delegate_dir}/launcher-result.json"
summary_file="${delegate_dir}/summary.md"

{
  echo "started_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "prompt_file=$prompt_file"
  echo "repo_dir=$repo_dir"
  echo "delegate_dir=$delegate_dir"
  echo "raw_output_file=$raw_output_file"
  echo "status_file=$status_file"
  echo "result_file=$result_file"
} > "$launcher_log_file"

cmd=(
  "$claude_bin"
  -p
  --output-format "$output_format"
  --add-dir "$repo_dir"
)

if [[ "$skip_permissions" -eq 1 ]]; then
  cmd+=(--dangerously-skip-permissions)
fi

if [[ "$disable_session_persistence" -eq 1 ]]; then
  cmd+=(--no-session-persistence)
fi

if [[ -n "$model" ]]; then
  cmd+=(--model "$model")
fi

if [[ -n "$max_turns" ]]; then
  cmd+=(--max-turns "$max_turns")
fi

if [[ -n "$permission_mode" ]]; then
  cmd+=(--permission-mode "$permission_mode")
fi

if [[ "$output_format" == "stream-json" && "$include_partial_messages" -eq 1 ]]; then
  cmd+=(--include-partial-messages)
fi

if [[ "$output_format" == "stream-json" && "$include_hook_events" -eq 1 ]]; then
  cmd+=(--include-hook-events)
fi

{
  echo "# Claude Delegate Command"
  echo
  echo "Prompt source:"
  echo "  $prompt_file"
  echo
  echo "Delegate directory:"
  echo "  $delegate_dir"
  echo
  echo "Command:"
  printf '  %q \\\n' "${cmd[@]}"
  echo "  < $prompt_file"
} > "$command_file"

cat > "$meta_file" <<EOF
{
  "delegate_dir": "$delegate_dir",
  "prompt_file": "$prompt_file",
  "repo_dir": "$repo_dir",
  "raw_output_file": "$raw_output_file",
  "status_file": "$status_file",
  "result_file": "$result_file",
  "summary_file": "$summary_file",
  "output_format": "$output_format",
  "permission_mode": "$permission_mode",
  "timeout_seconds": $timeout_seconds,
  "poll_interval": $poll_interval
}
EOF

if [[ ! -f "$status_file" ]]; then
  cat > "$status_file" <<EOF
{
  "status": "launching",
  "message": "Claude process is starting",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
fi

write_summary() {
  local phase="$1"
  cat > "$summary_file" <<EOF
# Delegate Summary

- phase: $phase
- delegate_dir: $delegate_dir
- prompt_file: $prompt_file
- status_file: $status_file
- result_file: $result_file
- raw_output_file: $raw_output_file
- launcher_log_file: $launcher_log_file
- command_file: $command_file
- launcher_meta_file: $meta_file
- launcher_result_file: $launcher_result_file

Recommended inspection order:
1. $summary_file
2. $status_file
3. $result_file
4. $raw_output_file
5. $launcher_log_file
6. $command_file
7. $meta_file
8. $prompt_file
EOF
}

write_summary "launching"

run_claude() {
  if [[ "$timeout_seconds" == "0" ]]; then
    "${cmd[@]}" < "$prompt_file"
    return $?
  fi

  "${cmd[@]}" < "$prompt_file" &
  local claude_pid=$!
  local watcher_pid=""

  (
    sleep "$timeout_seconds"
    if kill -0 "$claude_pid" 2>/dev/null; then
      kill "$claude_pid" 2>/dev/null || true
    fi
  ) &
  watcher_pid=$!

  wait "$claude_pid"
  local exit_code=$?

  kill "$watcher_pid" 2>/dev/null || true
  wait "$watcher_pid" 2>/dev/null || true

  return "$exit_code"
}

set +e
run_claude > >(tee "$raw_output_file") 2>>"$launcher_log_file"
claude_exit_code=$?
set -e

{
  echo "claude_exit_code=$claude_exit_code"
  echo "finished_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} >> "$launcher_log_file"

if [[ -f "$result_file" ]]; then
  write_summary "completed"
  exit "$claude_exit_code"
fi

if [[ "$output_format" == "stream-json" ]]; then
  sleep "$poll_interval"
fi

if [[ -f "$result_file" ]]; then
  write_summary "completed"
  exit "$claude_exit_code"
fi

cat > "$launcher_result_file" <<EOF
{
  "status": "blocked",
  "summary": "Claude process exited before writing result.json",
  "files_changed": [],
  "commands_run": [
    "See $command_file for the exact command"
  ],
  "verification": [
    "launcher observed no result.json at $result_file"
  ],
  "risks": [
    "delegate process may have been interrupted or terminated early",
    "Codex should inspect summary.md, raw-output.jsonl and launcher.log before retrying"
  ]
}
EOF

cat > "$status_file" <<EOF
{
  "status": "blocked",
  "message": "Claude exited without writing result.json",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

write_summary "blocked"

exit "$claude_exit_code"
