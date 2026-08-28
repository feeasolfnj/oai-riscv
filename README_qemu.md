# OAI 5G RISC-V 移植 — QEMU 使用指南

> 本指南针对**在 x86 主机上用 QEMU 模拟 RISC-V** 的情况（不需要真实 RISC-V 硬件）。
> 如果你用的是**进迭时空 K3 真实板子**，请看 [README_k3.md](README_k3.md)。

---

## 一、概述

在 **x86 主机**上**交叉编译** OAI 到 RISC-V，然后用 **QEMU（qemu-riscv64）** 模拟运行 gNB + UE，通过 **rfsim** 跑通端到端通信。

```
[x86 主机]
   交叉编译 ──► RISC-V 可执行文件
   QEMU 模拟 ──► gNB + UE 通过 rfsim 通信
```

---

## 二、环境要求

| 组件 | 版本 |
|---|---|
| 主机 | x86_64 Linux（Ubuntu 22.04）|
| 交叉编译链 | `riscv64-linux-gnu-gcc` ≥ 11 |
| QEMU | `qemu-riscv64` ≥ 6 |
| asn1c | v0.9.29 |
| CMake | ≥ 3.16 |

---

## 三、从零开始搭建

### 第 1 步：安装 RISC-V 交叉编译链

```bash
sudo apt update
sudo apt install -y gcc-riscv64-linux-gnu g++-riscv64-linux-gnu
```

验证：
```bash
riscv64-linux-gnu-gcc --version
```

### 第 2 步：安装 QEMU

```bash
sudo apt install -y qemu-user qemu-system
```

验证：
```bash
qemu-riscv64 --version
```

### 第 3 步：安装构建依赖

```bash
sudo apt install -y cmake build-essential libconfig-dev libsctp-dev \
  libblas-dev liblapack-dev libgfortran5 python3
```

### 第 4 步：安装 asn1c（v0.9.29）

```bash
cd /tmp
git clone https://github.com/vlm/asn1c.git
cd asn1c
git checkout v0.9.29
autoreconf -fi
./configure
make -j$(nproc)
sudo make install
```

验证：
```bash
asn1c -v   # 应显示 v0.9.29
```

> **重要**：asn1c 版本必须是 **v0.9.29**。不同版本生成的代码布局不同，可能导致编译错误。

### 第 5 步：克隆本仓库

```bash
git clone https://github.com/feeasolfnj/oai-riscv.git
cd oai-riscv
```

---

## 四、构建 OAI（在 x86 主机上交叉编译）

### 第 1 步：准备 stubs_link.o（RISC-V 运行时桩）

```bash
cd cmake_targets
riscv64-linux-gnu-gcc -c -march=rv64gcv -mabi=lp64d \
  -isystem ../cmake_targets/riscv64-stubs/include \
  -isystem /usr/riscv64-linux-gnu/include \
  ../riscv-env/stubs_link.c -o ../riscv-env/stubs_link.o
cd ..
```

### 第 2 步：配置 CMake（交叉编译）

```bash
mkdir -p build-riscv && cd build-riscv
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=../cmake_targets/riscv64-toolchain.cmake \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo
```

> **关键**：用 `riscv64-toolchain.cmake` 告诉 CMake 用 RISC-V 交叉编译链。

### 第 3 步：编译

```bash
make nr-softmodem -j$(nproc)    # 编译 gNB（基站）
make nr-uesoftmodem -j$(nproc)  # 编译 UE（终端）
make rfsimulator -j$(nproc)     # 编译 rfsim 库
```

### 第 4 步：把 stubs_link.o 加入链接命令（务必）

```bash
sed -i 's|CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|' \
  build-riscv/CMakeFiles/nr-softmodem.dir/link.txt

sed -i 's|CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|' \
  build-riscv/CMakeFiles/nr-uesoftmodem.dir/link.txt
```

> 把 `<USER>` 替换成你的用户名。然后重新 `make nr-softmodem nr-uesoftmodem`。

### 第 5 步：大文件编译优化（解决 JAL 跳转截断）

