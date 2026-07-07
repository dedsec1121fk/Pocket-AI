#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

OTHER_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$OTHER_DIR/.." && pwd)"
MODELS_DIR="$ROOT_DIR/Models"
DATA_DIR="${POCKETAI_HOME:-$OTHER_DIR/Saved Data}"
LLAMA_DIR="$DATA_DIR/llama.cpp"

FAST_MODEL="$MODELS_DIR/SmolLM2-135M-Instruct.Q2_K.gguf"
FAST_SHA="1e014d3c45f6cf502397a3b85b1d9d282605afb02079fd32665b0422c3f0106c"
QUALITY_MODEL="$MODELS_DIR/SmolLM2-135M-Instruct.Q4_1.gguf"
QUALITY_SHA="b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53"

if [ ! -d "/data/data/com.termux/files/usr" ]; then
  echo "This installer must be run inside Termux." >&2
  exit 1
fi

if [ -f "$OTHER_DIR/CHECKSUMS.sha256" ]; then
  echo "Verifying all bundled scripts, models, and documentation..."
  (cd "$ROOT_DIR" && sha256sum -c "Other Files/CHECKSUMS.sha256")
fi

verify_model() {
  local file="$1"
  local expected="$2"
  local label="$3"
  if [ ! -f "$file" ]; then
    echo "Missing bundled model: $file" >&2
    exit 1
  fi
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$actual" != "$expected" ]; then
    echo "$label checksum verification failed." >&2
    exit 1
  fi
  if [ "$(head -c 4 "$file")" != "GGUF" ]; then
    echo "$label has an invalid GGUF header." >&2
    exit 1
  fi
  echo "$label verified: $(du -h "$file" | awk '{print $1}')"
}

verify_model "$FAST_MODEL" "$FAST_SHA" "Fast Q2_K model"
verify_model "$QUALITY_MODEL" "$QUALITY_SHA" "Quality Q4_1 model"

pkg update -y
pkg install -y python git cmake clang make libandroid-spawn
mkdir -p "$DATA_DIR"

if [ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]; then
  if [ ! -d "$LLAMA_DIR/.git" ]; then
    rm -rf "$LLAMA_DIR"
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
  else
    git -C "$LLAMA_DIR" pull --ff-only || true
  fi

  rm -rf "$LLAMA_DIR/build"
  cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DGGML_OPENMP=OFF \
    -DGGML_LLAMAFILE=OFF \
    -DLLAMA_CURL=OFF \
    -DLLAMA_BUILD_SERVER=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=ON

  cmake --build "$LLAMA_DIR/build" --config Release --target llama-cli -j1
fi

if [ ! -x "$LLAMA_DIR/build/bin/llama-cli" ]; then
  echo "llama-cli was not produced by the build." >&2
  exit 1
fi

cat <<EOF

Installation complete.

Start Pocket AI:
  cd "$ROOT_DIR"
  python "Pocket AI.py"

Top-level package layout:
  Pocket AI.py
  Models/
  Other Files/

All settings, scans, databases, generated models, chat history, backups,
exports, and the llama.cpp runner are stored under:
  $DATA_DIR
EOF
