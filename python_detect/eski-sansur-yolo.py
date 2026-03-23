import cv2
import numpy as np
from mss import mss
from ultralytics import YOLO
import time

# --- ANA KOD ---
model = YOLO('yolov8L-best.pt')

with mss() as sct:
    monitor = sct.monitors[1]
    pTime = 0
    print("Blurlama ile tespit başlatıldı. Çıkmak için 'q' tuşuna basın.")
    
    while True:
        cTime = time.time()
        
        img_mss = sct.grab(monitor)
        img_np = np.array(img_mss)
        annotated_frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR) # Sonuçları işleyeceğimiz kare

        # YOLO ile tespit
        results = model(annotated_frame, stream=True, verbose=False)

        # Sonuçları işle
        for r in results:
            # Her bir tespit edilen kutu (box) için döngü
            for box in r.boxes:
                # 1. SINIRLAYICI KUTU KOORDİNATLARINI AL
                # xyxy formatında koordinatları al (x1, y1, x2, y2)
                # ve tam sayıya çevir
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                
                # 2. NESNENİN OLDUĞU BÖLGEYİ (ROI) KES
                # Koordinatların negatif olmadığından emin ol
                x1, y1 = max(0, x1), max(0, y1)
                nesne_bolgesi = annotated_frame[y1:y2, x1:x2]

                # Eğer bölge çok küçükse (hata almamak için) atla
                if nesne_bolgesi.shape[0] < 1 or nesne_bolgesi.shape[1] < 1:
                    continue

                # 3. KESİLEN BÖLGEYE BLUR UYGULA
                # ksize (kernel size) bulanıklık miktarını belirler.
                # (51, 51) gibi daha büyük tek sayılar daha fazla bulanıklık demektir.
                blurlu_bolge = cv2.GaussianBlur(nesne_bolgesi, (31, 31), 0)
                
                # 4. BLURLU BÖLGEYİ ORİJİNAL GÖRÜNTÜYE GERİ YERLEŞTİR
                annotated_frame[y1:y2, x1:x2] = blurlu_bolge

                # İsteğe bağlı: Blurlu alanın üstüne yine de kutu ve etiket çizebiliriz
                # cls: sınıf indeksi, conf: güven skoru
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{r.names[cls_id]} {conf:.2f}"
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


        # FPS değerini hesapla ve ekrana yazdır
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # Sonucu daha küçük bir pencerede göster
        scale_percent = 40
        width = int(annotated_frame.shape[1] * scale_percent / 100)
        height = int(annotated_frame.shape[0] * scale_percent / 100)
        resized_frame = cv2.resize(annotated_frame, (width, height), interpolation=cv2.INTER_AREA)
        cv2.imshow('YOLO Canlı Blurlama', resized_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()