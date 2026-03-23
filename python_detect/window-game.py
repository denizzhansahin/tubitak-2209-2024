import cv2
import numpy as np
from mss import mss
from ultralytics import YOLO
import time

# Görüntüyü en-boy oranını koruyarak yeniden boyutlandıran ve letterbox ekleyen fonksiyon
def resize_with_letterbox(image, target_size):
    """
    Görüntüyü hedef boyuta en-boy oranını koruyarak yeniden boyutlandırır.
    Gerekirse siyah bantlar (letterbox) ekler.
    
    :param image: Yeniden boyutlandırılacak görüntü (numpy array).
    :param target_size: Hedef boyut (width, height) tuple'ı.
    :return: Yeniden boyutlandırılmış görüntü.
    """
    target_w, target_h = target_size
    h, w, _ = image.shape
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Siyah bir tuval oluştur
    result = np.full((target_h, target_w, 3), 0, dtype=np.uint8)
    
    # Yeniden boyutlandırılmış görüntüyü tuvalin ortasına yerleştir
    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    result[top:top+new_h, left:left+new_w] = resized_image
    
    return result

# --- ANA KOD ---

# En hızlı model olan YOLOv8n'yi yüklüyoruz
model = YOLO('yolov8L-best.pt')

# Hedef çıktı çözünürlüğü
output_resolution = (1920, 1080) # 1080p

# Ekran görüntüsü almak için mss'i hazırlıyoruz
with mss() as sct:
    monitor = sct.monitors[1]

    pTime = 0
    print("Tam ekran tespiti başlatıldı. Çıktı penceresi 1080p olacak.")
    print(f"Taranan Alan: {monitor['width']}x{monitor['height']}")

    while True:
        cTime = time.time()
        
        img_mss = sct.grab(monitor)
        img_np = np.array(img_mss)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

        # YOLO ile tespit
        results = model(img_bgr, stream=True, verbose=False, imgsz=320)

        # Sonuçları işle ve kutuları çiz
        for r in results:
            annotated_frame = r.plot()

        # --- İŞLENMİŞ GÖRÜNTÜYÜ 1080P'YE ÇEVİRME ---
        # Görüntüyü en-boy oranını koruyarak 1080p'ye boyutlandır
        output_frame = resize_with_letterbox(annotated_frame, output_resolution)

        # FPS değerini hesapla ve 1080p tuvalin üzerine yazdır
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output_frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # 1080p boyutundaki pencereyi göster
        cv2.imshow('YOLO Canlı Ekran Tespiti (1080p)', output_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print("Tespit durduruldu.")