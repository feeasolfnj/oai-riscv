# OAI 5G RISC-V 移植（rfsim）

将 **OpenAirInterface（OAI）5G 协议栈** 移植到 **RISC-V 指令集架构**，并通过 **rfsim**（软件射频模拟）跑通 **gNB（基站）+ UE（终端）** 的端到端通信。

本项目基于 [OAI 官方 openairinterface5g](https://gitlab.eurecom.fr/oai/openairinterface5g) 的 riscv-port 分支，完成了 RISC-V 交叉编译、ASN.1 适配、SIMD 移植、rfsim 运行等全部工作。

---

## 功能概述

- ✅ OAI 5G **gNB + UE 编译到 RISC-V**
- ✅ 通过 **rfsim** 跑通端到端（RACH → RRC → DRB → 用户数据传输）
- ✅ 全部信令协议真实现（S1AP/F1AP/E1AP/M2AP/M3AP/NGAP/X2AP）
- ✅ 附带 Open5GS 5G 核心网部署（可选）

---

## 使用方式（二选一）

本项目支持两种运行环境，**请根据你使用的硬件选择对应指南**：

| 指南 | 适用场景 | 在哪里编译 |
|---|---|---|
| **[README_qemu.md](README_qemu.md)** | 用 **QEMU 模拟** RISC-V（无真实硬件）| 在 **x86 主机**上交叉编译 |
| **[README_k3.md](README_k3.md)** | 用 **进迭时空 K3 真实板子**（RISC-V CPU）| 在 **K3 板子**上原生编译 |

> **简单说**：用什么板子，就在哪里编译。
> - 用 QEMU → 看 `README_qemu.md`，在 x86 主机交叉编译
> - 用 K3 板子 → 看 `README_k3.md`，在板子上原生编译

---

## 一键运行脚本

| 脚本 | 用途 |
|---|---|
| `run_rfsim.sh` | QEMU 版（x86 主机 + QEMU）|
| `run_rfsim_k3.sh` | K3 板子版（真实 RISC-V，不需要 QEMU）|

---

## 目录结构

```
oai-riscv/
├── openair1/          # PHY 物理层
├── openair2/          # RRC/MAC/RLC/PDCP 等
├── openair3/          # NGAP/S1AP 等核心网接口
├── cmake_targets/     # 构建配置（riscv64-toolchain.cmake）
├── ci-scripts/conf_files/  # rfsim 配置文件
├── riscv-env/         # RISC-V 运行库和桩
├── riscv-port-scripts/ # 移植辅助脚本
├── run_rfsim.sh       # QEMU 一键运行脚本
├── run_rfsim_k3.sh    # K3 板子一键运行脚本
├── README_qemu.md     # QEMU 使用指南
├── README_k3.md       # K3 板子使用指南
└── build-riscv/       # 编译产物（gitignore）
```

---

## 致谢

- [OAI openairinterface5g](https://gitlab.eurecom.fr/oai/openairinterface5g)
- [asn1c](https://github.com/vlm/asn1c)
- [simde](https://github.com/simd-everywhere/simde)
- [Open5GS](https://open5gs.org)
- [进迭时空 SpacemiT](https://www.spacemit.com)

---

## 许可证

遵循 OAI 的 [OSI license](https://www.openairinterface.org/?page_id=698)。
