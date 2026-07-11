#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
CHOICE="${1:-best}"

model_repo() {
  case "$1" in
    fast)     echo "Qwen/Qwen3-0.6B-GGUF|Qwen3-0.6B-Q8_0.gguf|1100000000|Qwen3 0.6B Q8_0 Fast|official Qwen GGUF" ;;
    quality)  echo "ggml-org/Qwen3.5-0.8B-GGUF|Qwen3.5-0.8B-Q4_0.gguf|1000000000|Qwen3.5 0.8B Q4_0 Quality|ggml-org GGUF converted from official Qwen weights" ;;
    smart)    echo "Qwen/Qwen2.5-1.5B-Instruct-GGUF|qwen2.5-1.5b-instruct-q4_k_m.gguf|1700000000|Qwen2.5 1.5B Q4_K_M Smart|official Qwen GGUF" ;;
    ultra)    echo "Qwen/Qwen3-1.7B-GGUF|Qwen3-1.7B-Q4_K_M.gguf|2100000000|Qwen3 1.7B Q4_K_M Ultra|official Qwen GGUF" ;;
    advanced) echo "bartowski/Qwen_Qwen3.5-2B-GGUF|Qwen3.5-2B-Q4_K_M.gguf|2300000000|Qwen3.5 2B Q4_K_M Advanced|community GGUF conversion from official Qwen3.5-2B weights" ;;
    prime_q3) echo "Qwen/Qwen2.5-3B-Instruct-GGUF|qwen2.5-3b-instruct-q3_k_m.gguf|2700000000|Qwen2.5 3.09B Q3_K_M Prime|official Qwen GGUF" ;;
    prime_q4) echo "Qwen/Qwen2.5-3B-Instruct-GGUF|qwen2.5-3b-instruct-q4_k_m.gguf|3300000000|Qwen2.5 3.09B Q4_K_M Prime|official Qwen GGUF" ;;
    pro)      echo "Qwen/Qwen3-4B-GGUF|Qwen3-4B-Q4_K_M.gguf|3800000000|Qwen3 4B Q4_K_M Pro|official Qwen GGUF" ;;
    max)      echo "Qwen/Qwen3-8B-GGUF|Qwen3-8B-Q4_K_M.gguf|7000000000|Qwen3 8B Q4_K_M Max|official Qwen GGUF" ;;
    *) return 1 ;;
  esac
}

ram_bytes() { awk '/MemTotal:/ {printf "%.0f\\n", $2 * 1024}' /proc/meminfo 2>/dev/null || echo 0; }
available_ram_bytes() { awk '/MemAvailable:/ {printf "%.0f\\n", $2 * 1024}' /proc/meminfo 2>/dev/null || echo 0; }
free_bytes() { df -Pk "$MODELS_DIR" 2>/dev/null | awk 'NR==2 {printf "%.0f\\n", $4 * 1024}'; }
is_64_bit() { [[ "$(getconf LONG_BIT 2>/dev/null || echo 32)" == "64" ]]; }

prime_variant() {
  local total available
  total="$(ram_bytes)"; available="$(available_ram_bytes)"
  if (( total >= 9000000000 && available >= 3600000000 )); then echo prime_q4; else echo prime_q3; fi
}

select_best() {
  local total available storage
  total="$(ram_bytes)"; available="$(available_ram_bytes)"; storage="$(free_bytes)"
  if ! is_64_bit; then echo none; return; fi
  if (( total >= 13500000000 && available >= 6500000000 && storage >= 7500000000 )); then echo max
  elif (( total >= 9000000000 && available >= 3900000000 && storage >= 4300000000 )); then echo pro
  elif (( total >= 7000000000 && available >= 2500000000 && storage >= 3000000000 )); then prime_variant
  elif (( total >= 5900000000 && available >= 1950000000 && storage >= 2400000000 )); then echo advanced
  elif (( total >= 5200000000 && available >= 1600000000 && storage >= 2150000000 )); then echo ultra
  elif (( total >= 4550000000 && available >= 1400000000 && storage >= 1800000000 )); then echo smart
  elif (( total >= 3400000000 && available >= 950000000 && storage >= 1150000000 )); then echo quality
  elif (( total >= 2900000000 && available >= 820000000 && storage >= 1250000000 )); then echo fast
  else echo none
  fi
}

show_help() {
cat <<'HELP'
Usage:
  bash "Other Files/install_smart_models.sh" best       # strongest conservative live match
  bash "Other Files/install_smart_models.sh" fast       # Qwen3 0.6B Q8_0; regular minimum
  bash "Other Files/install_smart_models.sh" quality    # Qwen3.5 0.8B Q4_0
  bash "Other Files/install_smart_models.sh" smart      # Qwen2.5 1.5B Q4_K_M
  bash "Other Files/install_smart_models.sh" ultra      # Qwen3 1.7B Q4_K_M
  bash "Other Files/install_smart_models.sh" advanced   # Qwen3.5 2B Q4_K_M
  bash "Other Files/install_smart_models.sh" prime      # Qwen2.5 3.09B Q3/Q4 chosen by RAM
  bash "Other Files/install_smart_models.sh" compact    # install 0.6B through 1.7B
  bash "Other Files/install_smart_models.sh" extended   # install 0.6B through 3.09B
  bash "Other Files/install_smart_models.sh" pro|max    # optional 4B / 8B
  bash "Other Files/install_smart_models.sh" all        # every regular tier

Downloads resume after interruption. Completed models are verified using the
Hugging Face LFS SHA-256, exact byte size, and GGUF header. Hybrid routes are
sequential; parameter counts are never added together.
HELP
}

