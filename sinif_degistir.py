import os

# --- BU ALANLARI KENDİ BİLGİLERİNİZE GÖRE DİKKATLİCE DÜZENLEYİN ---

# 1. Asıl (hedef) veri setinin class.txt dosyasının yolu
hedef_class_dosyasi_yolu = "/Users/denizhan/Desktop/MakeleProjesi/class.txt"

# 2. Güncellenecek (kaynak) veri setinin class.txt dosyasının yolu
kaynak_class_dosyasi_yolu = "/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/class.txt"

# 3. İçindeki .txt'lerin güncelleneceği etiket klasörünün yolu
guncellenecek_etiketler_klasoru = "/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/Grup_1"

# 4. Hangi etiketin hangisine dönüşeceğini belirten eşleştirme haritası
# ÖNEMLİ: Buradaki isimlerin class.txt dosyalarınızdaki isimlerle BİREBİR AYNI olduğundan emin olun!
etiket_eslestirme_haritasi = {
    "atesli_silah": "firearm",
    "kesici_alet": "cutting_tool",
    "kilic": "cutting_tool",
    "patlayici": "explosive",
    "kan": "blood",
    "ceset": "dead_body"
}

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def siniflari_oku(dosya_yolu):
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            # GÜNCELLEME: Görünmez \u2060 karakterini ve diğer boşlukları temizle
            return [line.replace('\u2060', '').strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return None

def on_kontrol_yap():
    """Dosyaları değiştirmeden önce bir kontrol ve raporlama yapar."""
    print("--- ÖN KONTROL BAŞLATILDI ---")
    
    hedef_siniflar = siniflari_oku(hedef_class_dosyasi_yolu)
    kaynak_siniflar = siniflari_oku(kaynak_class_dosyasi_yolu)
    
    # Dosya varlık kontrolü
    if hedef_siniflar is None:
        print(f"❌ HATA: Hedef sınıf dosyası bulunamadı! -> {hedef_class_dosyasi_yolu}")
        return False, None, None, None
    if kaynak_siniflar is None:
        print(f"❌ HATA: Kaynak sınıf dosyası bulunamadı! -> {kaynak_class_dosyasi_yolu}")
        return False, None, None, None
    if not os.path.isdir(guncellenecek_etiketler_klasoru):
        print(f"❌ HATA: Güncellenecek etiket klasörü bulunamadı! -> {guncellenecek_etiketler_klasoru}")
        return False, None, None, None
        
    print(f"\n✅ Hedef Sınıf Dosyası Okundu ve Temizlendi ({len(hedef_siniflar)} etiket):")
    print(hedef_siniflar)
    
    print(f"\n✅ Kaynak Sınıf Dosyası Okundu ({len(kaynak_siniflar)} etiket):")
    print(kaynak_siniflar)

    # İndeks haritasını oluştur
    index_haritasi = {}
    basarisiz_etiketler = []
    
    for kaynak_isim, hedef_isim in etiket_eslestirme_haritasi.items():
        if kaynak_isim in kaynak_siniflar and hedef_isim in hedef_siniflar:
            eski_index = kaynak_siniflar.index(kaynak_isim)
            yeni_index = hedef_siniflar.index(hedef_isim)
            index_haritasi[eski_index] = yeni_index
        else:
            basarisiz_etiketler.append(f"'{kaynak_isim}' -> '{hedef_isim}'")

    print("\n--- İndeks Eşleştirme Raporu ---")
    if not index_haritasi:
        print("❌ HATA: Hiçbir geçerli etiket eşleşmesi yapılamadı.")
    else:
        for eski, yeni in index_haritasi.items():
            print(f"  - EŞLEŞTİRİLDİ: '{kaynak_siniflar[eski]}' ({eski}) -> '{hedef_siniflar[yeni]}' ({yeni})")

    if basarisiz_etiketler:
        print("\n❌ UYARI: Aşağıdaki etiketler ilgili class.txt dosyalarında bulunamadı:")
        for etiket in basarisiz_etiketler:
            print(f"  - {etiket}")
        print("   (Yazım hatası, büyük-küçük harf veya boşluk karakteri olup olmadığını kontrol edin.)")

    if not index_haritasi:
        return False, None, None, None

    print("\n--- ÖN KONTROL BAŞARILI ---")
    return True, index_haritasi, kaynak_siniflar, hedef_siniflar

def etiketleri_guncelle(index_haritasi):
    """Ön kontrol başarılı olduktan sonra etiket dosyalarını günceller."""
    onay = input(f"\n>> RAPOR YUKARIDADIR. '{guncellenecek_etiketler_klasoru}' içindeki dosyalar güncellenecektir.\n"
                 ">> Eşleşmeyen etiketlere dokunulmayacaktır. Onaylıyor musunuz? (evet/hayır): ")
    if onay.lower() != 'evet':
        print("İşlem kullanıcı tarafından iptal edildi.")
        return

    guncellenen_dosya_sayisi = 0
    for dosya_adi in os.listdir(guncellenecek_etiketler_klasoru):
        if not dosya_adi.endswith('.txt') or dosya_adi == os.path.basename(kaynak_class_dosyasi_yolu): continue
        
        dosya_yolu = os.path.join(guncellenecek_etiketler_klasoru, dosya_adi)
        yeni_satirlar = []
        dosya_degisti_mi = False
        
        with open(dosya_yolu, 'r') as f:
            orijinal_satirlar = f.readlines()

        for satir in orijinal_satirlar:
            parcalar = satir.strip().split()
            if not parcalar: continue
            
            try:
                eski_index = int(parcalar[0])
                if eski_index in index_haritasi:
                    yeni_index = index_haritasi[eski_index]
                    parcalar[0] = str(yeni_index)
                    yeni_satirlar.append(" ".join(parcalar) + "\n")
                    dosya_degisti_mi = True
                else:
                    yeni_satirlar.append(satir)
            except (ValueError, IndexError):
                yeni_satirlar.append(satir)
        
        if dosya_degisti_mi:
            with open(dosya_yolu, 'w') as f:
                f.writelines(yeni_satirlar)
            guncellenen_dosya_sayisi += 1

    print("\n--- İŞLEM TAMAMLANDI ---")
    print(f"Toplam {guncellenen_dosya_sayisi} etiket dosyasının içeriği güncellendi.")

if __name__ == "__main__":
    basarili, harita, _, _ = on_kontrol_yap()
    if basarili:
        etiketleri_guncelle(harita)
    else:
        print("\nÖn kontrol başarısız olduğu için hiçbir dosya değiştirilmedi.")

