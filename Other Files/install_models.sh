#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
shopt -s nullglob

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
PARTS_DIR="$MODELS_DIR/GGUF Parts"
DATA_DIR="${POCKETAI_HOME:-$OTHER_DIR/Saved Data}"
MODEL_CACHE_DIR="$DATA_DIR/GGUF Models"
LLAMA_DIR="$DATA_DIR/llama.cpp"

FAST_NAME="SmolLM2-135M-Instruct.Q2_K.gguf"
FAST_SHA="1e014d3c45f6cf502397a3b85b1d9d282605afb02079fd32665b0422c3f0106c"
QUALITY_NAME="SmolLM2-135M-Instruct.Q4_1.gguf"
QUALITY_SHA="b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53"
OPTIONAL_MODEL=""
for argument in "$@"; do
  case "$argument" in
    --smart) OPTIONAL_MODEL="smart" ;;
    --ultra) OPTIONAL_MODEL="ultra" ;;
    --all-smart-models) OPTIONAL_MODEL="all" ;;
    --help|-h)
      echo "Usage: bash Other\ Files/install_models.sh [--smart|--ultra|--all-smart-models]"
      exit 0
      ;;
    *) echo "Unknown argument: $argument" >&2; exit 2 ;;
  esac
done

if [ ! -d "/data/data/com.termux/files/usr" ]; then
  echo "This installer must be run inside Termux." >&2
  exit 1
fi

if [ -f "$OTHER_DIR/CHECKSUMS.sha256" ]; then
  echo "Verifying bundled scripts, split model parts, and documentation..."
  (cd "$ROOT_DIR" && sha256sum -c "Other Files/CHECKSUMS.sha256")
fi

mkdir -p "$DATA_DIR" "$MODEL_CACHE_DIR"

reconstruct_model() {
  local filename="$1" expected="$2" label="$3"
  local target="$MODEL_CACHE_DIR/$filename"
  local temp="$MODEL_CACHE_DIR/.${filename}.$$.tmp"
  local parts=("$PARTS_DIR/${filename}.part"[0-9][0-9][0-9])

  if [ -f "$target" ]; then
    local current
    current="$(sha256sum "$target" | awk '{print $1}')"
    if [ "$current" = "$expected" ] && [ "$(head -c 4 "$target")" = "GGUF" ]; then
      echo "$label already reconstructed and verified: $(du -h "$target" | awk '{print $1}')"
      return 0
    fi
    rm -f "$target"
  fi

  if [ "${#parts[@]}" -eq 0 ]; then
    echo "Missing split model parts for $filename in: $PARTS_DIR" >&2
    exit 1
  fi

  echo "Reconstructing $label from ${#parts[@]} package parts..."
  rm -f "$temp"
  cat "${parts[@]}" > "$temp"

  local actual
  actual="$(sha256sum "$temp" | awk '{print $1}')"
  if [ "$actual" != "$expected" ]; then
    rm -f "$temp"
    echo "$label checksum verification failed after reconstruction." >&2
    exit 1
  fi
  if [ "$(head -c 4 "$temp")" != "GGUF" ]; then
    rm -f "$temp"
    echo "$label has an invalid GGUF header after reconstruction." >&2
    exit 1
  fi

  mv "$temp" "$target"
  echo "$label verified: $(du -h "$target" | awk '{print $1}')"
}

reconstruct_model "$FAST_NAME" "$FAST_SHA" "Fast Q2_K model"
reconstruct_model "$QUALITY_NAME" "$QUALITY_SHA" "Quality Q4_1 model"

if [ -n "$OPTIONAL_MODEL" ]; then
  bash "$OTHER_DIR/install_smart_models.sh" "$OPTIONAL_MODEL"
fi

pkg update -y
pkg install -y python git cmake clang make libandroid-spawn ccache

if [ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]; then
  if [ ! -d "$LLAMA_DIR/.git" ]; then
    rm -rf "$LLAMA_DIR"
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
  else
    git -C "$LLAMA_DIR" pull --ff-only || true
  fi

  rm -rf "$LLAMA_DIR/build"
  export GGML_CCACHE=ON
  cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DGGML_OPENMP=OFF \
    -DGGML_LLAMAFILE=OFF \
    -DGGML_CCACHE=ON \
    -DLLAMA_CURL=OFF \
    -DLLAMA_OPENSSL=ON \
    -DLLAMA_BUILD_COMMON=ON \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_BUILD_UI=OFF \
    -DLLAMA_USE_PREBUILT_UI=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DLLAMA_BUILD_APP=OFF

  if ! cmake --build "$LLAMA_DIR/build" --config Release --target llama-cli -j1; then
    echo "Direct llama-cli target was unavailable; building the configured tools set..."
    cmake --build "$LLAMA_DIR/build" --config Release -j1
  fi
fi

if [ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]; then
  candidate="$(find "$LLAMA_DIR/build" -type f -name llama-cli -perm -u+x 2>/dev/null | head -n 1 || true)"
  if [ -n "$candidate" ]; then
    mkdir -p "$LLAMA_DIR/build/bin"
    cp "$candidate" "$LLAMA_DIR/build/bin/llama-cli"
    chmod +x "$LLAMA_DIR/build/bin/llama-cli"
  fi
fi

if [ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]; then
  echo "llama-cli was not produced by the build." >&2
  echo "Build directory: $LLAMA_DIR/build" >&2
  exit 1
fi

"$LLAMA_DIR/build/bin/llama-cli" --version || true

cat <<EOF2

Installation complete.

Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

The bundled 135M GGUF weights remain under 60 MB per package file in:
  $PARTS_DIR

Verified runtime GGUF files are reconstructed automatically in:
  $MODEL_CACHE_DIR

Optional stronger Qwen3 reasoning models can be installed with:
  bash "$OTHER_DIR/install_smart_models.sh" smart
  bash "$OTHER_DIR/install_smart_models.sh" ultra

All settings, scans, persona data, databases, generated models, history,
backups, exports, and the llama.cpp runner are stored under:
  $DATA_DIR
EOF2
