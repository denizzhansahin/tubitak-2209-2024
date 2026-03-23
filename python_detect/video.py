import cv2
import numpy as np
from ultralytics import YOLO
import time
import os # os kütüphanesini içe aktar

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
    # Görüntünün boyutlarını al
    h, w, _ = image.shape
    
    # En-boy oranını koruyarak ölçeklendirme faktörünü hesapla
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    # Görüntüyü yeni boyutlara yeniden boyutlandır
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Siyah bir tuval (letterbox) oluştur
    result = np.full((target_h, target_w, 3), 0, dtype=np.uint8)
    
    # Yeniden boyutlandırılmış görüntüyü tuvalin ortasına yerleştir
    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    result[top:top+new_h, left:left+new_w] = resized_image
    
    return result

# --- ANA KOD ---

# Kullanılacak YOLO modelini yükle
model = YOLO('yolov8L-best.pt') # 'yolov8L-best.pt' yerine daha genel bir model kullandım, değiştirebilirsiniz.

# İşlenecek video dosyasının yolu
video_dosya_yolu = '1.mp4' # LÜTFEN BU SATIRI KENDİ VİDEO DOSYANIZIN YOLUYLA GÜNCELLEYİN

# Videoyu okumak için bir VideoCapture nesnesi oluştur
cap = cv2.VideoCapture(video_dosya_yolu)

# Video başarıyla açılamazsa hata ver ve çık
if not cap.isOpened():
    print(f"Hata: '{video_dosya_yolu}' video dosyası açılamadı veya bulunamadı.")
    exit()

# Orijinal videonun FPS değerini al
video_fps = cap.get(cv2.CAP_PROP_FPS)

# Çıktı video dosyasının adını oluştur
dosya_adi, dosya_uzantisi = os.path.splitext(video_dosya_yolu)
output_video_yolu = f"{dosya_adi}_video{dosya_uzantisi}"

# Hedef çıktı çözünürlüğü
output_resolution = (1920, 1080) # 1080p

# Video yazmak için VideoWriter nesnesi oluştur
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec'i tanımla
video_writer = cv2.VideoWriter(output_video_yolu, fourcc, video_fps, output_resolution)

# FPS hesaplaması için zaman değişkeni
pTime = 0

print("Video tespiti başlatıldı. Çıktı penceresi 1080p olacak.")
print(f"İşlenmiş video şu yola kaydedilecek: {output_video_yolu}")

# Video açık olduğu sürece döngüye gir
while cap.isOpened():
    # Videodan bir kare oku
    success, frame = cap.read()

    if success:
        cTime = time.time()

        # YOLO ile kare üzerinde tespit yap
        # stream=True daha verimli bellek kullanımı sağlar
        results = model(frame, stream=True, verbose=False, imgsz=640)

        # Sonuçları işle ve tespit kutularını kare üzerine çiz
        for r in results:
            annotated_frame = r.plot()

        # --- İŞLENMİŞ GÖRÜNTÜYÜ 1080P'YE ÇEVİRME ---
        # Görüntüyü en-boy oranını koruyarak 1080p'ye boyutlandır
        output_frame = resize_with_letterbox(annotated_frame, output_resolution)

        # FPS değerini hesapla ve 1080p tuvalin üzerine yazdır
        # cTime ve pTime sıfırdan farklıysa FPS hesapla
        if cTime - pTime > 0:
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(output_frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # 1080p boyutundaki pencereyi göster
        cv2.imshow('YOLO Video Tespiti (1080p)', output_frame)
        
        # İşlenen kareyi video dosyasına yaz
        video_writer.write(output_frame)

        # 'q' tuşuna basıldığında döngüyü kır ve çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        # Video bittiğinde döngüden çık
        print("Video sonuna ulaşıldı.")
        break

# Video yakalama ve yazma nesnelerini serbest bırak
cap.release()
video_writer.release()
# Tüm OpenCV pencerelerini kapat
cv2.destroyAllWindows()
print("Tespit durduruldu.")

