# OAI 5G RISC-V 移植（rfsim）

将 **OpenAirInterface（OAI）5G 协议栈** 移植到 **RISC-V 指令集架构**，并在 **QEMU 虚拟机**上通过 **rfsim**（软件射频模拟）跑通 **gNB（基站）+ UE（终端）** 的端到端通信。

本项目基于 [OAI 官方 openairinterface5g](https://gitlab.eurecom.fr/oai/openairinterface5g) 的 riscv-port 分支，完成了 RISC-V 交叉编译、ASN.1 适配、SIMD 移植、rfsim 运行等全部工作。

---

## 一、功能概述

- ✅ OAI 5G **gNB + UE 交叉编译到 RISC-V**
- ✅ 在 **QEMU riscv64** 上运行
- ✅ 通过 **rfsim** 跑通端到端（RACH → RRC → DRB → 用户数据传输）
- ✅ 全部信令协议真实现（S1AP/F1AP/E1AP/M2AP/M3AP/NGAP/X2AP）
- ✅ 附带 Open5GS 5G 核心网部署（可选）

---

## 二、环境要求

| 组件 | 版本 |
|---|---|
| 主机 | x86_64 Linux（Ubuntu 22.04）|
| 交叉编译链 | `riscv64-linux-gnu-gcc` ≥ 11 |
| QEMU | `qemu-riscv64` ≥ 6 |
| asn1c | v0.9.29 |
| CMake | ≥ 3.16 |
| Python | 3.x |

---

## 三、从零开始搭建（一步一步）

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

OAI 的 ASN.1 代码需要特定版本的 asn1c 生成。从源码编译：

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

> **重要**：请确保 `asn1c` 在 PATH 中，版本为 **v0.9.29**。不同版本生成的代码布局不同，可能导致编译错误。

### 第 5 步：克隆本仓库

```bash
git clone https://github.com/feeasolfnj/oai-riscv.git
cd oai-riscv
```

---

## 四、构建 OAI（编译到 RISC-V）

### 方式一：使用一键构建脚本

```bash
# 准备 stubs_link.o（RISC-V 运行时桩）
cd cmake_targets
riscv64-linux-gnu-gcc -c -march=rv64gcv -mabi=lp64d \
  -isystem ../cmake_targets/riscv64-stubs/include \
  -isystem /usr/riscv64-linux-gnu/include \
  ../riscv-env/stubs_link.c -o ../riscv-env/stubs_link.o
cd ..

# CMake 配置
mkdir -p build-riscv && cd build-riscv
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=../cmake_targets/riscv64-toolchain.cmake \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo
```

### 方式二：手动配置 + 编译

```bash
# 1. 配置 CMake
mkdir -p build-riscv && cd build-riscv
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=../cmake_targets/riscv64-toolchain.cmake \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo

# 2. 编译 gNB（基站）
make nr-softmodem -j$(nproc)

# 3. 编译 UE（终端）
make nr-uesoftmodem -j$(nproc)

# 4. 编译 rfsim 库
make rfsimulator -j$(nproc)
```

---

## 五、关键构建处理（务必执行）

### 1. 添加 stubs_link.o 到链接命令

RISC-V 需要额外的运行时桩（`s1ap_config`、`__builtin_cpu_init` 等）。CMake 不会自动链接它，需要手动加入：

```bash
sed -i 's|CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-softmodem.dir/executables/nr-gnb.c.o|' \
  build-riscv/CMakeFiles/nr-softmodem.dir/link.txt

sed -i 's|CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|/home/<USER>/oai-riscv/riscv-env/stubs_link.o CMakeFiles/nr-uesoftmodem.dir/executables/nr-ue.c.o|' \
  build-riscv/CMakeFiles/nr-uesoftmodem.dir/link.txt
```

> **注意**：把 `<USER>` 替换成你的实际用户名。

### 2. 大文件编译优化（解决 RISC-V JAL 跳转截断）

`nr_ulsch_llr_computation.c` 等大文件在 `-O2` 下会因 RISC-V 指令跳转范围限制报错。需要单独用 `-Os -fno-unroll-loops` 编译：

```bash
cd build-riscv
# 找到该文件的编译命令（在 make 输出里），将 -O2 换成 -Os -fno-unroll-loops 重新编译
# 或直接用以下方式（假设编译命令已保存到 cmd.sh）
sed 's/-O2/-Os -fno-unroll-loops/' cmd.sh | bash
```

> **如果编译报 `relocation truncated to fit: R_RISCV_JAL`**，说明是这个问题。用 `-Os -fno-unroll-loops` 重新编译对应文件即可。

---

## 六、准备 RISC-V 运行库

OAI 在 QEMU 上运行需要 RISC-V 版的动态库。把这些库放到 `riscv-env/lib/`：

```bash
# 从 RISC-V sysroot 复制基础库
cp /usr/riscv64-linux-gnu/lib/libc.so.6 riscv-env/lib/
cp /usr/riscv64-linux-gnu/lib/libstdc++.so.6 riscv-env/lib/
# 编译/获取 libz、libsctp、libconfig、libopenblas 的 RISC-V 版放入 riscv-env/lib/
```

---

## 七、运行 rfsim（gNB + UE 端到端）

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

### 停止

```bash
sudo ./run_rfsim.sh stop
# 或
sudo pkill -f "qemu.*nr-softmodem"
sudo pkill -f "qemu.*nr-uesoftmodem"
sudo ip link delete oaitun_enb1 2>/dev/null
sudo ip link delete oaitun_ue1 2>/dev/null
```

---

## 八、验证运行成功

**完整流程跑通的标志**（在日志中依次出现）：

| 日志 | 含义 |
|---|---|
| `rfsim write[...]: active_clients=1` | gNB 发射信号，UE 连接 |
| `RAPROC ... preamble xx` | UE 随机接入 |
| `CBRA procedure succeeded!` | 接入成功 |
| `UE State = NR_RRC_CONNECTED` | RRC 连接建立 |
| `reconfiguring DRB 1` | 数据承载建立 |
| `enb_tun_read: read 48 bytes` / `deliver_sdu_drb` | **用户数据传输** |

日志位置：
```bash
tail -f /tmp/gnb_rfsim.log   # gNB
tail -f /tmp/ue_rfsim.log    # UE
```

---

## 九、命令行参数

| 参数 | 含义 |
|---|---|
| `-O <conf>` | 配置文件 |
| `--rfsim` | 使用 rfsim 软件射频 |
| `--sa` | 独立组网（Standalone）|
| `--noS1` | 不连核心网 |
| `-C <freq>` | 载波频率（Hz）|

---

## 十、常见问题

### Q1: 编译报 `relocation truncated to fit: R_RISCV_JAL`
大文件 JAL 跳转超范围。用 `-Os -fno-unroll-loops` 编译该文件。

### Q2: 链接报 `undefined reference to 's1ap_config'` / `'__builtin_cpu_init'`
没加 `stubs_link.o`。按"第五节"处理。

### Q3: gNB 启动崩溃
检查：`LD_LIBRARY_PATH` 是否设置、是否用 `sudo`、`riscv-env/lib` 库是否齐全。

### Q4: 接入很慢（几十秒）
正常。PHY 层用 simde 模拟 x86 SIMD，QEMU 上性能较慢。真实 RISC-V 板子快很多。

### Q5: 连核心网时 SCTP 报 `Protocol not available`
QEMU 用户态对 SCTP 支持不完整。noS1 模式不受影响。需连核心网请用 QEMU 系统模式或真实 RISC-V 板子。

---

## 十一、5G 核心网（可选）

已支持部署 **Open5GS** 5G 核心网（10 个组件），让 gNB 连真实核心网。

```bash
# 参考：安装 Open5GS（需从源码编译，见报告）
# 启动各组件
/usr/local/bin/open5gs-nrfd -c /usr/local/etc/open5gs/nrf.yaml
/usr/local/bin/open5gs-amfd -c /usr/local/etc/open5gs/amf.yaml
# ... 依此类推
```

> **注意**：QEMU 用户态连核心网会因 SCTP 缺陷失败，需 QEMU 系统模式或真实 RISC-V 板子（如进迭时空 K1/K3）。

---

## 十二、目录结构

```
oai-riscv/
├── openair1/          # PHY 物理层
├── openair2/          # RRC/MAC/RLC/PDCP 等
├── openair3/          # NGAP/S1AP 等核心网接口
├── cmake_targets/     # 构建配置（riscv64-toolchain.cmake）
├── ci-scripts/conf_files/  # rfsim 配置文件
├── riscv-env/         # RISC-V 运行库和桩
├── riscv-port-scripts/ # 移植辅助脚本
├── run_rfsim.sh       # 一键运行脚本
└── build-riscv/       # 编译产物（gitignore）
```

---

## 十三、致谢

- [OAI openairinterface5g](https://gitlab.eurecom.fr/oai/openairinterface5g)
- [asn1c](https://github.com/vlm/asn1c)
- [simde](https://github.com/simd-everywhere/simde)
- [Open5GS](https://open5gs.org)

---

## 许可证

遵循 OAI 的 [OSI license](https://www.openairinterface.org/?page_id=698)。
