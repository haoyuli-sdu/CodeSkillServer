---
name: "orangepi4pro"
description: "Use when working on or targeting an Orange Pi 4 Pro (A733 chip). Activates when Claude Code runs directly on the Orange Pi 4 Pro board for on-device development (GPIO, I2C, SPI, UART, PWM, NPU, camera, display, compile on target), or when cross-developing from a PC to deploy onto this board. Covers hardware specs, Linux/Android system config, wiringOP/wiringOP-Python programming, edge AI (3 TOPS NPU), orangepi-build SDK, and troubleshooting."
---

# Orange Pi 4 Pro (A733) 完整开发指南

---

## 速览：Claude Code 板载开发 · Onboard Development

> **核心场景：** Claude Code 直接运行在 Orange Pi 4 Pro 的 Debian/Ubuntu 系统上，此技能赋予它对硬件、驱动、命令的完整认知。你只需用自然语言描述需求，Claude Code 就能直接操控 GPIO、读取传感器、编译代码、配置服务——**秒级从想法到运行**。

### 典型对话示例

```
👤 你：写个程序，用 I2C OLED 显示 CPU 温度和 IP 地址
🤖 Claude Code：
    1. 检查 I2C 已启用 → sudo orangepi-config
    2. 扫描 I2C 设备 → i2cdetect -y 0 找到 0x3C
    3. 安装依赖 → pip3 install luma.oled
    4. 生成 Python 代码 → 读取 thermal_zone0 + hostname -I
    5. 运行 → python3 oled_info.py
    6. 创建 systemd 服务 → 开机自启
    ✅ 直接可用！

👤 你：GPIO 7 接的 LED 不亮，怎么排查？
🤖 Claude Code：
    1. gpio readall → 确认 wPi 映射
    2. gpio mode 2 out → 设置输出
    3. gpio write 2 1 → 输出高电平
    4. 用万用表测量 3.3V 引脚 → 确认电压正常
    5. 检查接线 → GPIO→电阻→LED→GND
    🔍 精确到每一步！

👤 你：编译一个带 NPU 加速的目标检测程序
🤖 Claude Code：
    1. 确认 NPU 驱动正常 → ls /dev/video8
    2. 直接生成 CMakeLists.txt + C++ 源码
    3. cmake && make → 板载编译
    4. ./yolo_detect /dev/video8 → 实时检测
    🚀 板载端到端！
```

### 技能优势

| 没有这个 Skill | 有这个 Skill |
|--------------|------------|
| ❌ Claude Code 不知道 GPIO 引脚映射 | ✅ 精确知道 Pin7=wPi2=PL4 |
| ❌ 生成的代码用错库（如 RPi.GPIO） | ✅ 自动使用 wiringOP/wiringOP-Python |
| ❌ 不知道哪些外设默认关闭 | ✅ 知道 SPI/I2C/UART/PWM 需 orangepi-config 启用 |
| ❌ Linux 命令不带 `sudo` 权限不足 | ✅ 知道何时需要 sudo（GPIO 操作等） |
| ❌ 不知道设备节点路径 | ✅ 精确：`/dev/spidev3.0`、`/dev/i2c-3`、`/sys/class/pwm/pwmchip20/pwm2` |
| ❌ Debian 12 用 `eth0` 找不到网口 | ✅ 知道 Debian 12 用 `end0` |
| ❌ 建议用 `dd` 烧录镜像 | ✅ 知道推荐用 balenaEtcher/PhoenixCard |
| ❌ 不知道 NPU 工具链版本 | ✅ 知道 RKNN SDK v2.0.10、pegasus 转换管线 |

### Claude Code 在板上的运行要求

```bash
# Claude Code 支持 aarch64 Linux，可在 Orange Pi 4 Pro 上本地运行
# 官方安装方式（Node.js >= 18）
curl -fsSL https://nodejs.org/dist/v20.x/node-v20.x-linux-arm64.tar.xz | sudo tar -xJ -C /usr/local --strip-components=1
npm install -g @anthropic-ai/claude-code

# 安装此 skill
# npx skills add HBConline/orangepi4pro-skill -g -y
# 或手动：git clone https://github.com/HBConline/orangepi4pro-skill.git
mkdir -p ~/.agents/skills/orangepi4pro
cp -r orangepi4pro-skill/* ~/.agents/skills/orangepi4pro/
mkdir -p ~/.claude/skills
ln -sf ~/.agents/skills/orangepi4pro ~/.claude/skills/orangepi4pro
```

---

## 第一章：基本特性与硬件规格

### 1.1 什么是 Orange Pi 4 Pro

Orange Pi 4 Pro 采用**全志 A733 八核处理器**，集成：
- **CPU：** 双核 Arm Cortex-A76 + 六核 Arm Cortex-A55 大小核架构
- **制程：** 12nm
- **最高主频：** 2.0GHz
- **协处理器：** RISC-V E902（200MHz）
- **GPU：** Imagination BXM-4-64
- **NPU：** 3 TOPS，满足边缘智能 AI 加速应用
- **内存：** 最高支持 16GB LPDDR5
- **视频解码：** 最高 8K@24fps H.265/VP9/AVS2
- **视频编码：** 最高 4K@30fps H.265/H.264
- **接口：** 千兆以太网、PCIe 3.0、USB 3.0、MIPI-CSI、MIPI-DSI、40Pin 扩展接口
- **操作系统：** Ubuntu、Debian、Android 13

### 1.2 用途

- 小型 Linux 桌面计算机 / 网络服务器
- Android 平板 / 游戏机
- 生成式 AI、人工智能算法场景化落地
- 智能工控、智能商显、零售支付、智慧教育、商用机器人、车载终端、视觉辅驾、边缘计算、智能配电终端

### 1.3 目标用户

创客、梦想家、业余爱好者 — 从创意到原型再到批量生产。

### 1.4 完整硬件规格表

| 类别 | 规格 |
|------|------|
| **处理器** | 全志 A733：2×Cortex-A76 + 6×Cortex-A55，最高 2.0GHz |
| **协处理器** | RISC-V E902（200MHz） |
| **GPU** | Imagination BXM-4-64 |
| **NPU** | 3 TOPS |
| **内存** | 最高 16GB LPDDR5 |
| **eMMC** | 可选模块：16GB/32GB/64GB/128GB |
| **SPI Flash** | 128Mb（默认贴）/ 256Mb 可选 |
| **M.2** | M-Key Socket，PCIe 3.0 NVMe SSD |
| **uSD 卡槽** | 支持最大 128GB uSD 卡 |
| **Wi-Fi + 蓝牙** | 二合一模块，Wi-Fi 6 + BT 5.4（BLE） |
| **以太网** | 千兆，板载 PHY 芯片 YT8531CA，支持 PoE 供电 |
| **HDMI** | 1×HDMI TX 2.0，最高 4K@60fps |
| **MIPI-DSI** | 1×4-lane |
| **MIPI-CSI** | 1×2-lane + 1×4-lane |
| **USB** | 1×USB Type-A 3.0 + 3×USB Type-A 2.0 HOST |
| **音频** | 3.5mm 耳机插孔（音频输入/输出），单扬声器，单麦克风 |
| **按键** | 1×BOOT，1×RESET，1×PWR ON |
| **40Pin** | GPIO、UART、I2C、SPI、PWM |
| **DEBUG** | 3Pin 调试串口 |
| **电源** | Type-C 5V 3A DC IN（不支持 PD 协商，仅固定 5V） |
| **LED** | 红色（电源指示，硬件控制常亮），绿色（软件控制，内核启动后闪烁） |
| **PCB 尺寸** | 89mm × 56mm |
| **重量** | 58g |
| **定位孔** | 4 个，直径 3.0mm |
| **支持 OS** | Ubuntu、Debian、Android 13 |

---

## 第二章：开发板使用介绍

### 2.1 准备需要的配件

| # | 配件 | 说明 |
|---|------|------|
| 1 | TF 卡 | 最小 8GB，Class 10 级或以上高速卡，建议闪迪 |
| 2 | TF 卡读卡器 | 用于读写 TF 卡 |
| 3 | HDMI 显示器 | 带 HDMI 接口 |
| 4 | HDMI 线 | HDMI 转 HDMI 连接线 |
| 5 | 10.1寸 MIPI 屏幕（可选） | 含转接板，兼容 OPi5Plus/OPi5B/OPi5/OPi5Pro/OPi5Max/OPi4A/OPi4Pro |
| 6 | 电源适配器 | **5V/3A** Type-C 电源（5V/4A 也可）。**严禁使用 >5V 的电源，会烧坏开发板！** |
| 7 | USB 鼠标和键盘 | 标准 USB 接口 |
| 8 | USB 摄像头（可选） | UVC 协议 |
| 9 | 网线 | 百兆或千兆 |
| 10 | USB 2.0 公对公数据线 | 用于 adb 调试、烧录镜像到 eMMC |
| 11 | USB 转 TTL 模块 + 杜邦线 | **3.3V** 电平的 USB 转 TTL 模块（用于串口调试） |
| 12 | X64 电脑 | Ubuntu 22.04 PC（可选，编译源码用）/ Windows PC（烧录镜像用） |
| — | NVMe SSD（可选） | M.2 PCIe 3.0 x1 接口，仅**樊想**和**广存**品牌测试可用 |

> ⚠️ **电源警告：** Type-C 电源接口**不支持 PD 协商功能**，只支持固定 5V 电压输入。不要插入电压大于 5V 的电源适配器。系统启动不稳定往往是供电问题导致，若有不断重启现象请更换电源或 Type-C 数据线。

### 2.2 下载开发板镜像和相关资料

**中文版资料：** `http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-4-Pro.html`

**英文版资料：** `http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-4-Pro.html`

**资料包含：**
- Linux 源码（GitHub）
- Android 镜像（百度云盘 + 谷歌网盘）
- Ubuntu 镜像（百度云盘 + 谷歌网盘）
- Debian 镜像（百度云盘 + 谷歌网盘）
- 用户手册和原理图
- 官方工具（烧录软件等）

### 2.3 基于 Windows PC 将 Linux 镜像烧写到 TF 卡

#### 2.3.1 使用 balenaEtcher 烧录

1. 准备 8GB+ Class 10 TF 卡，建议闪迪
2. 用读卡器将 TF 卡插入电脑
3. 从 Orange Pi 资料页面下载 Linux 镜像压缩包，解压得到 `.img` 文件（1GB 以上）
4. 下载 balenaEtcher：`https://www.balena.io/etcher/`
5. 下载 Windows 版本安装包并安装
6. 若提示错误，右键 → 以管理员身份运行
7. 操作步骤：
   - a. 点击 "Flash from file" 选择 Linux 镜像路径
   - b. 点击 "Select target" 选择 TF 卡盘符
   - c. 点击 "Flash" 开始烧录（紫色进度条）
8. 烧录完成后自动校验（绿色进度条）
9. 绿色指示图标出现 = 成功，退出 balenaEtcher，拔出 TF 卡

#### 2.3.2 使用 Win32DiskImager 烧录

1. 准备 8GB+ Class 10 TF 卡
2. 用读卡器插入电脑
3. **格式化 TF 卡：** 使用 SD Card Formatter
   - 下载：`https://www.sdcard.org/downloads/formatter/eula_windows/SDCardFormatterv5_WinEN.zip`
   - 选择 TF 卡盘符 → 点击 "Format" → 确认格式化
4. 下载 Linux 镜像压缩包，解压得到 `.img` 文件
5. 下载 Win32DiskImager：`http://sourceforge.net/projects/win32diskimager/files/Archive/`
6. 安装后打开：
   - a. 选择镜像文件路径
   - b. 确认 TF 卡盘符
   - c. 点击 "写入"
7. 完成后点击 "退出"，拔出 TF 卡

### 2.4 基于 Ubuntu PC 将 Linux 镜像烧写到 TF 卡

1. 准备 8GB+ Class 10 TF 卡
2. 用读卡器插入电脑
3. 下载 balenaEtcher Linux 版：`https://www.balena.io/etcher/`
4. 下载并解压镜像：
   ```bash
   test@test:~$ 7z x Orangepi4pro_1.0.0_ubuntu_jammy_desktop_linux5.15.147.7z
   test@test:~$ ls Orangepi4pro_1.0.0_ubuntu_jammy_desktop_linux5.15.147.*
   # .7z .sha .img
   ```
5. 校验镜像：
   ```bash
   test@test:~$ sha256sum -c *.sha
   Orangepi4pro_1.0.0_ubuntu_jammy_desktop_linux5.15.147.img: 成功
   ```
6. 双击 `balenaEtcher-1.14.3-x64.AppImage` 打开（无需安装）
7. 同 Windows 步骤选择镜像、TF 卡、Flash，等待校验完成
8. 拔出 TF 卡

> **注意：** 本手册未提供 `dd` 命令烧录方法，仅描述 balenaEtcher 图形界面方式。

### 2.5 烧写 Linux 镜像到 eMMC（见 3.36 节）

### 2.6 烧写 Linux 镜像到 SPIFlash + NVMe SSD（见 3.37 节）

### 2.7 烧写 Android 镜像到 TF 卡

> **关键要求：** 必须使用 **PhoenixCard-4.2.8**，严禁使用 Win32DiskImager 或 balenaEtcher。PhoenixCard 只有 Windows 版本。

1. 安装 **Microsoft Visual C++ 2008 Redistributable - x86**（可从官方工具或微软官网下载，未安装会导致格式化/烧录报错）
2. 准备 8GB+ Class 10 TF 卡
3. 用读卡器插入电脑
4. 从资料页面下载 Android 镜像和 PhoenixCard-4.2.8
5. 解压 Android 镜像得到 `.img` 文件
6. 解压 `PhoenixCard4.2.8.zip`，无需安装直接打开
7. 确认 TF 卡盘符识别正确（如未显示则拔插或点"刷新盘符"）
8. 点击 "恢复卡" 格式化 TF 卡
9. 烧录设置：
   - "固件" → 选择 Android 镜像路径
   - "制作卡的种类" → 选择 **启动卡**
   - 点击**烧卡**
10. 完成后退出，拔出 TF 卡

> **说明：** 烧录后在 Windows 中只能看到 128MB 分区（正常）。Android 有二十几个分区，在 Android 中用 `df -h` 查看。32GB TF 卡约有 24GB 可用。

### 2.8 烧写 Android 镜像到 eMMC

> 需要购买与开发板 eMMC 接口匹配的 eMMC 模块。

**方法：借助 TF 卡完成，分两步**
1. 先用 PhoenixCard 以**量产卡**方式烧录到 TF 卡
2. 用 TF 卡将固件自动刷到 eMMC

**步骤：**
1. 安装 eMMC 模块到开发板
2. 安装 VC++ 2008
3. 准备 8GB+ Class 10 TF 卡
4. 用读卡器插入电脑
5. 下载 Android 镜像和 PhoenixCard-4.2.8
6. 解压镜像和软件
7. 打开 PhoenixCard，确认盘符
8. 点击 "恢复卡" 格式化
9. 设置：
   - "固件" → 选择 Android 镜像路径
   - "制作卡的种类" → 选择**量产卡**
   - 点击"烧卡"
10. 烧录完成退出
11. 将 TF 卡插入开发板，上电启动 → **自动**将固件刷入 eMMC
12. 刷完后**自动关机**（LED 熄灭）
13. 拔出 TF 卡，重新上电启动 eMMC 中的 Android 系统

### 2.9 启动香橙派开发板

1. 插入烧录好镜像的 TF 卡到 TF 卡槽
2. 通过 HDMI 线连接显示器（或 LCD 屏幕）
3. 连接 USB 鼠标和键盘
4. 可选：连接网线
5. 连接 5V/3A Type-C 电源适配器
6. 打开电源开关，HDMI 显示器显示系统启动画面
7. 可选：连接调试串口查看系统输出

### 2.10 调试串口使用方法

#### 2.10.1 连接说明

**所需材料：** 3.3V USB 转 TTL 模块 + 杜邦线

**交叉连接：**
```
USB 转 TTL 模块 GND  →  开发板 GND
USB 转 TTL 模块 RX   →  开发板 TX
USB 转 TTL 模块 TX   →  开发板 RX
```
> 若不确定 TX/RX 顺序，先随便接上，无输出则交换 TX 和 RX。

#### 2.10.2 Ubuntu 平台调试串口（putty）

