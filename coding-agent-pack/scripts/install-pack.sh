#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PACK_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
CATALOG="$PACK_ROOT/catalog"
CORE_AGENTS="$CATALOG/core/agents"
CORE_SKILLS="$CATALOG/core/skills"
PI_ADAPTER="$CATALOG/adapters/pi"
PI_CONFIG="$SCRIPT_DIR/pi-config.py"
PI_MODEL_SYNC="$SCRIPT_DIR/sync-pi-models.py"

TARGET="$PWD"
HARNESS=""
SCOPE=""
AGENTS_SPEC=""
SKILLS_SPEC=""
EXTENSIONS_SPEC=""
MODELS_SPEC=""
MODELS_CATALOG="$PI_ADAPTER/models.json"
MODELS_SOURCE=template
MODEL_SCAN_DIR=""
SCAN_PROVIDER_SPEC=""
LMSTUDIO_SCAN_URL=""
OMLX_SCAN_URL=""
AGENTS_SET=0
SKILLS_SET=0
EXTENSIONS_SET=0
MODELS_SET=0
DRY_RUN=0
LIST_ONLY=0
INTERACTIVE=0
ARG_COUNT=$#
ANSWER=""

cleanup_model_scan() {
  if [ -n "$MODEL_SCAN_DIR" ]; then rm -rf -- "$MODEL_SCAN_DIR"; fi
}
trap cleanup_model_scan EXIT

