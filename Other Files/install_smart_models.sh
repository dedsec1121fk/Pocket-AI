#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
CHOICE="${1:-best}"

model_repo() {
  case "$1" in
    smart) echo "Qwen/Qwen3-0.6B-GGUF|Qwen3-0.6B-Q8_0.gguf|1050000000|Qwen3 0.6B Smart" ;;
    ultra) echo "Qwen/Qwen3-1.7B-GGUF|Qwen3-1.7B-Q4_K_M.gguf|1650000000|Qwen3 1.7B Ultra" ;;
    pro) echo "Qwen/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf|3800000000|Qwen3 4B Pro" ;;
    max) echo "Qwen/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf|7000000000|Qwen3 8B Max" ;;
    *) return 1 ;;
  esac
}

ram_bytes() { awk '/MemTotal:/ {print $2 * 1024}' /proc/meminfo 2>/dev/null || echo 0; }
available_ram_bytes() { awk '/MemAvailable:/ {print $2 * 1024}' /proc/meminfo 2>/dev/null || echo 0; }
free_bytes() { df -Pk "$MODELS_DIR" 2>/dev/null | awk 'NR==2 {print $4 * 1024}'; }
is_64_bit() { [[ "$(getconf LONG_BIT 2>/dev/null || echo 32)" == "64" ]]; }

select_best() {
  local total available storage
  total="$(ram_bytes)"; available="$(available_ram_bytes)"; storage="$(free_bytes)"
  if ! is_64_bit; then
    echo "none"; return
  fi
  # Match the download to total RAM, live MemAvailable, and storage. Runtime
  # still performs a stricter per-question thermal and working-set check.
  if (( total >= 13500000000 && available >= 6500000000 && storage >= 7500000000 )); then
    echo "max"
  elif (( total >= 7800000000 && available >= 3400000000 && storage >= 4000000000 )); then
    echo "pro"
  elif (( total >= 4800000000 && available >= 1500000000 && storage >= 2100000000 )); then
    echo "ultra"
  elif (( total >= 3000000000 && available >= 850000000 && storage >= 1300000000 )); then
    echo "smart"
  else
    echo "none"
  fi
}

if [[ "$CHOICE" == "--help" || "$CHOICE" == "-h" ]]; then
  cat <<'HELP'
Usage:
  bash "Other Files/install_smart_models.sh" best    # strongest safe match for this phone
  bash "Other Files/install_smart_models.sh" auto    # same as best
  bash "Other Files/install_smart_models.sh" smart   # Qwen3 0.6B Q8_0
  bash "Other Files/install_smart_models.sh" ultra   # Qwen3 1.7B Q4_K_M
  bash "Other Files/install_smart_models.sh" pro     # Qwen3 4B Q4_K_M
  bash "Other Files/install_smart_models.sh" max     # Qwen3 8B Q4_K_M
  bash "Other Files/install_smart_models.sh" all     # all four models

Downloads resume after an interruption. Every completed model is verified with
the official Hugging Face LFS SHA-256 object ID, byte size, and GGUF header.
HELP
  exit 0
fi

case "$CHOICE" in
  best|auto)
    CHOICE="$(select_best)"
    if [[ "$CHOICE" == "none" ]]; then
      echo "This phone should use the bundled Quality model; no larger optional model is safely recommended."
      exit 0
    fi
    echo "Strongest safe automatic match: $CHOICE"
    ;;
  smart|ultra|pro|max|all) ;;
  *) echo "Use best, auto, smart, ultra, pro, max, or all." >&2; exit 2 ;;
esac

if [[ ! -d "/data/data/com.termux/files/usr" ]]; then
  echo "This downloader is intended for Termux on Android." >&2
  exit 1
fi

pkg install -y curl coreutils python
mkdir -p "$MODELS_DIR"

available_bytes() { df -Pk "$MODELS_DIR" | awk 'NR==2 {print $4 * 1024}'; }

