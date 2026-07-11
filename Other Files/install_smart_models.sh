#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
CHOICE="${1:-best}"

model_repo() {
  case "$1" in
    fast)    echo "Qwen/Qwen3-0.6B-GGUF|Qwen3-0.6B-Q8_0.gguf|1100000000|Qwen3 0.6B Q8_0 Fast|official Qwen GGUF" ;;
    quality) echo "ggml-org/Qwen3.5-0.8B-GGUF|Qwen3.5-0.8B-Q4_0.gguf|1000000000|Qwen3.5 0.8B Q4_0 Quality|ggml-org GGUF from official Qwen weights" ;;
    smart)   echo "Qwen/Qwen2.5-1.5B-Instruct-GGUF|qwen2.5-1.5b-instruct-q4_k_m.gguf|1700000000|Qwen2.5 1.5B Q4_K_M Smart|official Qwen GGUF" ;;
    ultra)   echo "Qwen/Qwen3-1.7B-GGUF|Qwen3-1.7B-Q4_K_M.gguf|1900000000|Qwen3 1.7B Q4_K_M Ultra|official Qwen GGUF" ;;
    pro)     echo "Qwen/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf|3800000000|Qwen3 4B Q4_K_M Pro|official Qwen GGUF" ;;
    max)     echo "Qwen/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf|7000000000|Qwen3 8B Q4_K_M Max|official Qwen GGUF" ;;
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
  if ! is_64_bit; then echo "none"; return; fi

  # The downloader chooses a conservative first installation. Pocket AI then
  # applies stricter per-question RAM, CPU, and thermal checks and can downgrade.
  if (( total >= 13500000000 && available >= 6500000000 && storage >= 7500000000 )); then
    echo "max"
  elif (( total >= 7800000000 && available >= 3400000000 && storage >= 4000000000 )); then
    echo "pro"
  elif (( total >= 5400000000 && available >= 1700000000 && storage >= 2100000000 )); then
    echo "ultra"
  elif (( total >= 4800000000 && available >= 1500000000 && storage >= 1800000000 )); then
    echo "smart"
  elif (( total >= 4300000000 && available >= 1150000000 && storage >= 1300000000 )); then
    echo "quality"
  elif (( total >= 2800000000 && available >= 800000000 && storage >= 1300000000 )); then
    echo "fast"
  else
    echo "none"
  fi
}

if [[ "$CHOICE" == "--help" || "$CHOICE" == "-h" ]]; then
  cat <<'HELP'
Usage:
  bash "Other Files/install_smart_models.sh" best      # strongest conservative match
  bash "Other Files/install_smart_models.sh" auto      # same as best
  bash "Other Files/install_smart_models.sh" fast      # Qwen3 0.6B Q8_0; regular minimum
  bash "Other Files/install_smart_models.sh" quality   # Qwen3.5 0.8B Q4_0
  bash "Other Files/install_smart_models.sh" smart     # Qwen2.5 1.5B Q4_K_M
  bash "Other Files/install_smart_models.sh" ultra     # Qwen3 1.7B Q4_K_M
  bash "Other Files/install_smart_models.sh" compact   # install 0.6B, 0.8B, 1.5B, and 1.7B
  bash "Other Files/install_smart_models.sh" pro       # Qwen3 4B Q4_K_M
  bash "Other Files/install_smart_models.sh" max       # Qwen3 8B Q4_K_M
  bash "Other Files/install_smart_models.sh" all       # all regular models

Downloads resume after interruption. Every completed model is verified using
Hugging Face file metadata, SHA-256, exact byte size, and its GGUF header.
Hybrid routes are sequential workflows; their parameter counts are not added.
HELP
  exit 0
fi

case "$CHOICE" in
  best|auto)
    CHOICE="$(select_best)"
    if [[ "$CHOICE" == "none" ]]; then
      echo "No 0.6B+ model is safely recommended from the current live RAM/storage snapshot."
      echo "Pocket AI will retain the bundled 135M emergency fallbacks."
      exit 0
    fi
    echo "Strongest conservative automatic match: $CHOICE"
    ;;
  fast|quality|smart|ultra|pro|max|compact|all) ;;
  *) echo "Use best, auto, fast, quality, smart, ultra, compact, pro, max, or all." >&2; exit 2 ;;
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
  # `blobs=true` exposes the LFS object ID. Hugging Face uses that 64-hex
  # LFS object ID as the downloaded file's SHA-256, including repositories
  # whose storage backend is Xet. An Xet hash is deliberately not accepted as
  # a file checksum because it is separate metadata.
  local api="https://huggingface.co/api/models/${repo}?blobs=true"
  curl --fail --silent --show-error --location --retry 8 --retry-delay 3 --output "$metadata_file" "$api"
  python - "$metadata_file" "$filename" <<'PYMETA'
import json,re,sys
path,wanted=sys.argv[1:]
data=json.load(open(path,encoding='utf-8'))
if isinstance(data,dict):
    entries=data.get('siblings') or data.get('items') or []
else:
    entries=data
for entry in entries:
    item=str(entry.get('path') or entry.get('rfilename') or '')
    if item==wanted or item.endswith('/'+wanted):
        lfs=entry.get('lfs') or {}
        oid=str(lfs.get('oid') or lfs.get('sha256') or '').removeprefix('sha256:').strip('"')
        size=int(lfs.get('size') or entry.get('size') or 0)
        if re.fullmatch(r'[0-9a-fA-F]{64}',oid) and size>50_000_000:
            print(oid.lower(),size)
            raise SystemExit(0)
        raise SystemExit('The repository returned no LFS SHA-256 for '+wanted)
raise SystemExit('File metadata was not found for '+wanted+' in the selected Hugging Face repository')
PYMETA
}

valid_existing() {
  local target="$1" expected="$2" size="$3"
  [[ -f "$target" ]] || return 1
  [[ "$(head -c 4 "$target")" == "GGUF" ]] || return 1
  [[ "$(stat -c %s "$target")" == "$size" ]] || return 1
  [[ "$(sha256sum "$target" | awk '{print $1}')" == "$expected" ]]
}

install_one() {
  local key="$1" spec repo name fallback_min label origin
  spec="$(model_repo "$key")"
  IFS='|' read -r repo name fallback_min label origin <<<"$spec"
  local target="$MODELS_DIR/$name" partial="$target.partial" metadata="$target.metadata.tmp"
  local url="https://huggingface.co/${repo}/resolve/main/${name}?download=true"

  echo; echo "Retrieving repository metadata for $label..."
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
  python - "$target.source.json" "$repo" "$name" "$url" "$expected" "$expected_size" "$origin" <<'PY'
import json,sys
path,repo,name,url,sha,size,origin=sys.argv[1:]
with open(path,'w',encoding='utf-8') as f:
    json.dump({
        'repository':repo,'filename':name,'download_url':url,'sha256':sha,
        'size_bytes':int(size),'origin':origin,
        'verification':'Hugging Face metadata SHA-256, exact byte size, and GGUF header'
    },f,ensure_ascii=False,indent=2)
    f.write('\n')
PY
  echo "$label installed and verified: $(du -h "$target" | awk '{print $1}')"
}

case "$CHOICE" in
  compact) for model in fast quality smart ultra; do install_one "$model"; done ;;
  all) for model in fast quality smart ultra pro max; do install_one "$model"; done ;;
  *) install_one "$CHOICE" ;;
esac

cat <<DONE

Installation complete.
Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Recommended automatic orchestration:
  /llm-model auto
  /hybrid auto

Regular compact ladder:
  fast=0.6B, quality=0.8B, smart=1.5B, ultra=1.7B
DONE