```bash
# 1. 确认设备节点
test@test:~$ ls /dev/ttyUSB*
/dev/ttyUSB0

# 2. 安装 putty
test@test:~$ sudo apt update
test@test:~$ sudo apt install -y putty

# 3. 以 sudo 运行 putty
test@test:~$ sudo putty
```
**putty 串口设置：**
- Serial line: `/dev/ttyUSB0`
- Speed (baud): `115200`
- Flow control: `None`
- Connection type: `Serial`
- 点击 **Open**

#### 2.10.3 Windows 平台调试串口（MobaXterm）

1. 下载 MobaXterm Home 便携版：`https://mobaxterm.mobatek.net/`
   - 点击 GET XOBATERM NOW! → Home 版本 → Portable 版
2. 解压后双击打开
3. 新建 Session → 选择串口类型 → 选择端口号 → 波特率 `115200`
4. 若看不到端口号，用 360 驱动大师扫描安装 USB 转 TTL 驱动
5. 点击 OK，启动开发板即可看到串口输出

### 2.11 使用 40pin 接口 5V 引脚供电（备选方案）

> 推荐使用 Type-C 电源供电。此方法仅作备选。

**材料：** USB-A 转红黑杜邦线电源线
- USB-A 口插入 5V/3A 电源适配器（**不建议**插电脑 USB）
- **红色杜邦线** → 40pin 5V 引脚
- **黑色杜邦线** → 40pin GND 引脚
- **不要接反！**

---

## 第二章附录：官方工具包速查

> 工具文件位于本仓库 `tools/` 目录 | 详细说明见 `tools/README.md`

### 烧录工具