case "$CHOICE" in
  --help|-h|help) show_help; exit 0 ;;
  best|auto)
    CHOICE="$(select_best)"
    if [[ "$CHOICE" == none ]]; then
      echo "No 0.6B+ model is safely recommended from current RAM and storage."
      echo "Pocket AI will use the bundled 135M emergency fallbacks."
      exit 0
    fi
    echo "Strongest conservative automatic match: $CHOICE"
    ;;
  prime|3b) CHOICE="$(prime_variant)" ;;
  fast|0.6b) CHOICE=fast ;;
  quality|0.8b) CHOICE=quality ;;
  smart|1.5b) CHOICE=smart ;;
  ultra|1.7b) CHOICE=ultra ;;
  advanced|2b) CHOICE=advanced ;;
  prime_q3|prime_q4|pro|max|compact|extended|all) ;;
  *) echo "Use best, fast, quality, smart, ultra, advanced, prime, compact, extended, pro, max, or all." >&2; exit 2 ;;
esac

if [[ ! -d /data/data/com.termux/files/usr ]]; then
  echo "This downloader is intended for Termux on Android." >&2
  exit 1
fi

pkg install -y curl coreutils python
mkdir -p "$MODELS_DIR"
available_bytes() { df -Pk "$MODELS_DIR" | awk 'NR==2 {printf "%.0f\\n", $4 * 1024}'; }

official_metadata() {
  local repo="$1" filename="$2" metadata_file="$3"
  local api="https://huggingface.co/api/models/${repo}?blobs=true"
  curl --fail --silent --show-error --location --retry 8 --retry-delay 3 --output "$metadata_file" "$api"
  python - "$metadata_file" "$filename" <<'PYMETA'
import json,re,sys
path,wanted=sys.argv[1:]
data=json.load(open(path,encoding='utf-8'))
entries=(data.get('siblings') or data.get('items') or []) if isinstance(data,dict) else data
for entry in entries:
    item=str(entry.get('path') or entry.get('rfilename') or '')
    if item==wanted or item.endswith('/'+wanted):
        lfs=entry.get('lfs') or {}
        oid=str(lfs.get('oid') or lfs.get('sha256') or '').removeprefix('sha256:').strip('"')
        size=int(lfs.get('size') or entry.get('size') or 0)
        if re.fullmatch(r'[0-9a-fA-F]{64}',oid) and size>50_000_000:
            print(oid.lower(),size); raise SystemExit(0)
        raise SystemExit('No downloadable LFS SHA-256 was returned for '+wanted)
raise SystemExit('File metadata was not found for '+wanted+' in '+str(data.get('id','repository')))
PYMETA
}

valid_existing() {
  local target="$1" expected="$2" size="$3"
  [[ -f "$target" ]] || return 1
  [[ "$(head -c 4 "$target")" == GGUF ]] || return 1
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
  [[ "$(head -c 4 "$partial")" == GGUF ]] || { echo "Invalid GGUF header." >&2; exit 1; }

  mv -f "$partial" "$target"
  printf '%s  %s\n' "$expected" "$name" > "$target.sha256"
  python - "$target.source.json" "$repo" "$name" "$url" "$expected" "$expected_size" "$origin" <<'PYSOURCE'
import json,sys
path,repo,name,url,sha,size,origin=sys.argv[1:]
with open(path,'w',encoding='utf-8') as f:
    json.dump({'repository':repo,'filename':name,'download_url':url,'sha256':sha,
               'size_bytes':int(size),'origin':origin,
               'verification':'Hugging Face metadata SHA-256, exact byte size, and GGUF header'},
              f,ensure_ascii=False,indent=2); f.write('\n')
PYSOURCE
  echo "$label installed and verified: $(du -h "$target" | awk '{print $1}')"
}

case "$CHOICE" in
  compact) for model in fast quality smart ultra; do install_one "$model"; done ;;
  extended) for model in fast quality smart ultra advanced "$(prime_variant)"; do install_one "$model"; done ;;
  all) for model in fast quality smart ultra advanced "$(prime_variant)" pro max; do install_one "$model"; done ;;
  *) install_one "$CHOICE" ;;
esac

cat <<DONE

Installation complete.
Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Automatic orchestration:
  /llm-model auto
  /hybrid auto

Extended ladder:
  0.6B → 0.8B → 1.5B → 1.7B → 2B → 3.09B
The 135M models remain emergency-only. Sequential hybrid parameter counts are not additive.
DONE
