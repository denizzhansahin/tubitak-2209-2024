import cv2
import os
import datetime
import sys

# --- 1. Video Yolunu Al ---
video_yolu = input("Lütfen video dosyasının yolunu girin: ")
rastgele_isim = input("Lütfen rastgele yazı yazın ama kısa olacak: ")

# Dosyanın var olup olmadığını kontrol et
if not os.path.exists(video_yolu):
    print("Hata: Belirtilen yolda video dosyası bulunamadı.")
    sys.exit() # Programı sonlandır

# Videoyu açmayı dene
video = cv2.VideoCapture(video_yolu)

# Videonun açılıp açılmadığını kontrol et
if not video.isOpened():
    print("Hata: Video dosyası açılamadı veya dosya formatı desteklenmiyor.")
else:
    # --- 2. Video Bilgilerini Göster (İsteğiniz Üzerine) ---
    toplam_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)

    print("\n" + "="*40)
    print("VİDEO BİLGİLERİ")
    print(f"-> Toplam Frame Sayısı: {toplam_frame}")
    print(f"-> Saniye Başına Kare (FPS): {fps:.2f}")
    print("="*40 + "\n")


    # --- 3. Kullanıcıdan Kayıt Aralığını Al ---
    try:
        kayit_araligi = int(input("Kaç frame'de bir kayıt alınsın? (Örn: 10, 25, 100): "))
        if kayit_araligi <= 0:
            print("Hata: Lütfen 0'dan büyük bir tamsayı girin.")
            kayit_araligi = None
    except ValueError:
        print("Hata: Lütfen geçerli bir sayı girin.")
        kayit_araligi = None

    if kayit_araligi:
        # Kayıt klasörünü oluştur
        kayit_klasoru = "zaman_damgali_frameler"
        if not os.path.exists(kayit_klasoru):
            os.makedirs(kayit_klasoru)
            print(f"'{kayit_klasoru}' adında bir klasör oluşturuldu.\n")

        frame_sayaci = 0
        kaydedilen_sayac = 0

        # --- 4. Frame'leri İşle ve Kaydet ---
        while frame_sayaci < toplam_frame:
            # İlerleme durumunu göster
            sys.stdout.write(f"\rİşleniyor: Frame {frame_sayaci}/{toplam_frame} ")
            sys.stdout.flush()

            basarili, frame = video.read()
            if not basarili:
                break

            # Belirtilen aralıkta bir frame ise kaydet
            if frame_sayaci % kayit_araligi == 0:
                # Zaman damgasını saniye cinsinden hesapla
                zaman_saniye = frame_sayaci / fps if fps > 0 else 0
                # Zaman damgasını saat:dakika:saniye.milisaniye formatına dönüştür
                zaman_damgasi_obj = datetime.timedelta(seconds=zaman_saniye)
                zaman_damgasi_str = str(zaman_damgasi_obj)

                # Dosya adlarında kullanılamayacak karakterleri (-) ile değiştir
                dosya_adi_zaman = zaman_damgasi_str.replace(':', '-')
                # Milisaniye kısmını 3 haneye sabitle
                if '.' in dosya_adi_zaman:
                    bolumler = dosya_adi_zaman.split('.')
                    bolumler[1] = bolumler[1][:3].ljust(3, '0')
                    dosya_adi_zaman = ".".join(bolumler)

                # Dosyayı kaydet
                dosya_adi = os.path.join(kayit_klasoru, f"{dosya_adi_zaman+rastgele_isim}.png")
                cv2.imwrite(dosya_adi, frame)
                kaydedilen_sayac += 1

            frame_sayaci += 1

        print("\n\n" + "="*40)
        print("İŞLEM TAMAMLANDI")
        print(f"Toplam {frame_sayaci} frame işlendi.")
        print(f"{kaydedilen_sayac} adet frame '{kayit_klasoru}' klasörüne kaydedildi.")
        print("="*40)

        # Videoyu serbest bırak
        video.release()