import os
import urllib.request
from PIL import Image
import numpy as np
import torch

# Real-ESRGAN 官方實作使用的是 RealESRGANer + RRDBNet
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

WEIGHTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights')
WEIGHT_PATH = os.path.join(WEIGHTS_DIR, 'RealESRGAN_x4plus.pth')
WEIGHT_URL = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'

_upsampler = None

def _ensure_weights():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    if not os.path.exists(WEIGHT_PATH):
        print('Downloading RealESRGAN_x4plus.pth ...')
        urllib.request.urlretrieve(WEIGHT_URL, WEIGHT_PATH)
        print('Saved to', WEIGHT_PATH)

def _get_upsampler():
    global _upsampler
    if _upsampler is not None:
        return _upsampler

    _ensure_weights()

    # RRDBNet 結構（x4plus 對應的通道/層數）
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_block=23, num_grow_ch=32, scale=4)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 記憶體少時可把 tile 設大一點（例如 200~400），避免一次吃太多記憶體；0 代表不切 tile
    _upsampler = RealESRGANer(
        scale=4,
        model_path=WEIGHT_PATH,
        dni_weight=None,
        model=model,
        tile=0,                # 2GB 顯卡建議之後改成 200~400
        tile_pad=10,
        pre_pad=0,
        half=False,            # CPU 一律 False；GPU 可視需求改 True（需支援 FP16）
        device=device,
    )
    return _upsampler

def run_super_resolution(in_path: str, out_path: str):
    upsampler = _get_upsampler()
    img = Image.open(in_path).convert('RGB')
    img_np = np.array(img)
    # enhance 回傳 (output, face_enhance)；我們只需要 output
    output, _ = upsampler.enhance(img_np, outscale=4)
    Image.fromarray(output).save(out_path)

def run_denoise(in_path: str, out_path: str):
    import cv2
    img = cv2.imread(in_path)
    if img is None:
        raise RuntimeError('Failed to read image with OpenCV')
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 7, 7, 7, 21)
    cv2.imwrite(out_path, denoised)
