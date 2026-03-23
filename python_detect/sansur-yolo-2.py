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
model = YOLO('yyolov8L-best.pt')
output_resolution = (1920, 1080) # 1080p

with mss() as sct:
    monitor = sct.monitors[1]
    pTime = 0
    print("Blurlama ve 1080p çıktı ile tespit başlatıldı. Çıkmak için 'q' tuşuna basın.")
    
    while True:
        cTime = time.time()
        
        img_mss = sct.grab(monitor)
        img_np = np.array(img_mss)
        annotated_frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

        # YOLO ile tespit
        results = model(annotated_frame, stream=True, verbose=False)

        # --- NESNELERİ BLURLAMA BÖLÜMÜ ---
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1 = max(0, x1), max(0, y1)
                
                nesne_bolgesi = annotated_frame[y1:y2, x1:x2]
                if nesne_bolgesi.shape[0] < 1 or nesne_bolgesi.shape[1] < 1:
                    continue

                # Gaussian Blur uygula
                blurlu_bolge = cv2.GaussianBlur(nesne_bolgesi, (41, 41), 0)
                
                # Blurlu bölgeyi geri yerine koy
                annotated_frame[y1:y2, x1:x2] = blurlu_bolge

        # --- ÇIKTIYI 1080P'YE BOYUTLANDIRMA BÖLÜMÜ ---
        # Blurlama işlemi bitmiş kareyi en-boy oranını koruyarak 1080p'ye boyutlandır
        output_frame = resize_with_letterbox(annotated_frame, output_resolution)

        # FPS değerini hesapla ve son çıktı çerçevesinin üzerine yazdır
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output_frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # 1080p boyutundaki nihai pencereyi göster
        cv2.imshow('YOLO - Blurlu ve 1080p Cikti', output_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()