`nr_ulsch_llr_computation.c` 等大文件在 `-O2` 下会报 `relocation truncated to fit: R_RISCV_JAL`。用 `-Os -fno-unroll-loops` 单独编译：

```bash
# 找到该文件的编译命令（make 输出里），把 -O2 换成 -Os -fno-unroll-loops 重新编译
sed 's/-O2/-Os -fno-unroll-loops/' cmd.sh | bash
```

---

## 五、准备 RISC-V 运行库（QEMU 用）

QEMU 在 x86 上模拟 RISC-V，需要 RISC-V 版的动态库放到 `riscv-env/lib/`：

```bash
# 从 RISC-V sysroot 复制基础库
cp /usr/riscv64-linux-gnu/lib/libc.so.6 riscv-env/lib/
cp /usr/riscv64-linux-gnu/lib/libstdc++.so.6 riscv-env/lib/
# 编译/获取 libz、libsctp、libconfig、libopenblas 的 RISC-V 版放入 riscv-env/lib/
```

---

## 六、运行 rfsim（QEMU）

### 一键运行

```bash
cd /home/<USER>/oai-riscv
sudo ./run_rfsim.sh full
```

### 手动运行

**终端 1：启动 gNB（基站）**
```bash
cd /home/<USER>/oai-riscv
export LD_LIBRARY_PATH=/home/<USER>/oai-riscv/riscv-env/lib
sudo qemu-riscv64 -L /usr/riscv64-linux-gnu \
  ./build-riscv/nr-softmodem \
  -O ci-scripts/conf_files/gnb.sa.band78.106prb.rfsim.conf \
  --rfsim --sa --noS1
```

**终端 2：启动 UE（终端）**
```bash
cd /home/<USER>/oai-riscv
export LD_LIBRARY_PATH=/home/<USER>/oai-riscv/riscv-env/lib
sudo qemu-riscv64 -L /usr/riscv64-linux-gnu \
  ./build-riscv/nr-uesoftmodem \
  -O ci-scripts/conf_files/nrue.band78.106prb.rfsim.conf \
  --rfsim --noS1 --sa -C 3319680000
```

> **注意**：QEMU 用户态对 SCTP 支持不完整，连核心网（去掉 `--noS1`）会失败。noS1 模式不受影响。

### 停止

```bash
sudo ./run_rfsim.sh stop
```

---

## 七、验证运行成功

```bash
# 看状态
sudo ./run_rfsim.sh status

# Ping 测试
ping -I 10.0.1.1 -c 3 10.0.1.2
```

**完整流程跑通的标志**（日志中出现）：

| 日志 | 含义 |
|---|---|
| `rfsim write[...]: active_clients=1` | gNB 发射，UE 连接 |
| `CBRA procedure succeeded!` | 接入成功 |
| `UE State = NR_RRC_CONNECTED` | RRC 连接建立 |
| `reconfiguring DRB 1` | 数据承载建立 |
| `enb_tun_read: read 48 bytes` | **用户数据传输** |

---

## 八、命令行参数

| 参数 | 含义 |
|---|---|
| `-O <conf>` | 配置文件 |
| `--rfsim` | 使用 rfsim 软件射频 |
| `--sa` | 独立组网 |
| `--noS1` | 不连核心网 |
| `-C <freq>` | 载波频率（Hz）|

---

## 九、常见问题

### Q1: 编译报 `relocation truncated to fit: R_RISCV_JAL`
大文件 JAL 跳转超范围。用 `-Os -fno-unroll-loops` 编译该文件。

### Q2: 链接报 `undefined reference to 's1ap_config'` / `'__builtin_cpu_init'`
没加 `stubs_link.o`。按"第四节第 4 步"处理。

### Q3: gNB 启动崩溃
检查 `LD_LIBRARY_PATH`、`riscv-env/lib` 库、是否用 `sudo`。

### Q4: 接入很慢（几十秒到几分钟）
正常。QEMU + simde 模拟慢。真实板子快很多。

---

## 十、5G 核心网（可选）

QEMU 用户态连核心网会因 SCTP 缺陷失败，需 QEMU 系统模式或真实 RISC-V 板子。
