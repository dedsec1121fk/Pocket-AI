#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
CHOICE="${1:-smart}"

SMART_REPO="Qwen/Qwen3-0.6B-GGUF"
SMART_NAME="Qwen3-0.6B-Q8_0.gguf"
SMART_MIN_FREE=1050000000

ULTRA_REPO="Qwen/Qwen3-1.7B-GGUF"
ULTRA_NAME="Qwen3-1.7B-Q8_0.gguf"
ULTRA_MIN_FREE=2800000000

if [[ "$CHOICE" == "--help" || "$CHOICE" == "-h" ]]; then
  cat <<'EOF'
Usage:
  bash "Other Files/install_smart_models.sh" smart   # Qwen3 0.6B Q8_0; recommended reasoning tier
  bash "Other Files/install_smart_models.sh" ultra   # Qwen3 1.7B Q8_0; strongest guarded phone tier
  bash "Other Files/install_smart_models.sh" all     # Download both

Each model is downloaded only from the official Qwen Hugging Face repository.
Before acceptance, the installer retrieves the model's official LFS SHA-256
object ID and size through the Hugging Face API, checks the GGUF header, and
writes a local SHA-256 sidecar for future corruption detection.
EOF
  exit 0
fi

case "$CHOICE" in
  smart|ultra|all) ;;
  *) echo "Unknown choice: $CHOICE" >&2; echo "Use smart, ultra, or all." >&2; exit 2 ;;
esac

if [[ ! -d "/data/data/com.termux/files/usr" ]]; then
  echo "This downloader is intended for Termux on Android." >&2
  exit 1
fi

pkg install -y curl coreutils python
mkdir -p "$MODELS_DIR"

available_bytes() {
  df -Pk "$MODELS_DIR" | awk 'NR==2 {print $4 * 1024}'
}

official_metadata() {
  local repo="$1" filename="$2" metadata_file="$3"
  local api="https://huggingface.co/api/models/${repo}/tree/main?recursive=true&expand=true&limit=1000"
  curl --fail --silent --show-error --location --retry 8 --retry-delay 3 \
    --output "$metadata_file" "$api"
  python - "$metadata_file" "$filename" <<'PY'
import json, re, sys
path, wanted = sys.argv[1:]
data = json.load(open(path, encoding="utf-8"))
if isinstance(data, dict):
    data = data.get("siblings") or data.get("items") or []
for entry in data:
    item_path = str(entry.get("path") or entry.get("rfilename") or "")
    if item_path == wanted or item_path.endswith("/" + wanted):
        lfs = entry.get("lfs") or {}
        oid = str(lfs.get("oid") or entry.get("oid") or "")
        oid = oid.removeprefix("sha256:")
        size = int(lfs.get("size") or entry.get("size") or 0)
        if re.fullmatch(r"[0-9a-fA-F]{64}", oid) and size > 50_000_000:
            print(oid.lower(), size)
            raise SystemExit(0)
raise SystemExit("Official SHA-256 metadata for the selected GGUF was not found.")
PY
}

valid_existing() {
  local target="$1" expected="$2" expected_size="$3"
  [[ -f "$target" ]] || return 1
  [[ "$(head -c 4 "$target")" == "GGUF" ]] || return 1
  [[ "$(stat -c %s "$target")" == "$expected_size" ]] || return 1
  [[ "$(sha256sum "$target" | awk '{print $1}')" == "$expected" ]] || return 1
}

install_one() {
  local repo="$1" name="$2" fallback_min_free="$3" label="$4"
  local target="$MODELS_DIR/$name"
  local partial="$target.partial"
  local metadata="$target.metadata.json.tmp"
  local url="https://huggingface.co/${repo}/resolve/main/${name}?download=true"

  echo
  echo "Retrieving official metadata for $label..."
  local metadata_result expected expected_size
  metadata_result="$(official_metadata "$repo" "$name" "$metadata")"
  rm -f "$metadata"
  read -r expected expected_size <<<"$metadata_result"

  if valid_existing "$target" "$expected" "$expected_size"; then
    printf '%s  %s\n' "$expected" "$name" > "$target.sha256"
    echo "$label is already installed and verified against official metadata."
    return 0
  fi
  if [[ -f "$target" ]]; then
    echo "Removing an invalid or outdated existing file: $target"
    rm -f "$target" "$target.sha256" "$target.source.json"
  fi

  local required free
  required=$((expected_size + 350000000))
  if (( required < fallback_min_free )); then required="$fallback_min_free"; fi
  free="$(available_bytes)"
  if (( free < required )); then
    echo "Not enough free storage for $label." >&2
    echo "Available: $free bytes; required before download: $required bytes." >&2
    exit 1
  fi

  echo "Downloading $label from the official repository..."
  echo "Destination: $target"
  curl --fail --location --retry 8 --retry-delay 3 --continue-at - \
    --output "$partial" "$url"

  local actual_size actual
  actual_size="$(stat -c %s "$partial")"
  actual="$(sha256sum "$partial" | awk '{print $1}')"
  if [[ "$actual_size" != "$expected_size" ]]; then
    echo "Size verification failed for $label." >&2
    echo "Expected: $expected_size bytes" >&2
    echo "Actual:   $actual_size bytes" >&2
    exit 1
  fi
  if [[ "$actual" != "$expected" ]]; then
    echo "Official SHA-256 verification failed for $label." >&2
    echo "Expected: $expected" >&2
    echo "Actual:   $actual" >&2
    exit 1
  fi
  if [[ "$(head -c 4 "$partial")" != "GGUF" ]]; then
    echo "The downloaded file does not have a GGUF header." >&2
    exit 1
  fi

  mv -f "$partial" "$target"
  printf '%s  %s\n' "$expected" "$name" > "$target.sha256"
  cat > "$target.source.json" <<EOF
{
  "repository": "$repo",
  "filename": "$name",
  "download_url": "$url",
  "sha256": "$expected",
  "size_bytes": $expected_size,
  "verification": "Official Hugging Face LFS object SHA-256 plus GGUF header"
}
EOF
  echo "$label installed and verified: $(du -h "$target" | awk '{print $1}')"
}

if [[ "$CHOICE" == "smart" || "$CHOICE" == "all" ]]; then
  install_one "$SMART_REPO" "$SMART_NAME" "$SMART_MIN_FREE" "Qwen3 0.6B Smart"
fi
if [[ "$CHOICE" == "ultra" || "$CHOICE" == "all" ]]; then
  install_one "$ULTRA_REPO" "$ULTRA_NAME" "$ULTRA_MIN_FREE" "Qwen3 1.7B Ultra"
fi

cat <<EOF

Installation complete.
Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Inside Pocket AI use:
  /llm-model smart
or, when the 1.7B model is installed:
  /llm-model ultra

For strongest automatic routing:
  /llm always
  /hybrid auto
EOF
