# 使用 Codex 在 Windows 本機協助安裝

[回首頁](../README.md)

依 [OpenAI 官方快速入門](https://learn.chatgpt.com/docs/quickstart) 設定 Codex，開啟下載解壓後的本機專案根目錄。請選可存取此 Windows 電腦檔案與終端機的工作流程；雲端任務不能代替這台電腦的桌面與 GPU 驗收。Codex 是選用安裝助手，日常使用程式不必保持它開啟。

貼上：

```text
請在目前這台 Windows 11 x64 協助安裝 ollama-VLM-win11。
先讀 README.md、VALIDATION.md 與 environment.lock.json。
我授權您在此專案建立 .venv、安裝固定版本且有 SHA256 的套件、下載 basic 圖文模型。
先確認 Windows build、x64、Python 3.14、Ollama、網路與至少 15GB 可用磁碟。
缺少系統工具時只採官方來源；密碼、SmartScreen 或額外權限由我核對處理，不關閉安全機制。
依 README 執行 py -3.14 scripts/restore_windows.py --profile basic --yes。
保留既有不符的 venv 與模型，不刪私人資料、不取消 hash/digest、不自動降版。
確認環境檢查與真實圖文測試成功後，協助開啟 run_windows.cmd。
再依 docs/WINDOWS_ACCEPTANCE.md 核對視窗、中文、縮放、逐框預覽、人工框與匯出。
回報實際版本、重新安裝與沿用項目、通過與未測項目；不要把 Mac 測試當成 Windows 驗證。
此版語音尚未提供，不以安裝 Whisper 宣稱已支援。這次不提交或上傳 GitHub。
```

想安裝九模型時，在基本方案成功後另行授權 full 方案、至少預留 30GB，再執行 `py -3.14 scripts/restore_windows.py --profile full --yes`。模型仍使用本機推論；Codex 工作使用其帳號所選服務，請不要貼上不適合分享的私人圖片或金鑰。
