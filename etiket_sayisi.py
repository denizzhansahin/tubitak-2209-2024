import os
from collections import Counter

# --- BU ALANLARI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Etiket (.txt) dosyalarının bulunduğu ana klasörün yolu
# Bu klasörün içindeki alt klasörler de otomatik olarak taranacaktır.
dataset_klasoru = r"/Users/denizhan/Desktop/MakeleProjesi/gercek_zaman_damgali_frameler"

# Sınıf isimlerinin bulunduğu .txt dosyasının yolu (genellikle classes.txt veya names.txt)
sinif_dosyasi = r"/Users/denizhan/Desktop/MakeleProjesi/class.txt"

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---

def sinif_isimlerini_oku(dosya_yolu):
    """
    Verilen yoldaki sınıf dosyasını okur ve sınıf isimlerinin bir listesini döndürür.
    Dosyadaki her satır bir sınıf ismini temsil eder.
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            siniflar = [line.strip() for line in f.readlines()]
        print(f"'{os.path.basename(dosya_yolu)}' dosyasından {len(siniflar)} adet sınıf ismi başarıyla okundu.")
        return siniflar
    except FileNotFoundError:
        print(f"HATA: Sınıf dosyası bulunamadı! Yol: {dosya_yolu}")
        return None
    except Exception as e:
        print(f"Sınıf dosyası okunurken bir hata oluştu: {e}")
        return None

def etiketleri_say(ana_klasor, sinif_sayisi):
    """
    Belirtilen ana klasör ve tüm alt klasörlerindeki .txt uzantılı etiket 
    dosyalarını tarar ve her bir sınıf indeksinin kaç kez geçtiğini sayar.
    """
    etiket_sayilari = Counter()
    toplam_dosya = 0

    print(f"\n'{ana_klasor}' dizinindeki etiketler taranıyor...")

    for kok_dizin, alt_dizinler, dosyalar in os.walk(ana_klasor):
        for dosya_adi in dosyalar:
            # Sadece .txt dosyalarını ve sınıf dosyasının kendisini hariç tutarak işlem yap
            if dosya_adi.endswith('.txt') and os.path.basename(sinif_dosyasi) != dosya_adi:
                dosya_yolu = os.path.join(kok_dizin, dosya_adi)
                toplam_dosya += 1
                try:
                    with open(dosya_yolu, 'r') as f:
                        for satir in f:
                            # Satırın başındaki sınıf indeksini al
                            parcalar = satir.split()
                            if parcalar:
                                sinif_indeksi = int(parcalar[0])
                                # Geçerli bir indeks olup olmadığını kontrol et
                                if 0 <= sinif_indeksi < sinif_sayisi:
                                    etiket_sayilari[sinif_indeksi] += 1
                                else:
                                    print(f"UYARI: '{dosya_adi}' içinde geçersiz sınıf indeksi bulundu: {sinif_indeksi}")
                except Exception as e:
                    print(f"HATA: '{dosya_adi}' dosyası okunurken bir sorun oluştu: {e}")

    print(f"{toplam_dosya} adet etiket dosyası tarandı.")
    return etiket_sayilari

def sonuclari_goster(sayilar, sinif_isimleri):
    """
    Sayılan etiketleri sınıf isimleriyle eşleştirir ve düzenli bir şekilde ekrana yazdırır.
    """
    if not sayilar:
        print("\nHiç etiket bulunamadı. Klasör yolunu ve dosya yapısını kontrol edin.")
        return

    print("\n--- VERİ SETİ ETİKET DAĞILIMI ---")
    toplam_etiket = 0
    for i, sinif_adi in enumerate(sinif_isimleri):
        sayi = sayilar[i]
        print(f"{sinif_adi.ljust(20)}: {sayi} adet")
        toplam_etiket += sayi
    
    print("-----------------------------------")
    print(f"{'TOPLAM'.ljust(20)}: {toplam_etiket} adet")
    print("-----------------------------------")


if __name__ == "__main__":
    siniflar = sinif_isimlerini_oku(sinif_dosyasi)
    
    if siniflar:
        sayim_sonuclari = etiketleri_say(dataset_klasoru, len(siniflar))
        sonuclari_goster(sayim_sonuclari, siniflar)
