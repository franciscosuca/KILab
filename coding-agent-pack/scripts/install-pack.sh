#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PACK_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
CATALOG="$PACK_ROOT/catalog"
CORE_AGENTS="$CATALOG/core/agents"
CORE_SKILLS="$CATALOG/core/skills"

TARGET="$PWD"
HARNESS=""
SCOPE=""
AGENTS_SPEC=""
SKILLS_SPEC=""
AGENTS_SET=0
SKILLS_SET=0
DRY_RUN=0
LIST_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  install-pack.sh --harness <copilot|claude|pi> [options]

Options:
  --target <path>                 Project directory (default: current directory)
  --harness <name>                Harness to install: copilot, claude, or pi
  --scope <project|global>         Installation scope; prompts when omitted
  --agents <all|a,b,c|none>        Agents to install (default: all if no selector is given)
  --skills <all|a,b,c|none>        Skills to install (default: all if no selector is given)
  --all                            Install all available agents and skills
  --list                           List available agents and skills, then exit
  --dry-run                        Show changes without writing files
  -h, --help                       Show this help

Examples:
  install-pack.sh --harness copilot --agents all --skills all
  install-pack.sh --harness copilot --agents test-oracle,vitest --skills feature-planning
  install-pack.sh --harness pi --scope global --skills feature-planning
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || die "--target requires a path"
      TARGET=$2
      shift 2
      ;;
    --harness)
      [ "$#" -ge 2 ] || die "--harness requires a name"
      HARNESS=$2
      shift 2
      ;;
    --scope)
      [ "$#" -ge 2 ] || die "--scope requires project or global"
      SCOPE=$2
      shift 2
      ;;
    --agents)
      [ "$#" -ge 2 ] || die "--agents requires a selector"
      AGENTS_SPEC=$2
      AGENTS_SET=1
      shift 2
      ;;
    --skills)
      [ "$#" -ge 2 ] || die "--skills requires a selector"
      SKILLS_SPEC=$2
      SKILLS_SET=1
      shift 2
      ;;
    --all)
      AGENTS_SPEC=all
      SKILLS_SPEC=all
      AGENTS_SET=1
      SKILLS_SET=1
      shift
      ;;
    --list)
      LIST_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[ -d "$CATALOG" ] || die "catalog not found: $CATALOG"

if [ "$LIST_ONLY" -eq 1 ]; then
  printf 'Agents:\n'
  find "$CORE_AGENTS" -maxdepth 1 -type f -name '*.md' -print \
    | sed "s#^$CORE_AGENTS/##; s/\.md$//" | sort
  printf '\nSkills:\n'
  find "$CORE_SKILLS" -mindepth 1 -maxdepth 1 -type d -print \
    | sed "s#^$CORE_SKILLS/##" | sort
  exit 0
fi

[ -n "$HARNESS" ] || die "--harness is required"
case "$HARNESS" in
  copilot|claude|pi) ;;
  *) die "unsupported harness: $HARNESS" ;;
esac

if [ "$AGENTS_SET" -eq 0 ] && [ "$SKILLS_SET" -eq 0 ]; then
  AGENTS_SPEC=all
  SKILLS_SPEC=all
elif [ "$AGENTS_SET" -eq 0 ]; then
  AGENTS_SPEC=none
elif [ "$SKILLS_SET" -eq 0 ]; then
  SKILLS_SPEC=none
fi

case "$AGENTS_SPEC" in "" ) AGENTS_SPEC=none ;; esac
case "$SKILLS_SPEC" in "" ) SKILLS_SPEC=none ;; esac

TARGET=$(cd -- "$TARGET" 2>/dev/null && pwd) || die "target directory does not exist: $TARGET"

if [ -z "$SCOPE" ]; then
  if [ "$HARNESS" = "copilot" ]; then
    SCOPE=project
    printf 'Copilot resources are project-scoped and will be installed under %s/.github.\n' "$TARGET"
  elif [ -t 0 ]; then
    printf 'Install %s resources for this project or globally? [p/g] ' "$HARNESS"
    read -r answer
    case "${answer:-p}" in
      p|P|project) SCOPE=project ;;
      g|G|global) SCOPE=global ;;
      *) die "installation cancelled" ;;
    esac
  else
    SCOPE=project
    printf 'No interactive terminal; using project scope.\n'
  fi
fi

case "$SCOPE" in
  project|global) ;;
  *) die "scope must be project or global" ;;
esac

if [ "$HARNESS" = "copilot" ] && [ "$SCOPE" != "project" ]; then
  die "Copilot installation is project-scoped; use --scope project"
fi

case "$HARNESS:$SCOPE" in
  copilot:project) DEST="$TARGET/.github" ;;
  claude:project) DEST="$TARGET/.claude" ;;
  claude:global) DEST="${HOME}/.claude" ;;
  pi:project) DEST="$TARGET/.pi" ;;
  pi:global) DEST="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}" ;;
  *) die "unsupported harness/scope combination" ;;
esac

log() {
  printf '%s\n' "$*"
}

