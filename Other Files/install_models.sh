#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
shopt -s nullglob

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
PARTS_DIR="$MODELS_DIR/GGUF Parts"
DATA_DIR="${POCKETAI_HOME:-$OTHER_DIR/Saved Data}"
MODEL_CACHE_DIR="$DATA_DIR/GGUF Models"
LLAMA_DIR="$DATA_DIR/llama.cpp"
LLAMA_BUILD_MARKER="$LLAMA_DIR/.pocketai-build-v15"

EMERGENCY_FAST_NAME="SmolLM2-135M-Instruct.Q2_K.gguf"
EMERGENCY_FAST_SHA="1e014d3c45f6cf502397a3b85b1d9d282605afb02079fd32665b0422c3f0106c"
EMERGENCY_QUALITY_NAME="SmolLM2-135M-Instruct.Q4_1.gguf"
EMERGENCY_QUALITY_SHA="b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53"

# Normal Pocket AI setup starts from the strongest safe 0.6B-1.7B tier.
# --emergency-only is the explicit opt-out for offline or extremely weak phones.
OPTIONAL_MODEL="best"
for argument in "$@"; do
  case "$argument" in
    --best|--auto) OPTIONAL_MODEL="best" ;;
    --fast|--0.6b) OPTIONAL_MODEL="fast" ;;
    --quality|--0.8b) OPTIONAL_MODEL="quality" ;;
    --smart|--1.5b) OPTIONAL_MODEL="smart" ;;
    --ultra|--1.7b) OPTIONAL_MODEL="ultra" ;;
    --compact) OPTIONAL_MODEL="compact" ;;
    --pro) OPTIONAL_MODEL="pro" ;;
    --max) OPTIONAL_MODEL="max" ;;
    --all-models|--all-smart-models) OPTIONAL_MODEL="all" ;;
    --emergency-only|--offline) OPTIONAL_MODEL="" ;;
    --help|-h)
      cat <<'HELP'
Usage: bash "Other Files/install_models.sh" [OPTION]

Default / --best / --auto  Install strongest safe regular tier (minimum 0.6B)
--fast or --0.6b           Install Qwen3 0.6B Q8_0
--quality or --0.8b        Install Qwen3.5 0.8B Q4_0
--smart or --1.5b          Install Qwen2.5 1.5B Q4_K_M
--ultra or --1.7b          Install Qwen3 1.7B Q4_K_M
--compact                  Install all 0.6B, 0.8B, 1.5B, and 1.7B tiers
--pro / --max              Install Qwen3 4B / 8B
--all-models               Install every regular tier
--emergency-only           Reconstruct only the bundled 135M fallbacks

The 135M files remain emergency fallbacks and are not the normal starting tier.
HELP
      exit 0
      ;;
    *) echo "Unknown argument: $argument" >&2; exit 2 ;;
  esac
done

if [[ ! -d "/data/data/com.termux/files/usr" ]]; then
  echo "This installer must be run inside Termux." >&2
  exit 1
fi

if [[ -f "$OTHER_DIR/CHECKSUMS.sha256" ]]; then
  echo "Verifying the complete Pocket AI package..."
  (cd "$ROOT_DIR" && sha256sum -c "Other Files/CHECKSUMS.sha256")
fi

mkdir -p "$DATA_DIR" "$MODEL_CACHE_DIR"

reconstruct_model() {
  local filename="$1" expected="$2" label="$3"
  local target="$MODEL_CACHE_DIR/$filename"
  local temp="$MODEL_CACHE_DIR/.${filename}.$$.tmp"
  local parts=("$PARTS_DIR/${filename}.part"[0-9][0-9][0-9])

  if [[ -f "$target" ]]; then
    local current
    current="$(sha256sum "$target" | awk '{print $1}')"
    if [[ "$current" == "$expected" && "$(head -c 4 "$target")" == "GGUF" ]]; then
      echo "$label already reconstructed and verified: $(du -h "$target" | awk '{print $1}')"
      return 0
    fi
    rm -f "$target"
  fi

  if [[ "${#parts[@]}" -eq 0 ]]; then
    echo "Missing split model parts for $filename in: $PARTS_DIR" >&2
    exit 1
  fi

  echo "Reconstructing $label from ${#parts[@]} package parts..."
  rm -f "$temp"
  cat "${parts[@]}" > "$temp"

  local actual
  actual="$(sha256sum "$temp" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    rm -f "$temp"
    echo "$label checksum verification failed after reconstruction." >&2
    exit 1
  fi
  if [[ "$(head -c 4 "$temp")" != "GGUF" ]]; then
    rm -f "$temp"
    echo "$label has an invalid GGUF header after reconstruction." >&2
    exit 1
  fi

  mv "$temp" "$target"
  echo "$label verified: $(du -h "$target" | awk '{print $1}')"
}

reconstruct_model "$EMERGENCY_FAST_NAME" "$EMERGENCY_FAST_SHA" "Emergency Fast 135M Q2_K model"
reconstruct_model "$EMERGENCY_QUALITY_NAME" "$EMERGENCY_QUALITY_SHA" "Emergency Quality 135M Q4_1 model"

if [[ -n "$OPTIONAL_MODEL" ]]; then
  bash "$OTHER_DIR/install_smart_models.sh" "$OPTIONAL_MODEL"
fi

pkg update -y
pkg install -y python git cmake clang make libandroid-spawn ccache
python -m pip install --upgrade ddgs >/dev/null 2>&1 || echo "Optional DDGS metasearch was not installed; Bing RSS and Wikipedia remain available."

# Qwen3.5 support requires a current llama.cpp. Rebuild once for Pocket AI v15;
# later runs reuse the verified v15 build marker.
NEED_BUILD=0
if [[ ! -x "$LLAMA_DIR/build/bin/llama-cli" || ! -f "$LLAMA_BUILD_MARKER" ]]; then
  NEED_BUILD=1
fi

if [[ "$NEED_BUILD" -eq 1 ]]; then
  if [[ ! -d "$LLAMA_DIR/.git" ]]; then
    rm -rf "$LLAMA_DIR"
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
  else
    git -C "$LLAMA_DIR" fetch --depth 1 origin
    git -C "$LLAMA_DIR" reset --hard origin/master || git -C "$LLAMA_DIR" pull --ff-only
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

if [[ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]]; then
  candidate="$(find "$LLAMA_DIR/build" -type f -name llama-cli -perm -u+x 2>/dev/null | head -n 1 || true)"
  if [[ -n "$candidate" ]]; then
    mkdir -p "$LLAMA_DIR/build/bin"
    cp "$candidate" "$LLAMA_DIR/build/bin/llama-cli"
    chmod +x "$LLAMA_DIR/build/bin/llama-cli"
  fi
fi

if [[ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]]; then
  echo "llama-cli was not produced by the build." >&2
  echo "Build directory: $LLAMA_DIR/build" >&2
  exit 1
fi

touch "$LLAMA_BUILD_MARKER"
"$LLAMA_DIR/build/bin/llama-cli" --version || true

cat <<EOF2

Installation complete.

Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Regular ladder:
  fast    = Qwen3 0.6B
  quality = Qwen3.5 0.8B
  smart   = Qwen2.5 1.5B
  ultra   = Qwen3 1.7B

Emergency-only fallbacks:
  emergency_fast / emergency_quality = SmolLM2 135M

Install every compact tier later:
  bash "$OTHER_DIR/install_smart_models.sh" compact

Recommended inside Pocket AI:
  /llm-model auto
  /hybrid auto
EOF2
