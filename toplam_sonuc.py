import os
from collections import defaultdict

# --- BU ALANI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Taramak istediğiniz ana klasörün yolu.
# Bu klasör ve içindeki tüm alt klasörler taranacaktır.
ana_klasor_yolu = "/Users/denizhan/Desktop/MakeleProjesi/gercek_zaman_damgali_frameler"

# Tanımlı görsel dosyası uzantıları (küçük harfle yazılmalı)
GORSEL_UZANTILARI = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def veri_seti_denetimi(root_dir):
    """
    Belirtilen bir kök dizini ve tüm alt dizinlerini tarayarak,
    görsel ve etiket dosyaları arasındaki eşleşmeleri ve eksiklikleri raporlar.
    """
    if not os.path.isdir(root_dir):
        print(f"HATA: Belirtilen yol bir klasör değil veya bulunamadı: {root_dir}")
        return

    print(f"'{root_dir}' ve alt klasörleri taranıyor...\n")

    # Dosya taban adlarına göre tam yolları saklamak için sözlükler
    gorsel_dosyalari = {}
    etiket_dosyalari = {}

    # Tüm klasör ağacını yürü
    for kok_dizin, _, dosyalar in os.walk(root_dir):
        for dosya_adi in dosyalar:
            # Dosyanın uzantısız adını (taban adı) ve uzantısını al
            taban_adi, uzanti = os.path.splitext(dosya_adi)
            uzanti = uzanti.lower() # Uzantıyı küçük harfe çevirerek karşılaştır

            tam_yol = os.path.join(kok_dizin, dosya_adi)

            if uzanti in GORSEL_UZANTILARI:
                # Eğer aynı taban adına sahip başka bir görsel varsa uyar
                if taban_adi in gorsel_dosyalari:
                    print(f"UYARI: Aynı isme sahip birden fazla görsel bulundu: '{taban_adi}'. Sadece biri kullanılacak.")
                gorsel_dosyalari[taban_adi] = tam_yol
            elif uzanti == ".txt":
                if taban_adi in etiket_dosyalari:
                    print(f"UYARI: Aynı isme sahip birden fazla etiket bulundu: '{taban_adi}'. Sadece biri kullanılacak.")
                etiket_dosyalari[taban_adi] = tam_yol
    
    # Kümeler oluşturarak karşılaştırmayı kolaylaştır
    gorsel_taban_adlari = set(gorsel_dosyalari.keys())
    etiket_taban_adlari = set(etiket_dosyalari.keys())

    # 1. Eşleşen Çiftler (her iki kümede de olanlar)
    eslesen_adlar = gorsel_taban_adlari.intersection(etiket_taban_adlari)
    eslesen_sayisi = len(eslesen_adlar)

    # 2. Yetim Görseller (görsellerde olup etiketlerde olmayanlar)
    yetim_gorsel_adlari = gorsel_taban_adlari.difference(etiket_taban_adlari)
    yetim_gorsel_sayisi = len(yetim_gorsel_adlari)

    # 3. Yetim Etiketler (etiketlerde olup görsellerde olmayanlar)
    yetim_etiket_adlari = etiket_taban_adlari.difference(gorsel_taban_adlari)
    yetim_etiket_sayisi = len(yetim_etiket_adlari)

    # Sonuçları Raporla
    print("--- VERİ SETİ KONTROL RAPORU ---")
    print(f"Toplam Bulunan Görsel Sayısı\t: {len(gorsel_taban_adlari)}")
    print(f"Toplam Bulunan Etiket (.txt) Sayısı\t: {len(etiket_taban_adlari)}")
    print("-" * 35)
    print(f"✅ Eşleşen Görsel/Etiket Çifti Sayısı\t: {eslesen_sayisi}")
    print(f"❌ Etiketi Olmayan Görsel Sayısı\t\t: {yetim_gorsel_sayisi}")
    print(f"❌ Görseli Olmayan Etiket Sayısı\t\t: {yetim_etiket_sayisi}")
    print("-----------------------------------")

    # İsteğe bağlı olarak yetim dosyaları listele
    if yetim_gorsel_sayisi > 0 or yetim_etiket_sayisi > 0:
        cevap = input("\n> Eşleşmeyen (yetim) dosyaların listesini görmek ister misiniz? (evet/hayır): ")
        if cevap.lower() == 'evet':
            if yetim_gorsel_sayisi > 0:
                print("\n--- Etiketi Olmayan Görseller ---")
                for ad in sorted(list(yetim_gorsel_adlari)):
                    print(gorsel_dosyalari[ad])
            
            if yetim_etiket_sayisi > 0:
                print("\n--- Görseli Olmayan Etiketler ---")
                for ad in sorted(list(yetim_etiket_adlari)):
                    print(etiket_dosyalari[ad])

if __name__ == "__main__":
    veri_seti_denetimi(ana_klasor_yolu)