usage() {
  cat <<'EOF'
Usage:
  install-pack.sh
  install-pack.sh --harness <copilot|claude|pi> [options]

Run without arguments in a terminal to answer an interactive questionnaire.

Options:
  -i, --interactive                Ask for every choice; given options become the defaults
  --target <path>                 Project directory (default: current directory)
  --harness <name>                Harness to install: copilot, claude, or pi
  --scope <project|global>         Installation scope; prompts when omitted
  --agents <all|a,b,c|none>        Agents to install (default: all if no selector is given)
  --skills <all|a,b,c|none>        Skills to install (default: all if no selector is given)
  --all                            Install all available agents and skills
  --extensions <all|a,b,c|none>    Pi only: optional extensions/packages (default: none)
  --models <all|a,b|none>          Pi only: local model providers to add to models.json (default: none)
  --list                           List agents, skills, Pi extensions, and Pi models, then exit
  --dry-run                        Show changes without writing files
  -h, --help                       Show this help

Examples:
  install-pack.sh
  install-pack.sh --harness copilot --agents all --skills all
  install-pack.sh --harness copilot --agents test-oracle,vitest --skills feature-planning
  install-pack.sh --harness pi --scope global --skills feature-planning
  install-pack.sh --harness pi --scope global --all --extensions all --models lmstudio,omlx
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
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

in_list() {
  case "
$2
" in
    *"
$1
"*) return 0 ;;
  esac
  return 1
}

have_python() {
  python3 -c 'import sys; sys.exit(sys.version_info < (3, 7))' >/dev/null 2>&1
}

available_agents() {
  local file runtime
  for file in "$CORE_AGENTS"/*.md; do
    [ -f "$file" ] || continue
    runtime=$(runtime_name "$(basename "$file" .md)") || continue
    printf '%s\n' "$runtime"
  done
}

available_skills() {
  local file runtime
  for file in "$CORE_SKILLS"/*; do
    [ -d "$file" ] || continue
    runtime=$(runtime_name "$(basename "$file")") || continue
    printf '%s\n' "$runtime"
  done
}

# Bundled Pi extensions: *.ts and *.js files or extension directories.
pi_extension_files() {
  local file
  for file in "$PI_ADAPTER/extensions"/*; do
    if [ -d "$file" ]; then
      printf '%s\n' "$file"
    else
      case "$file" in
        *.ts|*.js) if [ -f "$file" ]; then printf '%s\n' "$file"; fi ;;
      esac
    fi
  done
}

pi_extension_name() {
  local name
  name=$(basename "$1")
  case "$name" in
    *.ts|*.js) name=${name%.*} ;;
  esac
  printf '%s' "$name"
}

# Pi packages from packages.txt: one "name source" pair per line.
pi_packages() {
  local name source rest
  [ -f "$PI_ADAPTER/packages.txt" ] || return 0
  while read -r name source rest || [ -n "$name" ]; do
    case "$name" in ''|\#*) continue ;; esac
    if [ -n "$source" ]; then printf '%s %s\n' "$name" "$source"; fi
  done < "$PI_ADAPTER/packages.txt"
}

# pi_extension_menu [bundled]: optional choices; local-models is managed automatically.
pi_extension_menu() {
  local file name source
  while IFS= read -r file; do
    name=$(pi_extension_name "$file")
    [ "$name" = "local-models" ] && continue
    printf '%s (bundled extension: %s)\n' "$name" "$(basename "$file")"
  done < <(pi_extension_files)
  if [ "${1:-}" = "bundled" ]; then
    return 0
  fi
  while read -r name source; do
    printf '%s (Pi package: %s)\n' "$name" "$source"
  done < <(pi_packages)
}

pi_packages_selected() {
  local name source
  while read -r name source; do
    case ",$EXTENSIONS_SPEC," in
      ,all,|*",$name,"*) return 0 ;;
    esac
  done < <(pi_packages)
  return 1
}

default_extensions() {
  local file name names=""
  while IFS= read -r file; do
    name=$(pi_extension_name "$file")
    [ "$name" = "local-models" ] && continue
    names="${names:+$names,}$name"
  done < <(pi_extension_files)
  printf '%s' "${names:-none}"
}

# Catalog models, one "provider<TAB>baseUrl<TAB>model id" line each (requires python3).
pi_models() {
  python3 "$PI_CONFIG" list-models "$PI_ADAPTER/models.json"
}

pi_model_providers() {
  pi_models | awk -F '\t' '!seen[$1]++ { print $1 }'
}

pi_model_menu() {
  pi_models | awk -F '\t' '
    !($1 in count) { order[++n] = $1; url[$1] = $2 }
    { count[$1]++ }
    END { for (i = 1; i <= n; i++) printf "%s (%d models at %s)\n", order[i], count[order[i]], url[order[i]] }
  '
}

# print_pi_models <all|provider,...>: catalog model IDs grouped by provider.
print_pi_models() {
  pi_models | awk -F '\t' -v spec=",$1," '
    spec != ",all," && index(spec, "," $1 ",") == 0 { next }
    $1 != last { printf "%s (%s)\n", $1, $2; last = $1 }
    { printf "  %s\n", $3 }
  '
}

pi_model_base_url() {
  local configured
  configured=$(python3 - "$(pi_target_models_path)" "$1" <<'PY'
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

try:
    providers = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).get("providers", {})
    candidate = providers.get(sys.argv[2], {}).get("baseUrl")
    parsed = urlsplit(candidate) if isinstance(candidate, str) else None
    if parsed and parsed.hostname in {"localhost", "127.0.0.1", "::1"} and parsed.port:
        print(candidate)
except (OSError, json.JSONDecodeError, ValueError):
    pass
PY
)
  if [ -n "$configured" ]; then
    printf '%s' "$configured"
  else
    pi_models | awk -F '\t' -v provider="$1" '$1 == provider { print $2; exit }'
  fi
}

pi_target_models_path() {
  if [ "$SCOPE" = project ]; then
    printf '%s/.pi/models.json' "$TARGET"
  else
    printf '%s/models.json' "${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
  fi
}

url_port() {
  python3 -c 'from urllib.parse import urlsplit; import sys; print(urlsplit(sys.argv[1]).port or "")' "$1"
}

print_models_warning() {
  printf 'WARNING: The installer only adds model IDs to models.json; it does not download models.\n'
  printf '         Download each model manually in LM Studio (Discover tab or "lms get") or oMLX\n'
  printf '         (model downloader in the /admin dashboard) before selecting it in Pi.\n'
}

scan_pi_model_catalog() {
  local options provider label default_url default_port port
  local -a sync_args

  printf '\nLive scanning supports only LM Studio and oMLX. Start each selected server before continuing.\n'
  options='both (LM Studio and oMLX)
lmstudio (LM Studio only)
omlx (oMLX only)'
  choose_one "Which local servers should I scan?" "$options" both
  case "$ANSWER" in
    both) SCAN_PROVIDER_SPEC=all ;;
    *) SCAN_PROVIDER_SPEC=$ANSWER ;;
  esac

  MODEL_SCAN_DIR=$(mktemp -d "${TMPDIR:-/tmp}/kilab-pi-model-scan.XXXXXX") \
    || die 'could not create a temporary model-scan directory'
  chmod 700 "$MODEL_SCAN_DIR"
  python3 - "$PI_ADAPTER/models.json" "$MODEL_SCAN_DIR/models.json" "$SCAN_PROVIDER_SPEC" "$(pi_target_models_path)" <<'PY'
import json
import sys
from pathlib import Path

source_path, destination_path, selected, existing_path = sys.argv[1:]
config = json.loads(Path(source_path).read_text(encoding="utf-8"))
providers = config.get("providers", {})
names = ["lmstudio", "omlx"] if selected == "all" else selected.split(",")
try:
    existing = json.loads(Path(existing_path).read_text(encoding="utf-8")).get("providers", {})
except (OSError, json.JSONDecodeError):
    existing = {}
config["providers"] = {name: providers[name] for name in names}
for name in names:
    current = existing.get(name)
    if isinstance(current, dict) and isinstance(current.get("apiKey"), str):
        config["providers"][name]["apiKey"] = current["apiKey"]
Path(destination_path).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
PY

  sync_args=(--config "$MODEL_SCAN_DIR/models.json" --require-api)
  for provider in lmstudio omlx; do
    case ",$SCAN_PROVIDER_SPEC," in
      ,all,|*,"$provider",*) ;;
      *) continue ;;
    esac
    default_url=$(pi_model_base_url "$provider")
    default_port=$(url_port "$default_url")
    [ -n "$default_port" ] || die "could not determine the default $provider port from the template"
    if [ "$provider" = lmstudio ]; then label='LM Studio'; else label='oMLX'; fi
    printf '\n%s endpoint shown in the template: %s\n' "$label" "$default_url"
    while :; do
      ask "$label server port [$default_port]: "
      port=${ANSWER:-$default_port}
      if [[ "$port" =~ ^[0-9]{1,5}$ ]] && ((10#$port >= 1 && 10#$port <= 65535)); then
        break
      fi
      printf 'Enter a port from 1 to 65535.\n'
    done
    if [ "$provider" = lmstudio ]; then
      default_url="http://localhost:$port/v1"
      LMSTUDIO_SCAN_URL=$default_url
    else
      default_url="http://127.0.0.1:$port/v1"
      OMLX_SCAN_URL=$default_url
    fi
    sync_args+=(--provider "$provider" --base-url "$provider=$default_url")
  done

  printf '\nQuerying the selected local server APIs...\n'
  if ! python3 "$PI_MODEL_SYNC" "${sync_args[@]}"; then
    die 'live model scan failed; check that the selected server(s) are running and the ports/API keys are correct'
  fi
  MODELS_CATALOG="$MODEL_SCAN_DIR/models.json"
  MODELS_SOURCE=scan
  printf '\nModels discovered on this machine:\n'
  print_pi_models all | sed 's/^/  /'
}

normalize_spec() {
  local spec
  spec=$(printf '%s' "$1" | tr -d '[:space:]')
  printf '%s' "${spec:-none}"
}

# check_spec <option> <spec> <available names>: rejects unknown names before anything is written.
check_spec() {
  local option=$1 spec=$2 names=$3 item count=0
  case "$spec" in all|none) return 0 ;; esac
  while IFS= read -r item; do
    [ -n "$item" ] || continue
    count=$((count + 1))
    in_list "$item" "$names" \
      || die "unknown $option value: $item (available: $(printf '%s' "$names" | tr '\n' ',' | sed 's/,/, /g'))"
  done <<EOF
$(printf '%s\n' "$spec" | tr ',' '\n')
EOF
  [ "$count" -gt 0 ] || die "$option requires all, none, or a comma-separated list"
}

ask() {
  printf '%s' "$1"
  if ! read -r ANSWER; then
    printf '\n'
    die "installation cancelled"
  fi
}

print_menu() {
  local line index=0
  while IFS= read -r line; do
    index=$((index + 1))
    printf '  %2d) %s\n' "$index" "$line"
  done <<EOF
$1
EOF
}

# menu_value <options> <answer>: prints the option name chosen by number or name.
menu_value() {
  local line index=0
  while IFS= read -r line; do
    index=$((index + 1))
    if [ "$2" = "$index" ] || [ "$2" = "${line%% *}" ]; then
      printf '%s' "${line%% *}"
      return 0
    fi
  done <<EOF
$1
EOF
  return 1
}

# choose_one <question> <options> [default]: sets ANSWER to one option name.
choose_one() {
  local options=$2 default=${3:-} value
  printf '\n%s\n' "$1"
  print_menu "$options"
  while :; do
    if [ -n "$default" ]; then ask "Choose [$default]: "; else ask "Choose: "; fi
    [ -n "$ANSWER" ] || ANSWER=$default
    if value=$(menu_value "$options" "$ANSWER"); then
      ANSWER=$value
      return 0
    fi
    printf 'Please enter a number or a name from the list.\n'
  done
}

# choose_many <question> <options> <default>: sets ANSWER to all, none, or a comma-separated list.
choose_many() {
  local options=$2 default=$3 token value result invalid
  printf '\n%s\n' "$1"
  print_menu "$options"
  printf '  Enter numbers or names separated by commas or spaces, "all", or "none".\n'
  while :; do
    ask "Select [$default]: "
    [ -n "$ANSWER" ] || ANSWER=$default
    value=$(printf '%s' "$ANSWER" | tr '[:upper:]' '[:lower:]')
    case "$value" in
      all|none) ANSWER=$value; return 0 ;;
    esac
    result=""
    invalid=""
    while IFS= read -r token; do
      [ -n "$token" ] || continue
      if value=$(menu_value "$options" "$token"); then
        case ",$result," in
          *",$value,"*) ;;
          *) result="${result:+$result,}$value" ;;
        esac
      else
        invalid="${invalid:+$invalid, }$token"
      fi
    done <<EOF
$(printf '%s\n' "$ANSWER" | tr ', \t' '\n\n\n')
EOF
    if [ -z "$invalid" ] && [ -n "$result" ]; then
      ANSWER=$result
      return 0
    fi
    printf 'Unknown choice: %s\n' "${invalid:-$ANSWER}"
  done
}

confirm() {
  while :; do
    ask "$1 [Y/n] "
    case "$ANSWER" in
      ''|y|Y|yes|Yes|YES) return 0 ;;
      n|N|no|No|NO) return 1 ;;
    esac
  done
}

ask_target() {
  local path resolved
  while :; do
    ask "Project directory [$TARGET]: "
    path=${ANSWER:-$TARGET}
    case "$path" in
      \~) path=$HOME ;;
      \~/*) path="$HOME/${path#\~/}" ;;
    esac
    if resolved=$(CDPATH='' cd -- "$path" 2>/dev/null && pwd); then
      TARGET=$resolved
      return 0
    fi
    printf 'Directory not found: %s\n' "$path"
  done
}

run_questionnaire() {
  local options default
  printf 'Coding agent pack installer. Press Enter to accept the [default] answer.\n'

  choose_one "Which harness do you want to install for?" "copilot (GitHub Copilot)
claude (Claude Code)
pi (Pi coding agent)" "$HARNESS"
  HARNESS=$ANSWER

  if [ "$HARNESS" = "copilot" ]; then
    SCOPE=project
    printf '\nCopilot resources are project-scoped and are installed under <project>/.github.\n'
  else
    choose_one "Where do you want to install the $HARNESS resources?" "project (this project only)
global (all projects of your user)" "${SCOPE:-project}"
    SCOPE=$ANSWER
  fi
  if [ "$SCOPE" = "project" ]; then
    printf '\n'
    ask_target
  fi

  options=$(available_agents)
  if [ -n "$options" ]; then
    choose_many "Which agents do you want to install?" "$options" "$AGENTS_SPEC"
    AGENTS_SPEC=$ANSWER
  fi
  options=$(available_skills)
  if [ -n "$options" ]; then
    choose_many "Which skills do you want to install?" "$options" "$SKILLS_SPEC"
    SKILLS_SPEC=$ANSWER
  fi

  if [ "$HARNESS" != "pi" ]; then
    EXTENSIONS_SET=0
    MODELS_SET=0
    return 0
  fi

  if have_python; then
    options=$(pi_extension_menu)
    printf '\nPi packages are third-party code that Pi downloads and runs on its next start.\n'
  else
    options=$(pi_extension_menu bundled)
    printf '\nSkipping Pi packages: python3 3.7 or newer is required to add them to settings.json.\n'
  fi
  EXTENSIONS_SPEC=$(normalize_spec "$EXTENSIONS_SPEC")
  if [ -n "$options" ]; then
    default=$EXTENSIONS_SPEC
    [ "$EXTENSIONS_SET" -eq 1 ] || default=$(default_extensions)
    choose_many "Which optional Pi extensions/packages do you want to install?" "$options" "$default"
    EXTENSIONS_SPEC=$ANSWER
    if [ "$EXTENSIONS_SPEC" = "all" ] && ! have_python; then
      EXTENSIONS_SPEC=$(default_extensions)
    fi
  fi
  EXTENSIONS_SET=1

  if have_python; then
    choose_one "Where should the Pi model choices come from?" "template (Use the static model IDs bundled with this pack)
scan (Discover models currently available on this machine)" template
    MODELS_SOURCE=$ANSWER
    if [ "$MODELS_SOURCE" = scan ]; then
      scan_pi_model_catalog
      printf '\n'
    else
      printf '\nLocal models for Pi (static template catalog):\n'
      print_pi_models all | sed 's/^/  /'
    fi
    print_models_warning
    default=$MODELS_SPEC
    [ "$MODELS_SET" -eq 1 ] || default=all
    choose_many "Which model providers do you want to add to Pi's models.json?" "$(pi_model_menu)" "$(normalize_spec "$default")"
    MODELS_SPEC=$ANSWER
    if [ "$MODELS_SOURCE" = scan ] && [ "$MODELS_SPEC" = all ]; then
      MODELS_SPEC=$(pi_model_providers | tr '\n' ',' | sed 's/,$//')
    fi
  else
    printf '\nSkipping Pi models: python3 3.7 or newer is required to update models.json.\n'
    MODELS_SPEC=none
  fi
  MODELS_SET=1
}

shell_quote() {
  case "$1" in
    ''|*[!A-Za-z0-9_,./:=@%+-]*) printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")" ;;
    *) printf '%s' "$1" ;;
  esac
}

equivalent_command() {
  local command
  command="$(shell_quote "$SCRIPT_DIR/install-pack.sh") --harness $HARNESS --scope $SCOPE"
  if [ "$SCOPE" = "project" ]; then
    command="$command --target $(shell_quote "$TARGET")"
  fi
  command="$command --agents $(shell_quote "$AGENTS_SPEC") --skills $(shell_quote "$SKILLS_SPEC")"
  if [ "$HARNESS" = "pi" ]; then
    command="$command --extensions $(shell_quote "$EXTENSIONS_SPEC") --models $(shell_quote "$MODELS_SPEC")"
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    command="$command --dry-run"
  fi
  printf '%s' "$command"
}

print_summary() {
  printf '\nSummary:\n'
  printf '  Harness:     %s\n' "$HARNESS"
  printf '  Scope:       %s\n' "$SCOPE"
  printf '  Destination: %s\n' "$DEST"
  printf '  Agents:      %s\n' "$AGENTS_SPEC"
  printf '  Skills:      %s\n' "$SKILLS_SPEC"
  if [ "$HARNESS" = "pi" ]; then
    printf '  Pi additions: %s\n' "$EXTENSIONS_SPEC"
    if [ "$SCOPE" = "project" ]; then
      printf '  Model adapter: local-models (automatic)\n'
    fi
    printf '  Models:      %s (%s source)\n' "$MODELS_SPEC" "$MODELS_SOURCE"
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '  Dry run:     no files are written\n'
  fi
  if [ "$MODELS_SOURCE" = scan ]; then
    printf '\nThe one-time command below uses the static template model list; live scan results are machine-specific.\n'
  fi
  printf '\n'
  print_overwrite_note
  printf '\nEquivalent one-time command:\n  %s\n\n' "$(equivalent_command)"
}

# Name of the instructions file the installer writes for the selected harness.
instructions_label() {
  case "$HARNESS" in
    copilot) printf 'copilot-instructions.md' ;;
    claude) printf 'CLAUDE.md' ;;
    *) printf 'APPEND_SYSTEM.md' ;;
  esac
}

# Resource files are replaced rather than merged; say so before asking to proceed.
print_overwrite_note() {
  local resources
  case "$HARNESS" in
    copilot) resources='selected agents and skills' ;;
    claude) resources='selected agents and commands' ;;
    *) resources='selected agents, skills, and extensions' ;;
  esac
  printf 'WARNING: existing files at the destination are overwritten, not merged:\n'
  printf '         the %s instructions file and %s.\n' "$(instructions_label)" "$resources"
  if [ "$HARNESS" = pi ]; then
    printf '         settings.json and models.json are merged. Nothing is ever deleted.\n'
  else
    printf '         Nothing is ever deleted.\n'
  fi
  return 0
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
    --extensions)
      [ "$#" -ge 2 ] || die "--extensions requires a selector"
      EXTENSIONS_SPEC=$2
      EXTENSIONS_SET=1
      shift 2
      ;;
    --models)
      [ "$#" -ge 2 ] || die "--models requires a selector"
      MODELS_SPEC=$2
      MODELS_SET=1
      shift 2
      ;;
    -i|--interactive)
      INTERACTIVE=1
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
  printf '\nOptional Pi extensions/packages (--extensions):\n'
  pi_extension_menu
  printf 'Project-scoped installs add local-models support automatically.\n'
  printf '\nPi models (--models; download them manually before use):\n'
  if have_python; then
    print_pi_models all
  else
    printf 'python3 3.7 or newer is required to list models.\n'
  fi
  exit 0
fi

if [ "$INTERACTIVE" -eq 0 ] && [ "$ARG_COUNT" -eq 0 ] && [ -t 0 ]; then
  INTERACTIVE=1
fi
if [ "$INTERACTIVE" -eq 1 ]; then
  [ -t 0 ] || die "--interactive requires a terminal; pass --harness and the other options instead"
  case "$HARNESS" in
    ''|copilot|claude|pi) ;;
    *) die "unsupported harness: $HARNESS" ;;
  esac
  case "$SCOPE" in
    ''|project|global) ;;
    *) die "scope must be project or global" ;;
  esac
  if [ "$AGENTS_SET" -eq 0 ]; then
    if [ "$SKILLS_SET" -eq 1 ]; then AGENTS_SPEC=none; else AGENTS_SPEC=all; fi
  fi
  if [ "$SKILLS_SET" -eq 0 ]; then
    if [ "$AGENTS_SET" -eq 1 ]; then SKILLS_SPEC=none; else SKILLS_SPEC=all; fi
  fi
  AGENTS_SPEC=$(normalize_spec "$AGENTS_SPEC")
  SKILLS_SPEC=$(normalize_spec "$SKILLS_SPEC")
  TARGET=$(cd -- "$TARGET" 2>/dev/null && pwd) || die "target directory does not exist: $TARGET"
  run_questionnaire
  AGENTS_SET=1
  SKILLS_SET=1
fi

[ -n "$HARNESS" ] || die "--harness is required; run without arguments (or with --interactive) in a terminal to be asked instead"
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

if [ "$HARNESS" = "pi" ]; then
  [ "$EXTENSIONS_SET" -eq 1 ] || EXTENSIONS_SPEC=$(default_extensions)
  EXTENSIONS_SPEC=$(normalize_spec "$EXTENSIONS_SPEC")
  MODELS_SPEC=$(normalize_spec "$MODELS_SPEC")
  check_spec --extensions "$EXTENSIONS_SPEC" "$(pi_extension_menu | sed 's/ .*//')"
  if [ "$MODELS_SPEC" != "none" ] || pi_packages_selected; then
    have_python || die "python3 3.7 or newer is required to install Pi packages and models"
  fi
  if [ "$MODELS_SPEC" != "none" ]; then
    check_spec --models "$MODELS_SPEC" "$(pi_model_providers)"
  fi
else
  [ "$EXTENSIONS_SET" -eq 0 ] || die "--extensions is only supported with --harness pi"
  [ "$MODELS_SET" -eq 0 ] || die "--models is only supported with --harness pi"
fi

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

if [ "$INTERACTIVE" -eq 1 ]; then
  print_summary
  confirm "Proceed?" || die "installation cancelled"
fi

log() {
  printf '%s\n' "$*"
}

# write_label <destination> <fresh-label> <existing-label>: must be evaluated BEFORE writing.
# Lets every writer announce when it is about to replace something that already exists.
write_label() {
  if [ -e "$1" ]; then printf '%s' "$3"; else printf '%s' "$2"; fi
}

copy_file() {
  local source=$1 destination=$2 planned done_verb
  planned=$(write_label "$destination" COPY REPLACE)
  if [ "$DRY_RUN" -eq 1 ]; then
    log "$planned $source -> $destination"
    return
  fi
  done_verb=$(write_label "$destination" installed replaced)
  mkdir -p "$(dirname -- "$destination")"
  cp -p "$source" "$destination"
  log "$done_verb ${destination#$TARGET/}"
}

copy_tree() {
  local source=$1 destination=$2 planned done_verb
  planned=$(write_label "$destination" "COPY TREE" "REPLACE TREE")
  if [ "$DRY_RUN" -eq 1 ]; then
    log "$planned $source -> $destination"
    return
  fi
  done_verb=$(write_label "$destination" installed updated)
  mkdir -p "$destination"
  cp -pR "$source/." "$destination/"
  log "$done_verb ${destination#$TARGET/}"
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
  local source=$1 destination=$2 name description agents_line argument_line done_verb
  name=$(frontmatter_line "$source" name || true)
  description=$(frontmatter_line "$source" description || true)
  argument_line=$(frontmatter_line "$source" argument-hint || true)
  agents_line=$(claude_agents "$source" || true)
  if [ "$DRY_RUN" -eq 1 ]; then
    log "$(write_label "$destination" RENDER REPLACE) $source -> $destination"
    return
  fi
  done_verb=$(write_label "$destination" rendered replaced)
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
  log "$done_verb ${destination#$TARGET/}"
}

render_pi_skill() {
  local source=$1 destination=$2 name description done_verb
  name=$(basename "$(dirname -- "$destination")")
  name=$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-//; s/-$//')
  [ -n "$name" ] || die "could not derive a valid Pi skill name for $destination"
  [ "${#name}" -le 64 ] || die "Pi skill name exceeds 64 characters: $name"
  description=$(frontmatter_value "$source" description || true)
  description=${description//\\/\\\\}
  description=${description//\"/\\\"}
  if [ "$DRY_RUN" -eq 1 ]; then
    log "$(write_label "$destination" RENDER REPLACE) $source -> $destination"
    return
  fi
  done_verb=$(write_label "$destination" rendered replaced)
  mkdir -p "$(dirname -- "$destination")"
  {
    printf '%s\n' '---'
    printf 'name: %s\n' "$name"
    printf 'description: "%s"\n' "$description"
    printf '%s\n' '---'
    strip_frontmatter "$source"
  } > "$destination"
  log "$done_verb ${destination#$TARGET/}"
}

render_claude_command() {
  local source=$1 destination=$2 done_verb
  if [ "$DRY_RUN" -eq 1 ]; then
    log "$(write_label "$destination" RENDER REPLACE) $source -> $destination"
    return
  fi
  done_verb=$(write_label "$destination" rendered replaced)
  mkdir -p "$(dirname -- "$destination")"
  strip_frontmatter "$source" > "$destination"
  log "$done_verb ${destination#$TARGET/}"
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

run_pi_config() {
  local command=$1
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    set -- --dry-run "$@"
  fi
  python3 "$PI_CONFIG" "$command" "$@"
}

install_pi_extensions() {
  local file name source
  while IFS= read -r file; do
    name=$(pi_extension_name "$file")
    if [ "$name" = "local-models" ]; then
      [ "$SCOPE" = "project" ] || continue
    else
      selected "$name" "$EXTENSIONS_SPEC" || continue
    fi
    if [ -d "$file" ]; then
      copy_tree "$file" "$DEST/extensions/$(basename "$file")"
    else
      copy_file "$file" "$DEST/extensions/$(basename "$file")"
    fi
  done < <(pi_extension_files)
  set --
  while read -r name source; do
    selected "$name" "$EXTENSIONS_SPEC" || continue
    set -- ${1+"$@"} "$source"
  done < <(pi_packages)
  if [ "$#" -gt 0 ]; then
    run_pi_config add-packages --label "${DEST#"$TARGET"/}/settings.json" "$DEST/settings.json" "$@" \
      || die "could not update $DEST/settings.json"
  fi
}

install_pi_models() {
  local provider
  [ "$MODELS_SPEC" != "none" ] || return 0
  set --
  while IFS= read -r provider; do
    selected "$provider" "$MODELS_SPEC" || continue
    set -- ${1+"$@"} "$provider"
  done < <(pi_model_providers)
  if [ "$MODELS_SOURCE" = scan ]; then
    set -- --update-base-url --label "${DEST#"$TARGET"/}/models.json" "$MODELS_CATALOG" "$DEST/models.json" "$@"
  else
    set -- --label "${DEST#"$TARGET"/}/models.json" "$MODELS_CATALOG" "$DEST/models.json" "$@"
  fi
  run_pi_config merge-models "$@" || die "could not update $DEST/models.json"
}

install_pi() {
  local file name runtime child child_name
  copy_file "$CATALOG/adapters/pi/APPEND_SYSTEM.md" "$DEST/APPEND_SYSTEM.md"
  install_pi_extensions
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
  install_pi_models
}

case "$HARNESS" in
  copilot) install_copilot ;;
  claude) install_claude ;;
  pi) install_pi ;;
esac

log "completed $HARNESS installation at $DEST"

if [ "$HARNESS" = "pi" ] && [ "$MODELS_SPEC" != "none" ]; then
  printf '\n'
  print_models_warning
  printf '\nSelected models for %s/models.json:\n' "$DEST"
  print_pi_models "$MODELS_SPEC"
fi
