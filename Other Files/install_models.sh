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
LLAMA_BUILD_MARKER="$LLAMA_DIR/.pocketai-build-v16"

EMERGENCY_FAST_NAME="SmolLM2-135M-Instruct.Q2_K.gguf"
EMERGENCY_FAST_SHA="1e014d3c45f6cf502397a3b85b1d9d282605afb02079fd32665b0422c3f0106c"
EMERGENCY_QUALITY_NAME="SmolLM2-135M-Instruct.Q4_1.gguf"
EMERGENCY_QUALITY_SHA="b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53"

OPTIONAL_MODEL=best
for argument in "$@"; do
  case "$argument" in
    --best|--auto) OPTIONAL_MODEL=best ;;
    --fast|--0.6b) OPTIONAL_MODEL=fast ;;
    --quality|--0.8b) OPTIONAL_MODEL=quality ;;
    --smart|--1.5b) OPTIONAL_MODEL=smart ;;
    --ultra|--1.7b) OPTIONAL_MODEL=ultra ;;
    --advanced|--2b) OPTIONAL_MODEL=advanced ;;
    --prime|--3b) OPTIONAL_MODEL=prime ;;
    --compact) OPTIONAL_MODEL=compact ;;
    --extended|--full-ladder) OPTIONAL_MODEL=extended ;;
    --pro) OPTIONAL_MODEL=pro ;;
    --max) OPTIONAL_MODEL=max ;;
    --all-models|--all-smart-models) OPTIONAL_MODEL=all ;;
    --emergency-only|--offline) OPTIONAL_MODEL="" ;;
    --help|-h)
      cat <<'HELP'
Usage: bash "Other Files/install_models.sh" [OPTION]

Default / --best       Install strongest conservative normal tier (minimum 0.6B)
--fast / --0.6b        Install 0.6B
--quality / --0.8b     Install 0.8B
--smart / --1.5b       Install 1.5B
--ultra / --1.7b       Install 1.7B
--advanced / --2b      Install 2B
--prime / --3b         Install 3.09B (Q3 or Q4 selected by RAM)
--compact              Install 0.6B through 1.7B
--extended             Install 0.6B through 3.09B
--pro / --max          Install optional 4B / 8B
--all-models            Install every normal tier
--emergency-only       Reconstruct only bundled 135M fallbacks
HELP
      exit 0 ;;
    *) echo "Unknown argument: $argument" >&2; exit 2 ;;
  esac
done

[[ -d /data/data/com.termux/files/usr ]] || { echo "Run this installer inside Termux." >&2; exit 1; }
if [[ -f "$OTHER_DIR/CHECKSUMS.sha256" ]]; then
  echo "Verifying the complete Pocket AI package..."
  (cd "$ROOT_DIR" && sha256sum -c "Other Files/CHECKSUMS.sha256")
fi
mkdir -p "$DATA_DIR" "$MODEL_CACHE_DIR"

reconstruct_model() {
  local filename="$1" expected="$2" label="$3"
  local target="$MODEL_CACHE_DIR/$filename" temp="$MODEL_CACHE_DIR/.${filename}.$$.tmp"
  local parts=("$PARTS_DIR/${filename}.part"[0-9][0-9][0-9])
  if [[ -f "$target" ]] && [[ "$(sha256sum "$target"|awk '{print $1}')" == "$expected" ]] && [[ "$(head -c 4 "$target")" == GGUF ]]; then
    echo "$label already reconstructed and verified."; return
  fi
  ((${#parts[@]})) || { echo "Missing split parts for $filename" >&2; exit 1; }
  rm -f "$temp" "$target"; cat "${parts[@]}" > "$temp"
  [[ "$(sha256sum "$temp"|awk '{print $1}')" == "$expected" ]] || { rm -f "$temp"; echo "$label checksum failed." >&2; exit 1; }
  [[ "$(head -c 4 "$temp")" == GGUF ]] || { rm -f "$temp"; echo "$label GGUF header failed." >&2; exit 1; }
  mv "$temp" "$target"; echo "$label reconstructed and verified."
}

reconstruct_model "$EMERGENCY_FAST_NAME" "$EMERGENCY_FAST_SHA" "Emergency Fast 135M Q2_K"
reconstruct_model "$EMERGENCY_QUALITY_NAME" "$EMERGENCY_QUALITY_SHA" "Emergency Quality 135M Q4_1"
[[ -z "$OPTIONAL_MODEL" ]] || bash "$OTHER_DIR/install_smart_models.sh" "$OPTIONAL_MODEL"

pkg update -y
pkg install -y python git cmake clang make libandroid-spawn ccache
python -m pip install --upgrade ddgs >/dev/null 2>&1 || echo "Optional DDGS was not installed; Bing RSS and Wikipedia remain available."

NEED_BUILD=0
[[ -x "$LLAMA_DIR/build/bin/llama-cli" && -f "$LLAMA_BUILD_MARKER" ]] || NEED_BUILD=1
if (( NEED_BUILD )); then
  if [[ ! -d "$LLAMA_DIR/.git" ]]; then
    rm -rf "$LLAMA_DIR"; git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
  else
    git -C "$LLAMA_DIR" fetch --depth 1 origin
    git -C "$LLAMA_DIR" reset --hard origin/master || git -C "$LLAMA_DIR" pull --ff-only
  fi
  rm -rf "$LLAMA_DIR/build"; export GGML_CCACHE=ON
  cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF \
    -DGGML_OPENMP=OFF -DGGML_LLAMAFILE=OFF -DGGML_CCACHE=ON -DLLAMA_CURL=OFF \
    -DLLAMA_OPENSSL=ON -DLLAMA_BUILD_COMMON=ON -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
    -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF
  cmake --build "$LLAMA_DIR/build" --config Release --target llama-cli -j1 || cmake --build "$LLAMA_DIR/build" --config Release -j1
fi
if [[ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]]; then
  candidate="$(find "$LLAMA_DIR/build" -type f -name llama-cli -perm -u+x 2>/dev/null | head -n1 || true)"
  [[ -z "$candidate" ]] || { mkdir -p "$LLAMA_DIR/build/bin"; cp "$candidate" "$LLAMA_DIR/build/bin/llama-cli"; chmod +x "$LLAMA_DIR/build/bin/llama-cli"; }
fi
[[ -x "$LLAMA_DIR/build/bin/llama-cli" ]] || { echo "llama-cli was not produced." >&2; exit 1; }
touch "$LLAMA_BUILD_MARKER"; "$LLAMA_DIR/build/bin/llama-cli" --version || true

cat <<EOF

Installation complete.
Normal ladder: 0.6B → 0.8B → 1.5B → 1.7B → 2B → 3.09B
Optional larger tiers: 4B → 8B
Emergency-only: SmolLM2 135M Q2_K / Q4_1

Start:
  cd "$ROOT_DIR" && python "Pocket AI.py"
Use: /llm-model auto and /hybrid auto
EOF
