# OAI 5G RISC-V 移植 — 进迭时空 K3 板子使用指南

> 本指南针对**使用真实 RISC-V 板子（进迭时空 SpacemiT K3）** 的情况，直接在板子上编译和运行，**不需要 QEMU**。
> 如果你用的是 **x86 主机 + QEMU 模拟**，请看 [README_qemu.md](README_qemu.md)。

---

## 一、概述

在 **K3 板子**上（CPU 本身就是 RISC-V）**原生编译**和**原生运行** OAI 的 gNB + UE，通过 **rfsim** 跑通端到端通信。

```
[K3 板子]  (RISC-V CPU，原生执行)
   原生编译 ──► gNB + UE
   原生运行 ──► rfsim 端到端
```

**优势**（对比 QEMU）：
- 无 QEMU 的 SCTP 限制，可连真实 5G 核心网
- 原生 RISC-V 执行 + RVV 向量指令，性能好
- 接入快

---

## 二、硬件要求

| 组件 | 说明 |
|---|---|
| 板子 | 进迭时空 SpacemiT K3（如 K3 Pico-ITX）|
| 内存 | 建议 ≥ 8GB（K3 Pico-ITX 16/32GB）|
| 存储 | 建议 ≥ 32GB（K3 Pico-ITX 128/256GB UFS）|
| 系统 | Debian/Ubuntu riscv64 版（官方镜像）|

> K3 Pico-ITX 规格：双通道 LPDDR5 16/32GB，板载 UFS 128/256GB。**资源足够在板子上编译 OAI**。

---

## 三、在 K3 板子上编译（原生编译）

> **注意**：K3 板子上编译**不需要交叉编译链**（板子自带 RISC-V 版 gcc），也不需要 `riscv64-toolchain.cmake`。

### 第 1 步：安装编译工具和依赖

```bash
sudo apt update
sudo apt install -y gcc g++ make cmake git python3 \
  libconfig-dev libsctp-dev libz-dev libopenblas-dev libgfortran5
```

### 第 2 步：安装 asn1c（必须用 mouse07410 分支的 `940dd5fa`，支持 -gen-APER 且生成完整 S1AP 布局）

> **⚠️ 重要**：OAI 的 CMake 使用 `-gen-APER` / `-no-gen-UPER` / `-no-gen-JER` 等新版 flags。
> 需要两个条件同时满足，否则编译失败：
> 1. **支持 `-gen-APER`**：`vlm/asn1c`（标准版）`v0.9.29` 标签**不支持**，报 `-gen-APER: Invalid argument`。
> 2. **生成完整 S1AP 布局**：mouse07410 的 `844f9ca` commit 虽支持 `-gen-APER`，但生成的 S1AP 类型是**不完整前向声明**，报 `error: field '...' has incomplete type`。
>
> **必须使用 `mouse07410/asn1c` 仓库的 `940dd5fa` commit**——它同时满足上述两个条件（支持 `-gen-APER`，且生成完整 S1AP 布局）。

```bash
cd /tmp
git clone https://github.com/mouse07410/asn1c.git
cd asn1c
git checkout 940dd5fa        # 关键：支持 -gen-APER 且生成完整 S1AP 布局的 commit
autoreconf -fi
./configure
make -j$(nproc)
sudo make install
```

验证（**必须确认支持 -gen-APER，不能只看版本号**）：
```bash
asn1c -v                              # 应显示 v0.9.29 或更新
asn1c -h | grep -E "no-gen-UPER|no-gen-APER"   # 有输出 = 支持 OAI flags（关键！）
asn1c -gen-APER >/dev/null 2>&1; echo $?       # 退出码=1 正常；=64 说明不支持（装错了）
```

> **排查**：
> - 如果 `asn1c -gen-APER` 退出码是 `64`（报 `Invalid argument`）→ asn1c 不支持 flags，重新装。
> - 如果编译报 `field 'E_RABSubjecttoDataForwardingList' has incomplete type` → asn1c 版本不对（用了 `844f9ca`），改成 `940dd5fa` 重装。

### 第 3 步：克隆本仓库

```bash
git clone https://github.com/feeasolfnj/oai-riscv.git
cd oai-riscv
```

### 第 4 步：准备 stubs_link.o（K3 板子用系统 gcc）

```bash
cd cmake_targets
gcc -c -march=rv64gcv -mabi=lp64d \
  -isystem ../cmake_targets/riscv64-stubs/include \
  ../riscv-env/stubs_link.c -o ../riscv-env/stubs_link.o
cd ..
```

### 第 5 步：配置 CMake（原生编译，不用交叉编译链）

```bash
mkdir -p build-riscv && cd build-riscv
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
```

> **关键区别**：K3 板子上原生编译**不需要 `-DCMAKE_TOOLCHAIN_FILE`**（因为本地就是 riscv64）。

### 第 6 步：编译

```bash
make nr-softmodem -j$(nproc)    # 编译 gNB（基站）
make nr-uesoftmodem -j$(nproc)  # 编译 UE（终端）
make rfsimulator -j$(nproc)     # 编译 rfsim 库
```

### 第 7 步：把 stubs_link.o 加入链接命令（务必）