copy_file() {
  local source=$1 destination=$2
  if [ "$DRY_RUN" -eq 1 ]; then
    log "COPY $source -> $destination"
    return
  fi
  mkdir -p "$(dirname -- "$destination")"
  cp -p "$source" "$destination"
  log "installed ${destination#$TARGET/}"
}

copy_tree() {
  local source=$1 destination=$2
  if [ "$DRY_RUN" -eq 1 ]; then
    log "COPY TREE $source -> $destination"
    return
  fi
  mkdir -p "$destination"
  cp -pR "$source/." "$destination/"
  log "installed ${destination#$TARGET/}"
}

runtime_name() {
  local name=$1
  case "$name" in
    *-copilot) [ "$HARNESS" = "copilot" ] || return 1; printf '%s' "${name%-copilot}" ;;
    *-claude) [ "$HARNESS" = "claude" ] || return 1; printf '%s' "${name%-claude}" ;;
    *-pi) [ "$HARNESS" = "pi" ] || return 1; printf '%s' "${name%-pi}" ;;
    *)
      case "$name" in
        *-copilot|*-claude|*-pi) return 1 ;;
        *) printf '%s' "$name" ;;
      esac
      ;;
  esac
}

selected() {
  local name=$1 spec=$2 item
  [ "$spec" = "all" ] && return 0
  [ "$spec" = "none" ] && return 1
  IFS=',' read -r -a items <<< "$spec"
  for item in "${items[@]}"; do
    item=$(printf '%s' "$item" | tr -d '[:space:]')
    [ "$item" = "$name" ] && return 0
  done
  return 1
}

frontmatter_value() {
  local file=$1 key=$2
  awk -v key="$key" '
    NR == 1 && $0 ~ /^---[[:space:]]*$/ { inside=1; next }
    inside && $0 ~ /^---[[:space:]]*$/ { exit }
    inside && index($0, key ":") == 1 {
      value=$0
      sub("^[^:]*:[[:space:]]*", "", value)
      sub(/^"/, "", value)
      sub(/"$/, "", value)
      print value
      exit
    }
  ' "$file"
}

frontmatter_line() {
  local file=$1 key=$2
  awk -v key="$key" '
    NR == 1 && $0 ~ /^---[[:space:]]*$/ { inside=1; next }
    inside && $0 ~ /^---[[:space:]]*$/ { exit }
    inside && index($0, key ":") == 1 { print; exit }
  ' "$file"
}

strip_frontmatter() {
  awk '
    NR == 1 && $0 ~ /^---[[:space:]]*$/ { inside=1; next }
    inside && $0 ~ /^---[[:space:]]*$/ { inside=0; next }
    !inside { print }
  ' "$1"
}

claude_tools() {
  local raw token mapped result=""
  raw=$(frontmatter_value "$1" tools || true)
  raw=${raw#\[}
  raw=${raw%\]}
  IFS=',' read -r -a tokens <<< "$raw"
  for token in "${tokens[@]}"; do
    token=$(printf '%s' "$token" | tr -d '[:space:]"')
    [ -n "$token" ] || continue
    case "$token" in
      read) mapped=Read ;;
      search|grep) mapped=Grep ;;
      edit) mapped=Edit ;;
      write) mapped=Write ;;
      execute|bash) mapped=Bash ;;
      agent) mapped=Agent ;;
      *) mapped="$token" ;;
    esac
    if [ -z "$result" ]; then result="$mapped"; else result="$result, $mapped"; fi
  done
  [ -n "$result" ] || result="Read, Edit, Bash, Grep"
  printf '[%s]' "$result"
}

claude_agents() {
  local raw token result=""
  raw=$(frontmatter_value "$1" agents || true)
  raw=${raw#\[}
  raw=${raw%\]}
  IFS=',' read -r -a tokens <<< "$raw"
  for token in "${tokens[@]}"; do
    token=$(printf '%s' "$token" | tr -d '[:space:]"')
    [ -n "$token" ] || continue
    if [ -z "$result" ]; then result="$token"; else result="$result, $token"; fi
  done
  [ -n "$result" ] && printf '[%s]' "$result"
}

render_claude_agent() {
  local source=$1 destination=$2 name description agents_line argument_line
  name=$(frontmatter_line "$source" name || true)
  description=$(frontmatter_line "$source" description || true)
  argument_line=$(frontmatter_line "$source" argument-hint || true)
  agents_line=$(claude_agents "$source" || true)
  if [ "$DRY_RUN" -eq 1 ]; then
    log "RENDER $source -> $destination"
    return
  fi
  mkdir -p "$(dirname -- "$destination")"
  {
    printf '%s\n' '---'
    [ -n "$name" ] && printf '%s\n' "$name"
    [ -n "$description" ] && printf '%s\n' "$description"
    printf 'model: inherit\n'
    printf 'tools: %s\n' "$(claude_tools "$source")"
    [ -n "$agents_line" ] && printf 'agents: %s\n' "$agents_line"
    [ -n "$argument_line" ] && printf '%s\n' "$argument_line"
    printf '%s\n' '---'
    strip_frontmatter "$source"
  } > "$destination"
  log "rendered ${destination#$TARGET/}"
}