| 工具 | 用途 | 平台 | 所在文件 |
|------|------|------|---------|
| **balenaEtcher** | Linux 镜像烧录（推荐） | Win/Mac/Linux/Arm64 | [balena.io/etcher](https://www.balena.io/etcher/) |
| **Win32DiskImager** | Linux 镜像烧录（备选） | Windows | `tools/Win32DiskImager-1.0.0-binary.zip` |
| **PhoenixCard 4.2.8** | Android 镜像烧录（唯一工具！） | Windows | `tools/PhoenixCard4.2.8.zip` |
| **VC++ 2008 Redist** | PhoenixCard 前置依赖 | Windows | `tools/vcredist_x86.exe` |
| **SDCardFormatter** | TF 卡格式化 | Windows | `tools/SDCardFormatterv5_WinEN.zip` |

### 连接与传输工具

| 工具 | 用途 | 所在文件 |
|------|------|---------|
| **MobaXterm Portable** | 串口调试 + SSH + SFTP | `tools/MobaXterm_Portable_v22.2.zip` |
| **FileZilla** | SFTP 文件传输 (Win) | `tools/FileZilla_3.62.2_win64_sponsored2-setup.exe` |
| **NoMachine arm64** | 远程桌面（安装在开发板上） | `tools/nomachine_8.5.3_1_arm64.deb` |

```bash
# NoMachine 安装（在开发板上）
sudo dpkg -i nomachine_8.5.3_1_arm64.deb
# 然后在 PC 上安装 NoMachine 客户端连接开发板 IP
```

### GPIO 开发库源码

| 工具 | 用途 | 所在文件 |
|------|------|---------|
| **wiringOP** | GPIO C 语言库（next 分支） | `tools/wiringOP.tar.gz` |
| **wiringOP-Python** | GPIO Python 绑定（next 分支） | `tools/wiringOP-Python.tar.gz` |

```bash
# 安装 wiringOP
tar xzf wiringOP.tar.gz && cd wiringOP && sudo ./build clean && sudo ./build

# 安装 wiringOP-Python
tar xzf wiringOP-Python.tar.gz && cd wiringOP-Python && python3 generate-bindings.py > bindings.i && sudo python3 setup.py install
```

### Android 开发工具

| 工具 | 用途 | 所在文件 |
|------|------|---------|
| **rootcheck.apk** | Android ROOT 验证 | `tools/rootcheck.apk` |
| **usbcamera.apk** | USB 摄像头测试 | `tools/usbcamera.apk` |

```bash
# 安装 Android APK（通过 ADB）
adb install tools/rootcheck.apk
adb install tools/usbcamera.apk
```

### 大型工具（需单独下载）

| 工具 | 大小 | 下载位置 |
|------|------|---------|
| **ai-sdk.tar.gz** | 1.3 GB | Orange Pi 官网 → 官方工具 |
| **toolchains.tar.gz** | 2.0 GB | orangepi-build 自动下载，或 [清华镜像](https://mirrors.tuna.tsinghua.edu.cn/armbian-releases/_toolchain/) |

---

## 第三章：Debian/Ubuntu Server 和 Xfce 桌面系统使用说明

### 3.1 已支持的 Linux 镜像类型和内核版本

| Linux 镜像类型 | 内核版本 | 桌面版 |
|---------------|---------|--------|
| Ubuntu 22.04-Jammy | Linux 5.15 | 支持 |
| Debian 12-Bookworm | Linux 5.15 | 支持 |
| Debian 11-Bullseye | Linux 5.15 | 支持 |

**镜像命名规则：**
```
开发板型号_版本号_Linux发行版类型_发行版代号_服务器或桌面_内核版本
例：Orangepi4pro_1.0.0_ubuntu_jammy_desktop_linux5.15.147.img
```
- 开发板型号：Orangepi4pro
- 版本号：1.x.x（最后一位为偶数）
- 发行版代号：jammy = Ubuntu 22.04，bookworm = Debian 12
- 服务器/桌面：server = 无桌面，desktop_gnome = GNOME 桌面
- 内核版本：linux5.15

### 3.2 Linux 内核驱动适配情况（Linux 5.15）

| 功能 | 状态 |
|------|------|
| HDMI 视频 | OK |
| HDMI 音频 | OK |
| USB 2.0 ×3 | OK |
| USB 3.0 ×1 | OK |
| TF 卡启动 | OK |
| eMMC | OK |
| NVMe SSD 识别 | OK |
| SPI Flash | OK |
| 千兆网卡 | OK |
| WiFi | OK |
| 蓝牙 | OK |
| 耳机音频 | OK |
| 板载 MIC | OK |
| 喇叭音频 | OK |
| LCD 屏幕 | OK |
| CAM1（MIPI） | 驱动 OK，3A 未适配 |
| CAM2（MIPI） | 驱动 OK，3A 未适配 |
| LED 灯 | OK |
| 40pin GPIO/I2C/SPI/UART/PWM | OK |
| 电源键 | OK |
| 温度传感器 | OK |
| 硬件看门狗 | OK |
| GPU | **仅 Debian Bullseye 支持** |
| NPU | OK |
| 视频编解码 | **仅 Debian Bullseye 支持** |

### 3.3 本手册 Linux 命令格式说明

| 提示符 | 含义 |
|--------|------|
| `orangepi@orangepi:~$` | 开发板普通用户（需 sudo） |
| `root@orangepi:~#` | 开发板 root 用户 |
| `test@test:~$` | Ubuntu PC 普通用户 |
| `root@test:~#` | Ubuntu PC root 用户 |

### 3.4 Linux 系统登录

#### 3.4.1 默认登录账号和密码

| 账号 | 密码 |
|------|------|
| root | orangepi |
| orangepi | orangepi |

> 输入密码时屏幕不显示任何字符。

#### 3.4.2 设置终端自动登录

```bash
# 设置 root 自动登录终端
orangepi@orangepi:~$ sudo auto_login_cli.sh root

# 禁止自动登录终端
orangepi@orangepi:~$ sudo auto_login_cli.sh -d

# 恢复 orangepi 用户自动登录
orangepi@orangepi:~$ sudo auto_login_cli.sh orangepi
```

#### 3.4.3 Linux 桌面版系统自动登录

桌面版默认自动登录，无需输入密码。

#### 3.4.4 桌面版 root 自动登录

```bash
# 设置 root 自动登录桌面
orangepi@orangepi:~$ sudo desktop_login.sh root
# 重启生效

# 恢复 orangepi 用户
orangepi@orangepi:~$ sudo desktop_login.sh orangepi
```

### 3.5 板载 LED 灯测试

- 红色 LED：接通电源后常亮（硬件控制，软件无法关闭）
- 绿色 LED：内核启动后闪烁（软件控制）

```bash
# 进入 LED 目录
root@orangepi:~# cd /sys/class/leds/status_led

# 停止闪烁（关闭）
root@orangepi:/sys/class/leds/status_led# echo none > trigger

# 常亮
root@orangepi:/sys/class/leds/status_led# echo default-on > trigger

# 闪烁
root@orangepi:/sys/class/leds/status_led# echo heartbeat > trigger
```

### 3.6 TF 卡 rootfs 分区容量操作

> **注意：** Linux 系统只有**一个 ext4 分区**，没有单独的 BOOT 分区。

#### 3.6.1 第一次启动自动扩容

通过 `orangepi-resize-filesystem.service` 自动调用 `orangepi-resize-filesystem` 脚本扩容 rootfs。在开发板上用 `df -h` 查看结果。

#### 3.6.2 禁止自动扩容

在 Ubuntu PC 上执行：
```bash
test@test:~$ sudo -i
root@test:~# cd /media/test/opi_root/
root@test:/media/test/opi_root# cd root
root@test:/media/test/opi_root/root# touch .no_rootfs_resize
root@test:/media/test/opi_root/root# ls .no_rootfs*
.no_rootfs_resize
```

**重新启用扩容（在开发板上）：**
```bash
root@orangepi:~# rm /root/.no_rootfs_resize
root@orangepi:~# systemctl enable orangepi-resize-filesystem.service
root@orangepi:~# sudo reboot
```

#### 3.6.3 手动扩容

1. 烧录 Linux 镜像到 TF 卡，创建 `.no_rootfs_resize` 禁止自动扩容
2. 将 TF 卡插入 Ubuntu PC
3. 安装并使用 gparted：
   ```bash
   test@test:~$ sudo apt install -y gparted
   test@test:~$ sudo gparted
   ```
4. 选择 rootfs 分区（如 `/dev/sdc1`）→ 右键 Umount → 右键 Resize/Move → 设置新大小 → Resize/Move → 绿色勾 → Apply
5. 完成后插入开发板，用 `df -h` 验证

#### 3.6.4 缩小 rootfs

同手动扩容步骤，但在 Resize/Move 时设置**更小的容量**即可。

### 3.7 网络连接测试

#### 3.7.1 以太网口测试

- 系统启动后通过 DHCP 自动分配 IP
- **Debian 12 注意：** 需将 `eth0` 改为 `end0`

```bash
# 查看 IP
orangepi@orangepi:~$ ip a eth0

# 测试连通性（Ctrl+C 中断）
orangepi@orangepi:~$ ping www.baidu.com -I eth0
```

#### 3.7.2 WiFi 连接测试

> **重要：** 不要修改 `/etc/network/interfaces` 来连接 WiFi！

**服务器版命令行连接：**
```bash
# 扫描 WiFi
orangepi@orangepi:~$ nmcli dev wifi

# 连接
orangepi@orangepi:~$ sudo nmcli dev wifi connect wifi_name password wifi_passwd

# 查看 WiFi IP
orangepi@orangepi:~$ ip a wlan0

# 测试
orangepi@orangepi:~$ ping www.orangepi.org -I wlan0
```

**服务器版图形界面连接（nmtui）：**
```bash
orangepi@orangepi:~$ sudo nmtui
# 选择 "Activate a connection" → 选择 WiFi → Activate → 输入密码
```

**桌面版连接：** 点击右上角网络图标 → More networks → 选择 WiFi → 输入密码 → Connect。

#### 3.7.3 通过 create_ap 创建 WiFi 热点

create_ap 已预装。GitHub：`https://github.com/oblique/create_ap`

**语法：** `create_ap [options] <wifi-interface> [<interface-with-internet>] [<access-point-name> [<passphrase>]]`

**NAT 模式：**
```bash
# 创建热点（名称 orangepi，密码 orangepi）
sudo create_ap -m nat wlan0 eth0 orangepi orangepi --no-virt

# 指定网段
sudo create_ap -m nat wlan0 eth0 orangepi orangepi -g 192.168.2.1 --no-virt

# 5GHz
sudo create_ap -m nat wlan0 eth0 orangepi orangepi --freq-band 5 --no-virt

# 隐藏 SSID
sudo create_ap -m nat wlan0 eth0 orangepi orangepi --hidden --no-virt
```

**Bridge 模式：**
```bash
sudo create_ap -m bridge wlan0 eth0 orangepi orangepi --no-virt
sudo create_ap -m bridge wlan0 eth0 orangepi orangepi --freq-band 5 --no-virt
sudo create_ap -m bridge wlan0 eth0 orangepi orangepi --hidden --no-virt
```

#### 3.7.4 设置静态 IP 地址

> **重要：** 不要修改 `/etc/network/interfaces`！

**使用 nmtui：**
```bash
orangepi@orangepi:~$ sudo nmtui
# 选择 "Edit a connection" → 选择接口 → IPv4 CONFIG 改为 Manual → 设置地址/网关/DNS → OK
# 停用后再激活接口
```

**使用 nmcli：**
```bash
# 查看连接
nmcli con show

# 设置静态 IP（以以太网为例）
sudo nmcli con mod "Wired connection 1" \
  ipv4.addresses "192.168.1.110" \
  ipv4.gateway "192.168.1.1" \
  ipv4.dns "8.8.8.8" \
  ipv4.method "manual"

# 重启
sudo reboot
```

#### 3.7.5 设置系统第一次启动自动连接网络

> 需要一台 Linux 机器修改 TF 卡 ext4 分区。

1. 烧录镜像到 TF 卡，插入 Ubuntu PC
2. 确认挂载：
   ```bash
   test@test:~$ df -h | grep "media"
   test@test:~$ ls /media/test/opi_root/
   ```
3. 进入 boot 目录：
   ```bash
   test@test:~$ cd /media/test/opi_root/boot/
   ```
4. 复制模板：
   ```bash
   sudo cp orangepi_first_run.txt.template orangepi_first_run.txt
   ```
5. 编辑配置：
   ```bash
   sudo vim orangepi_first_run.txt
   ```

**配置变量：**
- `FR_general_delete_this_file_after_completion`：1=首次启动后删除，0=重命名为 .old
- `FR_net_change_defaults`：**必须设为 1** 网络设置才生效
- `FR_net_ethernet_enabled`：1=以太网静态 IP
- `FR_net_wifi_enabled`：1=WiFi（设置后会禁用以太网）
- `FR_net_wifi_ssid`：WiFi 名称
- `FR_net_wifi_key`：WiFi 密码
- `FR_net_use_static`：1=静态 IP
- `FR_net_static_ip`：静态 IP 地址
- `FR_net_static_gateway`：网关

**示例 — WiFi 自动连接：**
```
FR_net_change_defaults=1
FR_net_wifi_enabled=1
FR_net_wifi_ssid=<your_ssid>
FR_net_wifi_key=<your_password>
```

**示例 — WiFi 静态 IP：**
```
FR_net_change_defaults=1
FR_net_wifi_enabled=1
FR_net_wifi_ssid=<your_ssid>
FR_net_wifi_key=<your_password>
FR_net_use_static=1
FR_net_static_ip=<ip>
FR_net_static_gateway=<gateway>
```

**示例 — 以太网静态 IP：**
```
FR_net_change_defaults=1
FR_net_ethernet_enabled=1
FR_net_use_static=1
FR_net_static_ip=<ip>
FR_net_static_gateway=<gateway>
```

> 此配置**仅在首次启动时**有效。

### 3.8 SSH 远程登录开发板

SSH 默认开启，允许 root 登录。

**Ubuntu 下 SSH 登录：**
```bash
test@test:~$ ssh orangepi@192.168.1.xxx
# 密码：orangepi（不显示）
```

**如果 SSH 失败，在开发板上执行：**
```bash
root@orangepi:~# reset_ssh.sh
```

**Windows 下 SSH 登录（MobaXterm）：**
- Session → SSH → Remote host 填写开发板 IP → 用户名 root/orangepi → OK → 输入密码

### 3.9 ADB 使用方法

#### 3.9.1 网络 ADB

**在开发板上：**
```bash
sudo /etc/adb_conf.sh
ps -ax | grep "adbd"
```

**在 Ubuntu PC 上：**
```bash
sudo apt-get update && sudo apt-get install -y adb
adb connect 192.168.1.xx:5555
adb devices
adb shell          # 进入开发板 shell
adb push filename /root   # 上传文件
adb reboot         # 重启开发板
```

#### 3.9.2 USB Type-C ADB

1. 用 USB 2.0 公对公线连接开发板 USB Device 口到 Ubuntu PC
2. 在开发板上执行 `sudo /etc/adb_conf.sh`
3. 在 PC 上安装 adb 并执行 `adb devices` → `adb shell`

### 3.10 HDMI 测试

#### 3.10.1 直接连接测试
用 HDMI 线连接开发板和 HDMI 显示器，正常显示即 OK。

> 大多数笔记本 HDMI 口是输出口（不支持输入）。

#### 3.10.2 HDMI 转 VGA 显示测试
需要 HDMI 转 VGA 转换器 + VGA 线 + VGA 显示器。无需额外配置。

### 3.11 蓝牙使用方法

#### 3.11.1 桌面版镜像测试

点击右上角蓝牙图标 → Adapter → Visibility Setting 设为 "Always visible" → 打开蓝牙设备 → Search → 选择设备右键 Pair → 双方确认配对 → 右键 Send a File

#### 3.11.2 服务器版镜像

```bash
# 安装 bluez
sudo apt update && sudo apt install -y bluez

# 检查蓝牙设备
hciconfig -a

# 进入 bluetoothctl
sudo bluetoothctl
[bluetooth]# power on
[bluetooth]# discoverable on
[bluetooth]# pairable on
[bluetooth]# scan on
# 记录目标设备 MAC
[bluetooth]# scan off
[bluetooth]# pair DC:72:9B:4C:F4:CF
[agent] Confirm passkey 764475 (yes/no): yes

# 连接音频设备
sudo apt update && sudo apt -y install pulseaudio-module-bluetooth
pulseaudio --start

sudo bluetoothctl
[bluetooth]# paired-devices
[bluetooth]# connect DC:72:9B:4C:F4:CF
```

### 3.12 USB 接口测试

#### 3.12.1 连接 USB 鼠标/键盘
直接插入即可使用（桌面版）。

#### 3.12.2 连接 USB 存储设备

```bash
# 检测设备
cat /proc/partitions | grep "sd*"

# 挂载
sudo mount /dev/sda1 /mnt/
ls /mnt/

# 查看挂载状态
df -h | grep "sd"
```

#### 3.12.3 USB 以太网卡测试

**已测试兼容型号：**
1. RTL8152B USB 百兆以太网卡
2. RTL8153 USB 千兆以太网卡

```bash
# 检查检测
dmesg | tail
# 查看新网络接口
sudo ifconfig
# 测试
ping www.baidu.com -I eth1
```

#### 3.12.4 USB 摄像头测试

```bash
# 检查内核模块
lsmod

# 安装 v4l-utils
sudo apt update && sudo apt install -y v4l-utils
v4l2-ctl --list-devices
```

**fswebcam 拍照测试：**
```bash
sudo apt-get install -y fswebcam
sudo fswebcam -d /dev/video0 --no-banner -r 1280x720 -S 5 ./image.jpg
# 服务器版传输到 PC
scp image.jpg test@192.168.1.55:/home/test
```

**mjpg-streamer 视频流测试：**
```bash
# 下载（二选一）
git clone https://github.com/jacksonliam/mjpg-streamer
git clone https://gitee.com/leeboby/mjpg-streamer

# 安装依赖（Ubuntu）
sudo apt-get install -y cmake libjpeg8-dev
# 安装依赖（Debian）
sudo apt-get install -y cmake libjpeg62-turbo-dev

# 编译安装
cd mjpg-streamer/mjpg-streamer-experimental
make -j4
sudo make install

# 运行
export LD_LIBRARY_PATH=.
sudo ./mjpg_streamer -i "./input_uvc.so -d /dev/video0 -u -f 30" -o "./output_http.so -w ./www"
# 浏览器访问：http://<开发板IP>:8080
```

### 3.13 音频测试

#### 3.13.1 使用命令行播放音频

**查看声卡设备：**
```bash
root@orangepi:~# aplay -l
# card0 = allwinnerhdmi (HDMI)
# card1 = sndi2s4 (耳机/喇叭 - ES8323)
```

**耳机播放：**
```bash
root@orangepi:~# aplay -Dhw:1,0 /usr/share/sounds/alsa/audio.wav
```

**喇叭播放：**
```bash
root@orangepi:~# aplay -Dhw:1,0 /usr/share/sounds/alsa/audio.wav
```

**HDMI 音频：**
```bash
orangepi@orangepi:~# aplay -D hw:0,0 /usr/share/sounds/alsa/audio.wav
```

#### 3.13.2 桌面版音频播放

文件管理器找到 `audio.wav` → 右键 → 用 VLC 打开；通过音量控制的 Playback 选项卡切换输出设备。

#### 3.13.3 录音测试

**板载 MIC 录音 + HDMI 回放：**
```bash
arecord -Dhw:1,0 -f cd | aplay -Dhw:0,0 -f cd
```

**耳机 MIC 录音：**
```bash
sudo i2cset -y -f 7 0x10 0x23 0x10
arecord -Dhw:1,0 -f cd | aplay -Dhw:0,0 -f cd
```

### 3.14 温度传感器

A733 有 **5 个温度传感器**（原始值除以 1000 为摄氏度）：

| 传感器 | 路径 | 用途 |
|--------|------|------|
| sensor0 | `/sys/class/thermal/thermal_zone0/temp` | CPU_L（cpul_thermal_zone） |
| sensor1 | `/sys/class/thermal/thermal_zone1/temp` | CPU_B（cpub_thermal_zone） |
| sensor2 | `/sys/class/thermal/thermal_zone4/temp` | GPU（gpu_thermal_zone） |
| sensor3 | `/sys/class/thermal/thermal_zone5/temp` | NPU（npu_thermal_zone） |
| sensor4 | `/sys/class/thermal/thermal_zone6/temp` | DDR（ddr_thermal_zone） |

```bash
# 示例：查看 CPU_L 温度
cat /sys/class/thermal/thermal_zone0/type   # cpul_thermal_zone
cat /sys/class/thermal/thermal_zone0/temp   # 如 54925 = 54.925°C
```

### 3.15 40pin 接口引脚说明

- 40pin 接口共有 **28 个 GPIO 引脚**
- 所有 GPIO 引脚电压为 **3.3V**
- 引脚编号见开发板丝印和手册 Page 116-117 的引脚图
- 使用 `gpio readall` 查看完整映射

### 3.16 安装 wiringOP 的方法

wiringOP 已在 Orange Pi Linux 镜像中预装。

**检查：**
```bash
orangepi@orangepi:~$ gpio readall
```

**重新安装：**
```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/orangepi-xunlong/wiringOP.git -b next
cd wiringOP
sudo ./build clean
sudo ./build
```

> **必须使用 `next` 分支（`-b next`）！**
> 备用路径：`/usr/src/wiringOP`
> 预编译 deb：`orangepi-build/external/cache/debs/arm64/wiringpi_x.xx.deb`

### 3.17 40pin 接口 GPIO、I2C、UART、SPI 和 PWM 测试

#### 3.17.1 40pin GPIO 口测试（以 Pin 7 = PL4 = wPi 2 为例）

```bash
cd ~/wiringOP

# 设置为输出模式
gpio mode 2 out

# 输出低电平（0V）
gpio write 2 0

# 输出高电平（3.3V）
gpio write 2 1
```

#### 3.17.2 40pin GPIO 口上下拉电阻设置

```bash
# 输入模式
gpio mode 2 in

# 上拉
gpio mode 2 up
gpio read 2   # 应显示 1

# 下拉
gpio mode 2 down
gpio read 2   # 应显示 0
```

#### 3.17.3 40pin SPI 测试

**可用 SPI：SPI3**

| 信号 | 40pin 引脚 |
|------|-----------|
| MOSI | Pin 19 |
| MISO | Pin 21 |
| CLK | Pin 23 |
| CS0 | Pin 24 |

SPI 默认关闭，通过 `sudo orangepi-config` 启用：
- System → Hardware → 空格选中 SPI → Save → Back → Reboot

```bash
# 检查设备节点
ls /dev/spidev*
# /dev/spidev3.0

# 无回环测试
sudo spidev_test -v -D /dev/spidev3.0

# 回环测试（短接 MOSI 和 MISO 后）
sudo spidev_test -v -D /dev/spidev3.0
# TX 和 RX 应匹配
```

#### 3.17.4 40pin I2C 测试

**可用 I2C 总线：i2c0, i2c1, i2c2, i2c3**

| I2C 总线 | SDA（40pin） | SCL（40pin） | dtbo 配置名 |
|----------|-------------|-------------|------------|
| I2C0 | Pin 3 | Pin 5 | i2c0 |
| I2C1 | Pin 27 | Pin 28 | i2c1 |
| I2C2 | Pin 19 | Pin 23 | i2c2 |
| I2C3 | Pin 26 | Pin 21 | i2c3 |

I2C 默认关闭，通过 `sudo orangepi-config` 启用：
- System → Hardware → 空格选中 I2C → Save → Back → Reboot

```bash
# 检查设备节点
ls /dev/i2c-*

# 安装 i2c-tools
sudo apt-get update && sudo apt-get install -y i2c-tools

# 扫描 I2C 设备
sudo i2cdetect -y -r 0   # i2c0
sudo i2cdetect -y -r 1   # i2c1
sudo i2cdetect -y -r 2   # i2c2
sudo i2cdetect -y -r 3   # i2c3
```

#### 3.17.5 40pin UART 测试

**可用 UART：uart7**

| UART 总线 | RX（40pin） | TX（40pin） | dtbo 配置名 |
|-----------|------------|------------|------------|
| UART7 | Pin 10 | Pin 8 | uart7 |

UART 默认关闭，通过 `sudo orangepi-config` 启用：
- System → Hardware → 空格选中 UART → Save → Back → Reboot

```bash
# 检查设备节点
ls /dev/ttyS*
# /dev/ttyS0 /dev/ttyS1 /dev/ttyS6 /dev/ttyS7

# 回环测试（短接 RX 和 TX）
gpioserial /dev/ttyS7
# Out: 0: -> 0
# Out: 1: -> 1
# ...
```

#### 3.17.6 使用 /sys/class/pwm/ 测试 PWM

**可用 PWM：s_pwm0_2, pwm0_0, pwm0_2, pwm0_3, pwm0_4, pwm0_5, pwm0_6, pwm0_7**

| PWM 总线 | 40pin 引脚 | dtbo 配置名 |
|----------|-----------|------------|
| SPWM0-2 | Pin 7 | spwm2 |
| PWM0-0 | Pin 29 | pwm0 |
| PWM0-2 | Pin 33 | pwm2 |
| PWM0-3 | Pin 35 | pwm3 |
| PWM0-4 | Pin 37 | pwm4 |
| PWM0-5 | Pin 32 | pwm5 |
| PWM0-6 | Pin 36 | pwm6 |
| PWM0-7 | Pin 38 | pwm7 |

PWM 默认关闭，通过 `sudo orangepi-config` 启用。

**测试 s_pwm0_2（Pin 7，需 root）：**
```bash
root@orangepi:~# echo 2 > /sys/class/pwm/pwmchip20/export
root@orangepi:~# echo 20000000 > /sys/class/pwm/pwmchip20/pwm2/period
root@orangepi:~# echo 1000000 > /sys/class/pwm/pwmchip20/pwm2/duty_cycle
root@orangepi:~# echo 1 > /sys/class/pwm/pwmchip20/pwm2/enable
```

**测试 pwm0_0（Pin 29，50Hz 方波）：**
```bash
root@orangepi:~# echo 0 > /sys/class/pwm/pwmchip0/export
root@orangepi:~# echo 20000000 > /sys/class/pwm/pwmchip0/pwm0/period
root@orangepi:~# echo 1000000 > /sys/class/pwm/pwmchip0/pwm0/duty_cycle
root@orangepi:~# echo 1 > /sys/class/pwm/pwmchip0/pwm0/enable
```

**测试 pwm2（Pin 33）、pwm4（Pin 35 通过 pwm3 export）：**
```bash
# pwm2
echo 2 > /sys/class/pwm/pwmchip0/export
echo 20000000 > /sys/class/pwm/pwmchip0/pwm2/period
echo 1000000 > /sys/class/pwm/pwmchip0/pwm2/duty_cycle
echo 1 > /sys/class/pwm/pwmchip0/pwm2/enable

# pwm4 (注意 export 编号为 3)
echo 3 > /sys/class/pwm/pwmchip0/export
echo 20000000 > /sys/class/pwm/pwmchip0/pwm3/period
echo 1000000 > /sys/class/pwm/pwmchip0/pwm3/duty_cycle
echo 1 > /sys/class/pwm/pwmchip0/pwm3/enable
```

### 3.18 wiringOP-Python 的安装和使用

#### 3.18.1 安装方法

```bash
# 安装依赖
sudo apt-get update && sudo apt-get -y install git swig python3-dev python3-setuptools

# 下载源码（next 分支）
git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python -b next
cd wiringOP-Python
git submodule update --init --remote

# 备用路径：/usr/src/wiringOP-Python

# 编译安装
python3 generate-bindings.py > bindings.i
sudo python3 setup.py install

# 验证安装
python3 -c "import wiringpi; help(wiringpi)"
```

#### 3.18.2 40pin GPIO 测试（Pin 7 = wPi 2）

```bash
# 设置为输出
python3 -c "import wiringpi; from wiringpi import GPIO; wiringpi.wiringPiSetup(); wiringpi.pinMode(2, GPIO.OUTPUT);"

# 输出低电平
python3 -c "import wiringpi; from wiringpi import GPIO; wiringpi.wiringPiSetup(); wiringpi.digitalWrite(2, GPIO.LOW)"

# 输出高电平
python3 -c "import wiringpi; from wiringpi import GPIO; wiringpi.wiringPiSetup(); wiringpi.digitalWrite(2, GPIO.HIGH)"
```

**Python 交互模式：**
```python
>>> import wiringpi
>>> from wiringpi import GPIO
>>> wiringpi.wiringPiSetup()
>>> wiringpi.pinMode(2, GPIO.OUTPUT)
>>> wiringpi.digitalWrite(2, GPIO.LOW)
>>> wiringpi.digitalWrite(2, GPIO.HIGH)
```

**运行闪烁示例：**
```bash
cd examples
python3 blink.py   # 循环测试所有 GPIO 引脚
```

#### 3.18.3 40pin SPI 测试

同 wiringOP 方法启用 SPI（`sudo orangepi-config`）。

```bash
cd examples
# 无回环
python3 spidev_test.py --channel x --port x
# 短接 MOSI+MISO 回环测试
python3 spidev_test.py --channel x --port x
```

#### 3.18.4 40pin I2C 测试

同 wiringOP 方法启用 I2C。

```bash
sudo apt-get install -y i2c-tools
sudo i2cdetect -y -r 0  # i2c0
sudo i2cdetect -y -r 1  # i2c1
sudo i2cdetect -y -r 2  # i2c2
sudo i2cdetect -y -r 3  # i2c3

# 运行 ds1307 RTC 示例
cd examples
python3 ds1307.py --device "/dev/i2c-1"
```

#### 3.18.5 40pin UART 测试

同 wiringOP 方法启用 UART。

```bash
ls /dev/ttyS*

# 回环测试（短接 RX 和 TX）
cd examples
python3 serialTest.py --device /dev/ttyS7
```

### 3.19 硬件看门狗测试

```bash
sudo watchdog_test 10
# 参数 10 = 倒计时秒数
# 按除 ESC 外的任意键喂狗（打印 "keep alive"）
# 超时不喂狗则系统自动重启
```

### 3.20 查看 A733 芯片的 ChipID

```bash
root@orangepi:~# cat /sys/class/sunxi_info/sys_info | grep sunxi_serial
sunxi_serial : 147d208d0161172000007c0000000000
```
每颗芯片有唯一 chipid。

### 3.21 Python 相关说明

#### 3.21.1 Python 源码编译安装

```bash
# 安装构建依赖
sudo apt-get update
sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
  libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev

# 下载编译 Python 3.9.10
wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
tar xvf Python-3.9.10.tgz
cd Python-3.9.10
./configure --enable-optimizations
make -j4
sudo make altinstall

# 验证
python3.9 --version   # Python 3.9.10

# 升级 pip
/usr/local/bin/python3.9 -m pip install --upgrade pip
```

#### 3.21.2 更换 pip 源

```bash
# 安装 pip
sudo apt-get update && sudo apt-get install -y python3-pip

# 永久更换为清华源
mkdir -p ~/.pip
cat <<EOF > ~/.pip/pip.conf
[global]
timeout = 6000
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 临时更换
pip3 install <包名> -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 3.22 安装 Docker

Docker 已预装但服务默认禁用。

```bash
# 启用 Docker
enable_docker.sh

# 测试
docker run hello-world

# 避免权限拒绝（需重新登录/重启生效）
sudo usermod -aG docker $USER
```

### 3.23 Home Assistant 安装

通过 Python 安装：

```bash
# 安装依赖（通用 Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev \
  libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libopenjp2-7 \
  libtiff5 libturbojpeg0-dev tzdata

# Debian 12 特殊依赖
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev \
  libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libopenjp2-7 \
  libturbojpeg0-dev tzdata

# 创建虚拟环境
sudo mkdir /srv/homeassistant
sudo chown orangepi:orangepi /srv/homeassistant
cd /srv/homeassistant
python3.9 -m venv .
source bin/activate

# 安装
python3 -m pip install wheel
pip3 install homeassistant

# 运行
hass
# 浏览器访问：http://<开发板IP>:8123
```

### 3.24 OpenCV 安装

```bash
sudo apt-get update && sudo apt-get install -y libopencv-dev python3-opencv

# Ubuntu 22.04 版本
python3 -c "import cv2; print(cv2.__version__)"   # 4.5.4

# Debian 12 版本
python3 -c "import cv2; print(cv2.__version__)"   # 4.6.0
```

### 3.25 宝塔 Linux 面板安装

```bash
# 扩容 /tmp 到 2G
sudo sed -i 's/nosuid/&,size=2G/' /etc/fstab
sudo reboot
df -h | grep "/tmp"   # 验证

# 安装（约 34 分钟）
sudo install_bt_panel.sh
# 输入 y 安装到 /www
# 浏览器访问显示的 URL
```

### 3.26 QT 安装

```bash
install_qt.sh
# Ubuntu 22.04 → QT 5.15.3
# Debian 12 → QT 5.15.8

# 打开 QTCreator
qtcreator
```

**配置步骤：**
1. Help → About Plugins → 取消勾选 ClangCodeModel
2. 重启 QTCreator
3. 确保使用 GCC 编译器（非 Clang），Debian 12 跳过此步

### 3.27 ROS2 Humble 安装（仅 Ubuntu 22.04）

```bash
# 安装
install_ros.sh ros2

# 测试
test_ros.sh
# [INFO] [talker]: Publishing: 'HelloWorld:1'
# [INFO] [listener]: I heard: [HelloWorld:1]

# 运行 rviz2
source /opt/ros/humble/setup.bash
ros2 run rviz2 rviz2
```

### 3.28 安装内核头文件

```bash
# 查看
ls /opt/linux-headers*
# /opt/linux-headers-xxx-sun60iw2_x.x.x_arm64.deb

# 安装
sudo dpkg -i /opt/linux-headers*.deb

# 测试 hello 内核模块
cd /usr/src/hello/
sudo make
sudo insmod hello.ko
dmesg | grep "Hello"   # [2871.893988] Hello OrangePi --init
sudo rmmod hello
```

### 3.29 OV13850 和 IMX219 MIPI 摄像头使用方法

支持的 MIPI 摄像头：OV13850（13MP）、IMX219（8MP）

```bash
# 安装依赖
sudo apt install python3-pip python3-opencv libopencv-dev
sudo apt install python3-pybind11 python3-dev

# 加载摄像头驱动
sudo modprobe vin_v4l2

# 检查设备节点
ls /dev/video*

# 进入 demo 目录
cd /opt/v4l2_opencv_demo/
ls
# Makefile  test_camera.cpp  test_camera.py  v4l2_camera_bind.cpp  v4l2_camera.cpp  v4l2_camera.h
```

**C++ 编译运行：**
```bash
make clean && make
./cam_test /dev/video8
# 修改 test_camera.cpp 中 V4L2Camera cam(device_str, 640, 480) 的宽高可改分辨率
```

**Python 运行：**
```bash
make python_module
# 编辑 test_camera.py 设置 cam = v4l2cam.V4L2Camera("/dev/video8", 640, 480)
python3 test_camera.py
```

### 3.30 10.1寸 MIPI LCD 屏幕使用方法

#### 3.30.1 组装

**所需部件：**
- 10.1寸 MIPI LCD + 触摸面板
- 转接板 + 31pin转40pin 排线
- 30pin MIPI 排线
- 12pin 触摸排线

**组装：** 排线蓝色绝缘面朝下连接转接板 → 31pin 转 40pin 排线连接转接板与 LCD → 12pin 排线连接触摸 → 30pin MIPI 排线连接开发板 LCD 接口。

#### 3.30.2 打开配置

默认关闭，通过 `sudo orangepi-config` 启用：
- System → Hardware → 空格选中 lcd → Save → Back → Reboot

或手动编辑：
```bash
sudo vim /boot/orangepiEnv.txt
# 添加：overlays=lcd
```

#### 3.30.3 服务器版旋转显示

编辑 `/boot/orangepiEnv.txt`：
```bash
overlays=lcd
extraargs=fbcon=rotate:3
```

旋转值：`0`=正常 / `1`=顺时针 90° / `2`=180° / `3`=顺时针 270°

### 3.31 Linux 系统支持的编程语言测试

| | Debian Bookworm | Ubuntu Jammy |
|---|---|---|
| **GCC** | gcc (Debian 12.2.0-14) 12.2.0 | gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0 |
| **Python3** | Python 3.11.2 | Python 3.10.12 |
| **Java** | `sudo apt install -y openjdk-17-jdk` | `sudo apt install -y openjdk-18-jdk` |

### 3.32 上传文件到开发板

#### 3.32.1 Ubuntu PC 上传

**scp：**
```bash
# 文件
scp file_path orangepi@192.168.xx.xx:/home/orangepi/
# 文件夹
scp -r dir_path orangepi@192.168.xx.xx:/home/orangepi/
```

**Filezilla：**
```bash
sudo apt install -y filezilla
filezilla
# 主机：开发板IP，用户名：orangepi/root，密码：orangepi，端口：22（SFTP）
```

#### 3.32.2 Windows PC 上传

下载 Filezilla：`https://filezilla-project.org/download.php?type=client`
安装后用相同 SFTP 参数连接。

### 3.33 Debian Bullseye 系统硬解测试

```bash
# 测试视频：http://bbb3d.renderfarming.net/download.html

# 使用 gstreamer 播放
gst-play-1.0 bbb_sunflower_1080p_60fps_normal.mp4

# 或
gst-launch-1.0 filesrc location=bbb_sunflower_1080p_60fps_normal.mp4 ! qtdemux ! h264parse ! omxh264dec ! xvimagesink
```
用 `top` 查看 CPU 使用率——低占用 = 硬解正常工作。

### 3.34 Debian Bullseye 系统 GPU 测试

```bash
LD_LIBRARY_PATH=/usr/local/lib glmark2-es2
LD_LIBRARY_PATH=/usr/local/lib glmark2-es2 --off-screen
```

### 3.35 NPU 使用说明

#### 3.35.1 PC 端开发环境配置

```bash
# 在 Ubuntu PC 上安装 Docker
sudo apt update && sudo apt install -y docker.io

# 下载 NPU Docker 镜像（从全志云盘 docker_images_v2.0.x.zip）
unzip docker_images_v2.0.x.zip
cd docker_images_v2.0.x
unzip ubuntu-npu_v2.0.10.tar.zip
sudo docker load -i ubuntu-npu_v2.0.10.tar

# 准备数据
mkdir docker_data
tar -xvf ai-sdk.tar.gz -C docker_data
cd docker_data
sudo docker run --ipc=host -itd -v ${PWD}:/workspace --name allwinner_v2.0.10 ubuntu-npu:v2.0.10 /bin/bash
sudo docker exec -it allwinner_v2.0.10 /bin/bash
```

**模型转换（YOLOv5s 示例）：**
```bash
cd /workspace/ai-sdk/models
source env.sh v3
cp ../scripts/* .

# YOLOv5s
./pegasus_import.sh yolov5s-sim
vim yolov5s-sim/yolov5s-sim_inputmeta.yml   # 设置 scale=0.00392157
./pegasus_quantize.sh yolov5s-sim uint8
./pegasus_inference.sh yolov5s-sim uint8
./pegasus_export_ovx.sh yolov5s-sim uint8
# 输出 NBG：yolov5s-sim/wksp/yolov5s-sim_uint8_nbg_unify/network_binary.nb
```

#### 3.35.2 板端模型部署

```bash
# 安装依赖
sudo apt update && sudo apt install libopencv-dev cmake

# 上传并解压 ai-sdk
tar -xvf ai-sdk.tar.gz
```

**YOLOv5 目标检测：**
```bash
cd ~/ai-sdk/examples/yolov5
mkdir build && cd build
cmake .. && make
./yolov5 ../model/v3/yolov5.nb ../input_data/dog.jpg ./yolov5nbginput
```

**ResNet50 图像分类：**
```bash
cd ~/ai-sdk/examples/resnet50
mkdir build && cd build
cmake .. && make
./resnet50 ../model/v3/resnet50.nb ../input_data/dog_224_224.jpg
```

**Struct2Depth 深度估计：**
```bash
cd ~/ai-sdk/examples/struct2depth
mkdir build && cd build
cmake .. && make
./struct2depth -b ../model/v3/struct2depth.nb -i ../input_data/0015.jpg
```

**Transformer 图像分类：**
```bash
cd ~/ai-sdk/examples/transformer_cls
mkdir build && cd build
cmake .. && make
./transformer_cls ../model/v3/transformer_cls.nb ../input_data/cat_224_224.jpg
```

**YOLACT 目标检测+分割：**
```bash
cd ~/ai-sdk/examples/yolact
mkdir build && cd build
cmake .. && make
./yolact ../model/v3/yolact.nb ../input_data/dog_550_550.jpg
```

**DeepSpeech2 语音识别：**
```bash
cd ~/ai-sdk/examples/deepspeech2
mkdir build && cd build
cmake .. && make
./deepspeech2 ../model/v3/deepspeech2.nb ../input_data/1188-133604-0010.flac_756_161_1.tensor
```

**ChineseOCR 文字识别：**
```bash
cd ~/ai-sdk/examples/chineseocr
mkdir build && cd build
cmake .. && make
./chineseocr -d ../model/v3/ -1 dbnet_1024 -2 angle_net -3 crnn_lite_lstm_256 -4 keys.txt -i ../input_data/1.jpg
```

### 3.36 烧写 Linux 镜像到 eMMC

> **TF 卡优先级高于 eMMC。** 若插入有系统的 TF 卡，默认启动 TF 卡系统。

**Debian Bullseye 预操作（卸载 GPU 驱动）：**
```bash
sudo service lightdm stop
sudo rmmod pvrsrvkm
```

**步骤：**
1. 将 Linux 镜像烧录到 TF 卡，用 TF 卡启动开发板
2. 运行安装脚本：`sudo nand-sata-install`
3. 选择 `2 Boot from eMMC - system on eMMC`
4. 确认擦除 `<Yes>`
5. 选择文件系统（ext2/ext3/ext4/f2fs/btrfs）
6. 等待格式化并烧录完成
7. 选择 `<Poweroff>` 关机
8. 拔出 TF 卡，重新上电启动 eMMC 系统

### 3.37 烧写 Linux 镜像到 SPIFlash + NVMe SSD

> ⚠️ **兼容性：** 目前仅在**樊想**和**广存** SSD 上测试通过。金士顿等可能存在兼容问题，v1.0.6 镜像已修复金士顿 NVMe SSD 启动失败问题。

**Debian Bullseye 预操作（卸载 GPU 驱动）：**
```bash
sudo service lightdm stop
sudo rmmod pvrsrvkm
```

**步骤：**
1. 将 NVMe SSD 插入 M.2 PCIe 3.0 x1 插槽并固定
2. 将 Linux 镜像烧录到 TF 卡，用 TF 卡启动开发板
3. 创建 NVMe 分区：
   ```bash
   sudo parted --script /dev/nvme0n1 mklabel gpt mkpart primary ext4 65536s 100%
   ```
4. 运行安装脚本：`sudo nand-sata-install`
5. 选择 `4 Boot from SPI - system on SATA, USB or NVMe`
6. 回车确认，选择 `<Yes>`，选择文件系统
7. 等待格式化并烧录
8. 确认 `<Yes>` 烧录 bootloader 到 SPI Flash
9. 选择 `<Poweroff>` 关机
10. 拔出 TF 卡，重新上电启动

### 3.38 系统备份脚本 opi-bkimg

```bash
# Debian Bullseye 预操作（卸载 GPU 驱动）
sudo service lightdm stop && sudo rmmod pvrsrvkm

# 运行备份
sudo opi-bkimg

# 备份文件
ls /mnt/   # backup.img
```

> 备用下载：`https://gitee.com/orangepi-xunlong/opi-bkimg`

### 3.39 关机和重启

```bash
# 关机
sudo poweroff
# 或短按电源键

# 开机：长按电源键

# 重启
sudo reboot
```

---

## 第四章：Linux SDK — orangepi-build 使用说明

### 4.1 编译系统需求

- **推荐主机 OS：** Ubuntu 22.04（jammy）X64 PC **仅限！**
- **不支持 WSL！** （未在 WSL 中测试过）
- **不要在 Orange Pi 开发板上编译！**
- **Ubuntu 22.04 ISO 下载：** `https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/ubuntu-22.04-desktop-amd64.iso`
- 安装软件包前将 Ubuntu apt 源换为清华镜像：`https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/`
- **/etc/apt/sources.list（清华源）：**

```
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
```

- 替换源后：`sudo apt-get update`
- PC 必须能从 GitHub 下载内核和 U-boot 源码

### 4.2 获取 Linux SDK 源码

#### 4.2.1 下载 orangepi-build

```bash
# 从 GitHub
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/orangepi-xunlong/orangepi-build.git -b next

# 从 Gitee 国内镜像
git clone https://gitee.com/orangepi-xunlong/orangepi-build.git -b next
```

> **A733 必须使用 `next` 分支！**
> **分支/版本对应：** branch=current, u-boot=v2018.05, kernel=linux5.15

**克隆后初始结构：**
```
build.sh  external/  LICENSE  README.md  scripts/
```

**首次完整构建后结构：**
```
build.sh  external/  kernel/  LICENSE  output/  README.md  scripts/  toolchains/  u-boot/  userpatches/
```

#### 4.2.2 下载交叉编译工具链

首次运行 `build.sh` 时自动下载到 `toolchains/` 目录。每次运行 `build.sh` 会检查：缺则重新下载，有则直接使用。

**工具链镜像：** `https://mirrors.tuna.tsinghua.edu.cn/armbian-releases/_toolchain/`

**全部工具链列表：**
- `gcc-arm-11.2-2022.02-x86_64-aarch64-none-linux-gnu` — **编译 A733 Linux kernel（linux5.15）**
- `gcc-linaro-7.4.1-2019.02-x86_64_arm-linux-gnueabi` — **编译 A733 u-boot（v2018.05）**
- + 其他 10 个工具链

#### 4.2.3 源码目录说明

**Linux 内核源码仓库：**
- GitHub：`https://github.com/orangepi-xunlong/linux-orangepi/tree/orange-pi-5.15-sun60iw2`
- Gitee：`https://gitee.com/orangepi-xunlong/orange-pi-5.15-sun60iw2`

**u-boot 源码仓库：**
- GitHub：`https://github.com/orangepi-xunlong/u-boot-orangepi/tree/v2018.05-sun60iw2`
- Gitee：`https://gitee.com/orangepi-xunlong/u-boot-orangepi/tree/v2018.05-sun60iw2`

### 4.3 编译 u-boot

```bash
cd ~/orangepi-build
# 使用 Gitee 加速
sudo ./build.sh GITEE_SERVER=yes
```
- 选 "U-boot package"
- 选 Board model：orangepi4pro

**输出信息：**
- u-boot 版本：`v2018.05`
- 编译器：`aarch64-linux-gnu-gcc 11`
- 目标目录：`output/debs/u-boot`
- 文件名：`linux-u-boot-current-orangepi4pro_x.x.x_arm64.deb`
- 耗时：约 1 分钟
- 快捷命令：`sudo ./build.sh BOARD=orangepi4pro BRANCH=current BUILD_OPT=u-boot`

**禁止源码自动更新（保留修改）：**
编辑 `userpatches/config-default.conf` 设置 `IGNORE_UPDATES="yes"`

**在开发板上测试修改的 u-boot：**
```bash
# 上传
cd output/debs/u-boot
scp linux-u-boot-current-orangepi4pro_x.x.x_arm64.deb root@192.168.1.xxx:/root

# 在开发板上安装
sudo dpkg -i linux-u-boot-current-orangepi4pro_x.x.x_arm64.deb
sudo nand-sata-install
# 选择 "5 Install/Update the bootloader on SD/eMMC"
# 确认后重启
```

### 4.4 编译 Linux 内核

```bash
sudo ./build.sh
```
- 选 "Kernel package"
- 选内核配置方式：
  - 选项 1：跳过配置（使用默认）
  - 选项 2：显示内核配置菜单（`make menuconfig`）
- 选 Board model：orangepi4pro

> 永久跳过配置提示：`KERNEL_CONFIGURE=no` 或在命令行传入。
> `make menuconfig` 失败时放大终端窗口。

**输出信息：**
- 内核版本：`5.15.147`
- 编译器：`aarch64-linux-gnu-gcc 11`
- 配置文件：`external/config/kernel/linux-5.15-sun60iw2-current.config`
- 目标目录：`output/debs/`
- 生成文件：`linux-image-current-sun60iw2_x.x.x_arm64.deb`
- 耗时：约 10 分钟
- 快捷命令：`sudo ./build.sh BOARD=orangepi4pro BRANCH=current BUILD_OPT=kernel KERNEL_CONFIGURE=no`

**生成的内核 deb 包：**
- `linux-dtb-current-sun60iw2_x.x.x_arm64.deb` — 设备树
- `linux-headers-current-sun60iw2_x.x.x_arm64.deb` — 内核头文件
- `linux-image-current-sun60iw2_x.x.x_arm64.deb` — 内核镜像和模块

**在开发板上更新内核：**
```bash
cd output/debs
scp linux-image-current-sun60iw2_x.x.x_arm64.deb root@192.168.1.xxx:/root
# 在开发板上
sudo dpkg -i linux-image-current-sun60iw2_x.x.x_arm64.deb
sudo reboot
```

### 4.5 编译 rootfs

```bash
sudo ./build.sh
```
- 选 "Rootfs and all deb packages"
- 选 Board model
- 选 rootfs 类型（Ubuntu/Debian）
- 选镜像类型：
  - "Image with console interface (server)" — **服务器版**，较小；可选 Standard 或 Minimal
  - "Image with desktop environment" — **桌面版**，较大；目前仅 GNOME 桌面
- 额外软件包：按 Enter 跳过

**输出文件在 `external/cache/rootfs/`：**
```
jammy-xfce-arm64.<hash>.tar.lz4         # 压缩 rootfs
jammy-xfce-arm64.<hash>.tar.lz4.list    # 已安装包列表
jammy-xfce-arm64.<hash>.tar.lz4.current
```
- 文件名分解：`jammy`=发行版代号 / `xfce`=桌面类型（cli=服务器）/ `arm64`=架构 / hash=所有已安装包名的 MD5
- 缓存命中则直接复用

### 4.6 编译 Linux 完整镜像

```bash
sudo ./build.sh
```
- 选 "Full OS image for flashing"
- 选 Board model → rootfs 类型 → 镜像类型（server/desktop）
- 额外软件包：按 Enter 跳过

**自动完整构建流程：**
1. 初始化 Ubuntu PC 构建环境
2. 下载 u-boot 和 Linux 内核源码
3. 编译 u-boot → 生成 deb 包
4. 编译 Linux 内核 → 生成 deb 包
5. 构建 `linux-firmware` deb 包
6. 构建 `orangepi-config` deb 包
7. 构建 board-support deb 包
8. （桌面版）构建桌面相关 deb 包
9. 检查/创建 rootfs 缓存
10. 安装所有 deb 包到 rootfs
11. 应用板级和镜像类型配置
12. 创建镜像文件并格式化 ext4 分区
13. 复制 rootfs 到镜像分区
14. 更新 initramfs
15. 用 `dd` 命令写入 u-boot 到镜像

**输出路径：** `output/images/orangepi4pro_x.x.x_debian_jammy_linux5.15.xx_xfce_desktop/`
**耗时：** 约 19 分钟
**快捷命令：** `sudo ./build.sh BOARD=orangepi4pro BRANCH=current BUILD_OPT=image RELEASE=jammy BUILD_MINIMAL=no BUILD_DESKTOP=no KERNEL_CONFIGURE=yes`

---

## 第五章：Android 13 系统使用说明

### 5.1 已支持的 Android 版本

| Android 版本 | 内核版本 |
|-------------|---------|
| Android 13 | Linux 5.15 |

### 5.2 Android 13 功能适配情况

| 功能 | 状态 |
|------|------|
| HDMI 视频/音频 | OK |
| USB 3.0/2.0 | OK |
| TF 卡启动 | OK |
| eMMC/NVMe SSD | OK |
| 千兆以太网 | OK |
| WiFi/蓝牙 | OK |
| 耳机音频/板载 MIC/喇叭音频 | **不支持** |
| LCD 屏幕 | OK |
| CAM1 | OK |
| CAM2 | 拍照有重影，录像正常 |
| LED/温度传感器/GPU/电源键 | OK |
| 40pin GPIO/I2C/SPI/UART/PWM | OK |

### 5.3 ADB 使用方法

#### 5.3.1 USB OTG 模式切换

- **4 个 USB 口**中，蓝色 USB 口支持 Host 和 Device 模式，其余 3 个仅 Host
- **默认 OTG 模式：** Host（连接鼠标/键盘等），需切换到 Device 才能 ADB
- **切换步骤：** 设置 → 关于平板 → 连续点击**版本号** → 开发者模式 → 系统 → 开发者选项 → **USB OTG Mode Switch**：ON=Device 模式，OFF=Host 模式

#### 5.3.2 使用数据线连接 ADB

1. 用 USB 2.0 公对公数据线连接开发板 USB Device 口到 Ubuntu PC
2. 在开发者选项中切换到 USB Device 模式
3. 在 PC 上：
   ```bash
   sudo apt-get update && sudo apt-get install -y adb
   adb devices   # 应显示设备
   adb shell     # 进入 Android shell（a733-demo:/ #）
   ```

#### 5.3.3 使用网络连接 ADB

1. 开发板连接网络，查看 IP
2. 检查 ADB TCP 端口：
   ```bash
   console:/ # getprop | grep "adb.tcp"
   # [service.adb.tcp.port]:[5555]
   ```
3. 若未设置：
   ```bash
   console:/ # setprop service.adb.tcp.port 5555
   console:/ # stop adbd
   console:/ # start adbd
   ```
4. PC 连接：
   ```bash
   adb connect 192.168.1.xxx:5555
   adb devices   # 192.168.1.xxx:5555 device
   adb shell     # a733-demo:/ #
   ```

### 5.4 HDMI 转 VGA 显示

需要 HDMI 转 VGA 转换器 + VGA 线 + VGA 显示器。无需配置即可使用。

### 5.5 WiFi 连接

设置 → 网络和互联网 → 互联网 → 开启 WiFi → 选择网络 → 输入密码 → 连接。

### 5.6 WiFi 热点

> 前提：以太网已连接并能上网。

设置 → 网络和互联网 → 热点和网络共享 → Wi-Fi 热点 → 开启 → 记录 SSID 和密码（修改前先关闭热点）。

### 5.7 查看以太网 IP

设置 → 网络和互联网 → 以太网 → 以太网设置 → 显示 IP 地址。

### 5.8 蓝牙连接

设置 → 已连接的设备 → 配对新设备 → 扫描 → 点击目标设备 → 配对 → 双方确认 → 文件传输（接收路径：文件管理器 Download 目录）。

### 5.9 10.1寸 MIPI 屏幕

- **需要镜像：** `OrangePi4Pro_A733_Android13_lcd_v1.x.x.img`
- 组装步骤参考 Linux 章节 3.30
- 连接屏幕后断开 HDMI，Type-C 供电即可显示（默认竖屏）

### 5.10 USB 摄像头

1. 插入 UVC USB 摄像头 → `ls /dev/video*` 确认 `/dev/video0`
2. 从官方工具下载 `usbcamera.apk`
3. 安装：`adb install usbcamera.apk`
4. 打开 "USB Camera" App 查看画面

### 5.11 Android 系统 ROOT

**Orange Pi Android 镜像默认已 ROOT。**
- 下载 `rootcheck.apk` → `adb install rootcheck.apk` → 打开点击 CHECK NOW 验证。

### 5.12 40pin 接口 GPIO/UART/SPI/I2C/PWM 测试

使用预装的 **wiringOP APP**（桌面版本）。

#### 5.12.1 GPIO 测试

1. 打开 wiringOP APP → 点击 **GPIO_TEST**
2. 界面显示 40pin 对应的 CheckBox：
   - **勾选** = 引脚 OUT 模式、HIGH（3.3V）
   - **取消勾选** = LOW（0V）
   - **GPIO READALL** = 查看 wPi 号、模式、电平状态
   - **BLINK ALL GPIO** = 循环闪烁所有引脚
3. 共 **28 个 GPIO 引脚**。例：Pin 7 = GPIO PB4 = wPi 编号 2

#### 5.12.2 UART 测试

- **默认开启：** UART7 和 UART8
- 设备节点：`/dev/ttyAS7`、`/dev/ttyAS8`
- UART7：TX=Pin 8，RX=Pin 10；UART8：TX=Pin 12，RX=Pin 11

1. 打开 wiringOP APP → **UART_TEST**
2. 选择 UART 节点 → 输入波特率 → **OPEN**
3. 用跳线短接 RX 和 TX
4. 在发送框输入字符 → **SEND** → 接收框应显示相同字符（回环测试）

#### 5.12.3 SPI 测试

- **可用 SPI：** SPI3，设备节点 `/dev/spidev3.0`
- 板载 SPI Flash（SPI0，`/dev/spidev0.0`）默认也开启

1. 打开 wiringOP APP → **SPI_TEST**
2. 选择设备节点 → **OPEN**
3. 填充数据（如 data[0] 写入 `0x9f` 读 ID） → **TRANSFER**
4. 查看返回：w25q64 制造商 ID=`EFh`，设备 ID=`4017h`

#### 5.12.4 I2C 测试

- **默认开启：** i2c0（`/dev/i2c-0`）和 i2c1（`/dev/i2c-1`）

1. 连接 I2C 设备（如 ds1307 RTC）：
   - VCC=Pin 2（5V），GND=Pin 6，SDA=Pin 3，SCL=Pin 5，地址 `0x68`
2. 验证连接：`console:/ # i2cdetect -y 0` → 应显示 `0x68`
3. 打开 wiringOP → **I2C_TEST** → 选择节点 → 地址 `0x68` → **OPEN**
4. 写：寄存器 `0x1c`，值 `0x55` → **WRITE BYTE**
5. 读：**READ BYTE** → 应返回 `0x55`

#### 5.12.5 PWM 测试

- **默认开启：** S_PWM0_2，PWM0_0，PWM0_2
- S_PWM0_2 基地址：`7023000`；PWM0_0/PWM0_2 基地址：`2527000`

1. 打开 wiringOP → **PWM_TEST**
2. S_PWM0_2 选择 `pwmchip20`（显示 `7023000.pwm`）
3. Channel 设为 `2`，默认周期 `50000ns`（20 kHz）
4. 点击 **EXPORT** → 拖动滑块调节占空比 → 勾选 **Enable**
5. 用示波器在 Pin 7 测量波形

---

## 第六章：Android 13 源码编译

### 6.1 下载 Android 13 源码

1. 从百度网盘或谷歌网盘下载拆分压缩包
2. 验证 MD5：`md5sum -c md5sum`
3. 解压：`cat a733_android13.tar.gz0* | tar -xvzf -`

### 6.2 编译 Android 13 源码

**主机要求：**
- Ubuntu 22.04 x86_64
- ISO：`https://repo.huaweicloud.com/ubuntu-releases/22.04/ubuntu-22.04.2-desktop-amd64.iso`
- 内存 16GB+，磁盘 200GB+，CPU 核越多越快

**步骤 1：安装所需软件包**
```bash
sudo apt-get update
sudo apt-get install -y git gnupg flex bison gperf build-essential \
  zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 \
  lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z1-dev ccache \
  libgl1-mesa-dev libxml2-utils xsltproc unzip u-boot-tools python-is-python3 \
  libssl-dev libncurses5 clang gawk
```

**步骤 2：编译 longan（u-boot + Linux 内核）**
```bash
cd a733_android13/longan
./build.sh config
# Platform → 0 (android)
# IC → 2 (a733)
# Board → 1 (demo_aiot)
# Flash → 0 (default)

./build.sh
# 成功输出：sun60iw2p1 compile all(Kernel+modules+boot.img) successful
```

**步骤 3：编译 Android 源码并生成最终镜像**
```bash
cd a733_android13
source build/envsetup.sh
lunch a733_demo_aiot_arm64-userdebug
make -j8
pack
```

**生成的镜像路径：** `longan/out/a733_android13_demo_aiot_uart0.img`

---

## 第七章：附录

### 7.1 用户手册更新历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2025-10-14 | 初始版本 |
| v1.1 | 2025-10-22 | 新增 Debian Bullseye 硬解、GPU、NPU 使用说明 |
| v1.2 | 2025-10-24 | 新增 create_ap WiFi 热点、ADB、Docker 安装 |
| v1.3 | 2025-10-28 | 新增 orangepi-build 从 Gitee 同步方法 |
| v1.4 | 2025-11-06 | 新增 OV13850 和 IMX219 MIPI 摄像头使用方法 |

### 7.2 镜像更新历史

**2025-10-14（初始版本）：**
- `OrangePi4Pro_A733_Android13_v1.0.0.tar.gz`
- `OrangePi4Pro_A733_Android13_lcd_v1.0.0.tar.gz`
- `Orangepi4pro_1.0.0_ubuntu_jammy_desktop_xfce_linux5.15.147.7z`
- `Orangepi4pro_1.0.0_debian_bookworm_desktop_xfce_linux5.15.147.7z`

**2025-10-22：**
- `Orangepi4pro_1.0.0_debian_bullseye_desktop_xfce_linux5.15.147.7z`
  - 桌面支持 GPU 加速、Gstreamer 硬编解码

**2025-10-24：**
- `Orangepi4pro_1.0.2_*_desktop_xfce_linux5.15.147.7z`（Jammy/Bullseye/Bookworm）
  - 新增 ADB、Docker、create_ap WiFi 热点支持

**2025-10-28：**
- `Orangepi4pro_1.0.4_*_desktop_xfce_linux5.15.147.7z`（Jammy/Bullseye/Bookworm）
  - 优化 SPI Flash + NVMe 启动稳定性

**2025-11-11（v1.0.6）：**
- `Orangepi4pro_1.0.6_*_desktop_xfce_linux5.15.147.7z`（Jammy/Bullseye/Bookworm）
- `Orangepi4pro_1.0.6_*_server_linux5.15.147.7z`（Jammy/Bullseye/Bookworm）— **首次发布服务器版**
  - 支持 OpenCV 打开 OV13850 和 IMX219 MIPI 摄像头
  - 新增开机 logo 显示
  - 修复金士顿 NVMe SSD 启动失败
  - 修复 LCD 配置时系统启动卡死

---

> 参考文档：Orange Pi 4 Pro 用户手册 v1.4（263页）

---

## 第八章：实战项目集

### 8.1 LED 流水灯（wiringOP C 语言）

**硬件连接：** GPIO Pin 7, 11, 13, 15 → 各串联 220Ω 电阻 → LED 正极 → LED 负极 → GND

```c
// blink_flow.c — 4 LED 流水灯
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>

int pins[] = {2, 3, 4, 5};  // wPi 编号：Pin7=2, Pin11=3, Pin13=4, Pin15=5
int count = 4;

int main(void) {
    if (wiringPiSetup() == -1) {
        printf("wiringPi 初始化失败！\n");
        return 1;
    }
    for (int i = 0; i < count; i++) {
        pinMode(pins[i], OUTPUT);
        digitalWrite(pins[i], LOW);
    }
    printf("LED 流水灯启动，按 Ctrl+C 停止\n");
    while (1) {
        for (int i = 0; i < count; i++) {
            digitalWrite(pins[i], HIGH);
            delay(100);  // 100ms
            digitalWrite(pins[i], LOW);
        }
    }
    return 0;
}
// 编译：gcc -o blink_flow blink_flow.c -lwiringPi -lpthread
// 运行：sudo ./blink_flow
```

### 8.2 温湿度传感器 DHT22 读取（wiringOP-Python）

**硬件连接：** DHT22 VCC → Pin2 (5V), GND → Pin6 (GND), DATA → Pin7 (GPIO wPi2)

```python
# dht22_read.py — 读取 DHT22 温湿度
import wiringpi
import time

class DHT22:
    def __init__(self, pin):
        self.pin = pin
        wiringpi.wiringPiSetup()
    
    def read(self):
        """返回 (humidity, temperature) 或 None"""
        data = []
        wiringpi.pinMode(self.pin, wiringpi.OUTPUT)
        wiringpi.digitalWrite(self.pin, wiringpi.LOW)
        wiringpi.delay(18)  # 18ms 起始信号
        wiringpi.digitalWrite(self.pin, wiringpi.HIGH)
        wiringpi.delayMicroseconds(40)
        wiringpi.pinMode(self.pin, wiringpi.INPUT)
        
        # 读取 40 位数据
        for _ in range(40):
            while wiringpi.digitalRead(self.pin) == wiringpi.LOW:
                pass
            t0 = time.time_ns()
            while wiringpi.digitalRead(self.pin) == wiringpi.HIGH:
                pass
            t1 = time.time_ns()
            data.append(1 if (t1 - t0) > 50000 else 0)
        
        # 解析
        hum = int(''.join(str(b) for b in data[0:8]), 2)
        hum_d = int(''.join(str(b) for b in data[8:16]), 2)
        temp = int(''.join(str(b) for b in data[16:24]), 2)
        temp_d = int(''.join(str(b) for b in data[24:32]), 2)
        checksum = int(''.join(str(b) for b in data[32:40]), 2)
        
        if checksum != ((hum + hum_d + temp + temp_d) & 0xFF):
            return None
        
        return (hum + hum_d * 0.1, temp + temp_d * 0.1)

dht = DHT22(2)  # wPi 2 = Pin 7
while True:
    result = dht.read()
    if result:
        print(f"湿度: {result[0]:.1f}% RH  温度: {result[1]:.1f}°C")
    time.sleep(2)
```

### 8.3 I2C OLED 显示屏（ssd1306，128x64）

**硬件连接：** OLED VCC→Pin1 (3.3V), GND→Pin9, SDA→Pin3 (I2C0 SDA), SCL→Pin5 (I2C0 SCL)

```bash
# 安装依赖
sudo apt install -y python3-pip python3-pil
pip3 install Adafruit-BBIO  # 或通过 pip 安装 luma.oled
pip3 install luma.oled
```

```python
# oled_display.py — ssd1306 显示系统信息
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import subprocess
import time

# I2C0 = /dev/i2c-0
serial = i2c(port=0, address=0x3C)
device = ssd1306(serial, width=128, height=64)

def get_ip():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        return result.stdout.strip() or "无网络"
    except:
        return "错误"

def get_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        return f"{int(f.read().strip()) / 1000:.1f}"

while True:
    with canvas(device) as draw:
        draw.text((0, 0), "Orange Pi 4 Pro", fill="white")
        draw.text((0, 16), f"IP: {get_ip()}", fill="white")
        draw.text((0, 32), f"CPU: {get_temp()}C", fill="white")
        # 水平线
        draw.line((0, 48, 128, 48), fill="white")
        draw.text((0, 52), "A733 @ 2.0GHz", fill="white")
    time.sleep(2)
```

### 8.4 USB 摄像头 + NPU 实时目标检测

```bash
# 安装 OpenCV
sudo apt install -y python3-opencv libopencv-dev
```

```python
# camera_yolo.py — USB 摄像头实时检测（使用 NPU 推理）
import cv2
import numpy as np
import subprocess
import os

# YOLOv5 COCO 标签（80 类）
CLASSES = ["person","bicycle","car","motorcycle","airplane","bus","train",
           "truck","boat","traffic light","fire hydrant","stop sign",
           "parking meter","bench","bird","cat","dog","horse","sheep",
           "cow","elephant","bear","zebra","giraffe","backpack","umbrella",
           "handbag","tie","suitcase","frisbee","skis","snowboard",
           "sports ball","kite","baseball bat","baseball glove","skateboard",
           "surfboard","tennis racket","bottle","wine glass","cup","fork",
           "knife","spoon","bowl","banana","apple","sandwich","orange",
           "broccoli","carrot","hot dog","pizza","donut","cake","chair",
           "couch","potted plant","bed","dining table","toilet","tv",
           "laptop","mouse","remote","keyboard","cell phone","microwave",
           "oven","toaster","sink","refrigerator","book","clock","vase",
           "scissors","teddy bear","hair drier","toothbrush"]

def run_npu_inference(image_path):
    """调用 C++ NPU 推理程序"""
    cmd = ["./yolov5", "../model/v3/yolov5.nb", image_path, "./output"]
    result = subprocess.run(cmd, cwd=os.path.expanduser("~/ai-sdk/examples/yolov5/build"),
                           capture_output=True, text=True)
    # 解析 NPU 输出结果（格式取决于具体实现）
    return result.stdout

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("摄像头目标检测启动，按 Q 退出")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # 保存帧 → NPU 推理
    cv2.imwrite("/tmp/frame.jpg", frame)
    run_npu_inference("/tmp/frame.jpg")
    
    cv2.imshow("Orange Pi 4 Pro - NPU Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 8.5 简易 Web 服务器控制 GPIO

```python
# web_gpio.py — Flask Web 服务器控制 GPIO
# 安装：pip3 install flask
from flask import Flask, render_template_string, request
import wiringpi

app = Flask(__name__)
wiringpi.wiringPiSetup()

# 初始化 GPIO 引脚（Pin 7, 11, 13, 15 = wPi 2, 3, 4, 5）
PINS = {
    "Pin 7 (LED1)": 2,
    "Pin 11 (LED2)": 3,
    "Pin 13 (LED3)": 4,
    "Pin 15 (LED4)": 5,
}
for p in PINS.values():
    wiringpi.pinMode(p, 1)  # OUTPUT

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Orange Pi 4 Pro GPIO</title>
<style>
  body { font-family: Arial; max-width: 400px; margin: 50px auto; text-align: center; }
  button { width: 200px; height: 60px; margin: 5px; font-size: 18px; border: none; border-radius: 10px; cursor: pointer; }
  .on { background: #4CAF50; color: white; }
  .off { background: #f44336; color: white; }
  .status { font-size: 14px; color: #666; margin: 10px; }
</style></head><body>
<h2>🔌 Orange Pi 4 Pro GPIO</h2>
{% for name, pin in pins.items() %}
  <p>{{ name }} (wPi {{ pin }}):
    <a href="/on/{{ pin }}"><button class="on">ON</button></a>
    <a href="/off/{{ pin }}"><button class="off">OFF</button></a>
    <span class="status">[{{ 'HIGH' if states[pin] else 'LOW' }}]</span>
  </p>
{% endfor %}
<p class="status">CPU温度: {{ temp }}°C | IP: {{ ip }}</p>
</body></html>
"""

@app.route('/')
def index():
    states = {p: wiringpi.digitalRead(p) for p in PINS.values()}
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = f"{int(f.read().strip()) / 1000:.1f}"
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    return render_template_string(HTML, pins=PINS, states=states, temp=temp, ip=ip)

@app.route('/on/<int:pin>')
def gpio_on(pin):
    wiringpi.digitalWrite(pin, 1)
    return '<script>location.href="/"</script>'

@app.route('/off/<int:pin>')
def gpio_off(pin):
    wiringpi.digitalWrite(pin, 0)
    return '<script>location.href="/"</script>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# 访问：http://<开发板IP>:8080
```

### 8.6 Docker Compose 家庭服务栈

```yaml
# docker-compose.yml — Orange Pi 4 Pro 家庭服务栈
version: '3.8'
services:
  homeassistant:
    image: homeassistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    volumes:
      - ./ha_config:/config
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "8123:8123"
    privileged: true
    network_mode: host

  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data

  node-red:
    image: nodered/node-red:latest
    container_name: node-red
    restart: unless-stopped
    user: root
    ports:
      - "1880:1880"
    volumes:
      - ./node_red:/data
    devices:
      - /dev/ttyS7:/dev/ttyS7  # UART7 for zigbee stick

  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    ports:
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./portainer:/data

  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./www:/var/www/html
```

```bash
# 部署命令
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# 重新登录后：
mkdir -p ~/opi-stack/{ha_config,mosquitto/{config,data},node_red,portainer,nginx/{conf,www}}
cd ~/opi-stack
docker compose up -d
```

### 8.7 Systemd 自启动服务模板

```ini
# /etc/systemd/system/my-gpio-app.service
[Unit]
Description=My GPIO Application
After=network.target

[Service]
Type=simple
User=orangepi
WorkingDirectory=/home/orangepi/my-app
ExecStart=/usr/bin/python3 /home/orangepi/my-app/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 硬件访问权限
DeviceAllow=/dev/gpiomem rw
DeviceAllow=/dev/mem rw
DeviceAllow=/dev/spidev* rw
DeviceAllow=/dev/i2c-* rw
DeviceAllow=/dev/ttyS* rw

[Install]
WantedBy=multi-user.target
```

```bash
# 部署命令
sudo systemctl daemon-reload
sudo systemctl enable my-gpio-app
sudo systemctl start my-gpio-app
sudo systemctl status my-gpio-app
```

---

## 第九章：故障排查决策树

### 9.1 系统无法启动决策树

```
系统上电后无任何反应？
├── 红色 LED 不亮？
│   ├── YES → 换 5V/3A Type-C 电源适配器（严禁 PD 充电器！）
│   └── NO  → 红色 LED 亮但绿色 LED 不闪？
│       ├── YES → TF 卡问题：
│       │   ├── 重烧镜像（balenaEtcher 校验通过了吗？）
│       │   ├── 换一张 Class 10 TF 卡（8GB+）
│       │   ├── 检查 TF 卡槽接触
│       │   └── 用 USB 转 TTL 看串口日志（115200 波特率）
│       └── NO  → 绿色 LED 闪烁但 HDMI 没显示？
│           ├── 换 HDMI 线 / 显示器
│           ├── 用 HDMI 转 VGA 测试
│           ├── SSH 登录确认系统实际已启动
│           └── 检查 /boot/orangepiEnv.txt（错误 overlay 可能导致不显示）
```

### 9.2 GPIO 故障决策树

```
gpio 命令不工作？
├── "command not found"？
│   └── wiringOP 未安装：
│       └── git clone https://github.com/orangepi-xunlong/wiringOP.git -b next
│           cd wiringOP && sudo ./build clean && sudo ./build
├── "gpio readall" 无输出？
│   └── sudo gpio readall（需要 root 权限）
├── gpio write 没反应？
│   ├── 用 gpio readall 确认 wPi 编号是否对应正确物理引脚
│   ├── gpio mode <pin> out — 确认已设为输出模式
│   ├── 用万用表测量引脚电压（应为 0V 或 3.3V）
│   ├── 检查是否通过 sudo orangepi-config 启用了该引脚（部分引脚默认禁用）
│   └── 确认 GPIO 是 3.3V 电平，5V 设备需电平转换！
└── I2C/SPI/UART 不工作？
    └── sudo orangepi-config → System → Hardware → 空格启用 → Save → Reboot
```

### 9.3 网络故障决策树

```
无法联网？
├── 以太网不通？
│   ├── ip a eth0 — 无 IP？
│   │   ├── Debian 12：试试 ip a end0（接口名不同！）
│   │   └── sudo dhclient eth0 — 手动 DHCP
│   ├── ping 网关通但 ping 外网不通？
│   │   └── 检查 /etc/resolv.conf DNS 配置
│   └── 网口灯不亮？
│       └── 换网线 / 路由器端口
├── WiFi 扫不到网络？
│   ├── nmcli dev wifi — 能扫到吗？
│   ├── rfkill list — 检查是否被软屏蔽
│   └── 检查天线是否接好（板载天线 / 外接天线）
└── WiFi 连不上？
    ├── 密码是否正确（区分大小写）
    ├── 路由器是否开启了 MAC 过滤
    └── 不要修改 /etc/network/interfaces（用 nmcli/nmtui！）
```

### 9.4 NPU 推理故障决策树

```
NPU 推理失败？
├── PC 端 Docker 环境问题？
│   ├── docker: command not found → sudo apt install docker.io
│   ├── 权限拒绝 → sudo usermod -aG docker $USER（重新登录）
│   └── 镜像未找到 → sudo docker load -i ubuntu-npu_v2.0.10.tar
├── 模型转换失败？
│   ├── source env.sh v3 — 确认版本
│   ├── 检查 inputmeta.yml scale 参数
│   └── 确认 ai-sdk 完整解压
└── 板端推理失败？
    ├── 检查 libopencv-dev 和 cmake 已安装
    ├── cmake .. 报错 → 检查依赖库
    ├── .nb 文件路径正确
    └── 内存不足 → free -h 检查，关闭其他进程
```

### 9.5 NVMe SSD 启动故障

```
SPIFlash+NVMe 启动失败？
├── SSD 型号兼容吗？
│   ├── ✅ 已知兼容：樊想、广存
│   ├── ⚠️ 金士顿：需要 v1.0.6+ 镜像
│   └── ❌ 其他品牌：可能不兼容
├── 烧录步骤正确吗？
│   ├── ① sudo parted --script /dev/nvme0n1 mklabel gpt mkpart primary ext4 65536s 100%
│   ├── ② sudo nand-sata-install → 选 4
│   ├── ③ 确认烧录 bootloader 到 SPI Flash → YES
│   └── ④ 关机后必须拔出 TF 卡再上电！
└── PCIe 接口检查：
    └── SSD 是否插紧？M.2 规格 = PCIe 3.0 x1
```

---

## 第十章：性能调优指南

### 10.1 CPU 频率调节

```bash
# 查看当前调度器
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# ondemand | performance | conservative | powersave | schedutil

# 查看可用频率
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies

# 设置为性能模式（固定最高频率 2.0GHz）
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 省电模式
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 永久设置：编辑 /etc/default/cpufrequtils
# GOVERNOR="performance"
```

### 10.2 内存优化

```bash
# 查看内存
free -h

# 清除缓存（释放内存）
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# 禁用 Swap（保护 TF 卡/eMMC 寿命）
sudo swapoff -a
sudo systemctl disable dphys-swapfile  # Debian
# 或在 /etc/fstab 中注释 swap 行

# 设置 swap 到 NVMe SSD（而非 TF 卡）
# 在 NVMe 分区上创建 swap 文件
sudo dd if=/dev/zero of=/mnt/nvme/swapfile bs=1M count=2048
sudo chmod 600 /mnt/nvme/swapfile
sudo mkswap /mnt/nvme/swapfile
sudo swapon /mnt/nvme/swapfile
```

### 10.3 TF 卡 / eMMC 性能优化

```bash
# 测试读写速度
sudo hdparm -Tt /dev/mmcblk1  # TF 卡
sudo hdparm -Tt /dev/mmcblk0  # eMMC

# 查看当前调度器
cat /sys/block/mmcblk1/queue/scheduler
# [mq-deadline] none

# 设置调度器
echo noop | sudo tee /sys/block/mmcblk1/queue/scheduler

# 使用 noatime 挂载减少写入（编辑 /etc/fstab）
# /dev/mmcblk1p1 / ext4 defaults,noatime,nodiratime 0 1
```

### 10.4 温度与散热管理

```bash
# 查看所有传感器温度（单位：千分之一°C）
for z in /sys/class/thermal/thermal_zone[0-9]*; do
    echo "$(cat $z/type): $(( $(cat $z/temp) / 1000 ))°C"
done

# 查看 CPU 温度触发降频的阈值
cat /sys/devices/virtual/thermal/thermal_zone0/trip_point_*_temp

# 推荐：加散热片 + 风扇（5V 接 40pin Pin2/4，GND 接 Pin6）
# 主动散热可维持 NPU+CPU 满负载运行
```

### 10.5 网络性能调优

```bash
# 查看网卡 ring buffer
ethtool -g eth0

# 增加 ring buffer
sudo ethtool -G eth0 rx 1024 tx 1024

# 查看当前速度
ethtool eth0 | grep Speed
# Speed: 1000Mb/s

# TCP 调优（编辑 /etc/sysctl.conf）
# net.core.rmem_max = 134217728
# net.core.wmem_max = 134217728
# net.ipv4.tcp_rmem = 4096 87380 134217728
# net.ipv4.tcp_wmem = 4096 65536 134217728
sudo sysctl -p
```

### 10.6 NPU 性能优化

```bash
# NPU 频率查看
cat /sys/class/thermal/thermal_zone5/temp
cat /sys/class/thermal/cooling_device*/type

# 推理前固定 CPU 频率
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 确保推理时关闭不必要的后台服务
sudo systemctl stop bluetooth
sudo systemctl stop ModemManager
```

### 10.7 开机启动优化

```bash
# 查看启动耗时
systemd-analyze

# 查看最慢的服务
systemd-analyze blame

# 禁用不必要的服务
sudo systemctl disable bluetooth    # 不用蓝牙
sudo systemctl disable ModemManager # 不用 4G 模块
sudo systemctl disable NetworkManager-wait-online.service  # 不等待网络
```

---

## 第十一章：安全加固指南

### 11.1 基础安全配置

```bash
# 修改默认密码！
passwd orangepi
sudo passwd root

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 fail2ban（防暴力破解 SSH）
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
# 默认配置即可保护 SSH
```

### 11.2 SSH 加固

```bash
# 编辑 /etc/ssh/sshd_config
sudo vim /etc/ssh/sshd_config

# 关键配置项：
# PermitRootLogin no              # 禁用 root SSH 登录
# PasswordAuthentication no       # 禁用密码登录（用密钥）
# Port 2222                       # 换端口
# AllowUsers orangepi             # 限制用户
# MaxAuthTries 3                  # 最大尝试次数
# ClientAliveInterval 300

sudo systemctl restart sshd
```

### 11.3 配置 SSH 密钥登录

```bash
# 在本地 PC 上生成密钥（如果还没有）
ssh-keygen -t ed25519 -C "orangepi4pro"

# 复制公钥到开发板
ssh-copy-id -i ~/.ssh/id_ed25519.pub orangepi@<开发板IP>

# 确认密钥登录成功后，再禁用密码登录
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 11.4 防火墙配置（iptables / ufw）

```bash
# 安装 ufw
sudo apt install -y ufw

# 默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许必要服务
sudo ufw allow 22        # SSH（如果改了端口则改这里）
sudo ufw allow 80        # HTTP
sudo ufw allow 443       # HTTPS
sudo ufw allow 1883      # MQTT
sudo ufw allow 8123      # Home Assistant
sudo ufw allow 8080      # 自定义 Web 服务

# 启用
sudo ufw enable
sudo ufw status verbose
```

### 11.5 只读文件系统保护（延长 TF 卡寿命）

```bash
# 将 /tmp 和 /var/log 挂载为 tmpfs（内存文件系统）
# 编辑 /etc/fstab 添加：
echo "tmpfs /tmp tmpfs defaults,noatime,nosuid,size=512M 0 0" | sudo tee -a /etc/fstab
echo "tmpfs /var/log tmpfs defaults,noatime,nosuid,size=256M 0 0" | sudo tee -a /etc/fstab

# 日志轮转（限制磁盘写入）
sudo apt install -y logrotate
# /etc/logrotate.conf 默认配置即可
```

### 11.6 内核安全参数

```bash
# 编辑 /etc/sysctl.d/99-security.conf
sudo tee /etc/sysctl.d/99-security.conf << 'EOF'
# 防止 IP 欺骗
net.ipv4.conf.all.rp_filter = 1
# 忽略 ICMP 重定向
net.ipv4.conf.all.accept_redirects = 0
# 忽略 ICMP echo（如不需要 ping）
# net.ipv4.icmp_echo_ignore_all = 1
# ASLR 随机化
kernel.randomize_va_space = 2
# 防止 SYN flood
net.ipv4.tcp_syncookies = 1
EOF
sudo sysctl -p /etc/sysctl.d/99-security.conf
```

---

## 附录A：快速参考卡片

### 最常用命令速查

| 操作 | 命令 |
|------|------|
| 查看所有 GPIO | `gpio readall` |
| GPIO 输出高 | `gpio mode 2 out && gpio write 2 1` |
| 扫描 I2C 总线 | `sudo i2cdetect -y -r 0` |
| 启用外设 | `sudo orangepi-config` |
| WiFi 连接 | `sudo nmcli dev wifi connect SSID password PASS` |
| 创建热点 | `sudo create_ap -m nat wlan0 eth0 orangepi orangepi --no-virt` |
| 查看 IP | `ip a eth0` / `ip a wlan0` |
| 查看温度 | `cat /sys/class/thermal/thermal_zone0/temp` |
| SSD 分区 | `sudo parted --script /dev/nvme0n1 mklabel gpt mkpart primary ext4 65536s 100%` |
| 扩容 TF 卡 | 自动扩容，或用 `sudo gparted` |
| 烧录到 eMMC | `sudo nand-sata-install` → 选 2 |
| 烧录到 NVMe | `sudo nand-sata-install` → 选 4 |
| LED 控制 | `echo heartbeat > /sys/class/leds/status_led/trigger` |
| 重启 SSH | `reset_ssh.sh` |
| 关机 | `sudo poweroff` |
| Docker 启用 | `enable_docker.sh` |
| 系统备份 | `sudo opi-bkimg` |

### 引脚快速对照

| 功能 | 总线 | Pin | 设备节点 |
|------|------|-----|----------|
| GPIO | — | 7(wPi2),11(wPi3),13(wPi4),15(wPi5)... | — |
| SPI | SPI3 | MOSI=19, MISO=21, CLK=23, CS0=24 | `/dev/spidev3.0` |
| I2C0 | I2C0 | SDA=3, SCL=5 | `/dev/i2c-0` |
| I2C1 | I2C1 | SDA=27, SCL=28 | `/dev/i2c-1` |
| I2C2 | I2C2 | SDA=19, SCL=23 | `/dev/i2c-2` |
| I2C3 | I2C3 | SDA=26, SCL=21 | `/dev/i2c-3` |
| UART | UART7 | TX=8, RX=10 | `/dev/ttyS7` |
| PWM | SPWM0-2 | 7 | `/sys/class/pwm/pwmchip20/pwm2` |
| PWM | PWM0-0 | 29 | `/sys/class/pwm/pwmchip0/pwm0` |
| PWM | PWM0-2 | 33 | `/sys/class/pwm/pwmchip0/pwm2` |
| PWM | PWM0-3 | 35 | `/sys/class/pwm/pwmchip0/pwm3` |
| PWM | PWM0-4 | 37 | `/sys/class/pwm/pwmchip0/pwm4` |
| PWM | PWM0-5 | 32 | `/sys/class/pwm/pwmchip0/pwm5` |
| PWM | PWM0-6 | 36 | `/sys/class/pwm/pwmchip0/pwm6` |
| PWM | PWM0-7 | 38 | `/sys/class/pwm/pwmchip0/pwm7` |

### 电源引脚
| 电压 | 引脚 |
|------|------|
| 3.3V | Pin 1, 17 |
| 5V | Pin 2, 4 |
| GND | Pin 6, 9, 14, 20, 25, 30, 34, 39 |

### 常用文件路径速查

| 文件/目录 | 用途 |
|-----------|------|
| `/boot/orangepiEnv.txt` | 设备树和内核参数 |
| `/boot/orangepi_first_run.txt` | 首次启动自动配置 |
| `/etc/network/interfaces` | **不要修改！** 用 nmcli/nmtui |
| `/sys/class/leds/status_led/trigger` | 绿色 LED 控制 |
| `/sys/class/thermal/thermal_zone*/temp` | 温度传感器 |
| `/sys/class/pwm/pwmchip*/` | PWM 控制 |
| `/opt/linux-headers*.deb` | 内核头文件 |
| `/opt/v4l2_opencv_demo/` | MIPI 摄像头 demo |
| `/usr/src/wiringOP/` | wiringOP 源码（备用） |
| `/usr/src/wiringOP-Python/` | wiringOP-Python 源码（备用） |
| `/usr/src/hello/` | hello 内核模块示例 |
| `orangepi-build/external/cache/rootfs/` | rootfs 缓存 |
| `orangepi-build/output/debs/` | 编译的 deb 包 |
| `orangepi-build/output/images/` | 编译的完整镜像 |

---

## 第十二章：硬件原理图与 PCB 设计文件

> **文件位置：** 本仓库 `schematics/` 目录
> **PCB 版本：** V1.3.2
> **设计日期：** 2026-01-09
> **文件格式：** PDF 电路图 + DXF PCB 版图

### 12.1 文件清单

| 文件 | 大小 | 格式 | 内容说明 |
|------|------|------|---------|
| `OPI 4 PRO V1_3_2_20260109.pdf` | 1.35 MB | PDF | 完整电路原理图（多页），包含所有芯片引脚连接、电源树、外设接口电路 |
| `OPi_4_Pro_V1_3_2-TOP.dxf` | 1.24 MB | DXF | PCB 顶层版图 — 元器件布局、顶层走线、丝印层、焊盘 |
| `OPi_4_Pro_V1_3_2-BOT.dxf` | 1.71 MB | DXF | PCB 底层版图 — 底层走线、过孔、测试点、散热区 |
| `OPi_4_Pro_V1_3_2-DXF.pdf` | 325 KB | PDF | DXF 版图预览（可打印查看整体布局与元件位置） |

### 12.2 原理图包含的关键电路模块

| 电路模块 | 说明 |
|---------|------|
| **A733 SoC Core** | 全志 A733 主芯片（BGA 封装），包括所有引脚定义、供电配置、时钟源 |
| **Power Tree · 电源树** | 多路 DC-DC 转换器（5V→3.3V/1.8V/1.2V/0.8V 等）、LDO、PMIC 电源管理芯片 |
| **DDR4/LPDDR5** | 内存颗粒焊接位置、阻抗匹配、信号完整性设计 |
| **eMMC Interface** | eMMC 模块插座引脚（包含 CLK/CMD/DATA0-7/RST） |
| **SPI Flash** | 128Mb SPI NOR Flash 连接（CS/CLK/MOSI/MISO/WP/HOLD） |
| **M.2 PCIe 3.0** | M-Key 插座引脚全映射（PCIe TX/RX lanes、REFCLK、PERST、SMBus） |
| **Gigabit Ethernet** | YT8531CA PHY → RJ45（含 PoE 供电电路、网络变压器） |
| **Wi-Fi 6 + BT 5.4** | 无线模组连接（SDIO 3.0 + UART/PCM for BT） |
| **HDMI TX 2.0** | HDMI 差分对走线、CEC/HPD/DDC 信号 |
| **MIPI CSI (×2)** | 双路摄像头输入（2-lane + 4-lane），含 I2C 控制、MCLK |
| **MIPI DSI** | 4-lane MIPI 显示输出，含背光控制、触摸 I2C |
| **USB 3.0 + USB 2.0 ×3** | USB 3.0 SuperSpeed 差分对 + USB 2.0 DP/DM |
| **Audio Codec** | ES8323 音频编解码器 → 3.5mm 耳机插孔 + 板载 MIC + 喇叭 |
| **40-Pin GPIO Header** | 完整 40pin 引脚到 SoC 的 GPIO 复用映射 |
| **Debug UART** | 3-pin 串口（TX/RX/GND）连接到 SoC 调试 UART |
| **Power Management** | 电源按键、复位按键、BOOT 按键、电池备份电路 |
| **Clock Generator** | 24MHz/32.768KHz 晶振、RTC 时钟源 |
| **SD Card Slot** | uSD 卡槽连接（含卡检测引脚） |

### 12.3 DXF PCB 版图用途

**TOP 层（`OPi_4_Pro_V1_3_2-TOP.dxf`）：**
- 元器件精确布局位置
- 顶层焊盘与过孔
- 丝印标注（元件编号、接口名称、版本号）
- 可用于制作 PCB 外壳/散热器/安装支架的机械图纸

**BOT 层（`OPi_4_Pro_V1_3_2-BOT.dxf`）：**
- 底层布线全貌
- 测试点位置
- 散热铜皮区域
- M.2 插座、eMMC 模块座等底部元件位置

### 12.4 如何使用这些文件

| 场景 | 使用的文件 | 工具 |
|------|-----------|------|
| **查看电路连接** | `OPI 4 PRO V1_3_2_20260109.pdf` | 任意 PDF 阅读器 |
| **焊接/维修** | 原理图 PDF | PDF 阅读器，查找元件位号和引脚号 |
| **设计外壳** | TOP.dxf + BOT.dxf | AutoCAD / Fusion 360 / FreeCAD |
| **PCB 改版** | DXF 文件 | Altium Designer / KiCad / Eagle |
| **定位安装孔** | DXF.pdf / DXF | 查看 4×3.0mm 定位孔精确位置 |
| **GPIO 追踪** | 原理图 PDF | 从 40pin 反向追踪到 SoC GPIO Bank |

### 12.5 重要设计细节

**电源设计：**
- Type-C 5V 直接供电，无 PD 协议芯片
- 多级 DC-DC 产生各电压域
- PoE 通过专用电路注入到 5V rail

**信号完整性：**
- HDMI/MIPI/PCIe 等高速信号采用差分对 + 等长走线
- DDR 内存采用 fly-by 拓扑
- 关键时钟线包地处理

**散热设计：**
- SoC 下方 BOT 层大面积铜皮 + 过孔矩阵（Thermal Via Array）
- M.2 SSD 位置预留散热间隙

**ESD 保护：**
- USB/HDMI/以太网接口均有 ESD 保护二极管
- 40pin GPIO 无内置 ESD（使用时注意！）

---

## 第十三章：常见传感器与模块接线大全

> 以下所有接线均直接可用，wPi 编号对应 wiringOP。使用 `gpio readall` 查看完整映射。

### 13.1 温湿度传感器

| 传感器 | VCC | GND | DATA | 其他引脚 | 协议 | 注意事项 |
|--------|-----|-----|------|---------|------|---------|
| **DHT11** | Pin 2 (5V) | Pin 6 (GND) | Pin 7 (wPi 2) | — | 单总线 | 采样间隔 ≥1 秒 |
| **DHT22** | Pin 2 (5V) | Pin 6 (GND) | Pin 7 (wPi 2) | — | 单总线 | 采样间隔 ≥2 秒，精度 ±0.5°C |
| **DS18B20** | Pin 2 (5V) | Pin 6 (GND) | Pin 7 (wPi 2) | 4.7kΩ 上拉 | 1-Wire | 需启用 w1-gpio overlay |
| **AHT10** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3 (I2C0) | SCL→Pin 5 (I2C0) | I2C | 地址 0x38，需启用 I2C0 |
| **SHT30** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3 | SCL→Pin 5 | I2C | 地址 0x44/0x45 |
| **BME280** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3 | SCL→Pin 5 | I2C | 地址 0x76/0x77，温度+湿度+气压 |

**DS18B20 启用 1-Wire：**
```bash
sudo orangepi-config  # System → Hardware → 选中 w1-gpio → Save → Reboot
# 设备路径：/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
```

### 13.2 距离与运动传感器

| 传感器 | VCC | GND | TRIG | ECHO | 其他 | 协议 | 注意事项 |
|--------|-----|-----|------|------|------|------|---------|
| **HC-SR04** | Pin 2 (5V) | Pin 6 (GND) | Pin 11 (wPi 3) | Pin 13 (wPi 4) | — | GPIO 脉冲 | ECHO 需分压！直连 5V 会烧 GPIO |
| **HC-SR04 安全接法** | — | — | Pin 11 | 分压到 3.3V → Pin 13 | 2×1kΩ 电阻 | — | ECHO→分压→GPIO |
| **VL53L0X** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3 | SCL→Pin 5 | XSHUT→任意 GPIO | I2C | 地址 0x29，ToF 激光测距 |
| **HC-SR501** | Pin 2 (5V) | Pin 6 (GND) | Pin 15 (wPi 5) | — | — | GPIO 数字 | 人体红外 PIR，OUT=3.3V 直连安全 |

> ⚠️ **HC-SR04 ECHO 分压电路：** ECHO→1kΩ→GPIO，GPIO→1kΩ→GND。两个 1kΩ 分压 5V→2.5V（安全）。

### 13.3 显示模块

| 模块 | VCC | GND | SDA | SCL | 其他 | 协议 | 地址 |
|------|-----|-----|-----|-----|------|------|------|
| **SSD1306 OLED (128×64)** | Pin 1 (3.3V) | Pin 9 (GND) | Pin 3 | Pin 5 | — | I2C | 0x3C |
| **SSH1106 OLED (128×64)** | Pin 1 (3.3V) | Pin 9 (GND) | Pin 3 | Pin 5 | — | I2C | 0x3C(SPI 可选) |
| **LCD1602 (I2C 转接板)** | Pin 2 (5V) | Pin 6 (GND) | Pin 3 | Pin 5 | — | I2C | 0x27/0x3F |
| **LCD1602 (4-bit)** | Pin 2 (5V) | Pin 6 (GND) | — | — | RS/EN/D4-D7→Pin 29/31/33/35/37/32 | GPIO | V0 接电位器调对比度 |
| **TM1637 数码管** | Pin 1 (3.3V) | Pin 9 (GND) | CLK→Pin 11 | DIO→Pin 13 | — | GPIO 模拟 | CLK/DIO 可换引脚 |
| **MAX7219 8×8 LED** | Pin 2 (5V) | Pin 6 (GND) | DIN→Pin 19 (MOSI) | CS→Pin 24 (CS0) | CLK→Pin 23 (CLK) | SPI | 需启用 SPI3 |

### 13.4 环境传感器

| 传感器 | VCC | GND | 信号线 | 协议 | 地址/说明 |
|--------|-----|-----|--------|------|----------|
| **BH1750 光照** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3, SCL→Pin 5 | I2C | 0x23/0x5C |
| **CCS811 空气质量** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3, SCL→Pin 5 | I2C | 0x5A/0x5B，需预热 20 分钟 |
| **PMS5003 PM2.5** | Pin 2 (5V) | Pin 6 (GND) | TX→Pin 8 (UART7 TX) | UART | 9600 baud，被动模式 |
| **MQ-2 烟雾** | Pin 2 (5V) | Pin 6 (GND) | AO→MCP3008 ADC | 模拟 | 需 ADC 模块，预热 ≥24h |
| **BMP280 气压** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3, SCL→Pin 5 | I2C | 0x76/0x77 |
| **MPU6050 六轴** | Pin 1 (3.3V) | Pin 9 (GND) | SDA→Pin 3, SCL→Pin 5 | I2C | 0x68 |

### 13.5 继电器与电机驱动

| 模块 | VCC | GND | IN/控制 | 负载 | 注意事项 |
|------|-----|-----|---------|------|---------|
| **单路继电器 (SRD-05VDC)** | Pin 4 (5V, JD-VCC) | Pin 6 (GND) | IN→Pin 11 (wPi 3) | 最大 10A/250VAC | 低电平触发，需共地 |
| **L298N 电机驱动** | 外部 12V | GND 共地 | IN1-IN4→Pin 11/13/15/16 | 2 路直流电机 | 逻辑供电可接 Pin 2 (5V) |
| **MG996R 舵机** | 外部 5V/2A | GND 共地 | PWM→Pin 7 (SPWM0-2) | 扭矩 10kg·cm | 周期 20ms，脉宽 0.5-2.5ms |
| **ULN2003 步进电机** | Pin 2 (5V) | Pin 6 (GND) | IN1-IN4→Pin 11/13/15/16 | 28BYJ-48 | 整步/半步模式 |
| **A4988 步进驱动** | 外部 12V | GND 共地 | STEP→Pin 11, DIR→Pin 13 | NEMA17 | MS1-MS3 设置微步 |

### 13.6 通信模块

| 模块 | VCC | GND | TX/RX | 其他 | 协议 | 注意事项 |
|------|-----|-----|-------|------|------|---------|
| **SIM800L GSM** | 外部 4.2V/2A | GND 共地 | TX→Pin 10 (UART7 RX) | RX→Pin 8 (UART7 TX) | UART | 不可用板载 5V，峰值 2A |
| **NEO-6M GPS** | Pin 1 (3.3V) | Pin 9 (GND) | TX→Pin 10 (UART7 RX) | — | UART | 9600 baud，需天线 |
| **RC522 RFID** | Pin 1 (3.3V) | Pin 9 (GND) | — | SDA→Pin 24 (CS0), SCK→Pin 23, MOSI→Pin 19, MISO→Pin 21 | SPI | RST 接任意 GPIO |
| **CAN MCP2515** | Pin 2 (5V) | Pin 6 (GND) | — | SCK→Pin 23, SI→Pin 19, SO→Pin 21, CS→Pin 24 | SPI | 需 can 内核支持 |

### 13.7 传感器接线速记

```
温度类     → I2C0 (Pin 3 SDA + Pin 5 SCL)：AHT10/BME280/SHT30/BMP280
单总线     → Pin 7 (wPi 2)：DHT11/DHT22/DS18B20
距离类     → Pin 11+13：HC-SR04  |  I2C0 Pin 3+5：VL53L0X
显示类     → I2C0 Pin 3+5：SSD1306/LCD1602  |  SPI3 Pin 19+21+23+24：MAX7219
继电器/MOS → Pin 11 (wPi 3)：开关控制  |  Pin 7 (SPWM0-2)：舵机
GPS/GSM    → UART7：Pin 8 (TX) + Pin 10 (RX)
RFID/CAN   → SPI3：Pin 19+21+23+24 (MOSI+MISO+CLK+CS0)
```

---

## 第十四章：Claude Code 板载开发模式与代码模板

### 14.1 标准开发循环

```
用户提出需求
  → Claude Code 读取 skill 获取引脚/驱动/命令
  → 直接读写文件系统生成代码
  → 执行编译/安装命令
  → 运行测试、查看日志
  → 根据输出修正
  → 创建 systemd 服务（可选）
```

### 14.2 新建项目模板（C 语言 GPIO）

```bash
# Claude Code 在板上自动执行的步骤：

# 1. 创建项目目录
mkdir -p ~/my-gpio-project && cd ~/my-gpio-project

# 2. 生成 CMakeLists.txt
cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.10)
project(my_gpio_project C)
set(CMAKE_C_STANDARD 11)
find_library(WIRINGPI_LIB wiringPi)
add_executable(app main.c)
target_link_libraries(app ${WIRINGPI_LIB} pthread)
EOF

# 3. 生成 main.c（GPIO 控制）
cat > main.c << 'EOF'
#include <wiringPi.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

volatile int running = 1;
void cleanup(int sig) { running = 0; }

int main() {
    signal(SIGINT, cleanup);
    signal(SIGTERM, cleanup);
    if (wiringPiSetup() == -1) { return 1; }
    pinMode(2, OUTPUT);     // Pin 7 = wPi 2
    pinMode(3, INPUT);      // Pin 11 = wPi 3，读按钮
    pullUpDnControl(3, PUD_UP);  // 上拉

    printf("GPIO 项目启动，Ctrl+C 退出\n");
    while (running) {
        int btn = digitalRead(3);
        digitalWrite(2, btn == LOW ? HIGH : LOW);  // 按钮按下→LED亮
        delay(50);
    }
    digitalWrite(2, LOW);
    printf("清理退出\n");
    return 0;
}
EOF

# 4. 编译运行
mkdir build && cd build
cmake .. && make
sudo ./app
```

### 14.3 新建项目模板（Python GPIO + MQTT）

```python
# Claude Code 自动生成的 Python MQTT + GPIO 项目
# ~/mqtt-sensor/main.py

import wiringpi
import paho.mqtt.client as mqtt
import json, time, socket

# ── 硬件配置 ──
SENSOR_PIN = 2          # wPi 2 = Pin 7
ALERT_PIN = 5           # wPi 5 = Pin 15
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_TOPIC = "home/device/data"
CLIENT_ID = f"opi4pro_{socket.gethostname()}"

# ── 初始化 ──
wiringpi.wiringPiSetup()
wiringpi.pinMode(SENSOR_PIN, wiringpi.INPUT)
wiringpi.pinMode(ALERT_PIN, wiringpi.OUTPUT)

client = mqtt.Client(client_id=CLIENT_ID)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def publish(data):
    payload = json.dumps({"ts": time.time(), "client": CLIENT_ID, **data})
    client.publish(MQTT_TOPIC, payload)
    print(f"[MQTT] {payload}")

# ── 主循环 ──
try:
    publish({"status": "online"})
    while True:
        val = wiringpi.digitalRead(SENSOR_PIN)
        wiringpi.digitalWrite(ALERT_PIN, val)
        publish({"sensor_value": val})
        time.sleep(5)
except KeyboardInterrupt:
    publish({"status": "offline"})
    client.disconnect()
```

### 14.4 实时调试模式

```
👤 你：GPIO Pin 7 输出不干活

🤖 Claude Code：
  1. sudo gpio readall
     → 确认 Pin 7 映射到 wPi 2，当前模式 IN
  2. gpio mode 2 out
     → 设为输出模式
  3. gpio write 2 1
     → 输出高电平
  4. 用万用表 DC 档测量 Pin 7 和 GND
     → 应有 3.3V
  5. 检查接线：GPIO→电阻（220Ω-1kΩ）→LED→GND
     → LED 长脚 (+), 短脚 (-)
  6. 若仍不亮：换 LED、测电阻、检查杜邦线
```

### 14.5 Claude Code 板载能力清单

| 能力 | 说明 | 示例 |
|------|------|------|
| **文件操作** | 读/写/搜索项目代码 | 生成 CMakeLists.txt、修改内核配置 |
| **Shell 执行** | 运行命令、安装软件包 | `apt install`, `cmake`, `make`, `systemctl` |
| **GPIO 直接操作** | 通过 wiringOP 读写引脚 | `gpio write 2 1`, Python wiringpi |
| **I2C 设备通信** | 扫描总线、读写寄存器 | `i2cdetect -y 0`, Python smbus2 |
| **SPI 传输** | 操作 SPI 设备 | `spidev_test -D /dev/spidev3.0` |
| **编译代码** | 板载 GCC/G++ 编译 | `gcc -o app main.c -lwiringPi` |
| **systemd 管理** | 创建/启停服务 | `systemctl enable my-app` |
| **网络配置** | WiFi、静态 IP、热点 | `nmcli`, `create_ap` |
| **Docker 操作** | 运行容器、compose | `docker compose up -d` |
| **内核模块** | 加载/卸载驱动 | `modprobe vin_v4l2`, `insmod hello.ko` |
| **DT Overlay** | 配置设备树 | `orangepi-config` |
| **性能分析** | CPU/内存/温度监控 | `top`, `free -h`, 读取 thermal_zone |

### 14.6 常见开发任务速成

**"写个守护进程监控 CPU 温度，超过 80°C 时打开风扇"**
```
Claude Code 直接：生成 bash 脚本 → 存入 /usr/local/bin/cpu-fan.sh
→ 创建 systemd timer：每 10 秒检查一次温度
→ GPIO Pin 15 控制 5V 风扇（通过 NPN 三极管）
```

**"把板子做成 MQTT 网关，串口收到的传感器数据转发到 MQTT"**
```
Claude Code 直接：生成 Python 脚本读 /dev/ttyS7
→ 解析数据 → paho-mqtt 发布到 broker
→ systemd 服务开机自启
```

**"这个项目用 git 管理，每次改完能自动编译测试"**
```
Claude Code 直接：生成 Makefile/CMakeLists.txt
→ 创建 .gitignore → git init → git add && git commit
→ 创建 pre-commit hook（编译检查）
```

---

## 第十五章：交叉编译与远程部署

### 15.1 从 PC 交叉编译到 Orange Pi 4 Pro

**主机要求：** Ubuntu 22.04 X64 + orangepi-build 工具链

```bash
# 1. 下载工具链（同 orangepi-build 编译时自动下载）
# 位置：orangepi-build/toolchains/
# 用于 aarch64：gcc-arm-11.2-2022.02-x86_64-aarch64-none-linux-gnu

# 2. 设置环境变量
export CC=~/orangepi-build/toolchains/gcc-arm-11.2-2022.02-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-gcc
export CXX=~/orangepi-build/toolchains/gcc-arm-11.2-2022.02-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-g++
export SYSROOT=~/orangepi-build/toolchains/gcc-arm-11.2-2022.02-x86_64-aarch64-none-linux-gnu/aarch64-none-linux-gnu/sysroot

# 3. CMake 交叉编译配置
cat > aarch64-toolchain.cmake << 'EOF'
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER aarch64-none-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-none-linux-gnu-g++)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
EOF

# 4. 编译
mkdir build-cross && cd build-cross
cmake .. -DCMAKE_TOOLCHAIN_FILE=../aarch64-toolchain.cmake
make -j$(nproc)
```

### 15.2 远程部署脚本模板

```bash
#!/bin/bash
# deploy.sh — PC 编译后自动部署到 Orange Pi 4 Pro
OPI_IP="192.168.1.110"
OPI_USER="orangepi"
OPI_PATH="/home/orangepi/my-app"

echo "=== 交叉编译 ==="
cmake .. -DCMAKE_TOOLCHAIN_FILE=../aarch64-toolchain.cmake && make -j4

echo "=== 停止远程服务 ==="
ssh $OPI_USER@$OPI_IP "sudo systemctl stop my-app"

echo "=== 上传二进制 ==="
scp my-app $OPI_USER@$OPI_IP:$OPI_PATH/

echo "=== 启动服务 ==="
ssh $OPI_USER@$OPI_IP "sudo systemctl start my-app && sudo systemctl status my-app"

echo "=== 部署完成 ==="
```

### 15.3 SSH 免密部署配置

```bash
# 在 PC 上执行
ssh-keygen -t ed25519 -f ~/.ssh/opi4pro-deploy
ssh-copy-id -i ~/.ssh/opi4pro-deploy.pub orangepi@192.168.1.110

# 配置 SSH alias
cat >> ~/.ssh/config << 'EOF'
Host opi4pro
    HostName 192.168.1.110
    User orangepi
    IdentityFile ~/.ssh/opi4pro-deploy
    StrictHostKeyChecking no
EOF

# 现在可以直接：
# scp file opi4pro:~/  或  ssh opi4pro
```

### 15.4 rsync 增量同步开发

```bash
# 实时同步源码到开发板（适合解释型语言 Python/Node.js）
rsync -avz --exclude '.git' --exclude '__pycache__' \
    ~/my-project/ opi4pro:~/my-project/

# 自动同步脚本（文件变化时触发）
# 需要 inotify-tools：sudo apt install inotify-tools
while inotifywait -r -e modify,create,delete ~/my-project; do
    rsync -avz --exclude '.git' ~/my-project/ opi4pro:~/my-project/
    echo "$(date): synced"
done
```

### 15.5 VS Code Remote-SSH 开发

```bash
# 在 VS Code 中安装 Remote-SSH 插件
# .ssh/config 配置好 opi4pro host 后
# Ctrl+Shift+P → Remote-SSH: Connect to Host → opi4pro
# VS Code 自动在开发板上安装 vscode-server (aarch64)
# 直接在 VS Code 中编辑、终端、调试板载代码
```

### 15.6 GDB 远程调试

```bash
# 在开发板上安装 gdbserver
sudo apt install -y gdbserver

# 在开发板上启动
gdbserver :2345 ./my-app

# 在 PC 上用交叉 GDB 连接
aarch64-none-linux-gnu-gdb ./my-app
(gdb) target remote 192.168.1.110:2345
(gdb) continue
```

---

> 参考文档：Orange Pi 4 Pro 用户手册 v1.4（263页）
>
> 原理图文件位于本仓库 `schematics/` 目录（PCB V1.3.2, 2026-01-09）
>
> 本 SKILL 涵盖手册全部 263 页内容 + 实战项目、故障决策树、性能调优、安全加固 + 完整电路原理图与 PCB 版图。
