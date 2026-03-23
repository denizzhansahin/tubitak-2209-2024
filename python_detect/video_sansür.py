import cv2
import numpy as np
from ultralytics import YOLO
import time
import os

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
model = YOLO('yolov8L-best.pt') # 'yolov8L-best.pt' yerine daha genel bir model kullandım, değiştirebilirsiniz.
output_resolution = (1920, 1080) # 1080p

# --- VİDEO İŞLEME AYARLARI ---
# İşlenecek video dosyasının yolu
video_dosya_yolu = '1.mp4' # LÜTFEN BU SATIRI KENDİ VİDEO DOSYANIZIN YOLUYLA GÜNCELLEYİN

# Videoyu okumak için bir VideoCapture nesnesi oluştur
cap = cv2.VideoCapture(video_dosya_yolu)

# Video başarıyla açılamazsa hata ver ve çık
if not cap.isOpened():
    print(f"Hata: '{video_dosya_yolu}' video dosyası açılamadı veya bulunamadı.")
    exit()

# --- VİDEO KAYIT AYARLARI ---
# Orijinal videonun FPS ve boyut bilgilerini al
video_fps = cap.get(cv2.CAP_PROP_FPS)

# Çıktı video dosyasının adını oluştur
dosya_adi, dosya_uzantisi = os.path.splitext(video_dosya_yolu)
output_video_yolu = f"{dosya_adi}_blurlu{dosya_uzantisi}"

fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec'i tanımla
video_writer = cv2.VideoWriter(output_video_yolu, fourcc, video_fps, output_resolution)

pTime = 0
print("Videodaki nesneleri blurlama işlemi başlatıldı.")
print(f"Video '{output_video_yolu}' dosyasına kaydediliyor. Çıkmak için 'q' tuşuna basın.")
    
while cap.isOpened():
    cTime = time.time()
    
    success, frame = cap.read()
    if not success:
        print("Video sonuna ulaşıldı veya okuma hatası.")
        break

    # YOLO ile tespit
    results = model(frame, stream=True, verbose=False, imgsz=320)

    # --- NESNELERİ BLURLAMA BÖLÜMÜ ---
    for r in results:
        for box in r.boxes:
            # Kutu koordinatlarını al
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            # Negatif koordinatları engelle
            x1, y1 = max(0, x1), max(0, y1)
            
            # Tespit edilen nesnenin olduğu bölgeyi kes
            nesne_bolgesi = frame[y1:y2, x1:x2]
            
            # Bölgenin geçerli bir boyuta sahip olduğundan emin ol
            if nesne_bolgesi.shape[0] < 1 or nesne_bolgesi.shape[1] < 1:
                continue

            # Gaussian Blur uygula (kernel boyutu tek sayı olmalı)
            blurlu_bolge = cv2.GaussianBlur(nesne_bolgesi, (51, 51), 0)
            
            # Blurlu bölgeyi ana görüntüdeki yerine geri koy
            frame[y1:y2, x1:x2] = blurlu_bolge

    # --- ÇIKTIYI 1080P'YE BOYUTLANDIRMA BÖLÜMÜ ---
    output_frame = resize_with_letterbox(frame, output_resolution)

    # Gerçek zamanlı FPS değerini hesapla ve son çıktı çerçevesinin üzerine yazdır
    if cTime > pTime:
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(output_frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    
    # 1080p boyutundaki nihai pencereyi göster
    cv2.imshow('YOLO - Blurlu Video', output_frame)
    
    # İşlenen kareyi video dosyasına yaz
    video_writer.write(output_frame)

    # 'q' tuşuna basıldığında döngüden çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
video_writer.release()
cv2.destroyAllWindows()
print(f"Kayıt tamamlandı ve '{output_video_yolu}' dosyasına kaydedildi.")
