# Windows 移植驗證紀錄

日期：2026-10-19。來源：Mac 專案 `da53224`，此資料夾為獨立 Windows 專案，不修改 Mac 原版。

## 已完成

- 只複製必要程式、素材、測試與 6 張已授權公開的示範圖；沒有複製 Mac `.venv`、模型、私人對話、錄音或 Git 歷史。機器人視角圖片未納入。
- 新增 Windows 11 x64／CPython 3.14 安裝器、基本／九模型重建器、日常啟動及 Windows 環境檢查；`.cmd` 使用 CRLF 並保留錯誤畫面。
- Windows 六個固定版本 wheel 已從官方 PyPI 實際下載，以 pip 的 Windows x64／Python 3.14 相容性規則解析並強制 SHA256 校驗；另逐檔重新計算 hash，均一致。這不是在 Mac 載入 Windows DLL。
- 在目前 Mac 主機，用已有的 Python 3.11／Qt 環境執行 Windows 副本的 236 項回歸：通過。包括新安裝器的環境保留、官方 hashed wheel 參數、服務不重啟、自己啟動失敗的程序清理、模型 digest 不符拒絕、未同意不下載等。
- Ruff 與格式檢查通過；共用圖文程式在 Mac 本機模型測試成功，不視為 Windows 模型驗證。
- 語音未完成 Windows 後端，介面與提示詞明確標示限制；設定 Windows 中文字型備援，仍須驗證真實 DPI／字型。

## Windows 原生自動化

已加入 [GitHub Actions](https://github.com/orinaisl33-max/ollama-VLM-win11/actions)：Windows runner、Python 3.14 x64、新建 venv、hash 套件安裝、pip／Qt 檢查及回歸測試。實際結果請以該提交的 workflow 為準，初次上傳前尚無結果，不先宣稱通過。

GitHub Windows runner 可能是 Windows Server；即使通過，也不等同 Windows 11 實機桌面、GPU、模型下載／推論及匯出人工驗收。CI 不下載模型、不錄音。

首輪 Windows CI 成功建立 venv、安裝校驗套件並通過 pip／Qt／Ruff；236 項測試中發現 2 個程序啟動失敗的計時器順序問題，以及 4 個測試 SQLite 連線未明確關閉而使暫存檔鎖住的錯誤。已把逾時計時器移到程序啟動前，並明確關閉測試連線，保留全部測試重新執行；未以跳過測試處理。

## 仍待驗收

依 [Windows 實機驗收表](docs/WINDOWS_ACCEPTANCE.md) 完成新機、Qt DLL、Ollama 驅動、模型、真實視窗、縮放、逐框預覽、匯出與紀錄操作。沒有 Windows 實機結果前，不對使用者宣稱全功能已驗證或百分之百可安裝。
