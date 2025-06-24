# 概述

## 2025/06/24 更新

华中师范大学的认证系统已经更改，此次代码更新用于适配新的认证系统。新的脚本为 `AutoCCNULogin.py`，源代码依旧保留，以供参考。

---

~~华中师范大学校园网认证使用了 [深澜(Srun)](https://srun.com/) 认证系统。~~本项目使用 Python 语言开发，可在任何支持 Python 环境的设备上使用命令行自动登录华中师范大学校园网认证系统。

此项目核心脚本会每隔一段时间（默认 30 秒）向百度的服务器发出请求，用于验证是否具有网络访问权限. 若无法访问百度，则立即尝试登录华中师范大学校园网认证系统.

# 使用说明

1. 本项目使用 Python3 语言开发，请确保系统已安装 Python3，并安装以下第三方库：`tenacity`, `requests`, `js2py`.
2. 将此项目的核心脚本 [AutoCCNUSrunLogin.py](https://raw.githubusercontent.com/K-JW/AutoCCNUSrunLogin/master/AutoCCNUSrunLogin.py) 下载保存到合适位置.
3. 修改脚本内的变量 `my_username` 与 `my_passwd`, 这两个变量分别指定了用户名和密码.
4. 直接运行脚本即可自动监测网络连接情况，并在检测到断网后尝试自动登录.

# 进阶用法

可以将脚本设为后台运行的守护进程，这样可以在启动系统后自动运行脚本，实现断网自动重连。下面简单介绍一下在 Linux 和 Windows 配置守护进程的方法。

## Linux

将可以正常运行的 `AutoCCNUSrunLogin.py` 脚本复制到 `/usr/bin` 目录内. 然后创建 `/etc/systemd/system/AutoCCNUSrunLogin.service` 文件, 并写入以下内容.

```
[Unit]
Description=AutoCCNUSrunLogin Service
ConditionPathExists=/usr/bin/AutoCCNUSrunLogin.py
After=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=30s
ExecStart=python3 /usr/bin/AutoCCNUSrunLogin.py
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

接下来依次运行以下命令完成配置:

```bash
# 重新加载配置文件
sudo systemctl daemon-reload
# 设置开机启动
sudo systemctl enable AutoCCNUSrunLogin
# 启动守护服务
sudo systemctl start AutoCCNUSrunLogin
```

## Windows

可以使用 [WinSW](https://github.com/winsw/winsw) 轻松配置.

---

## 参考项目

本项目在开发时参考了
[coffeehat/BIT-srun-login-script](https://github.com/coffeehat/BIT-srun-login-script) 的思路和代码. 在本项目中我们没有使用到 `Selenium` 框架, 因此更加稳定和轻量化.
