
<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_supervisor?name=astrbot_plugin_supervisor&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_supervisor

_✨ 赛博监工 ✨_  

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Zhalslar-blue)](https://github.com/Zhalslar)

</div>

## 🤝 介绍

赛博监工，检测到某人水群，就提醒他滚去干活

## 📦 安装

在astrbot的插件市场搜索astrbot_plugin_supervisor，点击安装即可

## ⚙️ 配置

### 插件配置

请在astrbot面板配置，插件管理 -> astrbot_plugin_supervisor -> 操作 -> 插件配置：

### Docker 部署配置

如果您是 Docker 部署，请务必将消息平台容器和AstrBot挂载容器到同一个文件夹，否则消息平台将无法解析文件路径。

示例挂载方式(NapCat)：

- 对 **AstrBot**：`/vol3/1000/dockerSharedFolder -> /app/sharedFolder`
- 对 **NapCat**：`/vol3/1000/dockerSharedFolder -> /app/sharedFolder`

## 使用说明

|     命令      |      说明       |
|:-------------:|:-----------------------------:|
| /监督@某人      | 将某人加进监督名单里  |
| /解除监督@某人  | 将某人移出监督名单里   |

## 👥 贡献指南

- 🌟 Star 这个项目！（点右上角的星星，感谢支持！）
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 📌 注意事项

- 想第一时间得到反馈的可以来作者的插件反馈群（QQ群）：460973561（不点star不给进）
