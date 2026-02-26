# 📈 股票价格聚类分析移动应用

将Python股票分析脚本转换为可在华为鸿蒙手机上运行的APP。

## 🎯 功能特点

- 📊 **多数据源支持**：腾讯、新浪、东方财富
- 🔍 **智能聚类分析**：使用KMeans算法识别支撑/压力位
- 📈 **可视化图表**：生成专业的股价分析图表
- 📱 **移动端优化**：适配手机屏幕，操作便捷
- 🌐 **多种部署方式**：支持APK安装、Pydroid运行、Web访问

## 📁 文件结构

```
stock_analyzer_app/
├── main.py                 # Kivy移动应用主程序
├── web_app.py             # Flask Web应用（适用于HarmonyOS Next）
├── buildozer.spec         # Buildozer打包配置
├── requirements.txt       # Python依赖列表
├── 部署说明.md            # 详细部署指南
├── 启动Web应用.bat       # Windows启动脚本
├── start_web.sh          # Linux/Mac启动脚本
└── README.md             # 本文件
```

## 🚀 快速开始

### 方案一：Web应用（推荐，支持所有鸿蒙版本）

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动Web服务器**
```bash
# Windows
启动Web应用.bat

# Linux/Mac
bash start_web.sh
```

3. **访问应用**
- 在电脑浏览器打开：`http://localhost:5000`
- 在鸿蒙手机浏览器打开：`http://<电脑IP>:5000`

### 方案二：Android APK（HarmonyOS 4.0及之前）

1. **安装Buildozer**
```bash
pip install buildozer
```

2. **构建APK**
```bash
buildozer android debug
```

3. **安装到手机**
```bash
adb install bin/stockanalyzer-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### 方案三：Pydroid 3直接运行

1. 在华为应用市场搜索并安装"Pydroid 3"
2. 打开Pydroid 3，安装所需库（pandas, numpy, matplotlib, scikit-learn, akshare, kivy）
3. 将`main.py`复制到手机
4. 在Pydroid 3中打开并运行

## 📱 使用说明

### 输入股票代码
- A股代码：如 `000001`（平安银行）、`600000`（浦发银行）
- 自动识别：系统会自动添加.SZ或.SH后缀

### 查看分析结果
1. **聚类中心**：显示5个支撑/压力位价格
2. **当前价格**：显示最新收盘价
3. **相对位置**：显示当前价格与各支撑/压力位的相对关系
4. **可视化图表**：直观的股价走势和支撑/压力线

## 🔧 系统要求

### 最低要求
- Python 3.8+
- 2GB RAM
- 网络连接（获取股票数据）

### 推荐配置
- Python 3.10+
- 4GB RAM
- 稳定的网络连接

## 📋 依赖库

```
kivy>=2.1.0          # 移动应用框架
pandas>=1.5.0        # 数据处理
numpy>=1.23.0        # 数值计算
matplotlib>=3.6.0    # 图表绘制
scikit-learn>=1.1.0  # 机器学习（KMeans）
akshare>=1.10.0      # 股票数据接口
flask>=2.0.0         # Web框架（Web应用方案）
```

## 🌟 界面预览

### Web应用界面
- 现代化UI设计
- 响应式布局，适配手机屏幕
- 实时加载动画
- 清晰的数据展示

### 移动应用界面
- 原生APP体验
- 流畅的交互操作
- 离线查看图表

## 🔍 技术原理

### 聚类分析算法
1. **数据获取**：从多个数据源获取股票历史数据
2. **特征提取**：提取收盘价作为聚类特征
3. **KMeans聚类**：使用KMeans算法将价格分为5个簇
4. **结果分析**：簇中心即为支撑/压力位

### 数据源
- **腾讯证券**：`stock_zh_a_hist_tx`
- **新浪财经**：`stock_zh_a_daily`
- **东方财富**：`stock_zh_a_hist`

## ⚠️ 注意事项

1. **网络权限**：应用需要访问网络获取股票数据
2. **数据安全**：股票数据来自公开接口，仅供学习参考
3. **投资建议**：本应用不构成投资建议，请谨慎决策
4. **性能考虑**：移动设备性能有限，大量数据分析可能需要时间

## 🐛 常见问题

### Q: 应用无法获取数据？
A: 检查网络连接，确认手机已连接互联网。

### Q: 图表无法显示？
A: 确保已授予存储权限，或尝试重新启动应用。

### Q: 打包失败？
A: 清理缓存后重试：`buildozer android clean`

### Q: HarmonyOS Next无法安装APK？
A: HarmonyOS Next不兼容安卓应用，请使用Web应用方案。

## 📞 技术支持

如遇到问题，可以：
1. 查看详细部署指南：`部署说明.md`
2. 参考Kivy官方文档：https://kivy.org/doc/stable/
3. 查阅AKShare文档：https://www.akshare.xyz/

## 📄 许可

本项目仅供学习交流使用，不构成投资建议。

## 🙏 致谢

- [Kivy](https://kivy.org/) - 跨平台Python框架
- [AKShare](https://www.akshare.xyz/) - 开源财经数据接口
- [scikit-learn](https://scikit-learn.org/) - 机器学习库

---

**祝您使用愉快！** 📈📱