render_pi_skill() {
  local source=$1 destination=$2 name description
  name=$(basename "$(dirname -- "$destination")")
  name=$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-//; s/-$//')
  [ -n "$name" ] || die "could not derive a valid Pi skill name for $destination"
  [ "${#name}" -le 64 ] || die "Pi skill name exceeds 64 characters: $name"
  description=$(frontmatter_value "$source" description || true)
  description=${description//\\/\\\\}
  description=${description//\"/\\\"}
  if [ "$DRY_RUN" -eq 1 ]; then
    log "RENDER $source -> $destination"
    return
  fi
  mkdir -p "$(dirname -- "$destination")"
  {
    printf '%s\n' '---'
    printf 'name: %s\n' "$name"
    printf 'description: "%s"\n' "$description"
    printf '%s\n' '---'
    strip_frontmatter "$source"
  } > "$destination"
  log "rendered ${destination#$TARGET/}"
}

render_claude_command() {
  local source=$1 destination=$2
  if [ "$DRY_RUN" -eq 1 ]; then
    log "RENDER $source -> $destination"
    return
  fi
  mkdir -p "$(dirname -- "$destination")"
  strip_frontmatter "$source" > "$destination"
  log "rendered ${destination#$TARGET/}"
}

install_copilot() {
  local file name runtime
  copy_file "$CATALOG/adapters/copilot/copilot-instructions.md" "$DEST/copilot-instructions.md"
  if [ "$AGENTS_SPEC" != "none" ]; then
    for file in "$CORE_AGENTS"/*.md; do
      [ -f "$file" ] || continue
      name=$(basename "$file" .md)
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$AGENTS_SPEC" || continue
      copy_file "$file" "$DEST/agents/$runtime.agent.md"
    done
  fi
  if [ "$SKILLS_SPEC" != "none" ]; then
    for file in "$CORE_SKILLS"/*; do
      [ -d "$file" ] || continue
      name=$(basename "$file")
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$SKILLS_SPEC" || continue
      copy_tree "$file" "$DEST/skills/$runtime"
    done
  fi
}

install_claude() {
  local file name runtime child child_name
  copy_file "$CATALOG/adapters/claude/CLAUDE.md" "$DEST/CLAUDE.md"
  if [ -f "$CATALOG/adapters/claude/commands/implementation-plan.md" ]; then
    copy_file "$CATALOG/adapters/claude/commands/implementation-plan.md" "$DEST/commands/implementation-plan.md"
  fi
  if [ "$AGENTS_SPEC" != "none" ]; then
    for file in "$CORE_AGENTS"/*.md; do
      [ -f "$file" ] || continue
      name=$(basename "$file" .md)
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$AGENTS_SPEC" || continue
      render_claude_agent "$file" "$DEST/agents/$runtime.md"
    done
  fi
  if [ "$SKILLS_SPEC" != "none" ]; then
    for file in "$CORE_SKILLS"/*; do
      [ -d "$file" ] || continue
      name=$(basename "$file")
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$SKILLS_SPEC" || continue
      if [ -f "$file/SKILL.md" ]; then
        render_claude_command "$file/SKILL.md" "$DEST/commands/$runtime.md"
      else
        for child in "$file"/*; do
          [ -f "$child/SKILL.md" ] || continue
          child_name=$(basename "$child")
          render_claude_command "$child/SKILL.md" "$DEST/commands/$child_name.md"
        done
      fi
    done
  fi
}

install_pi() {
  local file name runtime child child_name
  copy_file "$CATALOG/adapters/pi/APPEND_SYSTEM.md" "$DEST/APPEND_SYSTEM.md"
  copy_file "$CATALOG/adapters/pi/extensions/local-models.ts" "$DEST/extensions/local-models.ts"
  if [ "$AGENTS_SPEC" != "none" ]; then
    for file in "$CORE_AGENTS"/*.md; do
      [ -f "$file" ] || continue
      name=$(basename "$file" .md)
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$AGENTS_SPEC" || continue
      render_pi_skill "$file" "$DEST/skills/$runtime/SKILL.md"
    done
  fi
  if [ "$SKILLS_SPEC" != "none" ]; then
    for file in "$CORE_SKILLS"/*; do
      [ -d "$file" ] || continue
      name=$(basename "$file")
      runtime=$(runtime_name "$name") || continue
      selected "$runtime" "$SKILLS_SPEC" || continue
      if [ -f "$file/SKILL.md" ]; then
        render_pi_skill "$file/SKILL.md" "$DEST/skills/$runtime/SKILL.md"
      else
        for child in "$file"/*; do
          [ -f "$child/SKILL.md" ] || continue
          child_name=$(basename "$child")
          render_pi_skill "$child/SKILL.md" "$DEST/skills/$child_name/SKILL.md"
        done
      fi
    done
  fi
}

case "$HARNESS" in
  copilot) install_copilot ;;
  claude) install_claude ;;
  pi) install_pi ;;
esac

log "completed $HARNESS installation at $DEST"
