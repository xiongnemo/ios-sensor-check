# Sensor Check

一个把 iOS 应用能拿到的传感器和硬件输入都放在一屏上的小应用：每一项一行，实时数值（每秒刷新约 10 次），
以及它在这台设备上的状态——可用（available）、这台设备没有（not available on this device）、没有权限（no permission）、
等待数据（waiting for data）。每一节下面写着数值来自哪个 API。

最早是为了测 Redmi K40（alioth）上的 iOS 16.5 移植而写的：那里有的传感器靠移植自己的垫片工作，有的还没有。
普通 iPhone 上它就是一个普通应用。

- 环境光（lux）：私有的 IOHIDEventSystemClient，匹配苹果厂商页 0xff00、用途 4 的 HID 服务，读事件（类型 12）的
  Illuminance / Level；没有事件时用 `IOHIDServiceClientCopyEvent` 去问；都没有时退回 K40 移植自己的
  `sysctl kern.hakios.als_millilux`（标明是退路）。数值后面写着它来自哪里。另有屏幕亮度
- 距离传感器
- 加速度计、陀螺仪、磁力计（原始值）、设备运动（姿态、重力、用户加速度、校准后的磁场和精度）
- 气压计 / 相对高度、计步器（启动以来的步数）、运动状态
- 指南针（磁北、真北、精度）、定位（经纬度、精度、海拔、速度、授权状态）
- 电池电量和状态、温度状态、低电量模式
- 麦克风电平（平均 / 峰值 dBFS）
- 所有摄像头（类型、前后、名字）和摄像头权限，不拍照
- 蓝牙状态和授权
- 设备方向、音量键（音量和变化次数）
- 屏幕（最高帧率、分辨率、缩放）和 CADisplayLink 实测的帧率
- 多点触控：一块触摸板，显示现在几根手指、最多几根；有 3D Touch 时显示压力
- 触感反馈：轻 / 中 / 重、通知、振动的按钮，以及 Core Haptics 说这台设备有没有触感引擎

应用到前台时启动全部传感器，进入后台就全部停掉；每一项都先问有没有、有没有权限再用，缺了不会崩溃。

- 包名：`com.anzupop.com.ios.sensorcheck`
- 最低 iOS 15.0，iPhone，竖屏
- 只用 Objective-C 和系统框架，一个 `main.m`，没有 storyboard、asset catalog
- 图标由 `mkicon.py` 生成（纯 Python）

## 环境光和签名

环境光没有公开 API。应用要有 `com.apple.private.hid.client.event-monitor` 这项授权，才看得到光线传感器的 HID 服务。
所以 `build.sh` 在有 `ldid` 的时候，用 `Entitlements.plist` 给程序签上这一项（K40 移植不校验苹果的签名）；
没有 `ldid`（比如 macOS 上）就保留链接器给的签名。装到真 iPhone 上时会被重新签名，这项授权会被去掉，
光线那一行就会写着看不到服务，其他各项不受影响。

## 编译

产物是 `build/SensorCheck.ipa`，没有苹果签名，只适合不校验签名的系统，比如上面那个移植，或者自己重新签名后安装。

```sh
./build.sh                                                   # macOS，用 Xcode
CC=xnu-clang SDK=$THEOS/sdks/iPhoneOS16.5.sdk ./build.sh     # Linux / WSL，需要能链接 iOS 的 clang + ld64
```

每次推送 GitHub Actions 都会在 macOS 上编一次（也可以手动运行 `build`），IPA 作为运行的产物保存。

## 许可

MIT，见 `LICENSE`。

## 文件

| 文件 | 作用 |
|---|---|
| `main.m` | 整个应用（表格、各个传感器、触摸板、触感按钮） |
| `Info.plist` | 包名、版本、图标、各项权限说明 |
| `Entitlements.plist` | 用 `ldid` 签名时加上的授权（光线传感器的 HID 事件） |
| `mkicon.py` | 生成 60×60 @2x / @3x 图标 |
| `build.sh` | 编译并打包成 IPA |
