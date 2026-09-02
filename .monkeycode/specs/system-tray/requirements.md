# Requirements Document

## Introduction

为 AIwallpaper 增加 Windows 系统托盘后台运行能力。用户点击主窗口关闭或最小化后，程序隐藏到通知区域继续运行；通过托盘图标可恢复主界面、从本地优先随机更换壁纸，或彻底退出。开机自启动时默认静默进入托盘。该能力与现有单实例互斥、自定义图标、随机在线壁纸功能协同工作。

## Glossary

- **System**: AIwallpaper 桌面应用程序
- **Tray Icon**: 显示在 Windows 通知区域的程序图标
- **Main Window**: 程序主界面窗口
- **Restore**: 将主窗口从隐藏状态重新显示到前台
- **Quit**: 结束进程并清理临时文件
- **Autostart**: 现有的开机自启动设置
- **Launch Mode**: 启动方式，分为手动启动与开机自启动

## Requirements

### Requirement 1

**User Story:** AS 桌面用户, I want 关闭或最小化主窗口后程序仍在托盘运行, so that 我不必始终占用任务栏即可随时换壁纸

#### Acceptance Criteria

1. WHEN 用户点击主窗口关闭按钮, the System SHALL 隐藏 Main Window 并在通知区域保留 Tray Icon
2. WHEN 用户点击主窗口最小化按钮, the System SHALL 隐藏 Main Window 并在通知区域保留 Tray Icon
3. WHILE Main Window 处于隐藏状态, the System SHALL 继续运行天气刷新、时钟更新与已启动的后台线程
4. IF 创建 Tray Icon 失败, the System SHALL 保持 Main Window 可见并提示用户托盘不可用

### Requirement 2

**User Story:** AS 桌面用户, I want 通过托盘图标恢复或退出程序, so that 我能快速回到主界面或彻底关闭

#### Acceptance Criteria

1. WHEN 用户左键单击 Tray Icon, the System SHALL Restore Main Window 并将其置于前台
2. WHEN 用户右键单击 Tray Icon, the System SHALL 显示包含「显示主界面」「随机壁纸」「退出」的上下文菜单
3. WHEN 用户选择「显示主界面」, the System SHALL Restore Main Window 并将其置于前台
4. WHEN 用户选择「退出」, the System SHALL 移除 Tray Icon、清理临时目录并结束进程
5. IF Main Window 已可见, WHEN 用户再次请求 Restore, the System SHALL 将 Main Window 置于前台

### Requirement 3

**User Story:** AS 桌面用户, I want 从托盘一键更换壁纸, so that 无需打开主窗口也能换一张

#### Acceptance Criteria

1. WHEN 用户在托盘菜单选择「随机壁纸」且本地壁纸文件夹中存在至少一张受支持图片, the System SHALL 从本地壁纸列表中随机选择一张并设置为桌面壁纸
2. WHEN 用户在托盘菜单选择「随机壁纸」且本地壁纸文件夹为空或不存在, the System SHALL 从当前在线分类中随机选择一张并设置为桌面壁纸
3. WHILE 随机壁纸正在下载或设置, the System SHALL 忽略重复的「随机壁纸」请求
4. IF 随机壁纸设置失败, the System SHALL 通过系统气泡通知告知失败原因

### Requirement 4

**User Story:** AS 使用开机自启动的用户, I want 启动后直接进入托盘, so that 开机后不弹出主窗口

#### Acceptance Criteria

1. WHEN 用户通过开机自启动启动 System, the System SHALL 完成初始化后直接显示 Tray Icon 并保持 Main Window 隐藏
2. WHEN 用户手动启动 System, the System SHALL 显示 Main Window 与 Tray Icon
3. WHILE System 已在运行, WHEN 用户再次启动 System, the System SHALL 激活已有实例的主窗口并结束新进程

### Requirement 5

**User Story:** AS 桌面用户, I want 托盘图标与现有自定义图标设置保持一致, so that 托盘外观与窗口图标统一

#### Acceptance Criteria

1. WHEN System 创建 Tray Icon, the System SHALL 使用当前窗口图标对应的图像
2. WHEN 用户在设置中应用新的自定义图标, the System SHALL 更新 Tray Icon 为新图像
3. IF 自定义图标文件不存在或无法读取, the System SHALL 使用默认图标创建 Tray Icon
