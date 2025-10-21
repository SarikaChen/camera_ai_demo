# Camera AI Demo (Super-Resolution + Denoise)

這是一個 **三天面試衝刺** 用的小專案：
- 上傳一張照片 → 後端進行 **超分辨率 (Real-ESRGAN)** 或 **去雜訊 (OpenCV)** → 顯示 Before/After
- 架構：Flask (Backend) + HTML/JS (Frontend)
- 第一次執行會自動下載 `RealESRGAN_x4plus.pth` 權重

## 一鍵啟動
```bash
# 1) 建立虛擬環境 (建議)
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 2) 安裝依賴 (首次會較久，含 PyTorch & 模型)
pip install --upgrade pip
pip install -r requirements.txt

# 3) 執行
python app.py
# 瀏覽 http://127.0.0.1:5000
```

> **注意**
> - CPU 也能跑，只是 Real-ESRGAN 會較慢；若有 NVIDIA GPU + CUDA，速度更快。
> - 首次啟動會自動下載模型到 `weights/RealESRGAN_x4plus.pth`。

## 專案結構
```
camera_ai_demo/
├─ app.py
├─ inference.py
├─ requirements.txt
├─ README.md
├─ static/
│  └─ style.css
├─ templates/
│  └─ index.html
├─ uploads/
├─ results/
└─ weights/            # 會自動放置 RealESRGAN_x4plus.pth
```

## 功能說明
- **Super-Resolution (x4)：** 使用 Real-ESRGAN 將影像放大 & 提升細節。
- **Denoise：** 使用 OpenCV 的 fastNlMeansDenoisingColored 去雜訊。

## 面試講稿要點 (可直接背)
1. 這個 Demo 對應職缺的「Generative AI for Camera Productivity」：針對模糊/雜訊痛點做落地示範。
2. 架構採用 Flask + REST 風格端點，前端以 H5/JS 上傳檔案、後端回傳結果路徑，實作簡潔且可擴充。
3. 模型選擇 Real-ESRGAN (生成式架構)，兼顧畫質與部署可行性；去雜訊採傳統 CV 方法，利於對比與解釋。
4. 若要產品化，我會：
   - 做「即時預覽」(前端 WebAssembly 或行動端原生加速)
   - 模型壓縮 (Quantization/Pruning) 與 TFLite/TensorRT 導入
   - 加上資料庫紀錄與 A/B 測試，評估不同模型/參數對體驗的影響。

## 常見問題
- **Q: 首次啟動卡很久？** 安裝 PyTorch/下載模型需要時間，屬正常現象。
- **Q: 沒有 GPU 會失敗嗎？** 不會，會自動 fallback 到 CPU (較慢)。
- **Q: 權重放哪裡？** 自動下載至 `weights/RealESRGAN_x4plus.pth`。