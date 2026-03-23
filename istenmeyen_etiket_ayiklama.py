import os
import glob
import shutil

# --- BU ALANLARI KENDİ BİLGİLERİNİZE GÖRE DÜZENLEYİN ---

# Veri setinizin ana klasörü. İçinde 'images' ve 'labels' klasörleri olmalı.
dataset_base_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/Grup_1"

# Sınıf isimlerinin bulunduğu .txt dosyasının yolu
classes_file_path = r"/Users/denizhan/Desktop/MakeleProjesi/zaman_damgali_frameler/class.txt"

# SAKLAMAK İSTEDİĞİNİZ ETİKETLERİN LİSTESİ
# classes.txt dosyanızdaki isimlerle birebir aynı olmalı.
etiketleri_sakla = ["atesli_silah", "kesici_alet", "kilic", "patlayici"]

# İstenmeyen verilerin taşınacağı YENİ klasörün adı
# Bu klasör, 'dataset_base_path' içinde oluşturulacaktır.
hedef_klasor_adi = "istenmeyen_veriler"

# --- KODUN GERİ KALANINI DEĞİŞTİRMENİZE GEREK YOK ---


def sinif_isimlerini_oku(dosya_yolu):
    """Sınıf dosyasını okur ve sınıf isimlerinin bir listesini döndürür."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"HATA: Sınıf dosyası bulunamadı! Yol: {dosya_yolu}")
        return None

def filtrele_ve_tasi():
    """Veri setini, istenen etiketlere göre ayıklar ve istenmeyenleri taşır."""
    
    # Kaynak klasör yollarını oluştur
    source_labels_path = os.path.join(dataset_base_path, "labels")
    source_images_path = os.path.join(dataset_base_path, "images")

    # Hedef (istenmeyen veriler) klasör yollarını oluştur
    target_base_path = os.path.join(dataset_base_path, hedef_klasor_adi)
    target_labels_path = os.path.join(target_base_path, "labels")
    target_images_path = os.path.join(target_base_path, "images")

    if not os.path.isdir(source_labels_path) or not os.path.isdir(source_images_path):
        print(f"HATA: '{dataset_base_path}' içinde 'images' ve 'labels' klasörleri bulunamadı.")
        return

    # Hedef klasörleri oluştur (eğer yoksa)
    os.makedirs(target_labels_path, exist_ok=True)
    os.makedirs(target_images_path, exist_ok=True)
    print(f"İstenmeyen veriler '{target_base_path}' klasörüne taşınacak.")

    all_classes = sinif_isimlerini_oku(classes_file_path)
    if not all_classes:
        return

    try:
        saklanacak_indeksler = {all_classes.index(isim) for isim in etiketleri_sakla}
    except ValueError as e:
        print(f"HATA: 'etiketleri_sakla' listesindeki bir etiket sınıf dosyasında bulunamadı: {e}")
        return

    print(f"Saklanacak etiketler: {', '.join(etiketleri_sakla)}")
    print("-------------------------------------------")
    
    tasinan_dosya_sayisi = 0
    degistirilen_dosya_sayisi = 0
    toplam_label_dosyasi = 0

    # Tüm etiket dosyalarını tara
    for label_filename in os.listdir(source_labels_path):
        if not label_filename.endswith(".txt"):
            continue

        toplam_label_dosyasi += 1
        label_filepath_source = os.path.join(source_labels_path, label_filename)
        
        with open(label_filepath_source, 'r') as f:
            lines = f.readlines()

        saklanacak_satirlar = []
        for line in lines:
            try:
                class_index = int(line.split()[0])
                if class_index in saklanacak_indeksler:
                    saklanacak_satirlar.append(line)
            except (ValueError, IndexError):
                continue
        
        # Durum 1: Dosyada saklanacak etiket yoksa, dosyayı ve resmi TAŞI
        if not saklanacak_satirlar:
            # Etiket dosyasını taşı
            shutil.move(label_filepath_source, os.path.join(target_labels_path, label_filename))
            
            # İlgili resmi bul ve taşı
            base_name = os.path.splitext(label_filename)[0]
            image_files = glob.glob(os.path.join(source_images_path, base_name + '.*'))
            for img_file in image_files:
                shutil.move(img_file, os.path.join(target_images_path, os.path.basename(img_file)))
                print(f"TAŞINDI: {os.path.basename(label_filename)} ve {os.path.basename(img_file)}")
            
            tasinan_dosya_sayisi += 1

        # Durum 2: Dosya içeriği değiştiyse (istenmeyen etiketler çıkarıldıysa) dosyayı GÜNCELLE
        elif len(saklanacak_satirlar) < len(lines):
            with open(label_filepath_source, 'w') as f:
                f.writelines(saklanacak_satirlar)
            print(f"DEĞİŞTİRİLDİ: {label_filename} (istenmeyen etiketler temizlendi)")
            degistirilen_dosya_sayisi += 1

    print("\n--- İşlem Tamamlandı ---")
    print(f"Toplam {toplam_label_dosyasi} etiket dosyası incelendi.")
    print(f"'{hedef_klasor_adi}' klasörüne taşınan resim/etiket çifti: {tasinan_dosya_sayisi}")
    print(f"İçeriği güncellenerek korunan etiket dosyası: {degistirilen_dosya_sayisi}")
    print("--------------------------")


if __name__ == "__main__":
    filtrele_ve_tasi()


"""

1.  **Kaydedin:** Yukarıdaki kodu `veri_seti_ayikla.py` adıyla projenizin olduğu yere veya istediğiniz bir yere kaydedin.
2.  **Yolları Düzenleyin:** Kodun en üstündeki dört değişkeni kendi projenize göre güncelleyin:
    * `dataset_base_path`: Veri setinizin ana klasörünün yolu.
    * `classes_file_path`: `class.txt` dosyanızın yolu.
    * `etiketleri_sakla`: **En önemli kısım.** Veri setinizde kalmasını istediğiniz etiketlerin isimlerini listeye yazın.
    * `hedef_klasor_adi`: İstenmeyen verilerin taşınacağı klasörün ne olarak adlandırılacağını belirtin. Bu klasör, `dataset_base_path` içinde otomatik olarak oluşturulacaktır.
3.  **Çalıştırın:** Terminali açın, betiğin bulunduğu dizine gidin ve şu komutu çalıştırın:

    python veri_seti_ayikla.py

"""

### Nasıl Kullanılır?

    