official_metadata() {
  local repo="$1" filename="$2" metadata_file="$3"
  local api="https://huggingface.co/api/models/${repo}/tree/main?recursive=true&expand=true&limit=1000"
  curl --fail --silent --show-error --location --retry 8 --retry-delay 3 --output "$metadata_file" "$api"
  python - "$metadata_file" "$filename" <<'PY'
import json,re,sys
path,wanted=sys.argv[1:]
data=json.load(open(path,encoding='utf-8'))
if isinstance(data,dict): data=data.get('siblings') or data.get('items') or []
for entry in data:
    item=str(entry.get('path') or entry.get('rfilename') or '')
    if item==wanted or item.endswith('/'+wanted):
        lfs=entry.get('lfs') or {}
        oid=str(lfs.get('oid') or entry.get('oid') or '').removeprefix('sha256:')
        size=int(lfs.get('size') or entry.get('size') or 0)
        if re.fullmatch(r'[0-9a-fA-F]{64}',oid) and size>50_000_000:
            print(oid.lower(),size); raise SystemExit(0)
raise SystemExit('Official LFS SHA-256 metadata was not found for '+wanted)
PY
}

valid_existing() {
  local target="$1" expected="$2" size="$3"
  [[ -f "$target" ]] || return 1
  [[ "$(head -c 4 "$target")" == "GGUF" ]] || return 1
  [[ "$(stat -c %s "$target")" == "$size" ]] || return 1
  [[ "$(sha256sum "$target" | awk '{print $1}')" == "$expected" ]]
}

install_one() {
  local key="$1" spec repo name fallback_min label
  spec="$(model_repo "$key")"
  IFS='|' read -r repo name fallback_min label <<<"$spec"
  local target="$MODELS_DIR/$name" partial="$target.partial" metadata="$target.metadata.tmp"
  local url="https://huggingface.co/${repo}/resolve/main/${name}?download=true"

  echo; echo "Retrieving official metadata for $label..."
  local result expected expected_size
  result="$(official_metadata "$repo" "$name" "$metadata")"; rm -f "$metadata"
  read -r expected expected_size <<<"$result"

  if valid_existing "$target" "$expected" "$expected_size"; then
    printf '%s  %s\n' "$expected" "$name" > "$target.sha256"
    echo "$label is already installed and verified."
    return
  fi
  rm -f "$target" "$target.sha256" "$target.source.json"

  local required free
  required=$((expected_size + 450000000)); (( required < fallback_min )) && required="$fallback_min"
  free="$(available_bytes)"
  if (( free < required )); then
    echo "Not enough free storage for $label. Available $free; required $required bytes." >&2
    exit 1
  fi

  echo "Downloading $label (interrupted downloads resume automatically)..."
  curl --fail --location --retry 12 --retry-delay 3 --continue-at - --output "$partial" "$url"
  local actual actual_size
  actual_size="$(stat -c %s "$partial")"; actual="$(sha256sum "$partial" | awk '{print $1}')"
  [[ "$actual_size" == "$expected_size" ]] || { echo "Size verification failed." >&2; exit 1; }
  [[ "$actual" == "$expected" ]] || { echo "SHA-256 verification failed." >&2; exit 1; }
  [[ "$(head -c 4 "$partial")" == "GGUF" ]] || { echo "Invalid GGUF header." >&2; exit 1; }

  mv -f "$partial" "$target"
  printf '%s  %s\n' "$expected" "$name" > "$target.sha256"
  cat > "$target.source.json" <<META
{"repository":"$repo","filename":"$name","download_url":"$url","sha256":"$expected","size_bytes":$expected_size,"verification":"official Hugging Face LFS SHA-256, byte size, and GGUF header"}
META
  echo "$label installed and verified: $(du -h "$target" | awk '{print $1}')"
}

if [[ "$CHOICE" == "all" ]]; then
  for model in smart ultra pro max; do install_one "$model"; done
else
  install_one "$CHOICE"
fi

cat <<DONE

Installation complete.
Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Recommended automatic orchestration inside Pocket AI:
  /llm-model auto
  /hybrid auto
DONE