```bash
sed -i 's|CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|' \
  build-riscv/CMakeFiles/nr-softmodem.dir/link.txt

sed -i 's|CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|' \
  build-riscv/CMakeFiles/nr-uesoftmodem.dir/link.txt
```

> 把 `<USER>` 替换成你的用户名。然后重新 `make nr-softmodem nr-uesoftmodem`。

### 第 8 步：大文件编译优化（解决 JAL 跳转截断）

`nr_ulsch_llr_computation.c` 等大文件在 `-O2` 下会报 `relocation truncated to fit: R_RISCV_JAL`。用 `-Os -fno-unroll-loops` 单独编译：

```bash
sed 's/-O2/-Os -fno-unroll-loops/' cmd.sh | bash
```

---

## 四、运行 rfsim（K3 板子）

### 一键运行（推荐，K3 专用脚本）

```bash
cd /home/<USER>/oai-riscv
sudo ./run_rfsim_k3.sh full      # 完整运行（gNB + UE + 路由）
sudo ./run_rfsim_k3.sh status    # 查看状态
sudo ./run_rfsim_k3.sh ping      # Ping 测试
sudo ./run_rfsim_k3.sh stop      # 停止
```

> `run_rfsim_k3.sh` 直接用系统库（`/usr/lib:/usr/lib/riscv64-linux-gnu`），不需要 `riscv-env/lib/`。

### 手动运行

**终端 1：启动 gNB（基站）**
```bash
cd /home/<USER>/oai-riscv
sudo ./build-riscv/nr-softmodem \
  -O ci-scripts/conf_files/gnb.sa.band78.106prb.rfsim.conf \
  --rfsim --sa --noS1
```

**终端 2：启动 UE（终端）**
```bash
cd /home/<USER>/oai-riscv
sudo ./build-riscv/nr-uesoftmodem \
  -O ci-scripts/conf_files/nrue.band78.106prb.rfsim.conf \
  --rfsim --noS1 --sa -C 3319680000
```

### 停止

```bash
sudo pkill -f "nr-softmodem"
sudo pkill -f "nr-uesoftmodem"
sudo ip link delete oaitun_enb1 2>/dev/null
sudo ip link delete oaitun_ue1 2>/dev/null
```

---

## 五、验证运行成功

```bash
# 看状态
sudo ./run_rfsim_k3.sh status

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

## 六、连接 5G 核心网（可选）

K3 板子跑完整 Linux 内核，**SCTP 完整**，可以连真实 5G 核心网（Open5GS）：

```bash
# 去掉 --noS1，让 gNB 通过 NGAP 连核心网
sudo ./build-riscv/nr-softmodem \
  -O ci-scripts/conf_files/gnb.sa.band78.106prb.rfsim.conf \
  --rfsim --sa
```

> 需要先部署 5G 核心网（如 Open5GS），并配置 AMF 地址。

---

## 七、命令行参数

| 参数 | 含义 |
|---|---|
| `-O <conf>` | 配置文件 |
| `--rfsim` | 使用 rfsim 软件射频 |
| `--sa` | 独立组网 |
| `--noS1` | 不连核心网 |
| `-C <freq>` | 载波频率（Hz）|

---

## 八、常见问题

### Q0: 编译报 `-gen-APER: Invalid argument` / `ANY_aper.c] 错误 64`
**asn1c 版本不对**。OAI 的 CMake 需要 `-gen-APER`/`-no-gen-UPER` 等新版 flags，但 `vlm/asn1c` 标准版 `v0.9.29` 不支持。
**解决**：按"第三节第 2 步"安装 `mouse07410/asn1c` 的 `940dd5fa` commit（不要用 `v0.9.29` 标签，也不要只用 `844f9ca`——它虽支持 flags 但 S1AP 布局不完整）。装完用 `asn1c -gen-APER` 验证（退出码应为 1，不是 64）。

### Q0.1: 编译报 `field 'E_RABSubjecttoDataForwardingList' has incomplete type`
**asn1c 版本生成 S1AP 布局不完整**。`844f9ca` commit 生成的 `S1AP_E-RAB-IE-ContainerList.h` 里 `typedef struct S1AP_ProtocolIE_ContainerList` 是前向声明，未定义。
**解决**：改用 `940dd5fa` commit 重新编译 asn1c（该版本 typedef 到完整类型 `S1AP_ProtocolIE_ContainerList_7313P0_t`）。

### Q1: 编译报 `relocation truncated to fit: R_RISCV_JAL`
大文件 JAL 跳转超范围。用 `-Os -fno-unroll-loops` 编译该文件。

### Q2: 链接报 `undefined reference to 's1ap_config'` / `'__builtin_cpu_init'`
没加 `stubs_link.o`。按"第三节第 7 步"处理。

### Q3: 报 `Protocol not available`（SCTP）
板子内核需启用 `CONFIG_SCTP`。检查系统是否支持 SCTP。

### Q4: gNB 启动崩溃
检查库是否装齐、是否用 `sudo`。

---

## 九、注意

- K3 板子上**原生编译**，不需要交叉编译链（那是 QEMU 场景用的）
- 板子内存/存储资源足够编译（K3 Pico-ITX 16/32GB 内存，128/256GB UFS）
- 如果要在 x86 上交叉编译后拷到板子，参考 [README_qemu.md](README_qemu.md) 的编译部分
