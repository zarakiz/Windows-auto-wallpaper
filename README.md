(全程使用gemini製作)
# 📸 Unsplash 桌布自動更換器
[![下載 Windows 版本](https://img.shields.io/badge/下載-Windows%20版本-blue?style=for-the-badge&logo=windows)](https://github.com/zarakiz/Windows-auto-wallpaper/releases/tag/v1.0.0)

一個基於 Python 開發的輕量級 Windows 桌布自動換圖工具。利用 Unsplash API 獲取高品質 4K 圖片，並支援開機自啟動與後台執行。

## ✨ 功能特色
- **多樣化主題**：支援動漫、賽博龐克、自然風景等 14 種風格選擇。
- **高畫質體驗**：強制抓取橫向 (Landscape) 高清大圖。
- **後台運行**：關閉視窗後自動縮小至系統托盤（System Tray）。
- **開機自啟**：內建自啟動管理功能。
- **重複過濾**：自動記錄已使用的圖片 ID，避免短期內出現重複桌布。

## 🚀 快速開始

### 1. 取得 Unsplash API Key
本程式需要您自己的 API Key 才能運行：
1. 前往 [Unsplash Developers](https://unsplash.com/developers) 註冊帳號。
2. 建立一個新 Application，取得 **Access Key**。

### 2. 安裝環境
確保您的電腦已安裝 Python 3.8+，然後運行：
```bash
pip install -r requirements.txt
