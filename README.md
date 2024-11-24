<div align="center">

# AndUbeat -Controller-
使用 `adb shell getevent` 记录 Android 设备触屏事件并模拟Jubeat面板的虚拟控制器.

[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green.svg)](https://github.com/Inter1006/Handheld-Embedded-Emulator-Collection/blob/main/LICENSE)<br />
![ver](https://img.shields.io/badge/Lastest-Beta_0.90-blue.svg)<br />

</div>

## 📝关于这个项目
本项目通过ADB有线连接获取来自安卓设备的触摸事件,并将其映射为键盘的按键输入。<br />
您仅需进行一些简单的配置,就可以令其工作。<br />
注:项目灵感和部分代码来自 [ERR0RPR0MPT\maimai-android-touch-panel](https://github.com/ERR0RPR0MPT/maimai-android-touch-panel)

## 📥如何安装?
声明:本教程不提供游戏本体及其安装方法,请支持正版游戏。<br />
备注:下文中的"AUC"均为本项目名称的简写<br />

1. 安装Python 3.11.0 [点击直达官网](https://www.python.org/downloads/release/python-3110/)<br />
   安装 ADB 调试工具, 并将其安装路径添加到系统环境变量里面<br />
2. 从[发布页](https://github.com/Inter1006/AndUbeat-Controller-/releases)下载最新的AUC程序压缩包<br />
3. 解压压缩包到任意位置<br />
4. 根据注释或 详细教程 填写好 `config.yaml` 中的内容(或使用成品config文件替换)<br />
5. 双击文件夹中的 `install.bat` 安装依赖<br />
6. 安卓设备打开USB调试,用数据线连接电脑,将电脑画面串流至设备(分辨率设为1360x768,竖屏)<br />
7. 待依赖安装好后,右键单击文件夹内的 `start.bat` 并单击 `以管理员身份运行`<br />
8. 搞定啦! Have Fun！

## 🛠️配置文件[config.yaml]的详细使用教程

1. 启动游戏，使用任意串流工具将画面串流至安卓设备(分辨率建议为竖屏,1360x768),然后截图
2. 打开任意P图工具, 将游戏截图中的4×4(共计16个)方块分别用相同大小,不同颜色的正方形覆盖<br />
   (颜色RGB数据和映射的按键可在 `config.yaml` 的 `exp_image_dict`部分找到)<br />
   将编辑好的图片放到程序 `controllerdata` 目录下并取名 `jubeat_monitor.png`.
3. 编辑配置文件, 修改 `exp_image_dict` 配置, 将各区块对应的 RGB 通道颜色值改为刚P的图的对应区块颜色值(
   一般不用改默认就行)
7. 先将实际屏幕大小填入文件内 `ANDROID_ABS_MONITOR_SIZE` 配置, 打开终端, 运行 `adb shell getevent -l`, 点一下屏幕的最右下角的位置,
   在终端获取该次点击得到的 `ABS_MT_POSITION_X` 和 `ABS_MT_POSITION_Y` 的数值, 把十六进制转换到十进制,
   将得到的数据填入到 `ANDROID_ABS_INPUT_SIZE` 配置
8. Android 设备充电口朝下一般为屏幕的正向, 如需反向屏幕游玩可将配置 `ANDROID_REVERSE_MONITOR` 改为 true
9. 编辑配置文件, 按文件内注释修改多个配置
12. 电脑画面可使用 `IddSampleDriver`, `Sunshine` 和 `Moonlight` (提一嘴:想要竖屏串流必须使用支持竖屏的 Sunshine Nightly
    版本, [Releases 地址](https://github.com/LizardByte/Sunshine/releases/nightly-dev))
    或者延迟较大但比较方便的 `spacedesk` 等软件串流到 Android
    设备,
    详细过程请自行寻找, 不在本篇讨论范围之内

## ❗注意事项
  本项目使用了效率较为低下且抽象的方案(Python+读图+串流), 存在延迟, 仅供娱乐。<br />
  后续维护......随缘吧<br />
  PS:XiaomiPad6SPro用户可以使用作者做好的成品config<br />
  呐,如果有问题请一定要用issue或其它方式给我反馈啊~

## ℹ关于
作者:
<table>
  <tr>
    <td align="center"><a href="https://github.com/Inter1006"><img src="https://github.com/Inter1006/PenPointOS_Vbox/blob/Readme_Files/b_fa517952f054ca8c99a234cc1b50b50b.jpg" width="100px;" alt=""/><br /><sub><b>INTER_INIT</b></sub></a><br /></td>
  </tr>
</table>

[作者的b站个人主页](https://space.bilibili.com/1756824708)<br />
qq交流群:**981893945** 欢迎来玩

## 🤝友站链接
[351workshop官网](https://www.351workshop.top/)<br />
👆点击戳一下WNT351<br />
[樱之谷-MC服务器](www.sakuravalley.xyz)<br />
👆点击戳一下Axium. 钰<br />
[HCA-Project](https://github.com/Inter1006/Handheld-Embedded-Emulator-Collection/tree/main)<br />
👆点击去探索手持设备的过去,现在和将来
