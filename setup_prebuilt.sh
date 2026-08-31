#!/bin/bash
# setup_prebuilt.sh - 使用仓库附带的预生成 ASN.1 代码编译 OAI
#
# 为什么需要这个脚本：
#   OAI 的 ASN.1 代码（S1AP/X2AP/NGAP 等）由 asn1c 生成，但生成代码必须和
#   手写代码严格匹配（compat 头 + 适配）。直接用 asn1c 重新生成会导致
#   "生成代码布局不匹配"的编译错误。本仓库附带了一套**已验证可编译**的
#   预生成代码（prebuilt-asn1c/），本脚本负责解压并让 make 跳过重新生成。
#
# 用法：
#   cd oai-riscv
#   ./setup_prebuilt.sh
#   然后执行 make（见 README_k3.md）

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$REPO_DIR/build-riscv"
TARBALL="$REPO_DIR/prebuilt-asn1c/oai-asn1c-prebuilt-20260830.tar.gz"

echo "============================================"
echo "  OAI 使用预生成 ASN.1 代码配置"
echo "============================================"

# 0. 检查预生成代码存在
if [ ! -f "$TARBALL" ]; then
    echo "❌ 找不到预生成代码包: $TARBALL"
    echo "   请确认已 clone 完整仓库（含 prebuilt-asn1c/ 目录）。"
    exit 1
fi

# 1. 配置 CMake（如果还没配置）
if [ ! -d "$BUILD_DIR" ] || [ ! -f "$BUILD_DIR/CMakeCache.txt" ]; then
    echo "[1/4] 配置 CMake..."
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
    cd "$REPO_DIR"
else
    echo "[1/4] CMake 已配置，跳过"
fi

# 2. 解压预生成代码到 build-riscv（覆盖可能生成的）
echo "[2/4] 解压预生成 ASN.1 代码..."
cd "$REPO_DIR"
tar xzf "$TARBALL"

# 3. 让预生成文件比 ASN.1 源文件新（跳过 asn1c 重新生成）
echo "[3/4] 标记预生成代码为最新（跳过重新生成）..."
find "$BUILD_DIR/openair1" "$BUILD_DIR/openair2" "$BUILD_DIR/openair3" \
  -path "*MESSAGES*" \( -name "*.c" -o -name "*.h" \) -exec touch {} + 2>/dev/null || true

# 4. 准备 stubs_link.o
echo "[4/4] 准备 stubs_link.o..."
if [ -f "$REPO_DIR/riscv-env/stubs_link.c" ]; then
    cd "$REPO_DIR/cmake_targets"
    gcc -c -march=rv64gcv -mabi=lp64d \
      -isystem "$REPO_DIR/cmake_targets/riscv64-stubs/include" \
      "$REPO_DIR/riscv-env/stubs_link.c" -o "$REPO_DIR/riscv-env/stubs_link.o" 2>/dev/null || \
      echo "  (stubs_link.o 编译跳过，可能已存在)"
    cd "$REPO_DIR"
fi

echo ""
echo "============================================"
echo "  配置完成！现在可以编译："
echo "  cd build-riscv"
echo "  make nr-softmodem -j\$(nproc)"
echo "  make nr-uesoftmodem -j\$(nproc)"
echo "  make rfsimulator -j\$(nproc)"
echo "============================================"
